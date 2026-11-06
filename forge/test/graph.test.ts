import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {driveGraph,decideGraph,newGraph,type GraphDriver} from '../src/graph.js';

test('failed verification rolls back, retries, and pauses until an explicit checksum-bound decision',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'graph-test-'));const patch=join(dir,'candidate.diff'),file=join(dir,'state.json');await writeFile(patch,'sample test patch');
  const sha256=createHash('sha256').update('sample test patch').digest('hex');let makers=0,rollbacks=0,active=0,maxActive=0;
  const driver:GraphDriver={plan:async()=> 'frozen acceptance',make:async()=>({patch,sha256,trialId:String(++makers)}),
    verify:async(_candidate,lane)=>{active++;maxActive=Math.max(maxActive,active);await new Promise(r=>setTimeout(r,10));active--;return {lane,passed:makers===2,evidence:'unit-test-fixture'};},
    rollback:async()=>{rollbacks++;}};
  try {
    const s=await driveGraph(file,newGraph('fixture'),driver);assert.equal(s.node,'approval');assert.equal(makers,2);assert.equal(rollbacks,1);assert.equal(maxActive,2);
    await driveGraph(file,s,driver);assert.equal(makers,2);
    await assert.rejects(decideGraph(file,'approve','test-human','wrong'),/changed/);
    assert.equal((await decideGraph(file,'approve','test-human',sha256)).node,'done');
  }finally{await rm(dir,{recursive:true,force:true});}
});
test('graph never replays an ambiguous pending operation',async()=>{
  const s={...newGraph('fixture'),pendingOperation:'make-1'};
  await assert.rejects(driveGraph('/tmp/not-written.json',s,{} as GraphDriver),/Reconcile/);
});
