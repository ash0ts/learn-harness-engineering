import {readFile,mkdir,open} from 'node:fs/promises';
import {join} from 'node:path';
import {randomUUID} from 'node:crypto';
import {workshopAttempt} from './workshop-attempt.js';
import {workshopPolicy} from './workshop-policy.js';
import {safeWorkshopPath,sha256,validateSnapshot,type WorkshopManifest,type WorkshopSnapshot} from './workshop-contract.js';
import {writeJson} from './records.js';
import {publishTrial} from './campaign.js';
import {operationFile} from './operations.js';
export interface WorkshopGraphState {
  schemaVersion:1;kind:'workshop-graph';id:string;sourceCommit:string;snapshotSha256:string;
  policySha256:string;node:'plan'|'verify'|'repair'|'approval'|'stopped'|'recover'|'approved'|'rejected';
  repairs:number;maxRepairs:number;pending?:{id:string;node:'verify'|'repair'};
  candidate?:WorkshopSnapshot;verifiedSha256?:string;
  trials:Array<{id:string;node:string;outcome:string;candidateSha256:string;lanes?:unknown}>;
  events:Array<{at:string;event:string;detail?:unknown}>;
}
export function enforceGraphRoute(requested:unknown,observed:{phase:string;outcome:string;repairs:number;maxRepairs:number;cleanupVerified:boolean;usageComplete:boolean}){
  if(!['verify','repair','approval','stop','recover'].includes(String(requested)))throw new Error('Unknown graph route');
  if(!observed.cleanupVerified||!observed.usageComplete)return 'recover';
  if(requested==='approval'&&observed.outcome!=='passed')throw new Error('Approval requires a verified candidate; the student route cannot bypass checks');
  if(requested==='repair'&&observed.repairs>=observed.maxRepairs)return 'stop';
  if(observed.phase==='plan'&&requested!=='verify')throw new Error('Verify the starting snapshot before choosing another graph route');
  return requested as 'verify'|'repair'|'approval'|'stop'|'recover';
}
export async function workshopGraph(workspace:string,output:string,manifest:WorkshopManifest,snapshot:WorkshopSnapshot,v:Record<string,any>){
  if(snapshot.project!=='project-08')throw new Error('The graph exercise belongs to Project 08');
  const id=v.controller??v['operation-id']??randomUUID();
  if(!/^[a-zA-Z0-9-]+$/.test(id))throw new Error('Invalid graph ID');
  const file=await safeWorkshopPath(output,`workshop/controllers/${id}.json`);
  let state:WorkshopGraphState;
  try{state=JSON.parse(await readFile(file,'utf8'));}
  catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;state={schemaVersion:1,kind:'workshop-graph',id,sourceCommit:snapshot.sourceCommit,snapshotSha256:snapshot.sha256,policySha256:sha256(snapshot.files['workshop/graph.ts']),node:'plan',repairs:0,maxRepairs:2,trials:[],events:[]};}
  if(state.sourceCommit!==snapshot.sourceCommit||state.snapshotSha256!==snapshot.sha256)throw new Error('This graph is pinned to another snapshot; decide any pending approval before starting a new graph.');
  if(!v.execute)return {...state,paid:true,executeRequired:true};
  await mkdir(join(output,'workshop/controllers'),{recursive:true});
  if(state.pending){
    const trial=JSON.parse(await readFile(join(output,state.pending.id,'trial.json'),'utf8'));
    const operation=JSON.parse(await readFile(operationFile(output,state.pending.id),'utf8'));
    if(operation.cleanup!=='verified'||operation.telemetry!=='complete')throw new Error('Reconcile the pending graph node; no replacement work was launched');
    await completeNode(trial,true);if(!v['no-publish'])await publishTrial(output,trial.id);return state;
  }
  if(['approval','approved','rejected','stopped','recover'].includes(state.node))return state;
  if(state.trials.length>=5){state.node='stopped';state.events.push({at:new Date().toISOString(),event:'hard_node_limit'});await writeJson(file,state);return state;}
  if(state.node==='plan'){
    const observation={phase:'plan',outcome:'not_run',repairs:0,maxRepairs:2,cleanupVerified:true,usageComplete:true};
    const route=enforceGraphRoute(await workshopPolicy(snapshot.files['workshop/graph.ts'],'route',observation),observation);
    state.events.push({at:new Date().toISOString(),event:'plan',detail:{plan:snapshot.files['workshop/plan.md'],sha256:snapshot.checksums['workshop/plan.md'],route}});
    state.node='verify';
  }
  const mode=await workshopPolicy(snapshot.files['workshop/graph.ts'],'verificationMode',{});
  if(!['serial','parallel'].includes(mode))throw new Error('Choose serial or parallel verification');
  const trialId=v['operation-id']??randomUUID();
  if(state.trials.some(trial=>trial.id===trialId))return state;
  const node=state.node as 'verify'|'repair';
  state.pending={id:trialId,node};await writeJson(file,state);
  const candidate=state.candidate?validateSnapshot(state.candidate,manifest):snapshot;
  const latest=state.trials.at(-1);
  const previous=latest?JSON.parse(await readFile(join(output,latest.id,'trial.json'),'utf8')):undefined;
  const feedback='Student plan:\n'+snapshot.files['workshop/plan.md']+'\nObserved prior checks:\n'+JSON.stringify(previous?.checks??[]);
  const trial=await workshopAttempt(workspace,output,manifest,candidate,node==='repair'?'agent':'scenario',{...v,'operation-id':trialId,'no-publish':true,parallel:mode==='parallel'},{feedback,controllerId:id});
  if(trial.id!==trialId)throw new Error('The graph node needs recovery; no replacement was launched');
  await completeNode(trial,false);if(!v['no-publish'])await publishTrial(output,trialId);
  return {...JSON.parse(await readFile(join(output,trialId,'trial.json'),'utf8')),controller:state};

  async function completeNode(trial:any,recovered:boolean){
    const pending=state.pending!;
    const candidate=validateSnapshot(JSON.parse(await readFile(join(output,trial.id,'candidate.json'),'utf8')),manifest);
    if(pending.node==='repair')state.repairs++;
    let lanes;try{lanes=JSON.parse(await readFile(join(output,trial.id,'grader/lanes.json'),'utf8'));}catch{}
    state.trials.push({id:trial.id,node:pending.node,outcome:trial.outcome,candidateSha256:candidate.sha256,lanes});
    const observation={phase:'verified',outcome:trial.outcome,repairs:state.repairs,maxRepairs:state.maxRepairs,cleanupVerified:trial.cleanupStatus==='verified',usageComplete:trial.telemetryStatus==='complete'};
    const requested=await workshopPolicy(snapshot.files['workshop/graph.ts'],'route',observation);
    const route=enforceGraphRoute(requested,observation);
    if(trial.outcome==='passed'){state.candidate=candidate;state.verifiedSha256=candidate.sha256;}
    else if(pending.node==='repair'){
      state.events.push({at:new Date().toISOString(),event:'rollback_to_baseline',detail:{failedCandidate:candidate.sha256,restored:snapshot.sha256,retainedTrial:trial.id}});
      state.candidate=snapshot;delete state.verifiedSha256;
    }
    delete state.pending;state.node=route==='stop'?'stopped':route;
    state.events.push({at:new Date().toISOString(),event:recovered?'recovered_completed_node':'node_completed',detail:{trial:trial.id,requested,route,observation}});
    await writeJson(file,state);await writeJson(join(output,trial.id,'graph-checkpoint.json'),state);
  }
}
export async function decideWorkshopGraph(output:string,id:string,decision:string,checksum:string,actor:string,reason:string){
  if(!id||!/^[a-zA-Z0-9-]+$/.test(id)||!['approve','reject'].includes(decision)||!actor?.trim()||!reason?.trim())throw new Error('An explicit actor, reason and approve/reject decision are required');
  const file=await safeWorkshopPath(output,`workshop/controllers/${id}.json`);
  const state:WorkshopGraphState=JSON.parse(await readFile(file,'utf8'));
  const decisionFile=await safeWorkshopPath(output,`workshop/controllers/${id}-decision.json`);
  try{
    const existing=JSON.parse(await readFile(decisionFile,'utf8'));
    if(existing.decision!==decision||existing.candidateSha256!==checksum||existing.actor!==actor||existing.reason!==reason)throw new Error('An immutable decision already exists for this candidate checksum');
    if(state.node==='approval'){state.node=decision==='approve'?'approved':'rejected';state.events.push({at:new Date().toISOString(),event:'recovered_human_decision',detail:existing});await writeJson(file,state);}
    return existing;
  }catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
  if(state.node!=='approval'||!state.verifiedSha256||checksum!==state.verifiedSha256||checksum!==state.candidate?.sha256)throw new Error('The decision must match the current verified candidate checksum');
  const receipt={schemaVersion:1,controller:id,decision,candidateSha256:checksum,actor,reason,at:new Date().toISOString()};
  const handle=await open(decisionFile,'wx',0o600);try{await handle.writeFile(JSON.stringify(receipt,null,2)+'\n');}finally{await handle.close();}
  state.node=decision==='approve'?'approved':'rejected';state.events.push({at:receipt.at,event:'human_decision',detail:receipt});await writeJson(file,state);
  return receipt;
}
