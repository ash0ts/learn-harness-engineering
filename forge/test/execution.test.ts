import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile,rm} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {Execution} from '../src/execution.js';
import {Budget} from '../src/budget.js';
import {operationFile} from '../src/operations.js';
import {writeJson} from '../src/records.js';

const p={maxInputBytes:524288,maxOutputTokens:4096,pricing:{inputPerMillionUsd:.25,outputPerMillionUsd:1.25,cpuHourUsd:.128,memoryGiBHourUsd:.0212}};
test('a low student budget stops before dispatch, while known failed-response usage settles once',async()=>{
  const prior={...process.env};Object.assign(process.env,{WANDB_ENTITY:'test',WANDB_PROJECT:'private',FORGE_BUDGET_USD:'0.2',FORGE_BUDGET_MODE:'incremental'});
  const root=await mkdtemp(join(tmpdir(),'operation-budget-'));
  try{
    const run=new Execution(root,'student',p);await run.begin('trial','a'.repeat(40));
    await assert.rejects(new Execution(root,'student',p).begin('trial','a'.repeat(40)),/duplicate/);
    const hooks=run.requestHooks('maker');await hooks.beforeRequest(1,1000);
    await assert.rejects(hooks.beforeRequest(2,1000),/budget_exhausted/);
    await hooks.afterRequest({request:1,payloadBytes:1000,inputTokens:50,outputTokens:10,complete:true});
    await hooks.afterRequest({request:1,payloadBytes:1000,inputTokens:50,outputTokens:10,complete:true});
    const final=await run.finish('task_failed');assert.equal(final.usageComplete,true);assert.equal(final.estimatedCostUsd,.000025);
    const ledger=JSON.parse(await readFile(join(root,'budget.json'),'utf8'));assert.equal(ledger.spentEstimateUsd,.000025);assert.deepEqual(ledger.reservations,{});
    const next=new Execution(root,'student-repeat',p);await next.begin('trial','a'.repeat(40));await next.requestHooks('maker').beforeRequest(1,1000);
    await next.requestHooks('maker').afterRequest({request:1,payloadBytes:1000,inputTokens:0,outputTokens:0,complete:false});
    await assert.rejects(new Budget(join(root,'budget.json'),.2).reserve({other:.01}),/Missing usage/);
    assert.equal(JSON.parse(await readFile(operationFile(root,'student-repeat'),'utf8')).requests['maker-1'].status,'unknown');
  }finally{process.env=prior;await rm(root,{recursive:true,force:true});}
});
test('finalization retains a cleanup block for a missing or unverified child receipt',async()=>{
 const prior={...process.env};Object.assign(process.env,{WANDB_ENTITY:'test',WANDB_PROJECT:'private',FORGE_BUDGET_USD:'20',FORGE_BUDGET_MODE:'incremental'});
 const root=await mkdtemp(join(tmpdir(),'operation-child-'));
 try{
  const run=new Execution(root,'child-test',p);await run.begin('qualification','a'.repeat(40));await run.event('child_launch','child-test/app-child.json');
  assert.equal((await run.finish('qualification_failed')).cleanupVerified,false);
  await writeJson(join(root,'child-test/app-child.json'),{exitCode:0,cleanupVerified:false});assert.equal((await run.finish('qualification_failed')).cleanupVerified,false);
  assert.equal(JSON.parse(await readFile(operationFile(root,'child-test'),'utf8')).phase,'blocked_unknown');
  await writeJson(join(root,'child-test/app-child.json'),{exitCode:0,cleanupVerified:true});assert.equal((await run.finish('qualification_failed')).cleanupVerified,true);
 }finally{process.env=prior;await rm(root,{recursive:true,force:true});}
});
