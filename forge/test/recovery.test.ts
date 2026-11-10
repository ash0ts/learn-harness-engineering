import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createOperation,updateOperation} from '../src/operations.js';
import {writeJson} from '../src/records.js';
import {recoverAccounting,proveRejectedTag} from '../src/recovery.js';
import {createSandboxClient} from '@coreweave/cwsandbox/wandb';
import {disposeSandboxClient} from '../src/sandbox.js';
const pricing={inputPerMillionUsd:0.25,outputPerMillionUsd:1.25,cpuHourUsd:0.128,memoryGiBHourUsd:0.0212};
test('the actual pinned SDK rejects an overlength tag without reaching transport',async()=>{
 const client=createSandboxClient({apiKey:'unused-test-key',entity:'test',project:'private'});
 try{const proof=await proveRejectedTag(client,'control-project-01-baseline-43c63357-a96b-437a-aa01-c832eebace8e');assert.equal(proof.transportCalls,0);await assert.rejects(proveRejectedTag(client,'valid-tag'),/Only the observed/);}
 finally{await disposeSandboxClient(client,[]);}
});
test('transport failures can never be reconciled as zero-dispatch validation',async()=>{
 const transport={start:async()=>{}};const client={transport,create:()=>transport.start()};
 await assert.rejects(proveRejectedTag(client,'x'.repeat(60)),/unproven/);
});
async function fixture(){
 const root=await mkdtemp(join(tmpdir(),'recovery-'));
 const op=await createOperation(root,{id:'test',kind:'qualification',sourceCommit:'a'.repeat(40),protocolSha256:'b'.repeat(64),identity:{entity:'class',project:'private'}});
 await writeJson(join(root,'test/execution-configuration.json'),{protocol:{pricing},incremental:true});
 op.requests['agent-1']={status:'reported',payloadBytes:100,inputTokens:400,outputTokens:60};
 op.sandboxIds=['sandbox'];op.events=[{at:'2026-11-10T00:00:00Z',event:'sandbox_launch',detail:'test/qualification/sandbox.json'}];
 await writeJson(join(root,'test/qualification/sandbox.json'),{state:'terminated',sandboxId:'sandbox',requestedAt:'2026-11-10T00:00:00Z',terminatedAt:'2026-11-10T00:01:00Z'});
 return {root,op};
}
test('malformed response with provider usage and terminal receipts has known cost',async()=>{
 const {root,op}=await fixture();try{op.executionOutcome='qualification_failed';const r=await recoverAccounting(root,op);assert.equal(r.known,true);if(r.known){assert.equal(r.inputTokens,400);assert.equal(r.sandboxSeconds,60);assert.ok(r.estimatedCostUsd>0);}assert.equal(op.executionOutcome,'qualification_failed');}finally{await rm(root,{recursive:true});}
});
test('unknown, negative or nonfinite usage never becomes zero',async()=>{
 const {root,op}=await fixture();try{for(const usage of [{status:'unknown'},{status:'reported',inputTokens:-1,outputTokens:1},{status:'reported',inputTokens:NaN,outputTokens:1}] as const){op.requests['agent-2']={payloadBytes:100,...usage};assert.equal((await recoverAccounting(root,op)).known,false);}}finally{await rm(root,{recursive:true});}
});
test('ambiguous creation and incomplete cancellation retain accounting block',async()=>{
 const {root,op}=await fixture();try{for(const state of ['creation_unknown','cleanup_failed']){await writeJson(join(root,'test/qualification/sandbox.json'),{state,requestedAt:'2026-11-10T00:00:00Z'});assert.equal((await recoverAccounting(root,op)).known,false);}}finally{await rm(root,{recursive:true});}
});
test('known usage does not clear an unverified local child',async()=>{
 const {root,op}=await fixture();try{
  op.events.push({at:'2026-11-10T00:00:00Z',event:'child_launch',detail:'test/app-child.json'});
  assert.equal((await recoverAccounting(root,op)).known,false);
  await writeJson(join(root,'test/app-child.json'),{exitCode:0,cleanupVerified:false});assert.equal((await recoverAccounting(root,op)).known,false);
  await writeJson(join(root,'test/app-child.json'),{exitCode:0,cleanupVerified:true});assert.equal((await recoverAccounting(root,op)).known,true);
 }finally{await rm(root,{recursive:true});}
});
test('no-dispatch journal proves an unused reservation, but symlinks are refused',async()=>{
 const {root,op}=await fixture();try{op.sandboxIds=[];await writeJson(join(root,'test/qualification/sandbox.json'),{state:'creating'});const r=await recoverAccounting(root,op);assert.equal(r.known,true);if(r.known)assert.equal(r.sandboxSeconds,0);op.events[0].detail='../escape';await assert.rejects(recoverAccounting(root,op),/Unsafe/);}finally{await rm(root,{recursive:true});}
});
