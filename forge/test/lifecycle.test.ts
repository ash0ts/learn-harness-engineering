import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile,rm,writeFile,symlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {boundedChild,deadline} from '../src/lifecycle.js';
import {createOperation,evidenceReference,verifyEvidence} from '../src/operations.js';

test('a lingering child is bounded and its forced shutdown remains explicit',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'course-shutdown-'));
  try {const result=await boundedChild(process.execPath,['-e','process.on("SIGTERM",()=>{});setInterval(()=>{},1000)'],{cwd:dir,receipt:join(dir,'lifecycle.json'),timeoutMs:200,graceMs:50});assert.equal(result.forced,true);assert.equal(result.signal,'SIGKILL');assert.deepEqual(JSON.parse(await readFile(join(dir,'lifecycle.json'),'utf8')),result);}
  finally {await rm(dir,{recursive:true,force:true});}
});
test('shutdown timeouts are errors, never silent success',async()=>{await assert.rejects(deadline(new Promise(()=>{}),10,'trace shutdown'),/trace shutdown timed out/);});
test('operation IDs cannot launch twice and evidence is portable but immutable',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'course-operation-'));
  try {
    const seed={id:'trial-1',kind:'trial' as const,sourceCommit:'a'.repeat(40),protocolSha256:'b'.repeat(64),identity:{entity:'test',project:'private'}};
    await createOperation(dir,seed);await assert.rejects(createOperation(dir,seed),/EEXIST/);
    const file=join(dir,'patch.diff');await writeFile(file,'patch');const ref=await evidenceReference(dir,file);assert.equal(ref.path,'patch.diff');assert.equal(await verifyEvidence(dir,ref),file);
    await writeFile(file,'changed');await assert.rejects(verifyEvidence(dir,ref),/checksum/);
    await symlink(file,join(dir,'link'));await assert.rejects(evidenceReference(dir,join(dir,'link')),/symlink/);await assert.rejects(verifyEvidence(dir,{path:'../outside',sha256:''}),/Unsafe/);
  } finally {await rm(dir,{recursive:true,force:true});}
});
