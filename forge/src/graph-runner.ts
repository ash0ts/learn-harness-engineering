import {mkdir,readFile,writeFile,readdir,mkdtemp,rm} from 'node:fs/promises';
import {join,resolve,relative,isAbsolute} from 'node:path';
import {createHash} from 'node:crypto';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {tmpdir} from 'node:os';
import {compare} from './campaign.js';
import {driveGraph,newGraph,type GraphState,type Candidate,type Verification} from './graph.js';
import {sourceHead,readTask,stageTask,courseRoot,frozenFile} from './staging.js';
import {protocol} from './trial.js';
import {config,requirePrivateProject} from './config.js';
import {Budget,estimate} from './budget.js';
import {stageWorkspace,withWorkspace} from './sandbox.js';
import {writeJson,type TrialRecord} from './records.js';
import {Execution} from './execution.js';
import {evidenceReference,verifyEvidence,updateOperation,operationFile} from './operations.js';
import {runPi} from './pi.js';
import {requireControls} from './controls.js';
const exec=promisify(execFile);
const portable=(root:string,path:string)=>isAbsolute(path)?relative(root,path):path;

export async function verifyGraphLane(output:string,id:string,candidate:Candidate,lane:Verification['lane'],source:string){
  const p=await protocol(),task=await readTask('project-08',source),dir=join(output,id);await mkdir(dir,{recursive:true});
  const execution=new Execution(output,id,p);await execution.begin('trial',source);
  if(!execution.incremental){const ledger=JSON.parse(await readFile(execution.budget.file,'utf8'));if(!ledger.reservations[id]||ledger.halted)throw new Error('Verification requires its reserved complete block');}
  const startedAt=new Date().toISOString();let grade:{passed:boolean;error?:string}={passed:false};let failureKind:Verification['failureKind'];
  try{
    const patch=await verifyEvidence(output,{path:portable(output,candidate.patch),sha256:candidate.sha256});
    const staged=await stageTask(task,'graph',source);
    await withWorkspace({config:execution.c,image:p.sandbox.image,trialId:id,evidenceDir:join(dir,'sandbox'),...execution.workspace('lane',join(dir,'sandbox'))},async sandbox=>{
      await stageWorkspace(sandbox,staged.archive);const bytes=await readFile(patch);await sandbox.files.write('/tmp/candidate.diff',bytes);
      if(bytes.length)await sandbox.commands.run(['git','apply','/tmp/candidate.diff'],{cwd:'/workspace/task'});
      for(const file of ['graph-lane.cjs','poll.cjs'])await sandbox.files.write('/tmp/'+file,await frozenFile(source,'forge/graders/'+file));
      const command=await sandbox.commands.run(['xvfb-run','-a','node','/tmp/graph-lane.cjs',lane],{check:false,timeoutMs:180000,cwd:'/workspace/task'});await writeJson(join(dir,'command.json'),command);
      grade=JSON.parse(Buffer.from(await sandbox.files.read('/tmp/graph-grade.json')).toString());
      if(lane==='electron')try{await writeFile(join(dir,'electron.png'),await sandbox.files.read('/tmp/graph-electron.png'));}catch{}
    });
    if(!grade.passed)failureKind='code';
  }catch(error){grade={passed:false,error:String(error)};failureKind='infrastructure';}
  const accounting=await execution.finish(grade.passed?'passed':'task_failed');if(!execution.incremental)await execution.budget.settle(id,accounting.estimatedCostUsd);
  await writeJson(join(dir,'grade.json'),{...grade,candidateSha256:candidate.sha256,startedAt,finishedAt:new Date().toISOString(),failureKind,...accounting});
  const ref=await evidenceReference(output,join(dir,'grade.json'));
  await updateOperation(output,id,op=>{op.evidence.grade=ref;op.publication='not_required';op.phase=accounting.cleanupVerified&&accounting.usageComplete?'completed':'blocked_unknown';});
  return {lane,...grade,evidence:ref.path,evidenceSha256:ref.sha256,failureKind,startedAt,finishedAt:new Date().toISOString()};
}

async function recoverLane(output:string,id:string,lane:Verification['lane'],candidate:Candidate){
  const op=JSON.parse(await readFile(operationFile(output,id),'utf8'));
  if(op.cleanup!=='verified'||op.telemetry!=='complete'||!op.evidence.grade)return null;
  const file=await verifyEvidence(output,op.evidence.grade),grade=JSON.parse(await readFile(file,'utf8'));
  if(grade.candidateSha256!==candidate.sha256)throw new Error('Verification belongs to another candidate');
  return {lane,passed:grade.passed,error:grade.error,failureKind:grade.failureKind,evidence:op.evidence.grade.path,evidenceSha256:op.evidence.grade.sha256};
}

