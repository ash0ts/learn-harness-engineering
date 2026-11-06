import {spawn} from 'node:child_process';
import {readFile, mkdir, readdir} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {randomUUID, createHash} from 'node:crypto';
import {Budget, estimate} from './budget.js';
import {config, requireLive, requirePrivateProject} from './config.js';
import {courseRoot, readTask, sourceHead} from './staging.js';
import {protocol} from './trial.js';
import {writeJson, type TrialRecord} from './records.js';

export function balancedOrder(variants: string[], repeat: number) {
  const offset=(repeat-1)%variants.length;return [...variants.slice(offset),...variants.slice(0,offset)];
}
async function child(executable: string, args: string[], logfile?: string) {
  const {open}=await import('node:fs/promises');const file=logfile?await open(logfile,'a',0o600):undefined;
  try {
    return await new Promise<number>((resolve,reject)=>{
      const process=spawn(executable,args,{cwd:courseRoot,stdio:['ignore',file?.fd??'inherit',file?.fd??'inherit']});
      process.on('error',reject);process.on('close',code=>resolve(code??1));
    });
  } finally {await file?.close();}
}
export async function compare(options: {project?:string;variant?:string;repeats?:number;execute?:boolean;output?:string;source?:string;resumePatch?:string;trialId?:string;verificationFeedback?:string}) {
  const c=config(),p=await protocol();
  const output=resolve(options.output??join(courseRoot,'forge/local-results'));
  const source=options.source??await sourceHead();
  const tasks=await Promise.all((options.project?[options.project]:[1,2,3,4,5,6].map(n=>`project-0${n}`)).map(readTask));
  if(options.verificationFeedback && tasks.some(t=>!['project-07','project-08'].includes(t.id)))throw new Error('Retry feedback is restricted to the loop and graph exercises');
  const repeats=options.repeats??p.repeats;
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
  const qualifications=await Promise.all((await readdir(output)).filter(name=>name.startsWith('qualification-')).map(async name=>{
    try{return JSON.parse(await readFile(join(output,name,'qualification.json'),'utf8'));}catch{return null;}
  }));
  if(!qualifications.some(q=>q?.passed && q.protocolSha256===plan.protocolSha256))throw new Error('Run doctor --qualify --execute for the frozen protocol before paid comparisons');
  await writeJson(join(output,`campaign-${campaignId}.json`),plan);
  const budget=new Budget(join(output,'budget.json'),c.budgetUsd);
  const completed:TrialRecord[]=[];
  let stopReason:string|undefined;
  for(const block of plan.blocks) {
    const task=await readTask(block.project);
    if(block.variants.some(v=>!task.variants.includes(v)))throw new Error('Invalid treatment');
    const trials=block.variants.map(variant=>({id:options.trialId??randomUUID(),project:block.project,variant,trial:block.repeat,sourceCommit:source,output,ledger:budget.file,resumePatch:options.resumePatch,verificationFeedback:options.verificationFeedback}));
    try {await budget.reserve(Object.fromEntries(trials.map(t=>[t.id,reserve])));}
    catch(error){stopReason=String(error);break;}
    for(let offset=0;offset<trials.length;offset+=2) {
      const batch=trials.slice(offset,offset+2);
      const results=await Promise.all(batch.map(async trial=>{
        await mkdir(join(output,trial.id),{recursive:true});
        const code=await child(process.execPath,['--import',join(courseRoot,'forge/node_modules/tsx/dist/loader.mjs'),join(courseRoot,'forge/src/worker.ts'),JSON.stringify(trial)],join(output,trial.id,'worker.log'));
        try {return JSON.parse(await readFile(join(output,trial.id,'trial.json'),'utf8')) as TrialRecord;}
        catch {return {schemaVersion:1,...trial,model:c.model,startedAt:new Date().toISOString(),outcome:'infrastructure_failed',conversationIds:[],inputTokens:null,outputTokens:null,estimatedCostUsd:null,evidence:[],error:`Worker exited ${code} without a trial record`} as TrialRecord;}
      }));
      for(const record of results) {
        await budget.settle(record.id,record.estimatedCostUsd);
        const trialFile=join(output,record.id,'trial.json');await writeJson(trialFile,record);
        if(record.wandbRunId) {
          const logged=await child('uv',['run','--script',join(courseRoot,'forge/scripts/models.py'),trialFile],join(output,record.id,'models.log'));
          if(logged!==0){record.error=`${record.error??''}\nW&B Models upload failed; local evidence retained`;stopReason='Missing Models telemetry';}
        }
        completed.push(record);
        console.log(JSON.stringify({id:record.id,project:record.project,variant:record.variant,outcome:record.outcome,cost:record.estimatedCostUsd}));
        if(record.estimatedCostUsd===null)stopReason='Unknown usage or infrastructure state; paid launches stopped';
      }
      if(stopReason)break;
    }
    if(stopReason)break;
  }
  const report={...plan,completed,stopReason:stopReason??null,completedTrials:completed.length,
    estimatedCostUsd:completed.some(r=>r.estimatedCostUsd===null)?null:completed.reduce((a,b)=>a+b.estimatedCostUsd!,0)};
  await writeJson(join(output,`report-${campaignId}.json`),report);return report;
}
