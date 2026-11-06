import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {mkdtemp, rm, readFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {resolve, join} from 'node:path';

const apps = ['shared', ...Array.from({length: 6}, (_, i) => `project-0${i+1}/starter`),
  ...[1,2,3,4,6].map(i => `project-0${i}/solution`),
  ...['single-role','gen-eval','plan-gen-eval'].map(v => `project-05/solution/${v}`)];
const root = resolve(import.meta.dirname, '../../projects');
for (const app of apps) test(`${app}: optional provider persists real answers and rejects failed answers`, async () => {
  const req = createRequire(join(root,app,'package.json'));
  const {PersistenceService} = req('./src/services/persistence-service.ts');
  const {IndexingService} = req('./src/services/indexing-service.ts');
  const {QaService} = req('./src/services/qa-service.ts');
  const {setForgeHooks} = req('./src/services/forge-hooks.ts');
  const data = await mkdtemp(join(tmpdir(),'app-hooks-test-'));
  const persistence = new PersistenceService(data);
  const qa = new QaService(persistence, new IndexingService(persistence));
  let fail = false; let calls = 0;
  setForgeHooks({answer: async () => {calls++; if (fail) throw new Error('inference unavailable'); return 'fixture provider answer';},
    turn: (_: string, work: () => unknown) => work(), tool: (_: string, __: unknown, work: () => unknown) => work(), shutdown: async () => {}});
  try {
    assert.equal((await qa.ask('architecture')).answer, 'fixture provider answer');
    assert.equal(qa.getHistory().length,1);
    fail = true;
    await assert.rejects(qa.ask('architecture'), /inference unavailable/);
    assert.equal(qa.getHistory().length,1);
    assert.equal(calls,2);
    const template = (await readFile(resolve(import.meta.dirname,'../app-hooks.ts.template'),'utf8')).replace("from './shared/types'", "from '../shared/types'");
    assert.equal(await readFile(join(root,app,'src/services/forge-hooks.ts'),'utf8'),template);
  } finally {setForgeHooks(undefined); await rm(data,{recursive:true,force:true});}
});
