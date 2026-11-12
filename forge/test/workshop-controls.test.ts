import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,rm,readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {makeSnapshot,type WorkshopProject} from '../src/workshop-contract.js';
import {workshopHead,workshopTemplate,workshopCourseRoot} from '../src/workshop-workspace.js';
import {checkWorkshop} from '../src/workshop-local.js';

test('six unfinished labs fail; completed examples pass; isolated regressions fail',{timeout:300000},async()=>{
  const output=await mkdtemp(join(tmpdir(),'workshop-controls-'));
  const source=await workshopHead();
  const regressions=['src/renderer/workshop-import.ts','workshop/sandbox-task.ts','src/services/workshop-metadata.ts','workshop/instrumentation.ts','workshop/evaluation.py','workshop/benchmark.ts'];
  try{
    for(let number=1;number<=6;number++){
      const project=`project-0${number}` as WorkshopProject;
      const {manifest,files}=await workshopTemplate(project,source);
      const baseline=await checkWorkshop(makeSnapshot(manifest,files),manifest,output);
      assert.equal(baseline.outcome,'task_failed',project+' baseline must fail');
      const example=JSON.parse(await readFile(join(workshopCourseRoot,`forge/workshop/examples/${project}/files.json`),'utf8'));
      const completed={...files,...example};
      const reference=await checkWorkshop(makeSnapshot(manifest,completed,{assisted:true}),manifest,output);
      assert.equal(reference.outcome,'passed',project+' reference: '+JSON.stringify(reference.checks.filter(c=>!c.passed)));
      const name=regressions[number-1];
      const regression=await checkWorkshop(makeSnapshot(manifest,{...completed,[name]:files[name]}),manifest,output);
      assert.equal(regression.outcome,'task_failed',project+' targeted regression must fail');
      console.log(project+': baseline rejected, completed example passed, regression rejected');
    }
  }finally{await rm(output,{recursive:true,force:true});}
});
