import {readFile} from 'node:fs/promises';
import {join,resolve,relative,isAbsolute} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {setTimeout as delay} from 'node:timers/promises';
import {writeJson,type TrialRecord} from './records.js';
import {compare} from './campaign.js';
import {sourceHead,courseRoot} from './staging.js';
import {evidenceReference,verifyEvidence,updateOperation} from './operations.js';
import {Execution} from './execution.js';
import {protocol} from './trial.js';

export type LoopMode='goal'|'timer'|'maker-checker';
export interface LoopState {
  schemaVersion:1;id:string;mode:LoopMode;sourceCommit:string;startedAt:number;deadlineAt:number;
  intervalMs:number;maxRounds:number;status:'running'|'passed'|'deadline'|'round_limit'|'no_progress'|'blocked'|'cancelled';
  rounds:Array<{trialId:string;outcome:string;patchSha256?:string;feedbackSha256?:string}>;pendingTrialId?:string;candidatePatch?:string;verificationFeedback?:string;
  checkpointVersion?:2;candidateSha256?:string;
  interventions:Array<{at:string;note:string;source:'learner'|'observed'}>;error?:string;
}
export interface LoopDriver {
  now():number;sleep(ms:number,signal?:AbortSignal):Promise<void>;
  run(id:string,state:LoopState):Promise<{record:TrialRecord;patch?:string;patchSha256?:string}>;
  recover?:(id:string,state:LoopState)=>Promise<{record:TrialRecord;patch?:string;patchSha256?:string}|null>;
}
/** A persisted pending ID never automatically retries an ambiguous paid launch. */
export async function driveLoop(file:string,state:LoopState,driver:LoopDriver,signal?:AbortSignal) {
  if(state.pendingTrialId){
    const recovered=await driver.recover?.(state.pendingTrialId,state);
    if(!recovered)throw new Error(`Reconcile pending trial ${state.pendingTrialId} before resuming`);
    state.rounds.push({trialId:state.pendingTrialId,outcome:recovered.record.outcome,patchSha256:recovered.patchSha256});
    state.verificationFeedback=JSON.stringify((recovered.record as TrialRecord&{grade?:unknown}).grade??{outcome:recovered.record.outcome,error:recovered.record.error});
    if(recovered.patch){state.candidatePatch=recovered.patch;state.candidateSha256=recovered.patchSha256;}
    delete state.pendingTrialId;
    state.interventions.push({at:new Date().toISOString(),source:'observed',note:'Recovered completed trial without rerunning the agent'});
    if(recovered.record.outcome==='passed'&&state.mode!=='timer')state.status='passed';
    else if(['passed','task_failed'].includes(recovered.record.outcome))state.status='running';
    await writeJson(file,state);
  }
  if(state.status!=='running')return state;
  await writeJson(file,state);
  try {
    while(driver.now()<state.deadlineAt && state.rounds.length<state.maxRounds) {
      signal?.throwIfAborted();
      if(state.mode==='timer') {
        const due=state.startedAt+state.rounds.length*state.intervalMs;
        if(driver.now()<due)await driver.sleep(Math.min(due,state.deadlineAt)-driver.now(),signal);
        if(driver.now()>=state.deadlineAt)break;
      }
      const id=randomUUID();state.pendingTrialId=id;await writeJson(file,state);
      const result=await driver.run(id,state);
      state.rounds.push({trialId:id,outcome:result.record.outcome,patchSha256:result.patchSha256,feedbackSha256:state.verificationFeedback?createHash('sha256').update(state.verificationFeedback).digest('hex'):undefined});
      state.verificationFeedback=JSON.stringify((result.record as TrialRecord & {grade?:unknown}).grade??{outcome:result.record.outcome,error:result.record.error});
      delete state.pendingTrialId;
      if(result.patch){state.candidatePatch=result.patch;state.candidateSha256=result.patchSha256;}
      if(['infrastructure_failed','telemetry_missing','budget_exhausted'].includes(result.record.outcome)){state.status='blocked';state.error=result.record.error;break;}
      if(result.record.outcome==='passed' && state.mode!=='timer'){state.status='passed';break;}
      if(state.mode!=='timer' && state.rounds.length>=2 && result.patchSha256===state.rounds.at(-2)?.patchSha256){state.status='no_progress';break;}
      await writeJson(file,state);
    }
    // The real timer exercise covers the full wall-clock window without idle sandboxes.
    if(state.mode==='timer' && state.status==='running' && driver.now()<state.deadlineAt)await driver.sleep(state.deadlineAt-driver.now(),signal);
    if(state.status==='running')state.status=driver.now()>=state.deadlineAt?'deadline':'round_limit';
  } catch(error) {state.status=signal?.aborted?'cancelled':'blocked';state.error=String(error);}
  finally {await writeJson(file,state);}
  return state;
}
export async function runLoop(options:{mode:LoopMode;file:string;execute:boolean;durationSeconds?:number;intervalSeconds?:number;maxRounds?:number;resume?:boolean;output?:string;operationId?:string},signal?:AbortSignal) {
  if(!['goal','timer','maker-checker'].includes(options.mode))throw new Error('Unknown loop mode');
  const duration=options.durationSeconds??(options.mode==='timer'?7200:1800);
  const interval=options.intervalSeconds??900;const maxRounds=options.maxRounds??(options.mode==='timer'?8:3);
  if(duration<=0||duration>7200||interval<=0||maxRounds<1||maxRounds>8)throw new Error('Invalid loop bounds');
  const now=Date.now();
  if(!options.resume){try{await readFile(options.file);throw new Error('Existing checkpoint retained; choose a new execution ID');}catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}}
  const state:LoopState=options.resume?JSON.parse(await readFile(options.file,'utf8')):{schemaVersion:1,checkpointVersion:2,id:options.operationId??randomUUID(),mode:options.mode,sourceCommit:await sourceHead(),startedAt:now,deadlineAt:now+duration*1000,intervalMs:interval*1000,maxRounds,status:'running',rounds:[],interventions:[]};
  if(!options.execute)return state;
  if(state.mode!==options.mode)throw new Error('Resume mode must match checkpoint');
  const output=resolve(options.output??process.env.FORGE_RESULTS_DIR??join(courseRoot,'forge/local-results'));
  if(state.sourceCommit!==await sourceHead())throw new Error('Resume requires the original pinned runner revision');
  if(relative(output,resolve(options.file)).startsWith('..'))throw new Error('Checkpoint must belong to the evidence root');
  const execution=new Execution(output,state.id,await protocol());
  if(!options.resume)await execution.begin('loop',state.sourceCommit);
  const result=await driveLoop(options.file,state,{now:Date.now,sleep:async(ms,signal)=>{while(ms>0){const step=Math.min(ms,60000);await delay(step,undefined,{signal});ms-=step;}},
    async recover(id){
      const result=await (await import('./recovery.js')).recoverOperation(output,id,true);
      if(!result.recovered)return null;
      const record=JSON.parse(await readFile(join(output,id,'trial.json'),'utf8'));
      const ref=await evidenceReference(output,join(output,id,'candidate.diff')).catch(()=>undefined);
      return {record,patch:ref?.path,patchSha256:ref?.sha256};
    },
    async run(id,s) {
      const candidate=s.candidatePatch?(isAbsolute(s.candidatePatch)?relative(output,s.candidatePatch):s.candidatePatch):undefined;
      const resumePatch=candidate?await verifyEvidence(output,{path:candidate,sha256:s.candidateSha256??s.rounds.at(-1)?.patchSha256??''}):undefined;
      const result=await compare({project:'project-07',variant:s.mode,repeats:1,execute:true,source:s.sourceCommit,output,resumePatch,trialId:id,verificationFeedback:s.verificationFeedback});
      const record=(result as {completed?:TrialRecord[]}).completed?.[0];
      if(!record)throw new Error('No trial launched: budget exhausted or qualification unavailable');
      const patch=join(output,id,'candidate.diff');
      try {const ref=await evidenceReference(output,patch);return {record,patch:ref.path,patchSha256:ref.sha256};}
      catch{return {record};}
    },
  },signal);
  const ref=await evidenceReference(output,options.file);
  await updateOperation(output,state.id,op=>{op.evidence.checkpoint=ref;op.publication='not_required';op.executionOutcome=result.status;op.phase=result.pendingTrialId?'recoverable':'completed';op.cleanup=result.pendingTrialId?'unknown':'verified';op.telemetry=result.pendingTrialId?'missing':'complete';});
  return result;
}
export async function addIntervention(file:string,note:string) {
  if(!note.trim())throw new Error('Intervention note required');
  const state:LoopState=JSON.parse(await readFile(file,'utf8'));
  state.interventions.push({at:new Date().toISOString(),note,source:'learner'});await writeJson(file,state);
}
