import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {mkdtemp,readFile,writeFile,mkdir,symlink,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,relative} from 'node:path';
import {randomUUID} from 'node:crypto';
import {materializeSnapshot} from './workshop-stage.js';
import {workshopCourseRoot} from './workshop-workspace.js';
import {writeJson,redact} from './records.js';
import type {WorkshopManifest,WorkshopSnapshot,WorkshopResult} from './workshop-contract.js';
const exec=promisify(execFile);

/** No provider credentials, inference, notebook or sandbox launch. */
export async function checkWorkshop(snapshot:WorkshopSnapshot,manifest:WorkshopManifest,output:string){
  const id=randomUUID(),dir=join(output,id);await mkdir(dir,{recursive:true});
  // Vite 6's HTML proxy cache cannot resolve a C: workspace through dependencies
  // junctioned from D:. Keep Windows scratch builds on the runner's volume.
  // This remains an isolated directory, never the pinned source or student draft.
  const scratchRoot=process.platform==='win32'?join(workshopCourseRoot,'forge/local-results/check-workspaces'):tmpdir();
  await mkdir(scratchRoot,{recursive:true});
  const temp=await mkdtemp(join(scratchRoot,'workshop-check-'));
  const checks:WorkshopResult['checks']=[];
  const env={...process.env};for(const key of Object.keys(env))if(/(?:KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)/i.test(key))delete env[key];
  const record:WorkshopResult={schemaVersion:1,protocol:'workshop-v1',id,project:snapshot.project,snapshotId:snapshot.id,snapshotSha256:snapshot.sha256,sourceCommit:snapshot.sourceCommit,action:'check',startedAt:new Date().toISOString(),outcome:'task_failed',checks,evidence:[],conversationIds:[],sandboxIds:[],cleanupStatus:'pending',telemetryStatus:'not_requested',publicationStatus:'local',estimatedCostUsd:0};
  try{
    await materializeSnapshot(snapshot,manifest,temp);
    await symlink(join(workshopCourseRoot,'forge/workshop/base/node_modules'),join(temp,'node_modules'),process.platform==='win32'?'junction':'dir');
    for(const [name,args]of [['TypeScript and app build',['scripts/build.cjs']],['Focused lesson checks',['scripts/check.cjs']]] as const){
      try{const result=await exec(process.execPath,[...args],{cwd:temp,env,timeout:120000,maxBuffer:2_000_000});await writeFile(join(dir,name.startsWith('TypeScript')?'build.log':'checks.log'),result.stdout+result.stderr);checks.push({name,passed:true});}
      catch(error:any){await writeFile(join(dir,name.startsWith('TypeScript')?'build.log':'checks.log'),redact(String(error.stdout??'')+String(error.stderr??'')+String(error),[temp,workshopCourseRoot]));checks.push({name,passed:false,detail:'See saved build/check output'});if(name.startsWith('TypeScript'))break;}
    }
    try{const focused=JSON.parse(await readFile(join(temp,'.workshop-evidence/local-check.json'),'utf8'));checks.push(...focused.checks);await writeJson(join(dir,'local-check.json'),focused);}catch{}
    if(snapshot.project==='project-05'&&checks.length>1){
      await writeJson(join(dir,'evaluation-checks.json'),{checks});
      try{await exec(process.env.WORKSHOP_PYTHON??(process.platform==='win32'?'python':'python3'),[join(workshopCourseRoot,'forge/graders/workshop-evaluation.py'),join(temp,'workshop/evaluation.py'),join(dir,'evaluation-checks.json'),join(dir,'student-evaluation.json')],{env,timeout:15000,maxBuffer:100000});checks.push({name:'Student evaluation and W&B log call',passed:true});}
      catch(error){checks.push({name:'Student evaluation and W&B log call',passed:false,detail:redact(String(error),[temp,workshopCourseRoot])});}
    }
    record.outcome=checks.every(c=>c.passed)?'passed':'task_failed';
  }finally{await rm(temp,{recursive:true,force:true});record.cleanupStatus='verified';record.finishedAt=new Date().toISOString();record.evidence=[relative(output,join(dir,'build.log')),relative(output,join(dir,'checks.log'))];await writeJson(join(dir,'result.json'),record);}
  return record;
}
