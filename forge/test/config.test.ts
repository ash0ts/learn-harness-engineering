import {test} from 'node:test';
import assert from 'node:assert/strict';
import {config, publicConfig, requireLive, requirePrivateProject} from '../src/config.js';
import {redact} from '../src/records.js';

test('live configuration never falls back to anonymous or an unrelated project', () => {
  assert.throws(() => requireLive(config({})), /requires/);
  assert.throws(() => config({FORGE_BUDGET_USD: 'NaN'}));
  assert.throws(() => config({FORGE_BUDGET_USD: '51'}));
  assert.equal(JSON.stringify(publicConfig(config({WANDB_API_KEY: 'secret'}))).includes('secret'), false);
});
test('diagnostics redact credentials', () => {
  assert.equal(redact('Bearer token and my-secret', ['my-secret']), '[redacted authorization] and [redacted]');
});
test('paid destination preflight rejects public and inaccessible projects',async()=>{
  const c=config({WANDB_ENTITY:'test',WANDB_PROJECT:'private-course',WANDB_API_KEY:'fixture'});
  const reply=(access:string|null)=>(async(_url,options)=>{
    assert.deepEqual(JSON.parse(String(options?.body)).variables,{e:'test',p:'private-course'});
    return new Response(JSON.stringify({data:{project:access?{access}:null}}),{status:200});
  }) as typeof fetch;
  await requirePrivateProject(c,reply('PRIVATE'));
  await assert.rejects(requirePrivateProject(c,reply('PUBLIC')),/PRIVATE/);
  await assert.rejects(requirePrivateProject(c,reply(null)),/PRIVATE/);
});

test('unlimited budget requires an explicit configuration value',()=>{
  assert.equal(config({FORGE_BUDGET_USD:'unlimited'}).budgetUsd,Infinity);
  assert.equal(publicConfig(config({FORGE_BUDGET_USD:'unlimited'})).budgetUsd,'unlimited');
  assert.throws(()=>config({FORGE_BUDGET_USD:'Infinity'}));
});
