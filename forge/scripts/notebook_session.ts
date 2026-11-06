/** Account for the normal Forge EDIT workflow without uploading notebook source. */
import {readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {createSandboxClient} from '@coreweave/cwsandbox/wandb';
import {Budget} from '../src/budget.js';
import {config,requireLive} from '../src/config.js';
import {courseRoot} from '../src/staging.js';
import {writeJson} from '../src/records.js';

const [action,id,value]=process.argv.slice(2);
if(!['reserve','attach','stop'].includes(action)||!/^notebook-[\w-]+$/.test(id??''))throw new Error('reserve ID NOTEBOOK_ID | attach ID SANDBOX_ID | stop ID');
const c=config();requireLive(c);
const rates=JSON.parse(await readFile(join(courseRoot,'forge/notebook-runtime.json'),'utf8'));
const file=join(courseRoot,'forge/local-results/notebook-sessions',`${id}.json`);
const budget=new Budget(join(courseRoot,'forge/local-results/budget.json'),c.budgetUsd);
if(action==='reserve') {
  if(!value)throw new Error('Notebook ID required');
  await budget.reserve({[id]:rates.reservationPerEditorSessionUsd});
  await writeJson(file,{id,notebookId:value,reservedUsd:rates.reservationPerEditorSessionUsd,startedAt:new Date().toISOString(),status:'reserved'});
  console.log('Reserved notebook EDIT compute',id);
} else {
  const receipt=JSON.parse(await readFile(file,'utf8'));
  // Forge notebook runtimes use the sandbox billing project, while notebook
  // source/artifacts remain in the selected private course project.
  const client=createSandboxClient({apiKey:c.apiKey,entity:c.entity,project:'sandbox'});
  if(action==='attach') {
    if(!value)throw new Error('Observed sandbox ID required');
    const info=await client.get(value);
    if(info.resourceRequests?.cpu!=='2'||info.resourceRequests?.memory!=='4Gi')throw new Error('Notebook resource shape changed; verify rates before proceeding');
    Object.assign(receipt,{sandboxId:value,status:info.status,resourceRequests:info.resourceRequests,resourceLimits:info.resourceLimits,cpu:2,memoryGiB:4,estimatedHourlyUsd:rates.expectedHourlyUsd});
    await writeJson(file,receipt);console.log('Notebook resources verified',id);
  } else {
    if(!receipt.sandboxId)throw new Error('Attach and verify the observed runtime first');
    if(receipt.status==='terminated')throw new Error('Session already settled; do not double-charge');
    const response=await fetch('https://api.wandb.ai/graphql',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Basic '+Buffer.from('api:'+c.apiKey).toString('base64')},body:JSON.stringify({query:'mutation($i:TerminateSandboxInput!){terminateSandbox(input:$i){success}}',variables:{i:{sandboxId:receipt.sandboxId,reason:'USER_REQUEST'}}}),signal:AbortSignal.timeout(30000)});
    const result=await response.json() as {errors?:unknown;data?:{terminateSandbox:{success:boolean}}};
    if(!response.ok||result.errors||!result.data?.terminateSandbox.success)throw new Error('Notebook termination was not acknowledged');
    const sandbox=await client.fromId(receipt.sandboxId);
    await sandbox.wait({targetStatus:'terminal',timeoutMs:30000});
    const endedAt=new Date().toISOString();
    const seconds=(Date.parse(endedAt)-Date.parse(receipt.startedAt))/1000;
    const estimate=seconds/3600*receipt.estimatedHourlyUsd;
    await budget.settle(id,estimate);
    await writeJson(file,{...receipt,status:'terminated',endedAt,secondsUpperBound:seconds,estimatedCostUsd:estimate});
    console.log('Notebook terminated and accounted',id,estimate);
  }
}
