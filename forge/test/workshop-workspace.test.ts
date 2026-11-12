import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,rm,readFile,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {initWorkshop,snapshotWorkshop,workshopHead,importWorkshop} from '../src/workshop-workspace.js';
import {writeWorkshopEdits,type WorkshopProject} from '../src/workshop-contract.js';
test('five independent checkpoints freeze actual edits and round-trip without changing protected code',async()=>{
  const root=await mkdtemp(join(tmpdir(),'five-workshops-'));
  try{
    const source=await workshopHead(),fileSets=[];
    for(let n=1;n<=5;n++){
      const project=`project-0${n}` as WorkshopProject,workspace=join(root,project),evidence=join(root,'evidence');
      const manifest=await initWorkshop(project,workspace,source);fileSets.push(manifest.editable.join(','));
      const first=await snapshotWorkshop(workspace,evidence);
      assert.ok(!Object.keys(first.files).some(p=>p.includes('examples/')));
      const file=manifest.editable[0],old=await readFile(join(workspace,file),'utf8');
      const next=old+'\n';await writeWorkshopEdits(workspace,manifest,{[file]:next});
      const second=await snapshotWorkshop(workspace,evidence,{parent:first.id});
      assert.notEqual(first.sha256,second.sha256);assert.equal(second.parent,first.id);
      const bundle=join(root,'bundle.json');await writeFile(bundle,JSON.stringify(first));
      assert.deepEqual((await importWorkshop(workspace,bundle)).changes,[file]);
      assert.equal(await readFile(join(workspace,file),'utf8'),next);
      await importWorkshop(workspace,bundle,true);assert.equal(await readFile(join(workspace,file),'utf8'),old);
      await writeFile(join(workspace,'scripts/dev.cjs'),'changed');
      await assert.rejects(snapshotWorkshop(workspace,evidence),/Protected/);
    }
    assert.equal(new Set(fileSets).size,5);
  }finally{await rm(root,{recursive:true,force:true});}
});
