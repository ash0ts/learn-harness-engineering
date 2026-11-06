/** Qualify an unchanged saved patch with extra checker diagnostics; never rewrites a trial grade. */
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {config,requirePrivateProject} from '../src/config.js';
import {Budget,estimate} from '../src/budget.js';
import {courseRoot,sourceHead,readTask,stageTask} from '../src/staging.js';
import {withWorkspace,stageWorkspace} from '../src/sandbox.js';
import {writeJson} from '../src/records.js';

if(!process.argv.includes('--execute') || !process.argv[2])throw new Error('Usage: qualify_checker.ts TRIAL_JSON --execute [--checker PATH]');
const trialFile=resolve(process.argv[2]),trial=JSON.parse(await readFile(trialFile,'utf8'));
if(!['project-05','project-06'].includes(trial.project))throw new Error('Checker diagnostic requires Project 05 or 06');
const candidate=await readFile(join(trialFile,'..','candidate.diff'));
const c=config();await requirePrivateProject(c);
const id=`checker-diagnostic-${randomUUID()}`,root=join(courseRoot,'forge/local-results',id);
await mkdir(root,{recursive:true});
const record:Record<string,unknown>={schemaVersion:1,id,sourceCommit:await sourceHead(),project:trial.project,trialId:trial.id,
  candidateSourceCommit:trial.sourceCommit,candidateSha256:createHash('sha256').update(candidate).digest('hex'),
  startedAt:new Date().toISOString(),passed:false,qualification:true};
const task=await readTask(trial.project),staged=await stageTask(task,trial.variant,trial.sourceCommit);
const budget=new Budget(join(courseRoot,'forge/local-results/budget.json'),c.budgetUsd);
await budget.reserve({[id]:1});let cost:number|null=null;const start=Date.now();
try {
  // Apply the current stronger checker as a separate qualification. Never
  // rewrite the original frozen trial outcome or its original checker bytes.
  const override=process.argv.includes('--checker')?process.argv[process.argv.indexOf('--checker')+1]:undefined;
  record.checkerOverride=override??null;
  let checker=await readFile(override??join(courseRoot,task.protectedChecker),'utf8');
  checker=checker.replace('error:String(error)', 'error:String(error),stack:error?.stack');
  const marker="assert.ok((await page.locator('body').innerText()).includes(history[0].response.citations[0].excerpt));";
  if(!checker.includes(marker))throw new Error('Frozen history diagnostic location changed');
  checker=checker.replace(marker, `
        fs.writeFileSync(path.join(output,'history-diagnostic.json'),JSON.stringify({history,body:await page.locator('body').innerText(),clickedText:await citationControl.innerText()},null,2));
        await page.screenshot({path:path.join(output,'history-diagnostic.png')});
        ${marker}`);
  const support=await readFile(join(courseRoot,'forge/graders/poll.cjs'));
  if(!checker.includes('visible-answer.json'))throw new Error('Visible-answer checker required');
  record.checkerSha256=createHash('sha256').update(checker).update('\0').update(support).digest('hex');
  await writeFile(join(root,'checker.cjs'),checker);
  await writeFile(join(root,'poll.cjs'),support);
  await withWorkspace({config:c,image:trial.protocol.sandbox.image,trialId:id,evidenceDir:join(root,'sandbox'),signal:AbortSignal.timeout(900000)},async sandbox=>{
    record.sandboxId=sandbox.sandboxId;await stageWorkspace(sandbox,staged.archive);
    await sandbox.files.write('/tmp/candidate.diff',candidate);
    await sandbox.commands.run(['git','apply','/tmp/candidate.diff'],{cwd:'/workspace/task'});
    await sandbox.files.write('/tmp/check.cjs',checker);
    await sandbox.files.write('/tmp/poll.cjs',support);
    const result=await sandbox.commands.run(['xvfb-run','-a','node','/tmp/check.cjs',task.gradeAs??task.id],{cwd:'/workspace/task',check:false,timeoutMs:240000});
    await writeJson(join(root,'command.json'),result);
    const grade=JSON.parse(Buffer.from(await sandbox.files.read('/tmp/grade/result.json')).toString());
    record.grade=grade;record.passed=grade.passed;
    for(const file of ['result.json','build.log','visible-answer.png','visible-answer.json','electron.png','history-diagnostic.json','history-diagnostic.png']) {
      try{await writeFile(join(root,file),await sandbox.files.read('/tmp/grade/'+file));}catch{/* Missing evidence remains missing. */}
    }
  });
}catch(error){record.error=String(error);}
finally {
  const journal=JSON.parse(await readFile(join(root,'sandbox/sandbox.json'),'utf8').catch(()=>'{}'));
  if(journal.state==='terminated')cost=estimate(0,0,(Date.now()-start)/1000,trial.protocol.pricing);
  await budget.settle(id,cost);record.estimatedCostUsd=cost;record.finishedAt=new Date().toISOString();
  await writeJson(join(root,'diagnostic.json'),record);console.log(JSON.stringify(record,null,2));
}