export async function runGraph(file:string,execute:boolean,resume=false,options:{output?:string;operationId?:string}={}){
  if(!resume){try{await readFile(file);throw new Error('Existing graph retained; start another execution with a new checkpoint');}catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}}
  const state:GraphState=resume?JSON.parse(await readFile(file,'utf8')):newGraph(await sourceHead(),options.operationId);
  if(!execute)return state;
  const c=config(),p=await protocol(),task=await readTask('project-08',state.sourceCommit);
  const output=resolve(options.output??process.env.FORGE_RESULTS_DIR??join(courseRoot,'forge/local-results'));
  if(state.sourceCommit!==await sourceHead())throw new Error('Resume requires the original pinned runner');
  if(relative(output,resolve(file)).startsWith('..'))throw new Error('Checkpoint must be inside the evidence root');
  await requirePrivateProject(c);await requireControls(output,['project-08'],state.sourceCommit);
  const qualificationFiles=(await readdir(output)).filter(n=>n.startsWith('qualification-'));
  const qualified=await Promise.all(qualificationFiles.map(async n=>{try{return JSON.parse(await readFile(join(output,n,'qualification.json'),'utf8'));}catch{return null;}}));
  const hash=createHash('sha256').update(JSON.stringify(p)).digest('hex');
  if(!qualified.some(q=>q?.passed&&q.protocolSha256===hash))throw new Error('Frozen inference qualification required before graph planning');
  const execution=new Execution(output,state.id,p);
  if(!resume){await execution.begin('graph',state.sourceCommit);if(!execution.incremental)await execution.budget.reserve({[state.id]:estimate(p.maxInputBytes*4,p.maxOutputTokens*4,0,p.pricing)});}
  if(state.node==='infrastructure_recovery'){
    if(state.recoveryFrom==='make'&&state.makerOperationId){
      const recovered=await (await import('./recovery.js')).recoverOperation(output,state.makerOperationId,true);
      if(!recovered.recovered)throw new Error('Maker remains unresolved');
      const record=JSON.parse(await readFile(join(output,state.makerOperationId,'trial.json'),'utf8'));
      const patch=await evidenceReference(output,join(output,state.makerOperationId,'candidate.diff')),grade=await evidenceReference(output,join(output,state.makerOperationId,'trial.json'));
      state.candidate={patch:patch.path,sha256:patch.sha256,trialId:state.makerOperationId,protectedGrade:{passed:record.outcome==='passed',evidence:grade.path,sha256:grade.sha256}};state.node='verify';
    }else if(state.recoveryFrom==='plan'){
      throw new Error('Planning failure is retained. Reconcile unknown usage, then explicitly start a new graph execution');
    }else if(state.recoveryFrom==='verify')state.node='verify';
    else throw new Error('Interrupted route needs supporting reconciliation evidence');
    delete state.pendingOperation;
  }
  const result=await driveGraph(file,state,{
    async plan(s){
      const staged=await stageTask(task,'graph',s.sourceCommit),dir=await mkdtemp(join(tmpdir(),'graph-plan-'));
      let context='';try{const tar=join(dir,'task.tar');await writeFile(tar,staged.archive);context=(await exec('tar',['-xOf',tar,'./src/services/indexing-service.ts'],{maxBuffer:1e6})).stdout;}finally{await rm(dir,{recursive:true,force:true});}
      const op=JSON.parse(await readFile(operationFile(output,s.id),'utf8')),used=Object.keys(op.requests).length;
      if(used>=4)throw new Error('Planning allowance exhausted');
      const plan=await runPi({...c,maxTurns:4-used},{role:'planner',prompt:`${task.task}\nProduce a concrete repair and verification plan. You cannot edit code in this planning session. The unfinished indexing service follows:\n${context}`,tools:[],attributes:{'course.project':'project-08','course.source_commit':s.sourceCommit,'course.operation_id':s.id},signal:AbortSignal.timeout(180000),...execution.requestHooks(`plan-${used+1}`)});
      await writeJson(join(output,s.id,`plan-${used+1}.json`),plan);
      if(!plan.telemetryComplete||!plan.completed||!plan.finalText.trim())throw new Error('Planning deliverable or usage is missing');return plan.finalText;
    },
    async prepareVerification(s){
      if(execution.incremental)return;
      const ids=Object.values(s.lanes!).map(l=>l!.id),ledger=JSON.parse(await readFile(execution.budget.file,'utf8'));
      const absent=ids.filter(id=>!(id in ledger.reservations)&&!(id in ledger.settled));
      if(absent.length===ids.length)await execution.budget.reserve(Object.fromEntries(ids.map(id=>[id,estimate(0,0,1500,p.pricing)])));
      else if(absent.length)throw new Error('Partial verification reservation needs reconciliation');
    },
    async make(s){
      const verification=s.verification?await Promise.all(s.verification.map(async lane=>({lane:lane.lane,passed:lane.passed,error:lane.error,grade:JSON.parse(await readFile(await verifyEvidence(output,{path:portable(output,lane.evidence),sha256:lane.evidenceSha256??''}),'utf8'))}))):undefined;
      const previous=s.previous?await verifyEvidence(output,{path:portable(output,s.previous.patch),sha256:s.previous.sha256}):undefined;
      const result=await compare({project:'project-08',variant:'graph',repeats:1,execute:true,source:s.sourceCommit,output,resumePatch:previous,trialId:s.makerOperationId,agentTimeoutSeconds:420,verificationFeedback:JSON.stringify({plan:s.plan,attempt:s.attempts,verification,rollback:previous?'last verified checkpoint':'frozen baseline'})});
      const record=(result as {completed?:TrialRecord[]}).completed?.[0];
      if(!record||['infrastructure_failed','telemetry_missing','budget_exhausted'].includes(record.outcome))throw new Error('Maker unavailable; reconcile its stable operation before another launch');
      const patch=await evidenceReference(output,join(output,record.id,'candidate.diff')),grade=await evidenceReference(output,join(output,record.id,'trial.json'));
      return {patch:patch.path,sha256:patch.sha256,trialId:record.id,protectedGrade:{passed:record.outcome==='passed',evidence:grade.path,sha256:grade.sha256}};
    },
    verify:(candidate,lane,s)=>verifyGraphLane(output,s.lanes![lane]!.id,candidate,lane,s.sourceCommit),
    recoverLane:(candidate,lane,s)=>recoverLane(output,s.lanes![lane]!.id,lane,candidate),
    async rollback(s){await writeJson(join(output,`rollback-${s.id}-${s.attempts}.json`),{discarded:s.candidate,restored:s.previous??'frozen baseline',verification:s.verification});},
  });
  const accounting=await execution.finish(result.node);
  if(!execution.incremental)await execution.budget.settle(state.id,accounting.estimatedCostUsd);
  const ref=await evidenceReference(output,file);
  const childIds=[state.makerOperationId,...Object.values(state.lanes??{}).map(l=>l?.id)].filter((id):id is string=>Boolean(id));
  const children=await Promise.all(childIds.map(async id=>{try{return JSON.parse(await readFile(operationFile(output,id),'utf8'));}catch{return null;}}));
  const unresolved=children.some(child=>child&&(child.cleanup!=='verified'||child.telemetry!=='complete'));
  await updateOperation(output,state.id,op=>{op.evidence.checkpoint=ref;op.publication='not_required';op.phase=!accounting.usageComplete||unresolved?'blocked_unknown':result.node==='infrastructure_recovery'?'recoverable':'completed';op.executionOutcome=result.node;if(unresolved)op.cleanup='unknown';});return result;
}

