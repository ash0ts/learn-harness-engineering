/** Bind positive-control replays to the exact frozen checker and application bytes. */
import {readFile,readdir} from 'node:fs/promises';
import {join} from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {createHash} from 'node:crypto';
import {courseRoot,stageTask,type Task} from '../src/staging.js';
import {writeJson} from '../src/records.js';

const source=process.argv[2];
if(!/^[a-f0-9]{40}$/.test(source??''))throw new Error('Specify the exact frozen source commit');
const exec=promisify(execFile),local=join(courseRoot,'forge/local-results');
const frozen=async(path:string)=>(await exec('git',['show',`${source}:${path}`],{cwd:courseRoot,maxBuffer:5e6})).stdout;
const checker=await frozen('forge/graders/check.cjs'),support=await frozen('forge/graders/poll.cjs');
const hash=(value:string|Buffer)=>createHash('sha256').update(value).digest('hex');
const marker="assert.ok((await page.locator('body').innerText()).includes(history[0].response.citations[0].excerpt));";
const instrumented=checker.replace('error:String(error)', 'error:String(error),stack:error?.stack').replace(marker, `
        fs.writeFileSync(path.join(output,'history-diagnostic.json'),JSON.stringify({history,body:await page.locator('body').innerText(),clickedText:await citationControl.innerText()},null,2));
        await page.screenshot({path:path.join(output,'history-diagnostic.png')});
        ${marker}`);
const entries=[];
for(const name of await readdir(local))if(name.startsWith('checker-diagnostic-')) {
  try{const r=JSON.parse(await readFile(join(local,name,'diagnostic.json'),'utf8'));if(r.sourceCommit===source)entries.push(r);}catch{}
}
const results=[];
for(const project of ['project-05','project-06']) {
  const candidates=entries.filter(r=>r.project===project&&r.passed&&!r.checkerOverride);
  if(candidates.length!==1)throw new Error(`Expected one successful frozen positive control for ${project}`);
  const r=candidates[0],dir=join(local,r.id);
  if(!r.grade.checks.every((c:{passed:boolean})=>c.passed))throw new Error('Qualification grade is inconsistent');
  if(await readFile(join(dir,'checker.cjs'),'utf8')!==instrumented || r.checkerSha256!==hash(instrumented+'\0'+support))throw new Error('Qualification checker differs beyond diagnostic capture');
  const original=JSON.parse(await readFile(join(local,r.trialId,'trial.json'),'utf8'));
  if(hash(await readFile(join(local,r.trialId,'candidate.diff')))!==r.candidateSha256)throw new Error('Saved patch changed');
  const task=JSON.parse(await frozen(`forge/tasks/${project}.json`)) as Task;
  const staged=await stageTask(task,original.variant,source);
  if(staged.applicationSha256!==original.applicationSha256)throw new Error('Follow-up application bytes differ from the original controlled baseline');
  results.push({project,qualificationId:r.id,trialId:r.trialId,candidateSha256:r.candidateSha256,applicationSha256:staged.applicationSha256,passed:true});
}
const protocol=JSON.parse(await frozen('forge/protocol.json'));
const result={schemaVersion:1,verified:true,verifiedAt:new Date().toISOString(),sourceCommit:source,
  checkerSha256:hash(checker+'\0'+support),protocolSha256:hash(JSON.stringify(protocol)),projects:results,
  note:'Only diagnostic capture and error stacks differ in the replay; all protected assertions and original candidate bytes match.'};
await writeJson(join(local,'checker-qualification-summary.json'),result);console.log(JSON.stringify(result,null,2));
