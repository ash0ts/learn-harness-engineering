import {readFile,mkdir,rm} from 'node:fs/promises';
import {randomUUID} from 'node:crypto';
import {dirname,relative,isAbsolute} from 'node:path';
import {writeJson} from './records.js';
import {verifyEvidence,evidenceReference,operationFile,updateOperation} from './operations.js';

export type Node='plan'|'make'|'verify'|'code_repair'|'infrastructure_recovery'|'rollback'|'approval'|'done'|'rejected'|'failed';
export interface Candidate {patch:string;sha256:string;trialId:string;protectedGrade?:{passed:boolean;evidence:string;sha256?:string}}
export interface Verification {lane:'services'|'electron';passed:boolean;evidence:string;evidenceSha256?:string;error?:string;failureKind?:'code'|'infrastructure';startedAt?:string;finishedAt?:string}
export interface Lane {id:string;status:'prepared'|'running'|'completed'|'blocked';result?:Verification}
export interface GraphState {
  schemaVersion:1;checkpointVersion?:2;id:string;sourceCommit:string;node:Node;attempts:number;maxAttempts:number;
  plan?:string;candidate?:Candidate;previous?:Candidate;verification?:Verification[];
  lastProtectedGrade?:Candidate['protectedGrade'];failedCandidates?:Candidate[];
  lanes?:Partial<Record<Verification['lane'],Lane>>;verificationMode?:'serial'|'parallel';
  transitions:Array<{from:Node;to:Node;at:string;reason:string}>;
  pendingOperation?:string;error?:string;recoveryFrom?:Node;
  makerOperationId?:string;
  approval?:{decision:'approve'|'reject';candidateSha256:string;at:string;actor:string;decisionId?:string};
}
export interface GraphDriver {
  plan(state:GraphState):Promise<string>;
  make(state:GraphState):Promise<Candidate>;
  verify(candidate:Candidate,lane:Verification['lane'],state:GraphState):Promise<Verification>;
  prepareVerification?:(state:GraphState)=>Promise<void>;
  recoverLane?:(candidate:Candidate,lane:Verification['lane'],state:GraphState)=>Promise<Verification|null>;
  rollback(state:GraphState):Promise<void>;
}
async function transition(file:string,s:GraphState,to:Node,reason:string){
  s.transitions.push({from:s.node,to,at:new Date().toISOString(),reason});s.node=to;delete s.pendingOperation;await writeJson(file,s);
}
/** Explicit routes and durable lanes. A pause never grants permission to replay. */
export async function driveGraph(file:string,s:GraphState,driver:GraphDriver){
  if(s.pendingOperation&&(s.node!=='verify'||!s.lanes))throw new Error(`Reconcile interrupted operation ${s.pendingOperation} before resume`);
  if(s.node==='infrastructure_recovery')return s;
  await writeJson(file,s);
  let saves=Promise.resolve();const save=()=>{const snapshot=JSON.parse(JSON.stringify(s));saves=saves.then(()=>writeJson(file,snapshot));return saves;};
  try{
    while(!['approval','done','rejected','failed','infrastructure_recovery'].includes(s.node)){
      s.pendingOperation??=`${s.node}-${s.attempts}`;await save();
      switch(s.node){
        case 'plan':s.plan=await driver.plan(s);await transition(file,s,'make','planning inputs frozen; planner deliverable precedes code generation');break;
        case 'make':
          if(s.attempts>=s.maxAttempts){await transition(file,s,'failed','attempt limit');break;}
          s.attempts++;s.makerOperationId=randomUUID();await save();s.candidate=await driver.make(s);
          s.lanes={services:{id:randomUUID(),status:'prepared'},electron:{id:randomUUID(),status:'prepared'}};
          await transition(file,s,'verify','candidate and lane identities persisted');break;
        case 'verify':{
          if(!s.candidate)throw new Error('Missing candidate');
          s.lanes??={services:{id:randomUUID(),status:'prepared'},electron:{id:randomUUID(),status:'prepared'}};await save();
          await driver.prepareVerification?.(s);
          const verify=async(lane:Verification['lane'])=>{
            const entry=s.lanes![lane]!;
            if(entry.status==='completed'&&entry.result)return entry.result;
            if(entry.status==='running'||entry.status==='blocked'){
              const recovered=await driver.recoverLane?.(s.candidate!,lane,s);
              if(!recovered)throw new Error(`Reconcile verification lane ${entry.id}; paid replay refused`);
              entry.result=recovered;entry.status='completed';await save();return recovered;
            }
            entry.status='running';await save();
            try{const result=await driver.verify(s.candidate!,lane,s);entry.result=result;entry.status='completed';await save();return result;}
            catch(error){entry.status='blocked';await save();throw error;}
          };
          const results=s.verificationMode==='serial'?[await verify('services'),await verify('electron')]:await Promise.allSettled([verify('services'),verify('electron')]).then(values=>{const failure=values.find(v=>v.status==='rejected');if(failure?.status==='rejected')throw failure.reason;return values.map(v=>(v as PromiseFulfilledResult<Verification>).value);});
          s.verification=results;s.lastProtectedGrade=s.candidate.protectedGrade;
          if(results.some(v=>v.failureKind==='infrastructure')){s.recoveryFrom='verify';await transition(file,s,'infrastructure_recovery','verification infrastructure needs reconciliation');}
          else if(results.every(v=>v.passed)&&s.candidate.protectedGrade?.passed!==false){s.previous={...s.candidate};await transition(file,s,'approval','protected acceptance and independent verification passed');}
          else await transition(file,s,'code_repair','recorded code checks failed');
          break;
        }
        case 'code_repair':await transition(file,s,'rollback','preserve failed candidate and choose the last verified starting point');break;
        case 'rollback':
          if(s.candidate)(s.failedCandidates??=[]).push({...s.candidate});
          await driver.rollback(s);s.candidate=s.previous;delete s.lanes;
          await transition(file,s,s.attempts>=s.maxAttempts?'failed':'make','restored last verified checkpoint or frozen baseline');break;
      }
    }
  }catch(error){s.error=String(error);s.recoveryFrom=s.node;await transition(file,s,'infrastructure_recovery','operation interrupted; reconcile evidence before resuming');}
  await saves;return s;
}

