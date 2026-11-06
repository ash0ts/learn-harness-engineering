import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {acquireSlot} from '../src/slots.js';

test('independent controllers share two sandbox slots and cannot steal an orphan',async()=>{
  const directory=await mkdtemp(join(tmpdir(),'course-slots-'));
  const [first,second]=await Promise.all([acquireSlot('campaign',directory),acquireSlot('graph',directory)]);
  assert.notEqual(first.path,second.path);
  await assert.rejects(acquireSlot('notebook',directory,undefined,0),/occupied/);
  assert.equal(JSON.parse(await readFile(join(first.path,'owner.json'),'utf8')).owner,'campaign');
  await first.release();
  const next=await acquireSlot('notebook',directory);
  assert.equal(next.path,first.path);
  await Promise.all([second.release(),next.release()]);
});