/** Three balanced pairs share exact patch bytes; only verification scheduling differs. */
export async function verificationPairs(output:string,trialId:string,execute=false){
  output=resolve(output);const record=JSON.parse(await readFile(join(output,trialId,'trial.json'),'utf8'));
  if(record.outcome!=='passed'||record.protocol?.protocolRevision!==5)throw new Error('Pairs require a qualified protocol-five candidate');
  const patch=await evidenceReference(output,join(output,trialId,'candidate.diff'));
  const candidate:Candidate={patch:patch.path,sha256:patch.sha256,trialId,protectedGrade:{passed:true,evidence:`${trialId}/trial.json`}};
  const schedule=[['serial','parallel'],['parallel','serial'],['serial','parallel']] as const;
  if(!execute)return {candidate,schedule};
  const c=config(),p=await protocol();await requirePrivateProject(c);await requireControls(output,['project-08'],record.sourceCommit);
  const budget=new Budget(join(output,'budget.json'),c.budgetUsd),pairs=[];
  for(let repeat=0;repeat<3;repeat++){
    const block=schedule[repeat].map(mode=>({mode,state:{...newGraph(record.sourceCommit),node:'verify' as const,candidate,verificationMode:mode}}));
    const {randomUUID}=await import('node:crypto');
    for(const item of block)item.state.lanes={services:{id:randomUUID(),status:'prepared'},electron:{id:randomUUID(),status:'prepared'}};
    if(process.env.FORGE_BUDGET_MODE!=='incremental')await budget.reserve(Object.fromEntries(block.flatMap(item=>Object.values(item.state.lanes!).map(l=>[l!.id,estimate(0,0,1500,p.pricing)]))));
    for(const item of block){
      const start=Date.now();
      const s=await driveGraph(join(output,`verification-${item.state.id}.json`),item.state,{plan:async()=>'',make:async()=>{throw new Error('Verification cannot invoke a coding agent');},rollback:async()=>{},verify:(candidate,lane,state)=>verifyGraphLane(output,state.lanes![lane]!.id,candidate,lane,state.sourceCommit)});
      const row={repeat:repeat+1,order:schedule[repeat],mode:item.mode,candidateSha256:patch.sha256,elapsedMs:Date.now()-start,lanes:s.verification??[],completed:s.node==='approval'};pairs.push(row);
      await writeJson(join(output,`verification-pairs-${trialId}.json`),{schemaVersion:1,protocolRevision:5,sourceCommit:record.sourceCommit,candidateSha256:patch.sha256,pairs});
      if(!row.completed)return {pairs,stopReason:s.error??'Verification failed'};
    }
  }
  return {pairs};
}
