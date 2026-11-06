import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, readFile, rm} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {Budget} from '../src/budget.js';

test('complete blocks reserve in-flight costs and unknown usage halts subsequent launches', async () => {
  const dir = await mkdtemp(join(tmpdir(),'forge-budget-')); const file=join(dir,'budget.json');
  try {
    const b = new Budget(file, 2);
    await b.reserve({a:1,b:1});
    await assert.rejects(b.reserve({c:1}),/budget_exhausted/);
    await b.settle('a',0.1);
    await b.reserve({c:0.5});
    await b.settle('b',null);
    await assert.rejects(b.reserve({d:0.1}),/halted/);
    const l=JSON.parse(await readFile(file,'utf8'));
    assert.equal(l.reservations.b,1); assert.equal(l.spentEstimateUsd,0.1);
  } finally {await rm(dir,{recursive:true,force:true});}
});
