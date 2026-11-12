import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {mkdir,readFile,writeFile,lstat} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {writeJson} from './records.js';
import {makeSnapshot,readWorkshopFiles,safeWorkshopPath,sha256,storeSnapshot,validateSnapshot,writeWorkshopEdits,type WorkshopManifest,type WorkshopProject,type WorkshopSnapshot} from './workshop-contract.js';
const exec=promisify(execFile);
export const workshopCourseRoot=resolve(import.meta.dirname,'../..');
export async function workshopHead(){return (await exec('git',['rev-parse','HEAD'],{cwd:workshopCourseRoot})).stdout.trim();}
async function frozen(source:string,path:string){return (await exec('git',['show',`${source}:${path}`],{cwd:workshopCourseRoot,maxBuffer:8_000_000})).stdout;}
const templates=new Map<string,Promise<{manifest:WorkshopManifest;files:Record<string,string>}>>();
export async function workshopTemplate(project:WorkshopProject,source:string){
  const key=`${source}:${project}`;
  if(!templates.has(key))templates.set(key,loadTemplate(project,source).catch(error=>{templates.delete(key);throw error;}));
  return structuredClone(await templates.get(key)!);
}
async function loadTemplate(project:WorkshopProject,source:string){
  if(!/^[a-f0-9]{40}$/.test(source))throw new Error('Pin a complete source commit');
  const lessons=JSON.parse(await frozen(source,'forge/workshop/lessons.json'));
  const lesson=lessons.find((l:any)=>l.project===project);if(!lesson)throw new Error('Choose workshop project-01 through project-05');
  const prefix='forge/workshop/base/';
  const files:Record<string,string>={};
  const list=(await exec('git',['ls-tree','-r','--name-only',source,'--',prefix],{cwd:workshopCourseRoot})).stdout.trim().split('\n');
  for(const path of list.filter(Boolean))files[path.slice(prefix.length)]=await frozen(source,path);
  Object.assign(files,lesson.overlays);files['TASK.md']=lesson.task+'\n';
  const {overlays:_,...spec}=lesson;
  const manifest:WorkshopManifest={...spec,sourceCommit:source,files:Object.fromEntries(Object.entries(files).map(([name,value])=>[name,sha256(value)]))};
  return {manifest,files};
}
export async function initWorkshop(project:WorkshopProject,workspace:string,source=undefined as string|undefined){
  source??=await workshopHead();workspace=resolve(workspace);
  const {manifest,files}=await workshopTemplate(project,source);
  await mkdir(workspace,{recursive:true});
  try {
    const existing=await readManifest(workspace);
    if(existing.project!==project||existing.sourceCommit!==source)throw new Error('Existing workspace belongs to another lesson/revision');
    return existing;
  }catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
  for(const name of Object.keys(files)){
    const path=await safeWorkshopPath(workspace,name);
    if(await lstat(path).then(()=>true,()=>false))throw new Error(`Refusing to overwrite existing file ${name}`);
  }
  for(const [name,content]of Object.entries(files)){
    const path=await safeWorkshopPath(workspace,name);await mkdir(dirname(path),{recursive:true});await writeFile(path,content);
  }
  await writeJson(join(workspace,'workshop.json'),manifest);
  return manifest;
}
export async function readManifest(workspace:string):Promise<WorkshopManifest>{
  const manifest=JSON.parse(await readFile(await safeWorkshopPath(workspace,'workshop.json'),'utf8'));
  if(manifest.protocol!=='workshop-v1'||manifest.schemaVersion!==1)throw new Error('Invalid workshop manifest');
  // Read the authoritative file list from the pinned repository, never trust a modified local allowlist.
  const expected=(await workshopTemplate(manifest.project,manifest.sourceCommit)).manifest;
  if(JSON.stringify(manifest)!==JSON.stringify(expected))throw new Error('Workshop manifest changed; restore its pinned checkpoint');
  return expected;
}
export async function snapshotWorkshop(workspace:string,evidenceRoot:string,options:{assisted?:boolean;parent?:string}={}){
  const manifest=await readManifest(workspace);
  const snapshot=makeSnapshot(manifest,await readWorkshopFiles(workspace,manifest),{...options,secrets:[process.env.WANDB_API_KEY??'']});
  await storeSnapshot(evidenceRoot,snapshot);return snapshot;
}
export async function importWorkshop(workspace:string,file:string,apply=false){
  const manifest=await readManifest(workspace),snapshot:WorkshopSnapshot=JSON.parse(await readFile(file,'utf8'));
  validateSnapshot(snapshot,manifest,[process.env.WANDB_API_KEY??'']);
  const current=await readWorkshopFiles(workspace,manifest);
  const changes=manifest.editable.filter(name=>current[name]!==snapshot.files[name]);
  if(apply)await writeWorkshopEdits(workspace,manifest,Object.fromEntries(changes.map(name=>[name,snapshot.files[name]])));
  return {project:manifest.project,sourceCommit:manifest.sourceCommit,snapshot: snapshot.id,changes,applied:apply};
}
export async function workshopDiff(workspace:string,snapshot:WorkshopSnapshot){
  const {files}=await workshopTemplate(snapshot.project,snapshot.sourceCommit);
  return Object.keys(files).filter(name=>snapshot.files[name]!==files[name]).map(name=>({path:name,before:files[name],after:snapshot.files[name]}));
}
