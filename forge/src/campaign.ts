import {readFile, mkdir, readdir} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {randomUUID, createHash} from 'node:crypto';
import {Budget, estimate} from './budget.js';
import {config, requireLive, requirePrivateProject} from './config.js';
import {courseRoot, readTask, sourceHead} from './staging.js';
import {protocol} from './trial.js';
import {writeJson, type TrialRecord} from './records.js';
import {boundedChild} from './lifecycle.js';
import {updateOperation,evidenceReference,createOperation,operationFile} from './operations.js';

export function balancedOrder(variants: string[], repeat: number) {
  const offset=(repeat-1)%variants.length;return [...variants.slice(offset),...variants.slice(0,offset)];
}
export async function publishTrial(output:string,id:string){
  const dir=join(output,id),file=join(dir,'trial.json');
  const result=await boundedChild('uv',['run','--script',join(courseRoot,'forge/scripts/models.py'),file],{cwd:courseRoot,log:join(dir,'models.log'),receipt:join(dir,'publication-child.json'),timeoutMs:300000});
  let verified=false;
  if(result.exitCode===0&&!result.forced){try{verified=JSON.parse(await readFile(join(dir,'publication.json'),'utf8')).verified===true;}catch{}}
  const ref=await evidenceReference(output,file);
  await updateOperation(output,id,op=>{op.publication=verified?'verified':'failed';op.evidence.trial=ref;op.phase=op.cleanup==='verified'&&op.telemetry==='complete'?(verified?'completed':'recoverable'):'blocked_unknown';op.events.push({at:new Date().toISOString(),event:verified?'publication_verified':'publication_retry_required'});});
  return verified;
}
export async function compare(options: {project?:string;variant?:string;repeats?:number;execute?:boolean;output?:string;source?:string;operationId?:string}) {
  const c=config(),p=await protocol();
  const output=resolve(options.output??process.env.FORGE_RESULTS_DIR??join(courseRoot,'forge/local-results'));
  const source=options.source??await sourceHead();
  const tasks=await Promise.all((options.project?[options.project]:[1,2,3,4,5,6].map(n=>`project-0${n}`)).map(id=>readTask(id,source)));
  const repeats=options.repeats??p.repeats;
  const incremental=process.env.FORGE_BUDGET_MODE==='incremental';
  if(options.operationId&&(!options.project||!options.variant||repeats!==1))throw new Error('A stable operation ID requires exactly one selected treatment');
  if(!Number.isInteger(repeats)||repeats<1||repeats>3)throw new Error('Repeats must be 1–3');
  const reserve=estimate(p.maxInputBytes*24,4096*24,1200*2,p.pricing)*1.2;
  const campaignId=randomUUID();
  const plan={schemaVersion:1,campaignId,sourceCommit:source,protocol:p,protocolSha256:createHash('sha256').update(JSON.stringify(p)).digest('hex'),reservationPerTrialUsd:reserve,
    blocks:tasks.flatMap(task=>Array.from({length:repeats},(_,r)=>({project:task.id,repeat:r+1,
      variants:options.variant?[options.variant]:balancedOrder(task.variants,r+1)})))};
  if(!options.execute)return plan;
  requireLive(c);
  await requirePrivateProject(c);
  await mkdir(output,{recursive:true});
  if(options.operationId){
    try {const existing=JSON.parse(await readFile(operationFile(output,options.operationId),'utf8'));return {operation:existing,recoveryRequired:existing.phase!=='completed',launched:false};}
    catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
  }
  const qualifications=await Promise.all((await readdir(output)).filter(name=>name.startsWith('qualification-')).map(async name=>{
    try{return JSON.parse(await readFile(join(output,name,'qualification.json'),'utf8'));}catch{return null;}
  }));
  if(!qualifications.some(q=>q?.passed && q.protocolSha256===plan.protocolSha256))throw new Error('Run doctor --qualify --execute for the frozen protocol before paid comparisons');
  if(p.controlsRequired)await (await import('./controls.js')).requireControls(output,tasks.map(t=>t.id),source);
  await writeJson(join(output,`campaign-${campaignId}.json`),plan);
  const budget=new Budget(join(output,'budget.json'),c.budgetUsd);
  const completed:TrialRecord[]=[];
  let stopReason:string|undefined;
  for(const block of plan.blocks) {
    const task=await readTask(block.project,source);
    if(block.variants.some(v=>!task.variants.includes(v)))throw new Error('Invalid treatment');
    const trials=block.variants.map(variant=>({id:options.operationId??randomUUID(),project:block.project,variant,trial:block.repeat,sourceCommit:source,output,ledger:budget.file}));
    try {await budget.reserve(incremental?{}:Object.fromEntries(trials.map(t=>[t.id,reserve])));}
    catch(error){stopReason=String(error);break;}
    for(let offset=0;offset<trials.length;offset+=2) {
      const batch=trials.slice(offset,offset+2);
      const settledResults=await Promise.allSettled(batch.map(async trial=>{
        await mkdir(join(output,trial.id),{recursive:true});
        await createOperation(output,{id:trial.id,kind:'trial',sourceCommit:source,protocolSha256:plan.protocolSha256,identity:{entity:c.entity,project:c.project,owner:process.env.FORGE_NOTEBOOK_OWNER,notebook:process.env.FORGE_NOTEBOOK_ID}});
        const result=await boundedChild(process.execPath,['--import',join(courseRoot,'forge/node_modules/tsx/dist/loader.mjs'),join(courseRoot,'forge/src/worker.ts'),JSON.stringify(trial)],{cwd:courseRoot,log:join(output,trial.id,'worker.log'),receipt:join(output,trial.id,'child.json'),timeoutMs:1500000});
        try {
          const record=JSON.parse(await readFile(join(output,trial.id,'trial.json'),'utf8')) as TrialRecord;
          let finalized={cleanExit:false};try{finalized=JSON.parse(await readFile(join(output,trial.id,'worker-finalization.json'),'utf8'));}catch{}
          if(result.forced||result.exitCode!==0||!finalized.cleanExit){record.error=`${record.error??''}\nWorker shutdown required recovery`;record.outcome='infrastructure_failed';}
          return record;
        }
        catch {return {schemaVersion:1,...trial,model:c.model,startedAt:new Date().toISOString(),outcome:'infrastructure_failed',conversationIds:[],inputTokens:null,outputTokens:null,estimatedCostUsd:null,evidence:[],error:`Worker exited ${result.exitCode} without complete finalization evidence`} as TrialRecord;}
      }));
      const results=settledResults.map((result,index)=>result.status==='fulfilled'?result.value:{schemaVersion:1,...batch[index],model:c.model,startedAt:new Date().toISOString(),outcome:'infrastructure_failed',conversationIds:[],inputTokens:null,outputTokens:null,estimatedCostUsd:null,evidence:[],error:String(result.reason)} as TrialRecord);
      for(const record of results) {
        if(!incremental)await budget.settle(record.id,record.estimatedCostUsd);
        const trialFile=join(output,record.id,'trial.json');await writeJson(trialFile,record);const trialRef=await evidenceReference(output,trialFile);await updateOperation(output,record.id,op=>{op.evidence.trial=trialRef;});
        if(record.wandbRunId) {
          if(!await publishTrial(output,record.id))stopReason='Missing Models telemetry; recover publication without rerunning the agent';
        }
        completed.push(record);
        console.log(JSON.stringify({id:record.id,project:record.project,variant:record.variant,outcome:record.outcome,cost:record.estimatedCostUsd}));
        if(record.estimatedCostUsd===null)stopReason='Unknown usage or infrastructure state; paid launches stopped';
      }
      if(stopReason){
        // Reservations for later members of this block have no child or external
        // dispatch. Release only those IDs and record that proof explicitly.
        const unlaunched=trials.slice(offset+batch.length);
        for(const trial of unlaunched){await writeJson(join(output,trial.id,'not-launched.json'),{id:trial.id,reason:stopReason,externalLaunch:false});if(!incremental)await budget.settle(trial.id,0);}
        break;
      }
    }
    if(stopReason)break;
  }
  const report={...plan,completed,stopReason:stopReason??null,completedTrials:completed.length,
    estimatedCostUsd:completed.some(r=>r.estimatedCostUsd===null)?null:completed.reduce((a,b)=>a+b.estimatedCostUsd!,0)};
  await writeJson(join(output,`report-${campaignId}.json`),report);return report;
}
