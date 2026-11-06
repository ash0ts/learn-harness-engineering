import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {mkdtemp, mkdir, writeFile, readFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, dirname, resolve} from 'node:path';
import {createHash} from 'node:crypto';

const exec = promisify(execFile);
export const courseRoot = resolve(import.meta.dirname,'../..');
export interface Task {schemaVersion:1; id:string; starter:string; task:string; variants:string[]; repeats:number; sessions:number; protectedChecker:string; fixture:string; gradeAs?:string}
export async function readTask(id: string): Promise<Task> {
  if (!/^project-0[1-8]$/.test(id)) throw new Error('Unknown project');
  return JSON.parse(await readFile(join(courseRoot,'forge/tasks',`${id}.json`),'utf8'));
}
export async function sourceHead() {return (await exec('git',['rev-parse','HEAD'],{cwd:courseRoot})).stdout.trim();}
export async function stageTask(task: Task, variant: string, source: string) {
  if (!task.variants.includes(variant)) throw new Error('Unknown treatment');
  if (!/^[a-f0-9]{40}$/.test(source)) throw new Error('Freeze an exact source commit');
  const dir=await mkdtemp(join(tmpdir(),'forge-stage-')); const hash=createHash('sha256');
  try {
    const {stdout} = await exec('git',['ls-tree','-r','--name-only',source,'--',task.starter],{cwd:courseRoot});
    const files=stdout.trim().split('\n').sort().filter(file => {
      const relative=file.slice(task.starter.length+1);
      return relative.startsWith('src/') || /^(package\.json|tsconfig(\.node)?\.json|vite\.config\.ts|scripts\/dev\.js)$/.test(relative);
    });
    if (!files.length) throw new Error('No frozen application files');
    for (const file of files) {
      const rel=file.slice(task.starter.length+1);
      const {stdout: content}=await exec('git',['show',`${source}:${file}`],{cwd:courseRoot,maxBuffer:5e6});
      hash.update(rel+'\0'+content+'\0');
      const destination=join(dir,rel); await mkdir(dirname(destination),{recursive:true}); await writeFile(destination,content);
    }
    // Shared build compatibility, not a task solution. Preserve offline starters.
    // Include both the adaptation and its package changes in the baseline hash.
    const {stdout:bundler}=await exec('git',['show',`${source}:forge/fixtures/build-preload.cjs`],{cwd:courseRoot});
    await mkdir(join(dir,'scripts'),{recursive:true});
    await writeFile(join(dir,'scripts/forge-build-preload.cjs'),bundler);
    const pkg=JSON.parse(await readFile(join(dir,'package.json'),'utf8'));
    pkg.scripts.build='tsc -p tsconfig.node.json && node scripts/forge-build-preload.cjs && vite build';
    const packageSource=JSON.stringify(pkg,null,2)+'\n';await writeFile(join(dir,'package.json'),packageSource);
    hash.update('forge-runtime-overlay\0'+bundler+'\0'+packageSource+'\0');
    await mkdir(join(dir,'fixtures')); await writeFile(join(dir,'fixtures/course.txt'),await readFile(join(courseRoot,task.fixture)));
    await writeFile(join(dir,'TASK.md'),task.task+'\n');
    if (!['minimal','single-role'].includes(variant)) {
      await writeFile(join(dir,'AGENTS.md'),`# Course task\nRead TASK.md. Inspect before editing. Preserve main/preload/renderer boundaries. Work one acceptance criterion at a time. Run npm run check and npm run build. Test actual services and Electron; never claim success from simulated output. Record incomplete work honestly.\n${['recovery','workspace-docs','capstone'].includes(variant) ? 'Before ending each session, write session-handoff.md with completed work, failing checks, next steps and exact file paths. Read that file first on resume.' : ''}\n`);
      await mkdir(join(dir,'docs'));
      await writeFile(join(dir,'docs/ARCHITECTURE.md'),'# Architecture\nMain owns filesystem and services. Preload exposes typed IPC. Renderer uses window.knowledgeBase only. Data lives in PersistenceService. Import, indexing and QA are separate services. Test with the sample document in fixtures/.\n');
    }
    if (variant === 'runtime-feedback') {
      await writeFile(join(dir,'runtime-feedback.cjs'),"const {PersistenceService}=require('./dist/services/persistence-service');const {DocumentService}=require('./dist/services/document-service');const {IndexingService}=require('./dist/services/indexing-service');const fs=require('fs');const p=new PersistenceService(fs.mkdtempSync('/tmp/feedback-'));const d=new DocumentService(p);d.importDocument(require('path').resolve('fixtures/course.txt'));const i=new IndexingService(p);i.startIndexing().then(()=>console.log(JSON.stringify({chunks:i.getAllChunks(),status:i.getStatus()})));\n");
      await writeFile(join(dir,'FEEDBACK.md'),'Build the app, then run node runtime-feedback.cjs. Inspect actual chunks and indexing status.\n');
    }
    const tar=join(dir,'..',`${dir.split('/').pop()}.tar`);
    try {await exec('tar',['-cf',tar,'-C',dir,'.'],{env:{...process.env,COPYFILE_DISABLE:'1'}}); return {archive:await readFile(tar),applicationSha256:hash.digest('hex')};}
    finally {await rm(tar,{force:true});}
  } finally {await rm(dir,{recursive:true,force:true});}
}
