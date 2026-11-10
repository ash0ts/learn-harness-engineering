import {readFile, writeFile, mkdir,readdir} from 'node:fs/promises';
import {join} from 'node:path';
import {randomUUID, createHash} from 'node:crypto';
import type {Sandbox} from '@coreweave/cwsandbox';
import {config, publicConfig} from './config.js';
import {runPi} from './pi.js';
import {withWorkspace, stageWorkspace, sandboxTools} from './sandbox.js';
import {writeJson, redact, type TrialRecord} from './records.js';
import {stageTask, readTask, courseRoot,frozenFile} from './staging.js';
import {estimate} from './budget.js';
import {Execution} from './execution.js';
import {updateOperation,evidenceReference} from './operations.js';

export async function protocol() {return JSON.parse(await readFile(join(courseRoot,'forge/protocol.json'),'utf8'));}
export function roleSchedule(variant: string, sessions: number): Array<{role:string;turns:number;readOnly?:boolean}> {
  if(variant==='gen-eval')return [{role:'maker',turns:10},{role:'checker',turns:4,readOnly:true},{role:'maker-revision',turns:10}];
  if(variant==='plan-gen-eval')return [{role:'planner',turns:4,readOnly:true},{role:'maker',turns:8},{role:'checker',turns:4,readOnly:true},{role:'maker-revision',turns:8}];
  return Array.from({length:sessions},(_,i)=>({role:`maker-session-${i+1}`,turns:Math.floor(24/sessions)}));
}
async function patch(sandbox: Sandbox, baseline: string) {
  const r=await sandbox.commands.run(['bash','-lc',`git add -N . && git diff --binary ${baseline}`],{cwd:'/workspace/task',timeoutMs:15000});return r.stdout;
}
export async function runTrial(input: {id?:string;project:string;variant:string;trial:number;sourceCommit:string;output:string}) {
  const c=config(), p=await protocol(), task=await readTask(input.project,input.sourceCommit);
  if(c.model!==p.model || c.inferenceUrl!==p.inferenceUrl || c.maxInputBytes!==p.maxInputBytes)throw new Error('Frozen campaign model/provider/context mismatch');
  const id=input.id || randomUUID(); const dir=join(input.output,id);await mkdir(dir,{recursive:true});
  const execution=new Execution(input.output,id,p);await execution.begin('trial',input.sourceCommit);
  const record: TrialRecord & Record<string,unknown> = {schemaVersion:1,id,project:input.project,variant:input.variant,trial:input.trial,
    sourceCommit:input.sourceCommit,model:c.model,startedAt:new Date().toISOString(),outcome:'infrastructure_failed',
    conversationIds:[],wandbRunId:id.replaceAll('-','').slice(0,16),inputTokens:0,outputTokens:0,estimatedCostUsd:null,evidence:[]};
  record.configuration=publicConfig(c); record.protocol=p;
  let sandboxSeconds=0; let telemetryComplete=true; let actorComplete=true;
  const abort=new AbortController();const onSignal=()=>abort.abort(new Error('Cancelled'));
  process.once('SIGINT',onSignal);process.once('SIGTERM',onSignal);
  const timer=setTimeout(()=>abort.abort(new Error('Trial timeout')),p.sandbox.agentTimeoutSeconds*1000);
  try {
    const staged=await stageTask(task,input.variant,input.sourceCommit);
    record.applicationSha256=staged.applicationSha256;record.fixtureSha256=staged.fixtureSha256;
    record.frozenInputs={files:staged.filesSha256,taskSha256:createHash('sha256').update(JSON.stringify(task)).digest('hex'),modelSettingsSha256:createHash('sha256').update(JSON.stringify({model:p.model,temperature:p.temperature,maxInputBytes:p.maxInputBytes,maxOutputTokens:p.maxOutputTokens,thinkingLevel:p.thinkingLevel})).digest('hex'),image:p.sandbox.image};
    const checker=await frozenFile(input.sourceCommit,task.protectedChecker);
    const checkerSupport=await frozenFile(input.sourceCommit,'forge/graders/poll.cjs');
    const benchmarkProbe=await frozenFile(input.sourceCommit,'forge/graders/benchmark-probe.cjs');
    record.checkerSha256=createHash('sha256').update(checker).update('\0').update(checkerSupport).update(benchmarkProbe).digest('hex');
    await writeJson(join(dir,'trial.json'),record);
    const actorDir=join(dir,'actor');await mkdir(actorDir,{recursive:true});
    const actorStart=Date.now();
    try {
      await withWorkspace({config:c,image:p.sandbox.image,trialId:id,evidenceDir:actorDir,signal:abort.signal,...execution.workspace('actor',actorDir)},async sandbox=>{
        record.sandboxId=sandbox.sandboxId;await stageWorkspace(sandbox,staged.archive);
        const baseline=(await sandbox.commands.run(['git','rev-parse','HEAD'],{cwd:'/workspace/task'})).stdout.trim();
        let feedback='';let phase=0;
        for(const role of roleSchedule(input.variant,task.sessions)) {
          abort.signal.throwIfAborted();phase++;
          const saved=await patch(sandbox,baseline);
          let priorHandoff='';try{priorHandoff=Buffer.from(await sandbox.files.read('/workspace/task/session-handoff.md')).toString('utf8');}catch{}
          const result=await runPi({...c,maxTurns:role.turns},{role:role.role,
            prompt:`${task.task}\nRead TASK.md and AGENTS.md if present. You have ${role.turns} model turns. ${role.readOnly?'Inspect and return a concrete plan or review; your filesystem changes will be discarded.':'Implement and verify the task.'}\n${feedback}`,
            attributes:{'course.project':task.id,'course.task':task.id,'course.variant':input.variant,'course.trial':input.trial,'course.source_commit':input.sourceCommit,'course.sandbox_id':sandbox.sandboxId,'course.wandb_run_id':record.wandbRunId!},
            tools:sandboxTools(sandbox,join(actorDir,`phase-${phase}`)),signal:abort.signal,...execution.requestHooks(`phase-${phase}`),
            finalInstruction:role.readOnly?`This is your final allowed call. Return your concrete ${role.role==='planner'?'plan':'review'} now, with inspected files and observed checks. State omissions and failures explicitly.`:
              task.sessions>1&&['workspace-docs','recovery'].includes(input.variant)?'This is your final allowed call before interruption. Produce session-handoff.md content now: changes made, exact file paths, observed test results, unfinished work and next steps. The controller will save your response verbatim.':
              'This is your final allowed call. Report changes and observed checks, including unfinished work. Do not invent tests or results.'});
          record.conversationIds.push(result.conversationId);
          record.inputTokens! += result.inputTokens;record.outputTokens! += result.outputTokens;
          if(!result.telemetryComplete)telemetryComplete=false;
          actorComplete &&= result.completed;
          await writeJson(join(actorDir,`phase-${phase}.json`),result);
          const toolFiles=(await readdir(join(actorDir,`phase-${phase}`)).catch(()=>[])).filter(f=>/^tool-.*\.json$/.test(f));
          const toolRecords=await Promise.all(toolFiles.map(async f=>JSON.parse(await readFile(join(actorDir,`phase-${phase}`,f),'utf8'))));
          await writeJson(join(actorDir,`recovery-use-${phase}.json`),{priorHandoffSha256:priorHandoff?createHash('sha256').update(priorHandoff).digest('hex'):null,observedHandoffRead:Boolean(priorHandoff.trim()&&toolRecords.some(r=>r.stdout?.includes(priorHandoff.trim()))),patchBeforeSha256:createHash('sha256').update(saved).digest('hex'),patchAfterSha256:createHash('sha256').update(await patch(sandbox,baseline)).digest('hex')});
          await writeJson(join(actorDir,`deliverable-${phase}.json`),{role:role.role,produced:Boolean(result.finalText.trim()),text:result.finalText});
          if(task.sessions>1&&['workspace-docs','recovery'].includes(input.variant)&&result.finalText.trim())await sandbox.files.write('/workspace/task/session-handoff.md',result.finalText+'\n');
          if(role.readOnly) {
            // Review cannot alter the candidate delivered to the maker or protected checker.
            await sandbox.commands.run(['bash','-lc',`git reset --hard ${baseline} && git clean -fd`],{cwd:'/workspace/task'});
            if(saved){await sandbox.files.write('/tmp/restore.diff',saved);await sandbox.commands.run(['git','apply','/tmp/restore.diff'],{cwd:'/workspace/task'});}
            feedback=result.finalText.trim()?`Independent ${role.role} feedback:\n${result.finalText.slice(-12000)}`:`The ${role.role} did not produce a deliverable within its allowance.`;
          } else {
            feedback=task.sessions>1?'This is a fresh session after an interruption. Recover from the workspace files only.':feedback;
          }
          await writeFile(join(actorDir,`checkpoint-${phase}.diff`),await patch(sandbox,baseline));
          if(task.sessions>1){
            let handoff='';try{handoff=Buffer.from(await sandbox.files.read('/workspace/task/session-handoff.md')).toString('utf8');}catch{}
            await writeJson(join(actorDir,`interruption-${phase}.json`),{phase,at:new Date().toISOString(),conversationId:result.conversationId,patchSha256:createHash('sha256').update(await patch(sandbox,baseline)).digest('hex'),handoffProduced:Boolean(handoff),handoffSha256:handoff?createHash('sha256').update(handoff).digest('hex'):null,nextSessionContext:'fresh; recover from workspace files'});
          }
        }
        await writeFile(join(dir,'candidate.diff'),await patch(sandbox,baseline));
      });
    } finally {sandboxSeconds+=(Date.now()-actorStart)/1000;}
    clearTimeout(timer); // grading has its own bounded command and sandbox lifetime
    record.actorCompleted=actorComplete;
    await updateOperation(input.output,id,op=>{op.phase='grading';});
    const candidate=await readFile(join(dir,'candidate.diff'));
    const graderDir=join(dir,'grader');await mkdir(graderDir,{recursive:true});const gradeStart=Date.now();
    try {
      await withWorkspace({config:c,image:p.sandbox.image,trialId:`${id}-grade`,evidenceDir:graderDir,signal:abort.signal,...execution.workspace('grader',graderDir)},async sandbox=>{
        record.graderSandboxId=sandbox.sandboxId;await stageWorkspace(sandbox,staged.archive);
        if(candidate.length){await sandbox.files.write('/tmp/candidate.diff',candidate);await sandbox.commands.run(['git','apply','--reject','/tmp/candidate.diff'],{cwd:'/workspace/task',timeoutMs:20000});}
        await sandbox.files.write('/tmp/check.cjs',checker);
        await sandbox.files.write('/tmp/poll.cjs',checkerSupport);
        await sandbox.files.write('/tmp/benchmark-probe.cjs',benchmarkProbe);
        const result=await sandbox.commands.run(['xvfb-run','-a','node','/tmp/check.cjs',task.id],{cwd:'/workspace/task',check:false,timeoutMs:240000});
        await writeJson(join(graderDir,'command.json'),result);
        const grade=JSON.parse(Buffer.from(await sandbox.files.read('/tmp/grade/result.json')).toString('utf8'));
        await writeJson(join(graderDir,'result.json'),grade);record.grade=grade;
        for(const file of ['build.log','chunks.json','qa.json','electron.png','visible-answer.png','visible-answer.json','ui-events.json','ui-failure.png','restart.png','after-reset.png','benchmark.json','logs.json']) {
          try {await writeFile(join(graderDir,file),await sandbox.files.read(`/tmp/grade/${file}`));}catch{/* An absent artifact stays absent. */}
        }
        record.outcome=grade.passed?'passed':'task_failed';
      });
    } finally {sandboxSeconds+=(Date.now()-gradeStart)/1000;}
    if(!telemetryComplete)record.outcome='telemetry_missing';
  } catch(error) {
    record.error=redact(String(error),[c.apiKey||'']);
    record.outcome=telemetryComplete?'infrastructure_failed':'telemetry_missing';
    if(String(error).includes('budget_exhausted'))record.outcome='budget_exhausted';
  } finally {
    clearTimeout(timer);process.removeListener('SIGINT',onSignal);process.removeListener('SIGTERM',onSignal);
    const settled=await execution.finish(record.outcome);
    record.inputTokens=settled.inputTokens;record.outputTokens=settled.outputTokens;record.estimatedCostUsd=settled.estimatedCostUsd;
    record.cleanupStatus=settled.cleanupVerified?'verified':'unknown';record.telemetryStatus=settled.usageComplete&&telemetryComplete?'complete':'missing';record.publicationStatus='pending';record.taskOutcome=(record.grade as {passed?:boolean}|undefined)?.passed?'passed':record.grade?'task_failed':'not_graded';
    record.sandboxSecondsUpperBound=settled.sandboxSeconds;record.finishedAt=new Date().toISOString();
    record.evidence=['actor/sandbox.json','candidate.diff','grader/result.json'];
    await writeJson(join(dir,'trial.json'),record);
    const ref=await evidenceReference(input.output,join(dir,'trial.json'));await updateOperation(input.output,id,op=>{op.evidence.trial=ref;});
  }
  return record;
}
