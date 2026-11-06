import {test} from 'node:test';
import assert from 'node:assert/strict';
import {AppTracingLifecycle} from '../src/app-tracing.js';

test('concurrent app sessions share initialization and flush after the final close',async()=>{
  let starts=0,stops=0;
  const lifecycle=new AppTracingLifecycle(async()=>{starts++;},async()=>{stops++;});
  const [first,second]=await Promise.all([lifecycle.retain('project'),lifecycle.retain('project')]);
  assert.equal(starts,1);
  await assert.rejects(lifecycle.retain('other-project'),/same project/);
  await first();await first();assert.equal(stops,0);
  await second();assert.equal(stops,1);
  const next=await lifecycle.retain('other-project');await next();assert.equal(starts,2);assert.equal(stops,2);
});

test('failed initialization does not poison later app sessions',async()=>{
  let attempts=0;
  const lifecycle=new AppTracingLifecycle(async()=>{if(++attempts===1)throw new Error('tracing unavailable');},async()=>{});
  await assert.rejects(lifecycle.retain('project'),/unavailable/);
  await (await lifecycle.retain('project'))();assert.equal(attempts,2);
});
