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

export async function workshopCLI(args:string[]){
  const command=args[0];
  const {values:v}=parseArgs({args:args.slice(1),options:{project:{type:'string'},workspace:{type:'string'},source:{type:'string'},output:{type:'string'},input:{type:'string'},artifact:{type:'string'},candidate:{type:'boolean'},edits:{type:'string'},parent:{type:'string'},snapshot:{type:'string'},'operation-id':{type:'string'},scenario:{type:'string'},fixture:{type:'string'},question:{type:'string'},execute:{type:'boolean'},live:{type:'boolean'},apply:{type:'boolean'},assisted:{type:'boolean'},'single-role':{type:'boolean'},'no-publish':{type:'boolean'}}});
  if(!v.workspace)throw new Error('workshop requires --workspace DIRECTORY');
  const workspace=resolve(v.workspace),output=resolve(v.output??join(workspace,'.workshop-evidence'));
  if(command==='init'){if(!v.project)throw new Error('Choose --project project-01 through project-08');return initWorkshop(v.project as WorkshopProject,workspace,v.source);}
  const manifest=await readManifest(workspace);
  if(command==='inspect')return {manifest,files:await readWorkshopFiles(workspace,manifest)};
  if(command==='import'){
    if(v.artifact){
      if(v.input)throw new Error('Choose --artifact or --input');
      const temp=await mkdtemp(join(tmpdir(),'workshop-retrieve-'));
      try{
        const file=join(temp,'snapshot.json');
        await promisify(execFile)('uv',['run','--script',join(workshopCourseRoot,'forge/scripts/workshop_artifact.py'),v.artifact,v.candidate?'candidate.json':'submission.json',file],{cwd:workshopCourseRoot,timeout:120000,maxBuffer:1_000_000});
        // The same allowlist, source revision and checksum validation applies
        // to local uploads and authenticated artifact retrieval.
        return await importWorkshop(workspace,file,v.apply);
      }finally{await rm(temp,{recursive:true,force:true});}
    }
    if(!v.input)throw new Error('import requires --input snapshot.json or --artifact trial-ID:vN');
    return importWorkshop(workspace,resolve(v.input),v.apply);
  }
  if(command==='save'){
    if(!v.edits)throw new Error('save requires --edits FILE containing edited file contents');
    const edits=JSON.parse(await readFile(resolve(v.edits),'utf8'));await writeWorkshopEdits(workspace,manifest,edits);
  }
  const snapshot=v.snapshot?validateSnapshot(JSON.parse(await readFile(resolve(v.snapshot),'utf8')),manifest):await snapshotWorkshop(workspace,output,{parent:v.parent,assisted:v.assisted});
  if(['save','export'].includes(command)){
    if(command==='export'&&!v.input)throw new Error('export requires --input DESTINATION.json');
    if(command==='export')await writeJson(resolve(v.input!),snapshot);
    return {snapshot,diff:await workshopDiff(workspace,snapshot)};
  }
  if(command==='check')return checkWorkshop(snapshot,manifest,output);
  if(!['scenario','agent','resume'].includes(command))throw new Error('workshop: init | inspect | save | check | scenario | agent | resume | export | import');
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
  const request=join(dir,'request.json');await writeJson(request,{manifest,snapshot,options:{id,action:command,output,live:v.live,scenario:v.scenario,fixture:v.fixture,question:v.question,singleRole:v['single-role']}});
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
