import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,rm,readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {driveLoop,type LoopState} from '../src/loops.js';
import type {TrialRecord} from '../src/records.js';

function state(mode:LoopState['mode']):LoopState{return {schemaVersion:1,id:'test-fixture',mode,sourceCommit:'fixture',startedAt:0,deadlineAt:7200000,intervalMs:900000,maxRounds:8,status:'running',rounds:[],interventions:[]};}
test('accelerated timer schedules eight bounded sessions over the full two-hour window',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'loop-test-'));let now=0;const starts:number[]=[];
  try {
    const s=await driveLoop(join(dir,'checkpoint.json'),state('timer'),{now:()=>now,sleep:async ms=>{now+=ms;},run:async()=>{starts.push(now);now+=1000;return {record:{outcome:'passed'} as TrialRecord,patchSha256:'same'};}});
    assert.equal(s.status,'deadline');assert.equal(s.rounds.length,8);assert.equal(now,7200000);assert.deepEqual(starts,[0,900000,1800000,2700000,3600000,4500000,5400000,6300000]);
  } finally {await rm(dir,{recursive:true,force:true});}
});
test('goal stops on success and ambiguous pending launches are never retried',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'loop-goal-'));const driver={now:()=>0,sleep:async()=>{},run:async()=>({record:{outcome:'passed'} as TrialRecord})};
  try {
    const s=await driveLoop(join(dir,'checkpoint.json'),state('goal'),driver);assert.equal(s.status,'passed');assert.equal(s.rounds.length,1);
    await assert.rejects(driveLoop(join(dir,'checkpoint.json'),{...state('goal'),pendingTrialId:'uncertain'},driver),/Reconcile/);
  }finally{await rm(dir,{recursive:true,force:true});}
});
test('a retry receives durable independent checker feedback without carrying conversation context',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'loop-feedback-'));const file=join(dir,'checkpoint.json');let runs=0;
  try {
    const result=await driveLoop(file,state('goal'),{now:()=>0,sleep:async()=>{},run:async(_id,s)=>{
      if(++runs===1)return {record:{outcome:'task_failed',grade:{checks:[{name:'Electron preload',passed:false}]}} as unknown as TrialRecord,patchSha256:'first'};
      assert.match(s.verificationFeedback!,/Electron preload/);
      assert.equal(JSON.parse(await readFile(file,'utf8')).verificationFeedback,s.verificationFeedback);
      return {record:{outcome:'passed'} as TrialRecord,patchSha256:'repaired'};
    }});
    assert.equal(result.status,'passed');assert.equal(result.rounds.length,2);
  }finally{await rm(dir,{recursive:true,force:true});}
});
