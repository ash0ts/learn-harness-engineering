import {mkdtemp,mkdir,writeFile,readFile,rm,symlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,dirname,resolve} from 'node:path';
import {createRequire} from 'node:module';
import {validateSnapshot,workshopPath,type WorkshopManifest,type WorkshopSnapshot} from './workshop-contract.js';
import {workshopCourseRoot} from './workshop-workspace.js';

/** Portable USTAR writer: UTF-8 regular files only, no shell/tar dependency on laptops. */
export function workshopTar(files:Record<string,string|Uint8Array>){
  const parts:Buffer[]=[];
  for(const [name,value]of Object.entries(files).sort()){
    workshopPath(name);if(Buffer.byteLength(name)>100)throw new Error('Archive name is too long');
    const data=Buffer.from(value),header=Buffer.alloc(512);
    const field=(offset:number,length:number,value:string)=>header.write(value,offset,length,'ascii');
    header.write(name,0,100,'utf8');field(100,8,'0000600\0');field(108,8,'0000000\0');field(116,8,'0000000\0');
    field(124,12,data.length.toString(8).padStart(11,'0')+'\0');field(136,12,'00000000000\0');
    header.fill(32,148,156);field(156,1,'0');field(257,6,'ustar\0');field(263,2,'00');
    const sum=header.reduce((a,b)=>a+b,0);field(148,8,sum.toString(8).padStart(6,'0')+'\0 ');
    parts.push(header,data,Buffer.alloc((512-data.length%512)%512));
  }
  parts.push(Buffer.alloc(1024));return Buffer.concat(parts);
}
export async function materializeSnapshot(snapshot:WorkshopSnapshot,manifest:WorkshopManifest,root:string){
  validateSnapshot(snapshot,manifest,[process.env.WANDB_API_KEY??'']);
  await mkdir(root,{recursive:true});
  for(const [name,content]of Object.entries(snapshot.files)){const file=join(root,name);await mkdir(dirname(file),{recursive:true});await writeFile(file,content);}
  await writeFile(join(root,'workshop.json'),JSON.stringify(manifest,null,2));
}
export async function bundleWorkshop(snapshot:WorkshopSnapshot,manifest:WorkshopManifest){
  const temp=await mkdtemp(join(tmpdir(),'workshop-bundle-'));
  try{
    await materializeSnapshot(snapshot,manifest,temp);
    const modules=join(workshopCourseRoot,'forge/workshop/base/node_modules');
    await symlink(modules,join(temp,'node_modules'),process.platform==='win32'?'junction':'dir');
    const require=createRequire(join(modules,'../package.json'));
    const esbuild=require('esbuild');
    const app=await esbuild.build({entryPoints:[join(temp,'scripts/live-entry.ts')],bundle:true,platform:'node',format:'cjs',target:'node22',write:false,logLevel:'silent'});
    const sdk=await esbuild.build({entryPoints:[join(temp,'workshop/sandbox-task.ts')],bundle:true,platform:'node',format:'esm',target:'node22',write:false,logLevel:'silent'});
    return {app:Buffer.from(app.outputFiles[0].contents),sdk:Buffer.from(sdk.outputFiles[0].contents)};
  }finally{await rm(temp,{recursive:true,force:true});}
}
export async function stageWorkshop(snapshot:WorkshopSnapshot,manifest:WorkshopManifest){
  validateSnapshot(snapshot,manifest,[process.env.WANDB_API_KEY??'']);
  return workshopTar({...snapshot.files,'workshop.json':JSON.stringify(manifest,null,2)});
}
