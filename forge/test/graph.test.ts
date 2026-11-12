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
  let release:()=>void;let bothStarted=new Promise<void>(resolve=>{release=resolve;});
  const driver:GraphDriver={plan:async()=> 'frozen acceptance',make:async()=>({patch,sha256,trialId:String(++makers)}),
    verify:async(_candidate,lane)=>{
      active++;maxActive=Math.max(maxActive,active);if(active===2)release();
      const timeout=setTimeout(()=>release(),3000);
      await bothStarted;clearTimeout(timeout);active--;
      if(active===0)bothStarted=new Promise<void>(resolve=>{release=resolve;});
      return {lane,passed:makers===2,evidence:'unit-test-fixture'};
    },
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
test('passing parallel lanes cannot override a failed protected grade',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'graph-protected-grade-'));let rollbacks=0;
  const driver:GraphDriver={plan:async()=> 'frozen acceptance',
    make:async()=>({patch:'fixture.diff',sha256:'fixture',trialId:'fixture',protectedGrade:{passed:false,evidence:'trial.json'}}),
    verify:async(_candidate,lane)=>({lane,passed:true,evidence:'lane.json'}),
    rollback:async()=>{rollbacks++;}};
  try {
    const state=await driveGraph(join(dir,'state.json'),{...newGraph('fixture'),maxAttempts:1},driver);
    assert.equal(state.node,'failed');assert.equal(rollbacks,1);
    assert.ok(!state.transitions.some(t=>t.to==='approval'));
  }finally{await rm(dir,{recursive:true,force:true});}
});

test('an interrupted verification retains completed lanes and recovers the other without replay',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'graph-lanes-'));let calls=0,recoveries=0;
  const s=newGraph('fixture');s.node='verify';s.candidate={patch:'fixture.diff',sha256:'fixture',trialId:'fixture'};
  s.pendingOperation='verify-1';s.lanes={services:{id:'service-durable',status:'completed',result:{lane:'services',passed:true,evidence:'service.json'}},electron:{id:'electron-durable',status:'running'}};
  const driver:GraphDriver={plan:async()=>'',make:async()=>s.candidate!,rollback:async()=>{},verify:async()=>{calls++;throw new Error('must not replay');},recoverLane:async(_candidate,lane,state)=>{recoveries++;assert.equal(state.lanes![lane]!.id,'electron-durable');return {lane,passed:true,evidence:'electron.json'};}};
  try{const result=await driveGraph(join(dir,'graph.json'),s,driver);assert.equal(result.node,'approval');assert.equal(calls,0);assert.equal(recoveries,1);assert.equal(result.previous?.trialId,'fixture');}
  finally{await rm(dir,{recursive:true,force:true});}
});

test('infrastructure failures pause on their own route and preserve failed candidate evidence',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'graph-infra-'));const driver:GraphDriver={plan:async()=> 'plan',make:async()=>({patch:'patch.diff',sha256:'checksum',trialId:'maker'}),verify:async(_candidate,lane)=>{if(lane==='electron')throw new Error('gateway unavailable');return {lane,passed:true,evidence:'service.json'};},rollback:async()=>{throw new Error('infrastructure must not discard code');}};
  try{const s=await driveGraph(join(dir,'graph.json'),newGraph('fixture'),driver);assert.equal(s.node,'infrastructure_recovery');assert.equal(s.candidate?.trialId,'maker');assert.equal(s.lanes?.services?.status,'completed');assert.equal(s.lanes?.electron?.status,'blocked');}
  finally{await rm(dir,{recursive:true,force:true});}
});

test('each graph requires a new human decision even for an identical patch',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'graph-decisions-')),patch=join(dir,'candidate.diff');await writeFile(patch,'same patch');const sha256=createHash('sha256').update('same patch').digest('hex');
  try{const decisions=[];for(const name of ['a','b']){const file=join(dir,name+'.json'),s=newGraph('fixture');s.node='approval';s.candidate={patch:'candidate.diff',sha256,trialId:name};await writeFile(file,JSON.stringify(s));const decided=await decideGraph(file,'approve','test-human',sha256);decisions.push(decided.approval!.decisionId);await assert.rejects(decideGraph(file,'approve','test-human',sha256),/not awaiting/);}assert.notEqual(decisions[0],decisions[1]);}
  finally{await rm(dir,{recursive:true,force:true});}
});
