import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,rm,mkdir} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {enforceGraphRoute,decideWorkshopGraph} from '../src/workshop-graph.js';
test('routing cannot bypass a failed check or unknown usage',()=>{
  const observed={phase:'verified',outcome:'task_failed',repairs:0,maxRepairs:2,cleanupVerified:true,usageComplete:true};
  assert.throws(()=>enforceGraphRoute('approval',observed),/verified candidate/);
  assert.equal(enforceGraphRoute('repair',{...observed,usageComplete:false}),'recover');
  assert.equal(enforceGraphRoute('repair',{...observed,repairs:2}),'stop');
  assert.equal(enforceGraphRoute('approval',{...observed,outcome:'passed'}),'approval');
});
test('decisions require the exact current checksum and remain immutable',async()=>{
  const root=await mkdtemp(join(tmpdir(),'workshop-decision-'));
  try{
    const dir=join(root,'workshop/controllers');await mkdir(dir,{recursive:true});
    const hash='a'.repeat(64);await writeFile(join(dir,'graph-test.json'),JSON.stringify({node:'approval',verifiedSha256:hash,candidate:{sha256:hash},events:[]}));
    await assert.rejects(decideWorkshopGraph(root,'graph-test','approve','b'.repeat(64),'test-fixture','isolated test'),/checksum/);
    const first=await decideWorkshopGraph(root,'graph-test','reject',hash,'test-fixture','isolated test');
    assert.deepEqual(await decideWorkshopGraph(root,'graph-test','reject',hash,'test-fixture','isolated test'),first);
    assert.equal(JSON.parse(await readFile(join(dir,'graph-test.json'),'utf8')).node,'rejected');
    await assert.rejects(decideWorkshopGraph(root,'graph-test','approve',hash,'test-fixture','cannot overwrite'),/checksum/);
  }finally{await rm(root,{recursive:true,force:true});}
});
