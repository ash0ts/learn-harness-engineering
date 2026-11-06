/** Live app tracing qualification in a process that never initializes Pi/Weave. */
import {randomUUID} from 'node:crypto';
import {readFile,mkdir} from 'node:fs/promises';
import {join} from 'node:path';
import {createAppHooks} from '../src/app.js';
import {config} from '../src/config.js';
import {Budget,estimate} from '../src/budget.js';
import {courseRoot,sourceHead} from '../src/staging.js';
import {writeJson} from '../src/records.js';

if(!process.argv.includes('--execute'))throw new Error('Live concurrency qualification requires --execute');
const c=config(),id=`concurrency-${randomUUID()}`,sourceCommit=await sourceHead();
const directory=join(courseRoot,'forge/local-results',id);await mkdir(directory,{recursive:true});
const budget=new Budget(join(courseRoot,'forge/local-results/budget.json'),c.budgetUsd);
await budget.reserve({[id]:2});
const record:Record<string,unknown>={schemaVersion:1,id,sourceCommit,startedAt:new Date().toISOString(),passed:false};
let cost:number|null=null;
try {
  const sessions=await Promise.all(['alpha','beta'].map(label=>createAppHooks(`concurrency-${label}`,{
    conversationId:`app-${id}-${label}`,evidencePath:join(directory,`${label}.json`),
    attributes:{'course.project':'qualification','course.task':'concurrent-app-traces','course.variant':label,'course.trial':id,'course.source_commit':sourceCommit,'course.sandbox_id':'local-app-process','course.wandb_run_id':'course-audit-20261106'},
  })));
  const results=await Promise.allSettled(sessions.map(async(hooks,index)=>{
    try {
      for(let turn=1;turn<=2;turn++)await hooks.turn(`Concurrent session ${index} turn ${turn}`,async()=>{
        const citations=hooks.tool('read_sample_excerpt',{session:index,turn},()=>[{documentId:'sample',documentTitle:'Sample course fixture',chunkIndex:0,excerpt:`The measurement marker is session-${index}-turn-${turn}.`}]);
        return hooks.answer('Reply with only the measurement marker in the supplied excerpt.',citations);
      });
    } finally {await hooks.shutdown();}
  }));
  const evidence=await Promise.all(['alpha','beta'].map(async label=>JSON.parse(await readFile(join(directory,`${label}.json`),'utf8'))));
  record.sessions=evidence;record.results=results.map(r=>r.status==='fulfilled'?{status:r.status}:{status:r.status,error:String(r.reason)});
  if(results.some(r=>r.status==='rejected')||evidence.some(e=>e.usage.calls!==2))throw new Error('Concurrent live inference failed or omitted expected usage');
  const input=evidence.reduce((a,e)=>a+e.usage.inputTokens,0),output=evidence.reduce((a,e)=>a+e.usage.outputTokens,0);
  const protocol=JSON.parse(await readFile(join(courseRoot,'forge/protocol.json'),'utf8'));
  cost=estimate(input,output,0,protocol.pricing);record.inputTokens=input;record.outputTokens=output;record.passed=true;
}catch(error){record.error=String(error);}
finally {
  record.estimatedCostUsd=cost;record.finishedAt=new Date().toISOString();
  await writeJson(join(directory,'concurrency.json'),record);await budget.settle(id,cost);console.log(JSON.stringify(record,null,2));
}
