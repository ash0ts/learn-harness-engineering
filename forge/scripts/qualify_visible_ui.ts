/** Supplemental acceptance: verify a saved Pi patch renders its actual answers.
 * This does not alter the frozen campaign grade or count as another coding trial.
 */
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {config,requirePrivateProject} from '../src/config.js';
import {Budget,estimate} from '../src/budget.js';
import {courseRoot,sourceHead,readTask,stageTask} from '../src/staging.js';
import {withWorkspace,stageWorkspace} from '../src/sandbox.js';
import {writeJson} from '../src/records.js';

if(!process.argv.includes('--execute') || !process.argv[2])throw new Error('Usage: qualify_visible_ui.ts TRIAL_JSON --execute');
const trialFile=resolve(process.argv[2]),trial=JSON.parse(await readFile(trialFile,'utf8'));
const candidate=await readFile(join(trialFile,'..','candidate.diff'));
const c=config();await requirePrivateProject(c);
const id=`visible-ui-${randomUUID()}`,root=join(courseRoot,'forge/local-results',id);
await mkdir(root,{recursive:true});
const record:Record<string,unknown>={schemaVersion:1,id,sourceCommit:await sourceHead(),trialId:trial.id,
  candidateSourceCommit:trial.sourceCommit,candidateSha256:createHash('sha256').update(candidate).digest('hex'),
  startedAt:new Date().toISOString(),passed:false,qualification:true};
const task=await readTask(trial.project),staged=await stageTask(task,trial.variant,trial.sourceCommit);
const budget=new Budget(join(courseRoot,'forge/local-results/budget.json'),c.budgetUsd);
await budget.reserve({[id]:1});let cost:number|null=null;const start=Date.now();
try {
  // Reuse the protected assertions and strengthen the UI observation for this
  // separate qualification. Never modify or rescore the original trial record.
  const base=await readFile(join(courseRoot,task.protectedChecker),'utf8');
  const marker="await page.waitForFunction(async question=>(await window.knowledgeBase.qa.history()).some(h=>h.question===question),q,{timeout:10000});";
  if(!base.includes(marker))throw new Error('Unknown checker revision');
  const checker=base.replace(marker,marker+`
        const answer=await page.evaluate(async question=>(await window.knowledgeBase.qa.history()).find(h=>h.question===question).response.answer,q);
        await page.getByText(answer,{exact:true}).first().waitFor({timeout:10000});
        await page.screenshot({path:path.join(output,'visible-answer.png')});
        fs.writeFileSync(path.join(output,'visible-answer.json'),JSON.stringify({question:q,answer,body:await page.locator('body').innerText()}));`);
  record.checkerSha256=createHash('sha256').update(checker).digest('hex');
  await writeFile(join(root,'checker.cjs'),checker);
  await withWorkspace({config:c,image:trial.protocol.sandbox.image,trialId:id,evidenceDir:join(root,'sandbox'),signal:AbortSignal.timeout(900000)},async sandbox=>{
    record.sandboxId=sandbox.sandboxId;await stageWorkspace(sandbox,staged.archive);
    await sandbox.files.write('/tmp/candidate.diff',candidate);
    await sandbox.commands.run(['git','apply','/tmp/candidate.diff'],{cwd:'/workspace/task'});
    await sandbox.files.write('/tmp/check.cjs',checker);
    const result=await sandbox.commands.run(['xvfb-run','-a','node','/tmp/check.cjs',task.gradeAs??task.id],{cwd:'/workspace/task',check:false,timeoutMs:240000});
    await writeJson(join(root,'command.json'),result);
    const grade=JSON.parse(Buffer.from(await sandbox.files.read('/tmp/grade/result.json')).toString());
    record.grade=grade;record.passed=grade.passed;
    for(const file of ['result.json','build.log','visible-answer.png','visible-answer.json','electron.png']) {
      try{await writeFile(join(root,file),await sandbox.files.read('/tmp/grade/'+file));}catch{/* Missing evidence remains missing. */}
    }
  });
}catch(error){record.error=String(error);}
finally {
  const journal=JSON.parse(await readFile(join(root,'sandbox/sandbox.json'),'utf8').catch(()=>'{}'));
  if(journal.state==='terminated')cost=estimate(0,0,(Date.now()-start)/1000,trial.protocol.pricing);
  await budget.settle(id,cost);record.estimatedCostUsd=cost;record.finishedAt=new Date().toISOString();
  await writeJson(join(root,'visible-ui.json'),record);console.log(JSON.stringify(record,null,2));
}
