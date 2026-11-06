import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const {poll}=createRequire(import.meta.url)('../graders/poll.cjs') as {poll:(predicate:()=>Promise<boolean>,timeout?:number)=>Promise<void>};

test('grader waits for resolved application state instead of accepting a pending Promise',async()=>{
  let observed=false;
  const timer=setTimeout(()=>{observed=true;},70);
  try {await poll(async()=>observed,500);assert.equal(observed,true);}
  finally {clearTimeout(timer);}
});
test('an application state that never becomes true fails acceptance',async()=>{
  await assert.rejects(poll(async()=>false,60),/Timed out/);
});
