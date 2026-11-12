import {readFile,mkdir} from 'node:fs/promises';
import {join} from 'node:path';
import {randomUUID} from 'node:crypto';
import {workshopAttempt} from './workshop-attempt.js';
import {workshopPolicy} from './workshop-policy.js';
import {safeWorkshopPath,sha256,validateSnapshot,type WorkshopManifest,type WorkshopSnapshot} from './workshop-contract.js';
import {writeJson} from './records.js';
import {publishTrial} from './campaign.js';
import {operationFile} from './operations.js';

export interface WorkshopLoopState {
  schemaVersion:1;kind:'workshop-loop';id:string;sourceCommit:string;snapshotSha256:string;
  policySha256:string;startedAt:number;deadline:number;maxRounds:number;
  status:'ready'|'running'|'stopped'|'blocked';pending?:string;
  rounds:Array<{id:string;candidateSha256:string;feedbackSha256:string;outcome:string}>;
  candidate?:WorkshopSnapshot;checks:Array<{name:string;passed:boolean}>;outcome:string;
  events:Array<{at:string;event:string;detail?:unknown}>;
}
export function loopObservation(state:WorkshopLoopState,now=Date.now()){
  return {round:state.rounds.length,maxRounds:state.maxRounds,now,deadline:state.deadline,outcome:state.outcome,checks:state.checks};
}
export function loopBound(state:WorkshopLoopState,now=Date.now()){
  return state.rounds.length>=state.maxRounds||now>=state.deadline||state.outcome==='passed';
}
export async function workshopLoop(workspace:string,output:string,manifest:WorkshopManifest,snapshot:WorkshopSnapshot,v:Record<string,any>){
  if(snapshot.project!=='project-07')throw new Error('The loop exercise belongs to Project 07');
  const id=v.controller??v['operation-id']??randomUUID();
  if(!/^[a-zA-Z0-9-]+$/.test(id))throw new Error('Invalid controller ID');
  const file=await safeWorkshopPath(output,`workshop/controllers/${id}.json`);
  let state:WorkshopLoopState;
  try{state=JSON.parse(await readFile(file,'utf8'));}
  catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;state={schemaVersion:1,kind:'workshop-loop',id,sourceCommit:snapshot.sourceCommit,snapshotSha256:snapshot.sha256,policySha256:sha256(snapshot.files['workshop/loop.ts']),startedAt:Date.now(),deadline:Date.now()+1800000,maxRounds:2,status:'ready',rounds:[],checks:[],outcome:'not_run',events:[]};}
  if(state.sourceCommit!==snapshot.sourceCommit||state.snapshotSha256!==snapshot.sha256)throw new Error('This loop is pinned to another snapshot. Inspect it before starting a new execution.');
  if(!v.execute)return {...state,paid:true,executeRequired:true};
  await mkdir(join(output,'workshop/controllers'),{recursive:true});
  if(state.pending){
    const trial=JSON.parse(await readFile(join(output,state.pending,'trial.json'),'utf8'));
    const operation=JSON.parse(await readFile(operationFile(output,state.pending),'utf8'));
    if(operation.cleanup!=='verified'||operation.telemetry!=='complete'||operation.publication!=='verified')throw new Error('Reconcile the pending round before continuing; no replacement work was launched');
    await completeRound(trial,true);return state;
  }
  if(state.status==='stopped'||state.status==='blocked')return state;
  const observation=loopObservation(state);
  const action=await workshopPolicy(snapshot.files['workshop/loop.ts'],'nextAction',observation);
  if(!['stop','run'].includes(action))throw new Error('nextAction must return run or stop');
  state.events.push({at:new Date().toISOString(),event:'student_policy',detail:{observation,action}});
  if(action==='stop'||loopBound(state)){state.status='stopped';await writeJson(file,state);return state;}
  const feedback=await workshopPolicy(snapshot.files['workshop/loop.ts'],'nextPrompt',observation);
  if(typeof feedback!=='string'||feedback.length>20000)throw new Error('nextPrompt must return a bounded string');
  const roundId=v['operation-id']??randomUUID();
  if(state.rounds.some(round=>round.id===roundId))return state;
  state.pending=roundId;state.status='running';
  state.events.push({at:new Date().toISOString(),event:'round_reserved',detail:{id:roundId,feedback,feedbackSha256:sha256(feedback),candidateSha256:state.candidate?.sha256??snapshot.sha256}});
  await writeJson(file,state);
  const candidate=state.candidate?validateSnapshot(state.candidate,manifest):snapshot;
  const trial=await workshopAttempt(workspace,output,manifest,candidate,'agent',{...v,'operation-id':roundId,'no-publish':true},{feedback,controllerId:id});
  if(!trial.id||trial.id!==roundId)throw new Error('Pending round needs recovery; no replacement launched');
  await completeRound(trial,false);
  if(!v['no-publish'])await publishTrial(output,roundId);
  return {...JSON.parse(await readFile(join(output,roundId,'trial.json'),'utf8')),controller:state};

  async function completeRound(trial:any,recovered:boolean){
    const candidate=validateSnapshot(JSON.parse(await readFile(join(output,trial.id,'candidate.json'),'utf8')),manifest);
    state.candidate=candidate;state.checks=trial.checks??[];state.outcome=trial.outcome;
    state.rounds.push({id:trial.id,candidateSha256:candidate.sha256,feedbackSha256:trial.feedbackSha256??'',outcome:trial.outcome});
    delete state.pending;
    const action=await workshopPolicy(snapshot.files['workshop/loop.ts'],'nextAction',loopObservation(state));
    if(!['run','stop'].includes(action))throw new Error('Invalid loop policy after grading');
    state.status=trial.cleanupStatus!=='verified'||trial.telemetryStatus!=='complete'||!['passed','task_failed'].includes(trial.outcome)?'blocked':action==='stop'||loopBound(state)?'stopped':'ready';
    state.events.push({at:new Date().toISOString(),event:recovered?'recovered_completed_round':'round_completed',detail:{action,hardStop:loopBound(state),next:state.status}});
    await writeJson(file,state);await writeJson(join(output,trial.id,'loop-checkpoint.json'),state);
  }
}
