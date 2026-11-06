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
  // Apply the current stronger checker as a separate qualification. Never
  // rewrite the original frozen trial outcome or its original checker bytes.
  const checker=await readFile(join(courseRoot,task.protectedChecker),'utf8');
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
