import {mkdir,readFile,readdir,rm} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {hostname} from 'node:os';
import {createSandboxClient} from '@coreweave/cwsandbox/wandb';
import {config,requirePrivateProject} from './config.js';
import {Budget,estimate} from './budget.js';
import {operationFile,updateOperation,verifyEvidence,evidencePath,evidenceReference,type Operation} from './operations.js';
import {disposeSandboxClient} from './sandbox.js';
import {publishTrial} from './campaign.js';
import {writeJson} from './records.js';

async function readOptional(file:string){try{return JSON.parse(await readFile(file,'utf8'));}catch(error){if((error as NodeJS.ErrnoException).code==='ENOENT')return null;throw error;}}
export async function recoveryReport(root:string){
  root=resolve(root);const ledger=await readOptional(join(root,'budget.json'));
  const names=await readdir(join(root,'operations')).catch(()=>[]);
  const operations=await Promise.all(names.filter(n=>n.endsWith('.json')).map(n=>readOptional(join(root,'operations',n))));
  return {schemaVersion:2,operations:operations.map(op=>({id:op.id,sourceCommit:op.sourceCommit,phase:op.phase,taskOutcome:op.executionOutcome,cleanup:op.cleanup,telemetry:op.telemetry,publication:op.publication,sandboxIds:op.sandboxIds,pendingRequests:Object.keys(op.requests).filter(k=>op.requests[k].status!=='reported'),evidence:op.evidence})),budget:ledger,action:'Connect with the same owner and destination, then recover each operation. Unknown usage needs checksum-verified supporting evidence with reconcile; do not delete the ledger or rerun the agent.'};
}

/** Read back external state; this function never launches inference or coding. */
export async function recoverOperation(root:string,id:string,publish=false){
  root=resolve(root);const c=config();await requirePrivateProject(c);
  const lock=operationFile(root,id)+'.recovery-lock';await mkdir(lock);
  const client=createSandboxClient({apiKey:c.apiKey!,entity:c.entity,project:c.project});
  const ids:string[]=[];
  try{
    let op:Operation=await readOptional(operationFile(root,id));
    if(!op||op.schemaVersion!==2)throw new Error('A version-two operation or explicit legacy reconciliation evidence is required');
    if(op.identity.entity!==c.entity||op.identity.project!==c.project||(process.env.FORGE_NOTEBOOK_OWNER&&op.identity.owner!==process.env.FORGE_NOTEBOOK_OWNER)||(process.env.FORGE_NOTEBOOK_ID&&op.identity.notebook!==process.env.FORGE_NOTEBOOK_ID))throw new Error('Recovery owner or destination mismatch');
    for(const ref of Object.values(op.evidence))await verifyEvidence(root,ref);
    const finalized=await readOptional(join(root,id,'worker-finalization.json'));
    const host=op.events.find(e=>e.event==='execution_started')?.detail;
    let workerAlive=false;
    if(host===hostname()&&op.childPid){try{process.kill(op.childPid,0);workerAlive=true;}catch(error){if((error as NodeJS.ErrnoException).code!=='ESRCH')throw error;}}
    if(workerAlive&&!finalized)return {id,recovered:false,reason:'worker is still active'};
    const sandboxes=[];
    for(const sandboxId of op.sandboxIds){ids.push(sandboxId);const sandbox=await client.get(sandboxId,{timeoutMs:30000});sandboxes.push({sandboxId,status:sandbox.status});}
    const terminal=sandboxes.every(s=>['completed','failed','terminated'].includes(s.status));
    const record=await readOptional(join(root,id,op.kind==='qualification'?'qualification.json':'trial.json'));
    const complete=Object.values(op.requests).every(r=>r.status==='reported');
    // A read-back of terminal status cannot supply missing usage or erase an
    // ambiguous creation. A retained, complete receipt is required as well.
    if(!terminal||!complete||op.cleanup!=='verified'||record?.estimatedCostUsd==null){
      const report={id,recovered:false,reason:'Missing usage, cleanup, or final accounting evidence',workerAlive,sandboxes,pendingRequests:Object.keys(op.requests).filter(k=>op.requests[k].status!=='reported')};
      await updateOperation(root,id,current=>{current.phase='blocked_unknown';current.events.push({at:new Date().toISOString(),event:'recovery_blocked',detail:report.reason});});
      return report;
    }
    const budget=new Budget(join(root,'budget.json'),c.budgetUsd),ledger=await readOptional(budget.file);
    if(id in (ledger?.reservations??{}))await budget.settle(id,record.estimatedCostUsd);
    if(op.publication!=='not_required'&&publish)await publishTrial(root,id);
    await updateOperation(root,id,current=>{current.phase=current.publication==='verified'||current.publication==='not_required'?'completed':'recoverable';current.events.push({at:new Date().toISOString(),event:'recovered_without_agent_replay'});});
    op=await readOptional(operationFile(root,id));return {id,recovered:op.phase==='completed',operation:op};
  }finally{try{await disposeSandboxClient(client,ids);}finally{await rm(lock,{recursive:true});}}
}

