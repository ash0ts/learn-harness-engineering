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
import {createHash} from 'node:crypto';
import {courseRoot,frozenFile} from './staging.js';

/** Reproduce the pinned SDK's local tag rejection with transport disabled. */
export async function proveRejectedTag(client:any,id:string){
  if(id.length<=59)throw new Error('Only the observed overlength tag rejection is supported');
  let calls=0,rejection='';const start=client.transport.start;
  client.transport.start=async()=>{calls++;throw new Error('Transport reached; prelaunch rejection is unproven');};
  try{await client.create({tags:['harness-course',id]});}
  catch(error){rejection=String(error);}
  finally{client.transport.start=start;}
  if(calls!==0||!rejection.startsWith(`CWSandboxValidationError: tags contains invalid value: ${id}.`))throw new Error('Prelaunch rejection is unproven');
  return {transportCalls:calls,rejection};
}

async function reconcileRejectedTag(root:string,op:Operation,evidence:any,evidenceFile:string){
  const c=config();await requirePrivateProject(c);
  if((process.env.FORGE_NOTEBOOK_OWNER&&op.identity.owner!==process.env.FORGE_NOTEBOOK_OWNER)||(process.env.FORGE_NOTEBOOK_ID&&op.identity.notebook!==process.env.FORGE_NOTEBOOK_ID))throw new Error('Reconciliation owner or notebook mismatch');
  if(Object.keys(op.requests).length||op.sandboxIds.length||op.publication!=='not_required')throw new Error('Rejected-launch reconciliation cannot clear dispatched work');
  if(op.events.find(e=>e.event==='execution_started')?.detail!==hostname())throw new Error('Inspect the rejected launch in its original runtime');
  if(op.childPid)try{process.kill(op.childPid,0);throw new Error('Worker is still active');}catch(error){if((error as NodeJS.ErrnoException).code!=='ESRCH')throw error;}
  const launches=op.events.filter(e=>e.event==='sandbox_launch');
  if(launches.length!==1||!launches[0].detail||!op.evidence.control)throw new Error('One protected control launch receipt is required');
  const control=JSON.parse(await readFile(await verifyEvidence(root,op.evidence.control),'utf8'));
  const journalFile=await evidencePath(root,launches[0].detail),journal=await readOptional(journalFile);
  if(control.grade!==null||!control.error?.startsWith(`CWSandboxValidationError: tags contains invalid value: ${op.id}.`)||journal?.trialId!==op.id||journal.state!=='creation_unknown'||journal.sandboxId||journal.recoveredSandboxIds?.length)throw new Error('Original evidence does not prove this local rejection');
  const originalPackage=JSON.parse(await frozenFile(op.sourceCommit,'forge/package.json'));
  const installedPackage=JSON.parse(await readFile(join(courseRoot,'forge/node_modules/@coreweave/cwsandbox/package.json'),'utf8'));
  if(originalPackage.dependencies['@coreweave/cwsandbox']!=='1.0.0'||installedPackage.version!=='1.0.0')throw new Error('Pinned SDK version differs from the rejected launch');
  const sdk=await readFile(join(courseRoot,'forge/node_modules/@coreweave/cwsandbox/dist/grpc-transport-DlmDQLSO.js'));
  const client=createSandboxClient({apiKey:c.apiKey!,entity:c.entity,project:c.project});
  let proof;try{proof=await proveRejectedTag(client,op.id);}finally{await disposeSandboxClient(client,[]);}
  const attestation=await evidenceReference(root,await evidencePath(root,evidenceFile));
  const receipt=join(root,op.id,'rejected-launch-reconciliation.json');
  await writeJson(receipt,{schemaVersion:1,operationId:op.id,instructor:evidence.instructor,reason:evidence.reason,attestation,originalControl:op.evidence.control,originalJournal:await evidenceReference(root,journalFile),sdkVersion:'1.0.0',sdkSha256:createHash('sha256').update(sdk).digest('hex'),...proof,estimatedCostUsd:0,taskOutcomeRetained:op.executionOutcome,at:new Date().toISOString()});
  const ref=await evidenceReference(root,receipt),budget=new Budget(join(root,'budget.json'),c.budgetUsd),ledger=await readOptional(budget.file);
  for(const reservation of op.reservationIds){
    if(!reservation.startsWith(`${op.id}-sandbox-`))throw new Error('Unexpected non-sandbox reservation');
    if(reservation in ledger.reservations)await budget.reconcile(reservation,0,JSON.stringify(ref));
    else if(ledger.settled[reservation]!==0)throw new Error('Reservation has no verified zero-dispatch settlement');
  }
  for(const slot of ['0','1']){
    const directory=join(root,'.sandbox-slots',slot),owner=await readOptional(join(directory,'owner.json'));
    if(owner?.owner===op.id){await evidencePath(root,`.sandbox-slots/${slot}/owner.json`);if(owner.pid!==op.childPid)throw new Error('Slot worker differs from rejected operation');await rm(directory,{recursive:true});}
  }
  await updateOperation(root,op.id,current=>{current.cleanup='verified';current.telemetry='complete';current.phase='completed';current.evidence.rejectedLaunch=ref;current.events.push({at:new Date().toISOString(),event:'instructor_verified_no_dispatch',detail:evidence.reason});});
  return {id:op.id,recovered:true,estimatedCostUsd:0,receipt:ref,originalOutcomeRetained:true};
}

