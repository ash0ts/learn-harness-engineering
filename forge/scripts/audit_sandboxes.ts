/** Read-only remote cleanup audit for this course's recorded workers and editors. */
import {readFile,readdir} from 'node:fs/promises';
import {join,relative} from 'node:path';
import {createSandboxClient} from '@coreweave/cwsandbox/wandb';
import {config,requirePrivateProject} from '../src/config.js';
import {courseRoot} from '../src/staging.js';
import {writeJson} from '../src/records.js';

const c=config();await requirePrivateProject(c);
const root=join(courseRoot,'forge/local-results');
const ledger=JSON.parse(await readFile(join(root,'budget.json'),'utf8'));
const client=createSandboxClient({apiKey:c.apiKey,entity:c.entity,project:c.project});
const inventory=await client.listAll({tags:['harness-course'],showTerminated:true,timeoutMs:60000});
const statuses=new Map(inventory.map(s=>[s.sandboxId,s.status]));
const terminal=(status:unknown)=>['terminated','completed','failed'].includes(String(status));
const rows:Array<Record<string,unknown>>=[];
for(const entry of await readdir(root,{recursive:true})) {
  if(!entry.endsWith('/sandbox.json'))continue;
  const path=join(root,entry),journal=JSON.parse(await readFile(path,'utf8'));
  const reconciliation=ledger.reconciliations?.find((r:{id:string;estimatedUsd:number})=>r.id===journal.trialId&&r.estimatedUsd===0);
  if(!journal.sandboxId) {
    rows.push({journal:relative(root,path),trialId:journal.trialId,localState:journal.state,verified:!!reconciliation,evidence:reconciliation?.evidence??'No remote ID or proven local rejection'});
    continue;
  }
  const status=statuses.get(journal.sandboxId)??(await client.get(journal.sandboxId,{timeoutMs:30000})).status;
  rows.push({journal:relative(root,path),trialId:journal.trialId,sandboxId:journal.sandboxId,localState:journal.state,remoteStatus:status,verified:terminal(status)});
}
const notebookClient=createSandboxClient({apiKey:c.apiKey,entity:c.entity,project:'sandbox'});
for(const name of await readdir(join(root,'notebook-sessions'))) {
  if(!name.endsWith('.json'))continue;
  const receipt=JSON.parse(await readFile(join(root,'notebook-sessions',name),'utf8'));
  if(!receipt.sandboxId){rows.push({journal:'notebook-sessions/'+name,verified:false,evidence:'Editor receipt has no attached remote ID'});continue;}
  const remote=await notebookClient.get(receipt.sandboxId,{timeoutMs:30000});
  rows.push({journal:'notebook-sessions/'+name,sandboxId:receipt.sandboxId,remoteStatus:remote.status,verified:terminal(remote.status)});
}
const active=inventory.filter(s=>!terminal(s.status)).map(s=>({sandboxId:s.sandboxId,status:s.status}));
const result={schemaVersion:1,verifiedAt:new Date().toISOString(),allTerminal:rows.length>0&&rows.every(r=>r.verified)&&active.length===0,recordedWorkers:rows.length,remoteCourseWorkers:inventory.length,active,workers:rows};
await writeJson(join(root,'sandbox-final-audit.json'),result);
console.log(JSON.stringify({allTerminal:result.allTerminal,recordedWorkers:rows.length,active,unverified:rows.filter(r=>!r.verified)},null,2));
