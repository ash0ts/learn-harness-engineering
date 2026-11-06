/** Actual timeout, cancellation, exported progress, fresh-workspace resume and cleanup. */
import assert from 'node:assert/strict';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {randomUUID} from 'node:crypto';
import {config,requirePrivateProject} from '../src/config.js';
import {Budget,estimate} from '../src/budget.js';
import {courseRoot,sourceHead,readTask,stageTask} from '../src/staging.js';
import {withWorkspace,stageWorkspace,runSandboxCommand} from '../src/sandbox.js';
import {writeJson} from '../src/records.js';

if(!process.argv.includes('--execute'))throw new Error('Live sandbox qualification requires --execute');
const c=config();await requirePrivateProject(c);
const sourceCommit=await sourceHead(),id=`sandbox-qualification-${randomUUID()}`;
const root=join(courseRoot,'forge/local-results',id);await mkdir(root,{recursive:true});
const p=JSON.parse(await readFile(join(courseRoot,'forge/protocol.json'),'utf8'));
const budget=new Budget(join(courseRoot,'forge/local-results/budget.json'),c.budgetUsd);
const record:Record<string,unknown>={schemaVersion:1,id,sourceCommit,startedAt:new Date().toISOString(),passed:false,checks:[]};
const checks=record.checks as Array<{name:string;passed:boolean;detail?:unknown}>;
const staged=await stageTask(await readTask('project-01'),'minimal',sourceCommit);
const interruptId=randomUUID(),resumeId=randomUUID();
record.reservationIds={interruptId,resumeId};
await budget.reserve({[interruptId]:0.5});
let total=0,knownCost=true;
try {
  const interrupted=join(root,'interrupted');await mkdir(interrupted,{recursive:true});
  let start=Date.now(),cost:number|null=null;
  try {
    await withWorkspace({config:c,image:p.sandbox.image,trialId:interruptId,evidenceDir:interrupted,signal:AbortSignal.timeout(900000)},async sandbox=>{
      await stageWorkspace(sandbox,staged.archive);
      await sandbox.files.write('/workspace/task/progress.json',JSON.stringify({completed:['import inspection'],next:'indexing checks'}));
      let timeout=false;
      try {await runSandboxCommand(sandbox,'echo $$ > /tmp/qualification-process.pid; exec sleep 60',{timeoutMs:1000,cancellationEvidence:join(interrupted,'cancellation.json')});}
      catch(error){timeout=true;await writeJson(join(interrupted,'timeout.json'),{error:String(error)});}
      assert.ok(timeout,'the long command must exceed the bounded wait');
      checks.push({name:'bounded command wait times out',passed:true});
      const cancellation=JSON.parse(await readFile(join(interrupted,'cancellation.json'),'utf8'));
      assert.equal(cancellation.cleanup.exitCode,0);
      const probe=await sandbox.commands.run(['bash','-lc','pid=$(cat /tmp/qualification-process.pid); state=$(ps -o stat= -p "$pid" || true); case "$state" in ""|Z*) exit 0;; *) exit 1;; esac'],{check:false,timeoutMs:10000});
      await writeJson(join(interrupted,'process-probe.json'),probe);
      assert.equal(probe.exitCode,0,'cancelled process must no longer be running');
      checks.push({name:'cancelled remote process group is no longer running',passed:true});
      await writeFile(join(interrupted,'checkpoint.json'),await sandbox.files.read('/workspace/task/progress.json'));
      throw new Error('qualification: intentional session interruption');
    });
  }catch(error){if(!String(error).includes('qualification: intentional session interruption'))throw error;}
  finally {
    const journal=JSON.parse(await readFile(join(interrupted,'sandbox.json'),'utf8'));
    if(journal.state==='terminated')cost=estimate(0,0,(Date.now()-start)/1000,p.pricing);
    await budget.settle(interruptId,cost);total+=cost??0;knownCost&&=cost!==null;
  }
  const patch=await readFile(join(interrupted,'patch.diff'));
  assert.match(patch.toString(),/progress.json/);checks.push({name:'interrupted session exports patch and checkpoint before termination',passed:true});
  const resumed=join(root,'resumed');await mkdir(resumed,{recursive:true});start=Date.now();cost=null;
  await budget.reserve({[resumeId]:0.5});
  try {
    await withWorkspace({config:c,image:p.sandbox.image,trialId:resumeId,evidenceDir:resumed,signal:AbortSignal.timeout(900000)},async sandbox=>{
      await stageWorkspace(sandbox,staged.archive);await sandbox.files.write('/tmp/resume.diff',patch);
      await sandbox.commands.run(['git','apply','/tmp/resume.diff'],{cwd:'/workspace/task'});
      const checkpoint=JSON.parse(Buffer.from(await sandbox.files.read('/workspace/task/progress.json')).toString());
      assert.equal(checkpoint.next,'indexing checks');assert.deepEqual(checkpoint.completed,['import inspection']);
      await writeJson(join(resumed,'checkpoint.json'),checkpoint);
      checks.push({name:'fresh workspace resumes exact exported progress',passed:true});
    });
    const first=JSON.parse(await readFile(join(interrupted,'sandbox.json'),'utf8'));
    const second=JSON.parse(await readFile(join(resumed,'sandbox.json'),'utf8'));
    assert.notEqual(first.sandboxId,second.sandboxId);assert.equal(second.state,'terminated');
    checks.push({name:'both distinct sandboxes confirm terminal state',passed:true});
    cost=estimate(0,0,(Date.now()-start)/1000,p.pricing);record.passed=true;
  }finally{await budget.settle(resumeId,cost);total+=cost??0;knownCost&&=cost!==null;}
}catch(error){record.error=String(error);}
finally {
  record.finishedAt=new Date().toISOString();record.estimatedCostUsd=knownCost?total:null;
  await writeJson(join(root,'sandbox-qualification.json'),record);console.log(JSON.stringify(record,null,2));
}
