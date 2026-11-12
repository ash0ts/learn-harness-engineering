import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,symlink,rm,readFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {makeSnapshot,validateSnapshot,sha256,workshopPath,safeWorkshopPath,writeWorkshopEdits,storeSnapshot,type WorkshopManifest} from '../src/workshop-contract.js';
const manifest:WorkshopManifest={schemaVersion:1,protocol:'workshop-v1',project:'project-01',sourceCommit:'a'.repeat(40),title:'test',
  editable:['src/app.ts'],files:{'src/app.ts':sha256('TODO'),'package.json':sha256('{}')},scenarios:['import'],task:'task',hints:[],checks:[]};
test('snapshot records edits, detects tampering and protects runner files',()=>{
  const value=makeSnapshot(manifest,{'src/app.ts':'export const answer=42','package.json':'{}'});
  assert.equal(validateSnapshot(value,manifest).files['src/app.ts'],'export const answer=42');
  assert.throws(()=>validateSnapshot({...value,files:{...value.files,'src/app.ts':'changed'}},manifest),/checksum/);
  assert.throws(()=>makeSnapshot(manifest,{'src/app.ts':'x','package.json':'changed'}),/Protected/);
  assert.throws(()=>validateSnapshot(value,{...manifest,sourceCommit:'b'.repeat(40)}),/Incompatible/);
});
test('portable inputs reject traversal, credentials, home paths and links',async()=>{
  for(const path of ['../a','src/../a','/tmp/a','C:\\a','src\\a','.env','node_modules/a'])assert.throws(()=>workshopPath(path));
  assert.throws(()=>makeSnapshot(manifest,{'src/app.ts':'const path="/Users/someone/key"','package.json':'{}'}),/Private/);
  assert.throws(()=>makeSnapshot(manifest,{'src/app.ts':'secret-value','package.json':'{}'},{secrets:['secret-value']}),/Private/);
  const dir=await mkdtemp(join(tmpdir(),'workshop-contract-'));
  try {await symlink(tmpdir(),join(dir,'src'));await assert.rejects(safeWorkshopPath(dir,'src/app.ts'),/symlink/);}
  finally{await rm(dir,{recursive:true,force:true});}
});
test('save validates all edits first and immutable snapshots survive duplicate saves',async()=>{
  const dir=await mkdtemp(join(tmpdir(),'workshop-save-'));
  try {
    await mkdir(join(dir,'src'));await writeFile(join(dir,'src/app.ts'),'TODO');
    await assert.rejects(writeWorkshopEdits(dir,manifest,{'src/app.ts':'new','package.json':'bad'}));
    assert.equal(await readFile(join(dir,'src/app.ts'),'utf8'),'TODO');
    const snapshot=makeSnapshot(manifest,{'src/app.ts':'new','package.json':'{}'});
    const one=await storeSnapshot(dir,snapshot),two=await storeSnapshot(dir,snapshot);assert.equal(one,two);
  }finally{await rm(dir,{recursive:true,force:true});}
});
