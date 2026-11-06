import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, readFile, rm} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {Budget, estimate} from '../src/budget.js';

test('pricing metadata does not invalidate known inference and sandbox rates',()=>{
  const rates={inputPerMillionUsd:0.25,outputPerMillionUsd:1.25,cpuHourUsd:0.128,memoryGiBHourUsd:0.0212,notebookHourUsd:null,source:'official rate card'};
  assert.ok(estimate(1000,1000,60,rates)>0);
  assert.throws(()=>estimate(1000,1000,60,{...rates,cpuHourUsd:NaN}),/Missing/);
});

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

test('explicit unlimited authorization retains uncertain costs instead of inventing usage',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'unlimited-budget-'));const file=join(dir,'budget.json');
  const limited=new Budget(file,50);await limited.reserve({timeout:2});await limited.settle('timeout',null);
  await limited.authorizeUnlimited('User replied unlimited budget to the reservation question');
  const unlimited=new Budget(file,Infinity);
  await unlimited.chargeUnknownReservation('timeout','Authorized full reservation charge; token usage remains unknown');
  await unlimited.reserve({large:100});
  const ledger=JSON.parse(await readFile(file,'utf8'));
  assert.equal(ledger.limitUsd,null);assert.equal(ledger.spentEstimateUsd,2);assert.equal(ledger.uncertainEstimates.length,1);
  assert.equal(ledger.reservations.large,100);
  await assert.rejects(new Budget(file,50).reserve({wrong:1}),/limit changed/);
});
