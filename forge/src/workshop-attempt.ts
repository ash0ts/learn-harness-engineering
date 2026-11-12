import {parseArgs} from 'node:util';
import {readFile,mkdir,mkdtemp,rm} from 'node:fs/promises';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {randomUUID} from 'node:crypto';
import {initWorkshop,readManifest,snapshotWorkshop,workshopDiff,workshopTemplate,workshopCourseRoot} from './workshop-workspace.js';
import {writeWorkshopEdits,readWorkshopFiles,validateSnapshot,sha256,type WorkshopProject} from './workshop-contract.js';
import {importWorkshop} from './workshop-workspace.js';
import {checkWorkshop} from './workshop-local.js';
import {config} from './config.js';
import {createOperation,updateOperation,operationFile,evidenceReference} from './operations.js';
import {workshopProtocol} from './workshop-protocol.js';
import {boundedChild} from './lifecycle.js';
import {publishTrial} from './campaign.js';
import {writeJson} from './records.js';
import {Execution} from './execution.js';

import type {WorkshopManifest,WorkshopSnapshot} from './workshop-contract.js';

export async function workshopAttempt(workspace:string,output:string,manifest:WorkshopManifest,snapshot:WorkshopSnapshot,command:string,v:Record<string,any>,extra:Record<string,unknown>={}){
  const id=v['operation-id']??randomUUID();
  if(!v.execute)return {id,action:command,snapshotId:snapshot.id,sha256:snapshot.sha256,paid: true,executeRequired:true};
  if(process.platform==='win32')throw new Error('Paid worker process-tree cleanup is not qualified on Windows. Use the Forge notebook for paid runs; local dev, build, check and source exchange remain available.');
  try{const operation=JSON.parse(await readFile(operationFile(output,id),'utf8'));return {operation,launched:false,recoveryRequired:operation.phase!=='completed'};}
  catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
  process.env.FORGE_BUDGET_USD??='20';process.env.FORGE_BUDGET_MODE='incremental';
  const dir=join(output,id);await mkdir(dir,{recursive:true});const c=config(),p=await workshopProtocol();
  await createOperation(output,{id,kind:'trial',sourceCommit:snapshot.sourceCommit,protocolSha256:sha256(JSON.stringify(p)),identity:{entity:c.entity,project:c.project,owner:process.env.FORGE_NOTEBOOK_OWNER,notebook:process.env.FORGE_NOTEBOOK_ID}});
  const receipt=join(dir,'child.json');
  await updateOperation(output,id,op=>{op.events.push({event:'child_launch',at:new Date().toISOString(),detail:id+'/child.json'});});
  const request=join(dir,'request.json');await writeJson(request,{manifest,snapshot,options:{id,action:command,output,live:v.live,scenario:v.scenario,fixture:v.fixture,question:v.question,singleRole:v['single-role'],...extra}});
  const child=await boundedChild(process.execPath,['--import',join(workshopCourseRoot,'forge/node_modules/tsx/dist/loader.mjs'),join(workshopCourseRoot,'forge/src/workshop-worker.ts'),request],{cwd:workshopCourseRoot,log:join(dir,'worker.log'),receipt,timeoutMs:1250000,graceMs:120000});
  const record=JSON.parse(await readFile(join(dir,'trial.json'),'utf8'));
  const finalization=JSON.parse(await readFile(join(dir,'worker-finalization.json'),'utf8'));
  if(child.forced||child.exitCode!==0||!finalization.cleanExit){record.outcome='infrastructure_failed';record.error='Worker did not finish cleanly; inspect finalization receipt';await writeJson(join(dir,'trial.json'),record);await updateOperation(output,id,op=>{op.phase='recoverable';op.events.push({event:'worker_finalization_failed',at:new Date().toISOString()});});}
  // Reconcile after the parent has written the actual worker termination receipt.
  const operation=JSON.parse(await readFile(operationFile(output,id),'utf8'));
  const finalExecution=new Execution(output,id,p);
  for(const event of operation.events.filter((e:any)=>e.event==='sandbox_launch')){
    const label=event.detail.split('/').at(-2);finalExecution.journals.set(label,join(output,event.detail));
  }
  const settled=await finalExecution.finish(record.outcome);
  Object.assign(record,{cleanupStatus:settled.cleanupVerified?'verified':'unknown',estimatedCostUsd:settled.estimatedCostUsd});
  await writeJson(join(dir,'trial.json'),record);
  const trialRef=await evidenceReference(output,join(dir,'trial.json'));
  await updateOperation(output,id,op=>{op.evidence.trial=trialRef;});
  if(!v['no-publish'])await publishTrial(output,id);
  return JSON.parse(await readFile(join(dir,'trial.json'),'utf8'));
}
