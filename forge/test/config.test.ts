import {test} from 'node:test';
import assert from 'node:assert/strict';
import {config, publicConfig, requireLive} from '../src/config.js';
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

test('unlimited budget requires an explicit configuration value',()=>{
  assert.equal(config({FORGE_BUDGET_USD:'unlimited'}).budgetUsd,Infinity);
  assert.equal(publicConfig(config({FORGE_BUDGET_USD:'unlimited'})).budgetUsd,'unlimited');
  assert.throws(()=>config({FORGE_BUDGET_USD:'Infinity'}));
});
