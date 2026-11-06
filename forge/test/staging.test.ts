import {test} from 'node:test';
import assert from 'node:assert/strict';
import {stageTask,readTask,sourceHead} from '../src/staging.js';
import {balancedOrder} from '../src/campaign.js';
import {roleSchedule} from '../src/trial.js';

test('all treatments start with identical code and each role schedule has the same turn budget',async()=>{
  const task=await readTask('project-05'),source=await sourceHead();
  const staged=await Promise.all(task.variants.map(v=>stageTask(task,v,source)));
  assert.equal(new Set(staged.map(s=>s.applicationSha256)).size,1);
  for(const variant of task.variants)assert.equal(roleSchedule(variant,1).reduce((n,r)=>n+r.turns,0),24);
  assert.deepEqual(balancedOrder(['a','b','c'],2),['b','c','a']);
});
