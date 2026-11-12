import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile,rm,writeFile,symlink,mkdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {boundedChild,deadline,linuxGroupMembers,parseLinuxProcessStat} from '../src/lifecycle.js';
import {createOperation,evidenceReference,verifyEvidence,validateOperation} from '../src/operations.js';

test('a lingering child is bounded and its forced shutdown remains explicit',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'course-shutdown-'));
  try {const result=await boundedChild(process.execPath,['-e','process.on("SIGTERM",()=>{});setInterval(()=>{},1000)'],{cwd:dir,receipt:join(dir,'lifecycle.json'),timeoutMs:200,graceMs:50});assert.equal(result.forced,true);assert.equal(result.signal,'SIGKILL');assert.deepEqual(JSON.parse(await readFile(join(dir,'lifecycle.json'),'utf8')),result);}
  finally {await rm(dir,{recursive:true,force:true});}
});
test('shutdown timeouts are errors, never silent success',async()=>{await assert.rejects(deadline(new Promise(()=>{}),10,'trace shutdown'),/trace shutdown timed out/);});
test('Linux group inspection distinguishes exited descendants and preserves live members',async()=>{
 const root=await mkdtemp(join(tmpdir(),'course-proc-'));
 try{
  for(const [pid,state,group] of [[736,'Z',723],[737,'S',723],[738,'R',700]] as const){await mkdir(join(root,String(pid)));await writeFile(join(root,String(pid),'stat'),`${pid} (worker (test)) ${state} 1 ${group} 0 0`);}
  assert.deepEqual(await linuxGroupMembers(723,root),[{pid:736,state:'Z'},{pid:737,state:'S'}]);
  assert.deepEqual(parseLinuxProcessStat('736 (esbuild) Z 1 723 0 0'),{pid:736,group:723,state:'Z'});
  await writeFile(join(root,'737/stat'),'invalid');await assert.rejects(linuxGroupMembers(723,root),/Malformed/);
 }finally{await rm(root,{recursive:true,force:true});}
});
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

test('a spawn failure has a receipt rather than a missing child outcome',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'course-spawn-'));
 try{const result=await boundedChild('/does-not-exist',[],{cwd:dir,receipt:join(dir,'child.json'),timeoutMs:100});assert.equal(result.exitCode,1);assert.equal(result.cleanupVerified,true);assert.match(result.error??'',/ENOENT/);assert.equal(JSON.parse(await readFile(join(dir,'child.json'),'utf8')).exitCode,1);}finally{await rm(dir,{recursive:true});}
});
test('operation contract rejects malformed usage and source revisions',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'course-contract-'));
 try{const op=await createOperation(dir,{id:'contract',kind:'trial',sourceCommit:'a'.repeat(40),protocolSha256:'b'.repeat(64),identity:{entity:'class',project:'private'}});op.requests.bad={status:'reported',payloadBytes:10,inputTokens:-1,outputTokens:1};await assert.rejects(validateOperation(op),/constraint/);delete op.requests.bad;op.sourceCommit='HEAD';await assert.rejects(validateOperation(op),/constraint/);}finally{await rm(dir,{recursive:true});}
});
