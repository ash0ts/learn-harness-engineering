import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {join} from 'node:path';
import {randomUUID, createHash} from 'node:crypto';
import type {Sandbox} from '@coreweave/cwsandbox';
import {config, publicConfig} from './config.js';
import {runPi} from './pi.js';
import {withWorkspace, stageWorkspace, sandboxTools} from './sandbox.js';
import {writeJson, redact, type TrialRecord} from './records.js';
import {stageTask, readTask, courseRoot} from './staging.js';
import {estimate} from './budget.js';

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
  const c=config(), p=await protocol(), task=await readTask(input.project);
  if(c.model!==p.model || c.inferenceUrl!==p.inferenceUrl)throw new Error('Frozen campaign model/provider mismatch');
  const id=input.id || randomUUID(); const dir=join(input.output,id);await mkdir(dir,{recursive:true});
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
    record.applicationSha256=staged.applicationSha256;
    const checker=await readFile(join(courseRoot,task.protectedChecker));
    record.checkerSha256=createHash('sha256').update(checker).digest('hex');
    await writeJson(join(dir,'trial.json'),record);
    const actorDir=join(dir,'actor');await mkdir(actorDir,{recursive:true});
    const actorStart=Date.now();
    try {
      await withWorkspace({config:c,image:p.sandbox.image,trialId:id,evidenceDir:actorDir,signal:abort.signal},async sandbox=>{
        record.sandboxId=sandbox.sandboxId;await stageWorkspace(sandbox,staged.archive);
        const baseline=(await sandbox.commands.run(['git','rev-parse','HEAD'],{cwd:'/workspace/task'})).stdout.trim();
        let feedback='';let phase=0;
        for(const role of roleSchedule(input.variant,task.sessions)) {
          abort.signal.throwIfAborted();phase++;
          const saved=await patch(sandbox,baseline);
          const result=await runPi({...c,maxTurns:role.turns},{role:role.role,
            prompt:`${task.task}\nRead TASK.md and AGENTS.md if present. You have ${role.turns} model turns. ${role.readOnly?'Inspect and return a concrete plan or review; your filesystem changes will be discarded.':'Implement and verify the task.'}\n${feedback}`,
            attributes:{'course.project':task.id,'course.task':task.id,'course.variant':input.variant,'course.trial':input.trial,'course.source_commit':input.sourceCommit,'course.sandbox_id':sandbox.sandboxId,'course.wandb_run_id':record.wandbRunId!},
            tools:sandboxTools(sandbox,join(actorDir,`phase-${phase}`)),signal:abort.signal});
          record.conversationIds.push(result.conversationId);
          record.inputTokens! += result.inputTokens;record.outputTokens! += result.outputTokens;
          if(!result.telemetryComplete)telemetryComplete=false;
          actorComplete &&= result.completed;
          await writeJson(join(actorDir,`phase-${phase}.json`),result);
          if(role.readOnly) {
            // Review cannot alter the candidate delivered to the maker or protected checker.
            await sandbox.commands.run(['bash','-lc',`git reset --hard ${baseline} && git clean -fd`],{cwd:'/workspace/task'});
            if(saved){await sandbox.files.write('/tmp/restore.diff',saved);await sandbox.commands.run(['git','apply','/tmp/restore.diff'],{cwd:'/workspace/task'});}
            feedback=`Independent ${role.role} feedback:\n${result.text.slice(-12000)}`;
          } else {
            feedback=task.sessions>1?'This is a fresh session after an interruption. Recover from the workspace files only.':feedback;
          }
          await writeFile(join(actorDir,`checkpoint-${phase}.diff`),await patch(sandbox,baseline));
        }
        await writeFile(join(dir,'candidate.diff'),await patch(sandbox,baseline));
      });
    } finally {sandboxSeconds+=(Date.now()-actorStart)/1000;}
    clearTimeout(timer); // grading has its own bounded command and sandbox lifetime
    record.actorCompleted=actorComplete;
    const candidate=await readFile(join(dir,'candidate.diff'));
    const graderDir=join(dir,'grader');await mkdir(graderDir,{recursive:true});const gradeStart=Date.now();
    try {
      await withWorkspace({config:c,image:p.sandbox.image,trialId:`${id}-grade`,evidenceDir:graderDir,signal:abort.signal},async sandbox=>{
        record.graderSandboxId=sandbox.sandboxId;await stageWorkspace(sandbox,staged.archive);
        if(candidate.length){await sandbox.files.write('/tmp/candidate.diff',candidate);await sandbox.commands.run(['git','apply','--reject','/tmp/candidate.diff'],{cwd:'/workspace/task',timeoutMs:20000});}
        await sandbox.files.write('/tmp/check.cjs',checker);
        const result=await sandbox.commands.run(['xvfb-run','-a','node','/tmp/check.cjs',task.id],{cwd:'/workspace/task',check:false,timeoutMs:240000});
        await writeJson(join(graderDir,'command.json'),result);
        const grade=JSON.parse(Buffer.from(await sandbox.files.read('/tmp/grade/result.json')).toString('utf8'));
        await writeJson(join(graderDir,'result.json'),grade);record.grade=grade;
        for(const file of ['build.log','chunks.json','qa.json','electron.png']) {
          try {await writeFile(join(graderDir,file),await sandbox.files.read(`/tmp/grade/${file}`));}catch{/* An absent artifact stays absent. */}
        }
        record.outcome=grade.passed?'passed':'task_failed';
      });
    } finally {sandboxSeconds+=(Date.now()-gradeStart)/1000;}
    if(!telemetryComplete)record.outcome='telemetry_missing';
    record.estimatedCostUsd=telemetryComplete?estimate(record.inputTokens!,record.outputTokens!,sandboxSeconds,p.pricing):null;
  } catch(error) {
    record.error=redact(String(error),[c.apiKey||'']);
    record.outcome=telemetryComplete?'infrastructure_failed':'telemetry_missing';
    // Preserve the reservation after any ambiguous failure; a reconciliation is required.
    record.estimatedCostUsd=null;
  } finally {
    clearTimeout(timer);process.removeListener('SIGINT',onSignal);process.removeListener('SIGTERM',onSignal);
    record.sandboxSecondsUpperBound=sandboxSeconds;record.finishedAt=new Date().toISOString();
    record.evidence=['actor/sandbox.json','candidate.diff','grader/result.json'];
    await writeJson(join(dir,'trial.json'),record);
  }
  return record;
}