export async function decideGraph(file:string,decision:'approve'|'reject',actor:string,expectedSha256:string,root=process.env.FORGE_RESULTS_DIR??dirname(file)){
  const lock=file+'.approval-lock';await mkdir(lock);
  try{
    const state:GraphState=JSON.parse(await readFile(file,'utf8'));
    if(state.node!=='approval'||!state.candidate||state.pendingOperation)throw new Error('Graph is not awaiting approval');
    if(expectedSha256!==state.candidate.sha256)throw new Error('Candidate changed since review');
    const path=isAbsolute(state.candidate.patch)?relative(root,state.candidate.patch):state.candidate.patch;
    await verifyEvidence(root,{path,sha256:expectedSha256});
    if(!actor.trim())throw new Error('Explicit human decision actor required');
    state.approval={decision,actor,candidateSha256:expectedSha256,at:new Date().toISOString(),decisionId:randomUUID()};
    await transition(file,state,decision==='approve'?'done':'rejected',`explicit ${decision} decision`);
    // Keep the mutable checkpoint reference current after the human decision.
    const exists=await readFile(operationFile(root,state.id),'utf8').then(()=>true,error=>{if(error.code==='ENOENT')return false;throw error;});
    if(exists){const ref=await evidenceReference(root,file);await updateOperation(root,state.id,op=>{op.evidence.checkpoint=ref;op.executionOutcome=state.node;op.events.push({at:state.approval!.at,event:'human_decision',detail:state.approval!.decisionId});});}
    return state;
  }finally{await rm(lock,{recursive:true});}
}
export function newGraph(sourceCommit:string,id:string=randomUUID()):GraphState{
  return {schemaVersion:1,checkpointVersion:2,id,sourceCommit,node:'plan',attempts:0,maxAttempts:3,transitions:[],failedCandidates:[],verificationMode:'parallel'};
}
