import {readFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {setTimeout as delay} from 'node:timers/promises';
import {writeJson,type TrialRecord} from './records.js';
import {compare} from './campaign.js';
import {sourceHead,courseRoot} from './staging.js';

export type LoopMode='goal'|'timer'|'maker-checker';
export interface LoopState {
  schemaVersion:1;id:string;mode:LoopMode;sourceCommit:string;startedAt:number;deadlineAt:number;
  intervalMs:number;maxRounds:number;status:'running'|'passed'|'deadline'|'round_limit'|'no_progress'|'blocked'|'cancelled';
  rounds:Array<{trialId:string;outcome:string;patchSha256?:string}>;pendingTrialId?:string;candidatePatch?:string;verificationFeedback?:string;
  interventions:Array<{at:string;note:string;source:'learner'|'observed'}>;error?:string;
}
export interface LoopDriver {
  now():number;sleep(ms:number,signal?:AbortSignal):Promise<void>;
  run(id:string,state:LoopState):Promise<{record:TrialRecord;patch?:string;patchSha256?:string}>;
}
/** A persisted pending ID never automatically retries an ambiguous paid launch. */
export async function driveLoop(file:string,state:LoopState,driver:LoopDriver,signal?:AbortSignal) {
  if(state.pendingTrialId)throw new Error(`Reconcile pending trial ${state.pendingTrialId} before resuming`);
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
      state.rounds.push({trialId:id,outcome:result.record.outcome,patchSha256:result.patchSha256});
      state.verificationFeedback=JSON.stringify((result.record as TrialRecord & {grade?:unknown}).grade??{outcome:result.record.outcome,error:result.record.error});
      delete state.pendingTrialId;
      if(result.patch)state.candidatePatch=result.patch;
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
export async function runLoop(options:{mode:LoopMode;file:string;execute:boolean;durationSeconds?:number;intervalSeconds?:number;maxRounds?:number;resume?:boolean;output?:string},signal?:AbortSignal) {
  if(!['goal','timer','maker-checker'].includes(options.mode))throw new Error('Unknown loop mode');
  const duration=options.durationSeconds??(options.mode==='timer'?7200:1800);
  const interval=options.intervalSeconds??900;const maxRounds=options.maxRounds??(options.mode==='timer'?8:3);
  if(duration<=0||duration>7200||interval<=0||maxRounds<1||maxRounds>8)throw new Error('Invalid loop bounds');
  const now=Date.now();
  const state:LoopState=options.resume?JSON.parse(await readFile(options.file,'utf8')):{schemaVersion:1,id:randomUUID(),mode:options.mode,sourceCommit:await sourceHead(),startedAt:now,deadlineAt:now+duration*1000,intervalMs:interval*1000,maxRounds,status:'running',rounds:[],interventions:[]};
  if(!options.execute)return state;
  if(state.mode!==options.mode)throw new Error('Resume mode must match checkpoint');
  const output=resolve(options.output??join(courseRoot,'forge/local-results'));
  return driveLoop(options.file,state,{now:Date.now,sleep:(ms,signal)=>delay(ms,undefined,{signal}),
    async run(id,s) {
      const result=await compare({project:'project-07',variant:s.mode,repeats:1,execute:true,source:s.sourceCommit,output,resumePatch:s.candidatePatch,trialId:id,verificationFeedback:s.verificationFeedback});
      const record=(result as {completed?:TrialRecord[]}).completed?.[0];
      if(!record)throw new Error('No trial launched: budget exhausted or qualification unavailable');
      const patch=join(output,id,'candidate.diff');
      try {return {record,patch,patchSha256:createHash('sha256').update(await readFile(patch)).digest('hex')};}
      catch{return {record};}
    },
  },signal);
}
export async function addIntervention(file:string,note:string) {
  if(!note.trim())throw new Error('Intervention note required');
  const state:LoopState=JSON.parse(await readFile(file,'utf8'));
  state.interventions.push({at:new Date().toISOString(),note,source:'learner'});await writeJson(file,state);
}