async function readOptional(file:string){try{return JSON.parse(await readFile(file,'utf8'));}catch(error){if((error as NodeJS.ErrnoException).code==='ENOENT')return null;throw error;}}
export async function recoveryReport(root:string){
  root=resolve(root);const ledger=await readOptional(join(root,'budget.json'));
  const names=await readdir(join(root,'operations')).catch(()=>[]);
  const operations=await Promise.all(names.filter(n=>n.endsWith('.json')).map(n=>readOptional(join(root,'operations',n))));
  return {schemaVersion:2,operations:operations.map(op=>({id:op.id,sourceCommit:op.sourceCommit,phase:op.phase,taskOutcome:op.executionOutcome,cleanup:op.cleanup,telemetry:op.telemetry,publication:op.publication,sandboxIds:op.sandboxIds,pendingRequests:Object.keys(op.requests).filter(k=>op.requests[k].status!=='reported'),evidence:op.evidence})),budget:ledger,action:'Connect with the same owner and destination, then recover each operation. Unknown usage needs checksum-verified supporting evidence with reconcile; do not delete the ledger or rerun the agent.'};
}

/** Derive costs from persisted dispatch and terminal-resource receipts only. */
export async function recoverAccounting(root:string,op:Operation){
  const configuration=await readOptional(join(root,op.id,'execution-configuration.json'));
  if(!configuration?.protocol?.pricing)return {known:false as const,reason:'Frozen pricing receipt is missing'};
  const requests=Object.values(op.requests);
  if(requests.some(r=>r.status!=='reported'||![r.inputTokens,r.outputTokens].every(n=>Number.isFinite(n)&&n!>=0)))return {known:false as const,reason:'A dispatched request has missing usage'};
  for(const event of op.events.filter(e=>e.event==='child_launch')){
    let child=null;
    try{child=event.detail?await readOptional(await evidencePath(root,event.detail)):null;}
    catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
    if(child?.cleanupVerified!==true)return {known:false as const,reason:'Local child termination is unverified'};
  }
  const journals:Array<{journal:import('./sandbox.js').SandboxJournal;seconds:number;reference:{path:string;sha256:string}}>=[];
  for(const event of op.events.filter(e=>e.event==='sandbox_launch')){
    if(!event.detail)return {known:false as const,reason:'Sandbox launch has no journal reference'};
    const file=await evidencePath(root,event.detail),journal=await readOptional(file);
    if(!journal)return {known:false as const,reason:'Sandbox launch journal is missing'};
    // A journal with no requestedAt was saved before the external call. It is
    // proof that this workspace did not launch, even if its budget was reserved.
    if(journal.requestedAt&&(journal.state!=='terminated'||!journal.terminatedAt||!journal.sandboxId))return {known:false as const,reason:'Sandbox creation or termination is uncertain'};
    const seconds=journal.requestedAt?(Date.parse(journal.terminatedAt)-Date.parse(journal.requestedAt))/1000:0;
    if(!Number.isFinite(seconds)||seconds<0)return {known:false as const,reason:'Invalid sandbox timing receipt'};
    journals.push({journal,seconds,reference:await evidenceReference(root,file)});
  }
  if(op.sandboxIds.some(id=>!journals.some(j=>j.journal.sandboxId===id)))return {known:false as const,reason:'Sandbox has no bounded lifetime receipt'};
  const inputTokens=requests.reduce((n,r)=>n+r.inputTokens!,0),outputTokens=requests.reduce((n,r)=>n+r.outputTokens!,0);
  const seconds=journals.reduce((n,j)=>n+j.seconds,0),prices=configuration.protocol.pricing;
  return {known:true as const,inputTokens,outputTokens,sandboxSeconds:seconds,estimatedCostUsd:estimate(inputTokens,outputTokens,seconds,prices),prices,journals,incremental:configuration.incremental};
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
    let record:any=null,recordFile:string|undefined;
    for(const name of ['qualification.json','trial.json','control.json','grade.json']){
      const candidate=join(root,id,name),value=await readOptional(candidate);
      if(value){record=value;recordFile=candidate;break;}
    }
    const accounting=await recoverAccounting(root,op);
    if(!terminal||!accounting.known){
      const report={id,recovered:false,reason:!terminal?'Sandbox is not terminal':accounting.known?'':accounting.reason,workerAlive,sandboxes,pendingRequests:Object.keys(op.requests).filter(k=>op.requests[k].status!=='reported')};
      await updateOperation(root,id,current=>{current.phase='blocked_unknown';current.events.push({at:new Date().toISOString(),event:'recovery_blocked',detail:report.reason});});
      return report;
    }
    // Composite controllers retain their routes and child decisions. Accounting
    // recovery must not advance the graph or restart the next loop round.
    if(op.kind==='loop'||op.kind==='graph'){
      const checkpoint=op.evidence.checkpoint?await readOptional(await verifyEvidence(root,op.evidence.checkpoint)):null;
      const children=new Set<string>([...(checkpoint?.rounds??[]).map((r:any)=>r.id??r.trialId),checkpoint?.pendingTrialId,checkpoint?.makerOperationId,...Object.values(checkpoint?.lanes??{}).map((lane:any)=>lane.id)].filter(Boolean));
      for(const child of children){const state=await readOptional(operationFile(root,child));if(!state||state.phase!=='completed')return {id,recovered:false,reason:`Child ${child} requires recovery first`};}
      if(!checkpoint||!['approval','done','rejected','failed','deadline','round_limit','cancelled','succeeded'].includes(checkpoint.node??checkpoint.status))return {id,recovered:false,reason:'Controller checkpoint needs explicit CLI resume; recovery will not launch work'};
    }
    const budget=new Budget(join(root,'budget.json'),c.budgetUsd),ledger=await readOptional(budget.file);
    if(id in (ledger?.reservations??{}))await budget.settle(id,accounting.estimatedCostUsd);
    for(const [key,r]of Object.entries(op.requests)){const reservation=`${id}-request-${key}`;if(reservation in (ledger?.reservations??{}))await budget.settle(reservation,estimate(r.inputTokens!,r.outputTokens!,0,accounting.prices));}
    for(const row of accounting.journals){
      const label=Object.entries(op.evidence).find(([,ref])=>ref.path===row.reference.path)?.[0]?.replace(/^sandbox-/,'');
      const reservation=label?`${id}-sandbox-${label}`:op.reservationIds.find(r=>r.startsWith(`${id}-sandbox-`)&&row.reference.path.split('/').at(-2)===r.slice(`${id}-sandbox-`.length));
      if(reservation&&reservation in (ledger?.reservations??{}))await budget.settle(reservation,estimate(0,0,row.seconds,accounting.prices));
    }
    const recoveredFile=join(root,id,'recovery-accounting.json');await writeJson(recoveredFile,{...accounting,sandboxes,at:new Date().toISOString(),taskOutcomeRetained:op.executionOutcome,workerFinalization:finalized??'unverified; preserved as recovery event'});
    const recoveredRef=await evidenceReference(root,recoveredFile);
    // If a worker died after grading but before final accounting, annotate its
    // existing record. Never manufacture a grade or replace a failed outcome.
    if(recordFile&&record.estimatedCostUsd==null){
      Object.assign(record,{inputTokens:accounting.inputTokens,outputTokens:accounting.outputTokens,estimatedCostUsd:accounting.estimatedCostUsd,cleanupStatus:'verified',recoveryAccounting:recoveredRef});
      await writeJson(recordFile,record);
      const ref=await evidenceReference(root,recordFile);await updateOperation(root,id,current=>{const key=Object.keys(current.evidence).find(k=>current.evidence[k].path===ref.path)??'recoveredRecord';current.evidence[key]=ref;});
    }
    await updateOperation(root,id,current=>{current.cleanup='verified';current.telemetry=record?.telemetryStatus==='missing'?'missing':'complete';current.evidence.recoveryAccounting=recoveredRef;current.events.push({at:new Date().toISOString(),event:'recovered_without_agent_replay'});});
    if(op.publication!=='not_required'&&publish&&recordFile?.endsWith('/trial.json')&&record.wandbRunId)await publishTrial(root,id);
    await updateOperation(root,id,current=>{current.phase=current.telemetry==='complete'&&(current.publication==='verified'||current.publication==='not_required')?'completed':'recoverable';});
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
  if(evidence.prelaunchRejection===true)return reconcileRejectedTag(root,op,evidence,evidenceFile);
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
  if(!record)throw new Error('Original trial record is missing; provide a recovered record before accounting reconciliation');
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
