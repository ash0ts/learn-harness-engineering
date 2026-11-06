import {readFile} from 'node:fs/promises';
import {randomUUID,createHash} from 'node:crypto';
import {writeJson} from './records.js';

export type Node='plan'|'make'|'verify'|'rollback'|'approval'|'done'|'rejected'|'failed';
export interface Candidate {patch:string;sha256:string;trialId:string;protectedGrade?:{passed:boolean;evidence:string}}
export interface Verification {lane:'services'|'electron';passed:boolean;evidence:string;error?:string}
export interface GraphState {
  schemaVersion:1;id:string;sourceCommit:string;node:Node;attempts:number;maxAttempts:number;
  plan?:string;candidate?:Candidate;previous?:Candidate;verification?:Verification[];
  lastProtectedGrade?:Candidate['protectedGrade'];
  transitions:Array<{from:Node;to:Node;at:string;reason:string}>;
  pendingOperation?:string;error?:string;
  approval?:{decision:'approve'|'reject';candidateSha256:string;at:string;actor:string};
}
export interface GraphDriver {
  plan(state:GraphState):Promise<string>;
  make(state:GraphState):Promise<Candidate>;
  verify(candidate:Candidate,lane:Verification['lane'],state:GraphState):Promise<Verification>;
  rollback(state:GraphState):Promise<void>;
}
async function transition(file:string,s:GraphState,to:Node,reason:string) {
  s.transitions.push({from:s.node,to,at:new Date().toISOString(),reason});s.node=to;delete s.pendingOperation;await writeJson(file,s);
}
/** Durable, explicit routing. Approval is a terminal pause, never an automatic edge. */
export async function driveGraph(file:string,s:GraphState,driver:GraphDriver) {
  if(s.pendingOperation)throw new Error(`Reconcile interrupted operation ${s.pendingOperation} before resume`);
  await writeJson(file,s);
  try {
    while(!['approval','done','rejected','failed'].includes(s.node)) {
      s.pendingOperation=`${s.node}-${s.attempts}`;await writeJson(file,s);
      switch(s.node) {
        case 'plan':s.plan=await driver.plan(s);await transition(file,s,'make','frozen task acceptance criteria');break;
        case 'make':
          if(s.attempts>=s.maxAttempts){await transition(file,s,'failed','attempt limit');break;}
          s.attempts++;s.candidate=await driver.make(s);await transition(file,s,'verify','candidate patch exported');break;
        case 'verify':
          if(!s.candidate)throw new Error('Missing candidate');
          s.verification=await Promise.all(['services','electron'].map(lane=>driver.verify(s.candidate!,lane as Verification['lane'],s)));
          s.lastProtectedGrade=s.candidate.protectedGrade;
          await transition(file,s,s.verification.every(v=>v.passed)&&s.candidate.protectedGrade?.passed!==false?'approval':'rollback','protected grade and independent parallel verification results');break;
        case 'rollback':
          await driver.rollback(s);s.candidate=s.previous;
          await transition(file,s,s.attempts>=s.maxAttempts?'failed':'make','restore last verified patch or frozen baseline');break;
      }
    }
  } catch(error){s.error=String(error);await transition(file,s,'failed','operation failed; inspect evidence before another paid run');}
  return s;
}
export async function decideGraph(file:string,decision:'approve'|'reject',actor:string,expectedSha256:string) {
  const state:GraphState=JSON.parse(await readFile(file,'utf8'));
  if(state.node!=='approval'||!state.candidate||state.pendingOperation)throw new Error('Graph is not awaiting approval');
  const actual=createHash('sha256').update(await readFile(state.candidate.patch)).digest('hex');
  if(actual!==expectedSha256||actual!==state.candidate.sha256)throw new Error('Candidate changed since review');
  if(!actor.trim())throw new Error('Explicit human decision actor required');
  state.approval={decision,actor,candidateSha256:actual,at:new Date().toISOString()};
  await transition(file,state,decision==='approve'?'done':'rejected',`explicit ${decision} decision`);return state;
}
export function newGraph(sourceCommit:string):GraphState {
  return {schemaVersion:1,id:randomUUID(),sourceCommit,node:'plan',attempts:0,maxAttempts:3,transitions:[]};
}
