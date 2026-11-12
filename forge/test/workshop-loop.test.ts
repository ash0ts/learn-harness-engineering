import {test} from 'node:test';
import assert from 'node:assert/strict';
import {workshopPolicy} from '../src/workshop-policy.js';
import {loopBound,loopObservation,type WorkshopLoopState} from '../src/workshop-loop.js';
test('student policy changes decisions without inheriting credentials or hanging the runner',async()=>{
  assert.equal(await workshopPolicy('export function nextAction(x:any){return x.passed?"stop":"run"}', 'nextAction',{passed:true}),'stop');
  assert.equal(await workshopPolicy('export function nextAction(x:any){return "run"}', 'nextAction',{passed:true}),'run');
  await assert.rejects(workshopPolicy('export function nextAction(){while(true){}}','nextAction',{}),/timed out/);
  await assert.rejects(workshopPolicy('export function nextAction(){return process.env.WANDB_API_KEY}','nextAction',{}),/process is not defined/);
});
test('saved deadline and hard round cap remain authoritative even with a permissive student rule',()=>{
  const state={rounds:[],maxRounds:2,deadline:100,outcome:'task_failed',checks:[{name:'real check',passed:false}]} as unknown as WorkshopLoopState;
  assert.equal(loopBound(state,99),false);assert.equal(loopBound(state,100),true);
  assert.equal(loopObservation(state,99).deadline,100);
  state.rounds=[{} as any,{} as any];assert.equal(loopBound(state,99),true);
  state.rounds=[];state.outcome='passed';assert.equal(loopBound(state,99),true);
});
