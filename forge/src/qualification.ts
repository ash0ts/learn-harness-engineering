import {mkdir, readFile} from 'node:fs/promises';
import {join, resolve} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {config, requireLive, requirePrivateProject} from './config.js';
import {Budget, estimate} from './budget.js';
import {protocol} from './trial.js';
import {courseRoot,readTask,sourceHead,stageTask} from './staging.js';
import {sandboxTools,stageWorkspace,withWorkspace} from './sandbox.js';
import {runPi} from './pi.js';
import {writeJson,redact} from './records.js';

export async function qualify(output=join(courseRoot,'forge/local-results')) {
  output=resolve(output);await mkdir(output,{recursive:true});
  const c=config();requireLive(c);await requirePrivateProject(c);const p=await protocol();const source=await sourceHead();
  const id=`qualification-${randomUUID()}`;const dir=join(output,id);await mkdir(dir);
  const budget=new Budget(join(output,'budget.json'),c.budgetUsd);await budget.reserve({[id]:2});
  const record:Record<string,unknown>={schemaVersion:1,id,sourceCommit:source,protocolSha256:createHash('sha256').update(JSON.stringify(p)).digest('hex'),startedAt:new Date().toISOString(),passed:false};
  let spend:number|null=null;
  try {
    const response=await fetch(`${c.inferenceUrl}/models`,{headers:{Authorization:`Bearer ${c.apiKey}`,'OpenAI-Project':`${c.entity}/${c.project}`},signal:AbortSignal.timeout(30000)});
    if(!response.ok)throw new Error(`Inference catalog HTTP ${response.status}`);
    const models=await response.json() as {data?:Array<{id:string}>};
    if(!models.data?.some(m=>m.id===c.model))throw new Error(`Frozen model unavailable: ${c.model}`);
    record.modelAvailable=true;
    const staged=await stageTask(await readTask('project-04'),'minimal',source);
    let input=0,outputTokens=0;
    const started=Date.now();
    await withWorkspace({config:c,image:p.sandbox.image,trialId:id,evidenceDir:join(dir,'sandbox'),signal:AbortSignal.timeout(300000)},async sandbox=>{
      record.sandboxId=sandbox.sandboxId;await stageWorkspace(sandbox,staged.archive);
      const sleeping=await sandbox.commands.start(['sleep','30'],{check:false});
      try {await sleeping.wait({timeoutMs:100});throw new Error('Timeout probe unexpectedly completed');}
      catch(error){if(String(error).includes('unexpectedly'))throw error;await sleeping.cancel({timeoutMs:10000});}
      try {
        const cancelled=await sleeping.wait({timeoutMs:10000});record.cancelledExitCode=cancelled.exitCode;
        if(cancelled.exitCode===0)throw new Error('Cancellation was not observed');
      } catch(error) {
        if(!/cancelled/i.test(String(error)))throw error;
        record.cancelledObserved=true;
      }
      const result=await runPi({...c,maxTurns:3},{role:'qualification',prompt:'Call sandbox_command once to run node --version and python3 --version. Report the actual versions. Do not edit files.',attributes:{'course.project':'qualification','course.source_commit':source,'course.sandbox_id':sandbox.sandboxId},tools:sandboxTools(sandbox,join(dir,'tools')),signal:AbortSignal.timeout(180000)});
      record.agent=result;
      if(!result.telemetryComplete || !result.completed)throw new Error('Pi capability/usage qualification failed');
      input=result.inputTokens;outputTokens=result.outputTokens;
    });
    const seconds=(Date.now()-started)/1000;
    const appEvidence=join(dir,'app-telemetry.json');const appResult=join(dir,'app-results.json');
    const exitCode=await new Promise<number>((resolve,reject)=>{
      const child=spawn(process.execPath,['--import',join(courseRoot,'forge/node_modules/tsx/dist/loader.mjs'),join(courseRoot,'forge/src/cli.ts'),'services',join(courseRoot,'projects/shared'),appResult,join(courseRoot,'forge/fixtures/course.txt'),'--live'],{cwd:courseRoot,env:{...process.env,FORGE_APP_EVIDENCE:appEvidence,FORGE_SOURCE_COMMIT:source},stdio:'inherit'});
      child.on('error',reject);child.on('close',code=>resolve(code??1));
    });
    const app=JSON.parse(await readFile(appEvidence,'utf8'));record.app=app;
    if(exitCode!==0 || app.usage.calls!==2)throw new Error('Live app service qualification failed');
    input+=app.usage.inputTokens;outputTokens+=app.usage.outputTokens;
    spend=estimate(input,outputTokens,seconds,p.pricing);
    record.passed=true;record.inputTokens=input;record.outputTokens=outputTokens;
  } catch(error) {record.error=redact(String(error),[c.apiKey]);}
  finally {
    record.estimatedCostUsd=spend;record.finishedAt=new Date().toISOString();
    await writeJson(join(dir,'qualification.json'),record);await budget.settle(id,spend);
  }
  return record;
}