/** Instructor attestation is explicit and checksum-bound; never accept a bare cost. */
export async function reconcileOperation(root:string,id:string,evidenceFile:string){
  root=resolve(root);const c=config(),budget=new Budget(join(root,'budget.json'),c.budgetUsd);
  const op:Operation=await readOptional(operationFile(root,id));
  if(!op||op.identity.entity!==c.entity||op.identity.project!==c.project)throw new Error('Reconciliation destination mismatch');
  const evidence=await readOptional(await evidencePath(root,evidenceFile));
  if(evidence?.schemaVersion!==1||evidence.operationId!==id||!evidence.instructor?.trim()||!evidence.reason?.trim()||!Array.isArray(evidence.requests)||!Array.isArray(evidence.sandboxes))throw new Error('Reconciliation requires operation ID, instructor, reason, request usage and cleanup evidence');
  for(const row of [...evidence.requests,...evidence.sandboxes])await verifyEvidence(root,row.receipt);
  for(const row of evidence.requests){
    if(!op.requests[row.key]||![row.inputTokens,row.outputTokens].every(n=>Number.isFinite(n)&&n>=0)||row.inputTokens+row.outputTokens===0)throw new Error('Every unknown dispatched request needs nonzero provider-reported usage');
  }
  const covered=new Set(evidence.requests.map((r:any)=>r.key));
  if(Object.entries(op.requests).some(([key,r])=>r.status!=='reported'&&!covered.has(key)))throw new Error('Evidence does not cover every unresolved request');
  if(op.sandboxIds.some(id=>!evidence.sandboxes.some((s:any)=>s.id===id&&s.cleanup==='verified'&&Number.isFinite(s.seconds)&&s.seconds>=0)))throw new Error('Evidence must cover every sandbox and its metered or bounded lifetime');
  await requirePrivateProject(c);const client=createSandboxClient({apiKey:c.apiKey!,entity:c.entity,project:c.project});
  try{for(const id of op.sandboxIds){const sandbox=await client.get(id,{timeoutMs:30000});if(!['completed','failed','terminated'].includes(sandbox.status))throw new Error('Sandbox is not terminal');}}
  finally{await disposeSandboxClient(client,op.sandboxIds);}
  const recordFile=join(root,id,op.kind==='qualification'?'qualification.json':'trial.json'),record=await readOptional(recordFile);
  if(!record?.protocol?.pricing&&!evidence.protocol?.pricing)throw new Error('Original frozen pricing evidence is required');
  const prices=record?.protocol?.pricing??evidence.protocol.pricing;
  const requests={...op.requests};for(const row of evidence.requests)requests[row.key]={...requests[row.key],status:'reported',inputTokens:row.inputTokens,outputTokens:row.outputTokens};
  const inputTokens=Object.values(requests).reduce((s,r)=>s+(r.inputTokens??0),0),outputTokens=Object.values(requests).reduce((s,r)=>s+(r.outputTokens??0),0);
  const seconds=evidence.sandboxes.reduce((s:number,r:any)=>s+r.seconds,0),cost=estimate(inputTokens,outputTokens,seconds,prices);
  const receipt=await evidenceReference(root,await evidencePath(root,evidenceFile));
  const ledger=await readOptional(budget.file);
  if(id in ledger.reservations)await budget.reconcile(id,cost,JSON.stringify(receipt));
  for(const [key,r]of Object.entries(requests)){const reservation=`${id}-request-${key}`;if(reservation in ledger.reservations)await budget.reconcile(reservation,estimate(r.inputTokens!,r.outputTokens!,0,prices),JSON.stringify(receipt));}
  for(const row of evidence.sandboxes){if(row.reservationId in ledger.reservations)await budget.reconcile(row.reservationId,estimate(0,0,row.seconds,prices),JSON.stringify(receipt));}
  // Historical task outcomes are deliberately retained. This is an accounting
  // amendment linked to its evidence, never a new successful trial.
  Object.assign(record,{inputTokens,outputTokens,estimatedCostUsd:cost,cleanupStatus:'verified',reconciliation:receipt});await writeJson(recordFile,record);
  const ref=await evidenceReference(root,recordFile);
  await updateOperation(root,id,current=>{current.requests=requests;current.cleanup='verified';current.telemetry='complete';current.phase='recoverable';current.evidence[op.kind==='qualification'?'qualification':'trial']=ref;current.evidence.reconciliation=receipt;current.events.push({at:new Date().toISOString(),event:'instructor_reconciliation',detail:evidence.reason});});
  return recoverOperation(root,id,false);
}
