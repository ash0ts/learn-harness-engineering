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

test('Forge staging removes historical scores and defect hints without exposing controls',async()=>{
  const {mkdtemp,writeFile,readFile,rm}=await import('node:fs/promises');const {tmpdir}=await import('node:os');const {join}=await import('node:path');const {execFile}=await import('node:child_process');const {promisify}=await import('node:util');const exec=promisify(execFile);
  const source=await sourceHead();
  for(const [project,variant]of [['project-02','workspace-docs'],['project-04','minimal'],['project-04','runtime-feedback']]){
    const dir=await mkdtemp(join(tmpdir(),'frozen-treatment-'));
    try{
      const staged=await stageTask(await readTask(project),variant,source);await writeFile(join(dir,'task.tar'),staged.archive);await exec('tar',['-xf','task.tar'],{cwd:dir});
      assert.ok(!Object.keys(staged.filesSha256).some(p=>p.includes('solution')||p.includes('graders')||p.includes('results')));
      if(project==='project-02'){
        const features=JSON.parse(await readFile(join(dir,'feature_list.json'),'utf8'));
        assert.ok(features.features.every((f:any)=>f.status==='not-verified'&&f.evidence===null&&f.testedAt===null));
        assert.match(await readFile(join(dir,'docs/PRODUCT.md'),'utf8'),/Core Features/);
      }else{
        const service=await readFile(join(dir,'src/services/indexing-service.ts'),'utf8');
        assert.ok(!service.includes('// BUG:'));assert.ok(!service.includes('// This causes files'));
        assert.ok(service.includes("content.length > 1000 ? '' : buffer.trim()"));
      }
    }finally{await rm(dir,{recursive:true,force:true});}
  }
});
