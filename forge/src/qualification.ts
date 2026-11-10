import {mkdir,readFile} from 'node:fs/promises';
import {join,resolve,relative} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {config,requireLive,requirePrivateProject} from './config.js';
import {protocol} from './trial.js';
import {courseRoot,readTask,sourceHead,stageTask} from './staging.js';
import {sandboxTools,stageWorkspace,withWorkspace,runSandboxCommand} from './sandbox.js';
import {runPi} from './pi.js';
import {writeJson,redact} from './records.js';
import {boundedChild} from './lifecycle.js';
import {Execution} from './execution.js';
import {updateOperation,evidenceReference} from './operations.js';

export async function qualify(output=process.env.FORGE_RESULTS_DIR??join(courseRoot,'forge/local-results'),operationId?:string){
  output=resolve(output);await mkdir(output,{recursive:true});
  const c=config();requireLive(c);await requirePrivateProject(c);const p=await protocol(),source=await sourceHead();
  const id=operationId??`qualification-${randomUUID()}`,dir=join(output,id);await mkdir(dir,{recursive:true});
  const execution=new Execution(output,id,p);await execution.begin('qualification',source);
  if(!execution.incremental)await execution.budget.reserve({[id]:2});
  const record:Record<string,any>={schemaVersion:2,id,sourceCommit:source,protocolSha256:createHash('sha256').update(JSON.stringify(p)).digest('hex'),protocol:p,startedAt:new Date().toISOString(),passed:false};
  let appLaunched=false,appReserved=0;
  try {
    const response=await fetch(`${c.inferenceUrl}/models`,{headers:{Authorization:`Bearer ${c.apiKey}`,'OpenAI-Project':`${c.entity}/${c.project}`},signal:AbortSignal.timeout(30000)});
    if(!response.ok)throw new Error(`Inference catalog HTTP ${response.status}`);
    const models=await response.json() as {data?:Array<{id:string}>};
    if(!models.data?.some(m=>m.id===c.model))throw new Error(`Frozen model unavailable: ${c.model}`);
    record.modelAvailable=true;
    const staged=await stageTask(await readTask('project-04'),'minimal',source),sandboxDir=join(dir,'sandbox');
    await withWorkspace({config:c,image:p.sandbox.image,trialId:id,evidenceDir:sandboxDir,signal:AbortSignal.timeout(300000),...execution.workspace('qualification',sandboxDir)},async sandbox=>{
      record.sandboxId=sandbox.sandboxId;await stageWorkspace(sandbox,staged.archive);
      try{await runSandboxCommand(sandbox,'sleep 30',{timeoutMs:500,cancellationEvidence:join(dir,'cancellation.json')});throw new Error('Timeout probe unexpectedly completed');}
      catch(error){if(/unexpectedly|unverified/.test(String(error)))throw error;record.cancellationVerified=true;}
      const result=await runPi({...c,maxTurns:3},{role:'qualification',prompt:'Call sandbox_command once to run node --version and python3 --version. Report the actual versions. Do not edit files.',attributes:{'course.project':'qualification','course.source_commit':source,'course.sandbox_id':sandbox.sandboxId},tools:sandboxTools(sandbox,join(dir,'tools')),signal:AbortSignal.timeout(180000),...execution.requestHooks('agent')});
      record.agent=result;
      if(!result.telemetryComplete||!result.completed)throw new Error('Pi capability/usage qualification failed');
    });
    const appEvidence=join(dir,'app-telemetry.json'),appHooks=execution.requestHooks('app');
    // Both bounded app calls are covered before launching its isolated process.
    // Each dispatch and response is also journaled by the app before proceeding.
    await appHooks.beforeRequest(1,p.maxInputBytes);appReserved=1;await appHooks.beforeRequest(2,p.maxInputBytes);appReserved=2;
    await execution.event('child_launch',relative(output,join(dir,'app-child.json')));
    appLaunched=true;
    const result=await boundedChild(process.execPath,['--import',join(courseRoot,'forge/node_modules/tsx/dist/loader.mjs'),join(courseRoot,'forge/src/cli.ts'),'services',join(courseRoot,'projects/shared'),join(dir,'app-results.json'),join(courseRoot,'forge/fixtures/course.txt'),'--live'],{cwd:courseRoot,log:join(dir,'app.log'),receipt:join(dir,'app-child.json'),timeoutMs:300000,env:{...process.env,FORGE_APP_EVIDENCE:appEvidence,FORGE_SOURCE_COMMIT:source}});
    const app=JSON.parse(await readFile(appEvidence,'utf8'));record.app=app;record.appChild=result;
    for(let i=0;i<2;i++){
      const request=app.requests?.[i];
      await appHooks.afterRequest({request:i+1,payloadBytes:p.maxInputBytes,inputTokens:request?.inputTokens??0,outputTokens:request?.outputTokens??0,complete:request?request.status==='reported':Array.isArray(app.requests)});
    }
    if(result.exitCode!==0||result.forced||app.usage.calls!==2||app.tracingStatus!=='complete')throw new Error('Live app service qualification failed');
    record.passed=true;
  }catch(error){record.error=redact(String(error),[c.apiKey]);}
  finally{
    if(!appLaunched)for(let i=1;i<=appReserved;i++)await execution.requestHooks('app').afterRequest({request:i,payloadBytes:p.maxInputBytes,inputTokens:0,outputTokens:0,complete:true});
    const accounting=await execution.finish(record.passed?'passed':'qualification_failed');Object.assign(record,accounting);
    record.finishedAt=new Date().toISOString();await writeJson(join(dir,'qualification.json'),record);
    if(!execution.incremental)await execution.budget.settle(id,accounting.estimatedCostUsd);
    const ref=await evidenceReference(output,join(dir,'qualification.json'));
    await updateOperation(output,id,op=>{op.evidence.qualification=ref;if(accounting.cleanupVerified&&accounting.usageComplete)op.phase='completed';});
  }
  return record;
}
