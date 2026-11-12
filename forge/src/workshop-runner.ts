import {mkdir,readFile,writeFile,readdir,mkdtemp,rm} from 'node:fs/promises';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {randomUUID} from 'node:crypto';
import {tmpdir} from 'node:os';
import {config,publicConfig,requirePrivateProject} from './config.js';
import {Execution} from './execution.js';
import {protocol,roleSchedule} from './trial.js';
import {runPi} from './pi.js';
import {stageWorkspace,withWorkspace,sandboxTools} from './sandbox.js';
import {updateOperation,evidenceReference,operationFile} from './operations.js';
import {writeJson,redact} from './records.js';
import {makeSnapshot,storeSnapshot,sha256,validateSnapshot,type WorkshopSnapshot,type WorkshopManifest,type WorkshopResult} from './workshop-contract.js';
import {bundleWorkshop,stageWorkshop} from './workshop-stage.js';
import {workshopCourseRoot,workshopHead} from './workshop-workspace.js';
import {deadline} from './lifecycle.js';

export interface WorkshopRunOptions {action:'scenario'|'agent'|'resume';output:string;id?:string;live?:boolean;scenario?:string;fixture?:string;question?:string;singleRole?:boolean;internalChild?:boolean}
export async function runWorkshop(snapshot:WorkshopSnapshot,manifest:WorkshopManifest,options:WorkshopRunOptions){
  validateSnapshot(snapshot,manifest,[process.env.WANDB_API_KEY??'']);
  if(options.action==='resume'&&(snapshot.project!=='project-03'||!snapshot.parent))throw new Error('Resume requires Project 03 and an explicit parent snapshot');
  const scenario=options.scenario??(snapshot.project==='project-05'?'clear-history':'restart');
  if(!manifest.scenarios.includes(scenario))throw new Error('Unknown lesson scenario');
  const id=options.id??randomUUID(),dir=join(options.output,id);
  try{const existing=JSON.parse(await readFile(operationFile(options.output,id),'utf8'));if(!options.internalChild)return {operation:existing,launched:false,recoveryRequired:existing.phase!=='completed'};}
  catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
  process.env.FORGE_BUDGET_MODE='incremental';process.env.FORGE_BUDGET_USD??='20';
  const c=config(),p=await protocol();await requirePrivateProject(c);
  if(c.model!==p.model||c.inferenceUrl!==p.inferenceUrl)throw new Error('Workshop model/provider changed; capability qualification is required');
  const execution=new Execution(options.output,id,p);await execution.budget.reserve({});
  await mkdir(dir,{recursive:true});await execution.begin('trial',snapshot.sourceCommit);
  const record:WorkshopResult={schemaVersion:1,protocol:'workshop-v1',id,project:snapshot.project,sourceCommit:snapshot.sourceCommit,runnerRevision:await workshopHead(),snapshotId:snapshot.id,snapshotSha256:snapshot.sha256,assisted:snapshot.assisted,action:options.action,variant:options.action==='scenario'?(options.live?'live-app':'offline-app'):options.singleRole?'single-role':snapshot.project==='project-05'?'maker-checker':options.action,trial:1,startedAt:new Date().toISOString(),outcome:'infrastructure_failed',checks:[],evidence:[],conversationIds:[],sandboxIds:[],cleanupStatus:'pending',telemetryStatus:'pending',publicationStatus:'pending',wandbRunId:id.replaceAll('-','').slice(0,20),model:c.model,configuration:publicConfig(c)};
  record.wandbRunId=sha256(id).slice(0,20);
  await writeJson(join(dir,'submission.json'),snapshot);await writeJson(join(dir,'manifest.json'),manifest);
  const abort=new AbortController(),onSignal=()=>abort.abort(new Error('Cancelled'));
  process.once('SIGINT',onSignal);process.once('SIGTERM',onSignal);
  const timer=setTimeout(()=>abort.abort(new Error('Workshop execution timeout')),1100000);
  let candidate=snapshot,telemetry=true;
  try{
    if(options.action!=='scenario'){
      const actor=join(dir,'actor');await mkdir(actor,{recursive:true});
      await withWorkspace({config:c,image:p.sandbox.image,trialId:id,evidenceDir:actor,signal:abort.signal,...execution.workspace('actor',actor)},async sandbox=>{
        record.sandboxIds.push(sandbox.sandboxId);await stageWorkspace(sandbox,await stageWorkshop(snapshot,manifest));
        const roles=snapshot.project==='project-05'&&!options.singleRole?roleSchedule('gen-eval',1):[{role:options.action==='resume'?'fresh-session':'maker',turns:snapshot.project==='project-03'?12:24,readOnly:false}];
        let feedback='';let phase=0;
        for(const role of roles){
          phase++;const toolsDir=join(actor,`phase-${phase}`);await mkdir(toolsDir,{recursive:true});
          const before:Record<string,string>={};for(const name of Object.keys(snapshot.files))before[name]=Buffer.from(await sandbox.files.read('/workspace/task/'+name)).toString('utf8');
          const roleText=snapshot.project==='project-05'?snapshot.files[role.readOnly?'prompts/checker.md':'prompts/maker.md']:'';
          const result=await runPi({...c,maxTurns:role.turns},{role:role.role,prompt:`${manifest.task}\nRead TASK.md and AGENTS.md. You may edit only these files: ${manifest.editable.join(', ')}. ${roleText}\n${options.action==='resume'?'This is a fresh session. Recover from the workspace files, including session-handoff.md, before editing. No previous conversation is supplied.':''}\n${feedback}\n${role.readOnly?'Inspect the candidate and produce a concrete REVIEW with findings and verification. Your filesystem edits will be discarded.':'Implement the narrow task and run its checks.'}`,attributes:{'course.protocol':'workshop-v1','course.project':snapshot.project,'course.snapshot':snapshot.id,'course.source_commit':snapshot.sourceCommit,'course.sandbox_id':sandbox.sandboxId,'course.wandb_run_id':String(record.wandbRunId)},tools:sandboxTools(sandbox,toolsDir),signal:abort.signal,...execution.requestHooks(`phase-${phase}`),finalInstruction:role.readOnly?'Final allowed call: deliver your REVIEW, with findings and observed checks. Do not invent results.':'Final allowed call: describe completed changes, observed checks, failures and next steps. Do not invent results.'});
          record.conversationIds.push(result.conversationId);telemetry&&=result.telemetryComplete;
          await writeJson(join(actor,`phase-${phase}.json`),result);
          const files:Record<string,string>={};for(const name of Object.keys(snapshot.files))files[name]=Buffer.from(await sandbox.files.read('/workspace/task/'+name)).toString('utf8');
          await writeJson(join(actor,`changes-${phase}.json`),Object.keys(files).filter(name=>files[name]!==before[name]).map(path=>({path,before:before[path],after:files[path]})));
          const toolRecords=await Promise.all((await readdir(toolsDir)).filter(name=>name.startsWith('tool-')).map(async name=>JSON.parse(await readFile(join(toolsDir,name),'utf8'))));
          const handoff=before['session-handoff.md'];
          await writeJson(join(actor,`reads-${phase}.json`),{inputFiles:Object.fromEntries(Object.entries(before).map(([name,text])=>[name,sha256(text)])),handoffSha256:sha256(handoff),observedHandoffRead:toolRecords.some(r=>handoff.trim()&&r.stdout?.includes(handoff.trim())),commands:toolRecords.map(r=>({command:r.command,exitCode:r.exitCode})),conversationId:result.conversationId});
          if(role.readOnly){
            for(const [name,text]of Object.entries(before))await sandbox.files.write('/workspace/task/'+name,text);
            const produced=result.completed&&/REVIEW/i.test(result.finalText)&&result.finalText.length>80;
            await writeJson(join(actor,'review.json'),{produced,text:result.finalText,conversationId:result.conversationId});
            record.checks.push({name:'Checker produced its own review',passed:produced});feedback=produced?'Checker review:\n'+result.finalText:'The checker did not produce a review within its allowance.';
          }else{candidate=makeSnapshot(manifest,files,{parent:candidate.id,assisted:snapshot.assisted});await storeSnapshot(options.output,candidate);await writeJson(join(actor,`snapshot-${phase}.json`),candidate);}
        }
      });
    }
    await writeJson(join(dir,'candidate.json'),candidate);record.candidateId=candidate.id;record.candidateSha256=candidate.sha256;
    const grader=join(dir,'grader');await mkdir(grader,{recursive:true});
    const bundle=await bundleWorkshop(candidate,manifest);
    await updateOperation(options.output,id,op=>{op.phase='grading';});
    await withWorkspace({config:c,image:p.sandbox.image,trialId:id+'-grade',evidenceDir:grader,signal:abort.signal,forgeAppNetwork:options.live,...execution.workspace('grader',grader)},async sandbox=>{
      record.sandboxIds.push(sandbox.sandboxId);await stageWorkspace(sandbox,await stageWorkshop(candidate,manifest));
      for(const file of ['workshop.cjs','workshop-process.py','workshop-evaluation.py']){const data=await readFile(join(workshopCourseRoot,'forge/graders',file));await sandbox.files.write('/tmp/'+file,data);record[file+'Sha256']=sha256(data);}
      await sandbox.files.write('/tmp/workshop-adapter.cjs',bundle.app);
      await sandbox.files.write('/tmp/scenario.json',JSON.stringify({project:snapshot.project,snapshotId:candidate.id,snapshotSha256:candidate.sha256,live:Boolean(options.live),scenario,fixture:options.fixture??'long',question:options.question}));
      if(snapshot.project==='project-02'){
        const temp=await mkdtemp(join(tmpdir(),'workshop-sdk-'));
        try{const file=join(temp,'exercise.mjs');await writeFile(file,bundle.sdk);const sdk=await import(pathToFileURL(file).href);const result=await deadline(sdk.inspectWorkspace(sandbox),70000,'Student sandbox command');await writeJson(join(grader,'student-sdk.json'),{sourceSha256:candidate.checksums['workshop/sandbox-task.ts'],result});}
        catch(error){record.checks.push({name:'Student sandbox command',passed:false,detail:redact(String(error),[c.apiKey??''])});}
        finally{await rm(temp,{recursive:true,force:true});}
      }
      const hooks=execution.requestHooks('app');let reserved=0;
      try{if(options.live)for(let number=1;number<=2;number++){await hooks.beforeRequest(number,0);reserved++;}}
      catch(error){
        await execution.event('app_not_launched','Request reservation failed before the app command was created');
        for(let number=1;number<=reserved;number++)await hooks.afterRequest({request:number,payloadBytes:0,inputTokens:0,outputTokens:0,complete:true});
        throw error;
      }
      const env:Record<string,string>={WORKSHOP_PRE_RESERVED:'true',WORKSHOP_MAX_REQUESTS:'2',WORKSHOP_SNAPSHOT:candidate.id,FORGE_PROJECT:snapshot.project,FORGE_TASK:snapshot.project,FORGE_SOURCE_COMMIT:snapshot.sourceCommit,FORGE_SANDBOX_ID:sandbox.sandboxId,FORGE_WANDB_RUN_ID:String(record.wandbRunId),FORGE_APP_ADAPTER:'file:///tmp/workshop-adapter.cjs',FORGE_CONVERSATION_ID:`app-${id}`,FORGE_APP_EVIDENCE_DIR:'/tmp/workshop-grade/app-evidence',FORGE_BUDGET_USD:String(c.budgetUsd),WANDB_ENTITY:c.entity,WANDB_PROJECT:c.project};
      if(options.live)env.WANDB_API_KEY=c.apiKey!;
      try{
        const child=await sandbox.commands.start(['python3','/tmp/workshop-process.py'],{stdin:true,cwd:'/workspace/task',check:false,timeoutMs:500000});
        // The pinned gateway imposes a five-second completion probe on stdin
        // close. The wrapper reads one newline-delimited message, so keep stdin
        // open until the bounded command has actually exited.
        await child.stdin.writeln(JSON.stringify({environment:env}));
        const completed=await child.wait({timeoutMs:470000,signal:abort.signal});
        await child.stdin.close();
        await writeJson(join(grader,'command.json'),{exitCode:completed.exitCode,stdout:redact(completed.stdout,[c.apiKey??'']),stderr:redact(completed.stderr,[c.apiKey??''])});
      }finally{
        // Collect before termination even when grading or the connection failed.
        const names=['result.json','local-check.json','build.log','process.log','process.json','chunks.json','answers.json','ui-events.json','images.json','app-evidence/app.json','app-evidence/request-receipts.json'];
        for(const name of names){try{const bytes=await sandbox.files.read('/tmp/workshop-grade/'+name);await mkdir(join(grader,name,'..'),{recursive:true});await writeFile(join(grader,name),bytes);}catch{}}
        try{const images=JSON.parse(await readFile(join(grader,'images.json'),'utf8'));for(const item of images){if(!/^[a-z0-9-]+\.png$/.test(item.file))throw new Error('Unsafe screenshot name');await writeFile(join(grader,item.file),await sandbox.files.read('/tmp/workshop-grade/'+item.file));}}catch{}
        if(options.live){
          let app:any;try{app=JSON.parse(await readFile(join(grader,'app-evidence/app.json'),'utf8'));}catch{}
          const finished=app?.tracingStatus==='complete';telemetry&&=finished;
          if(app?.conversationId)record.conversationIds.push(app.conversationId);
          for(let number=1;number<=reserved;number++){
            const usage=app?.requests?.[number-1],complete=usage?.status==='reported'||finished&&!usage;
            await hooks.afterRequest({request:number,payloadBytes:0,inputTokens:usage?.inputTokens??0,outputTokens:usage?.outputTokens??0,complete});
          }
        }
      }
      const grade=JSON.parse(await readFile(join(grader,'result.json'),'utf8'));
      record.checks.push(...grade.checks);
      const processReceipt=JSON.parse(await readFile(join(grader,'process.json'),'utf8'));
      record.checks.push({name:'Grader process exited within its bound',passed:processReceipt.childExited&&!processReceipt.forced});
      if(snapshot.project==='project-05'){
        const evaluation=await sandbox.commands.run(['python3','/tmp/workshop-evaluation.py','workshop/evaluation.py','/tmp/workshop-grade/result.json','/tmp/student-evaluation.json'],{cwd:'/workspace/task',check:false,timeoutMs:20000});
        record.checks.push({name:'Student evaluation and W&B log call',passed:evaluation.exitCode===0,detail:evaluation.exitCode?evaluation.stderr:undefined});
        if(evaluation.exitCode===0){const data=await sandbox.files.read('/tmp/student-evaluation.json');await writeFile(join(dir,'student-evaluation.json'),data);}
      }
      record.outcome=record.checks.every(check=>check.passed)?'passed':'task_failed';
    });
  }catch(error){record.error=redact(String(error),[c.apiKey??'',workshopCourseRoot]);record.outcome=String(error).includes('budget_exhausted')?'budget_exhausted':'infrastructure_failed';}
  finally{
    clearTimeout(timer);process.removeListener('SIGINT',onSignal);process.removeListener('SIGTERM',onSignal);
    const settled=await execution.finish(record.outcome);Object.assign(record,{inputTokens:settled.inputTokens,outputTokens:settled.outputTokens,estimatedCostUsd:settled.estimatedCostUsd,sandboxSecondsUpperBound:settled.sandboxSeconds,cleanupStatus:settled.cleanupVerified?'verified':'unknown',telemetryStatus:settled.usageComplete&&telemetry?'complete':'missing'});
    record.grade={passed:record.outcome==='passed',checks:record.checks};record.finishedAt=new Date().toISOString();record.evidence=['submission.json','candidate.json','grader/result.json'];
    await writeJson(join(dir,'trial.json'),record);const ref=await evidenceReference(options.output,join(dir,'trial.json'));await updateOperation(options.output,id,op=>{op.evidence.trial=ref;if(!telemetry){op.telemetry='missing';op.phase='recoverable';}});
  }
  return record;
}
