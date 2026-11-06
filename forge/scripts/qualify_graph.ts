/** Deterministic control-flow qualification; never counted as a coding-agent trial. */
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {createHash,randomUUID} from 'node:crypto';
import {config,requirePrivateProject} from '../src/config.js';
import {Budget,estimate} from '../src/budget.js';
import {courseRoot,sourceHead,readTask,stageTask} from '../src/staging.js';
import {withWorkspace,stageWorkspace} from '../src/sandbox.js';
import {driveGraph,newGraph} from '../src/graph.js';
import {writeJson} from '../src/records.js';

if(!process.argv.includes('--execute'))throw new Error('Qualification requires --execute');
const c=config();await requirePrivateProject(c);
const source=await sourceHead(),task=await readTask('project-08');
const p=JSON.parse(await readFile(join(courseRoot,'forge/protocol.json'),'utf8'));
const state=newGraph(source);state.maxAttempts=2;
const output=join(courseRoot,'forge/local-results'),file=join(output,`project-08-control-flow-qualification-${state.id}.json`);
Object.assign(state,{qualification:'deterministic control-flow fixture; excluded from coding trial counts'});
const budget=new Budget(join(output,'budget.json'),c.budgetUsd);
const root=join(output,`graph-qualification-${state.id}`);await mkdir(root,{recursive:true});
let ids:Record<string,string>={};
const result=await driveGraph(file,state,{
  async plan(){return 'Verify the seeded baseline fails, rollback, verify a documented manual repair, then pause for a human decision.';},
  async make(s){
    const data=s.attempts===1?Buffer.from(''):await readFile(join(courseRoot,'forge/fixtures/qualification/graph-repair.diff'));
    const patch=join(root,`candidate-${s.attempts}.diff`);await writeFile(patch,data);
    const protectedId=randomUUID(),protectedDir=join(root,`attempt-${s.attempts}-protected`);
    await mkdir(protectedDir,{recursive:true});await budget.reserve({[protectedId]:1});
    const started=Date.now();let protectedCost:number|null=null,protectedPassed=false;
    const evidence=join(protectedDir,'grade.json');
    try {
      const staged=await stageTask(task,'graph',source);
      await withWorkspace({config:c,image:p.sandbox.image,trialId:protectedId,evidenceDir:protectedDir,signal:AbortSignal.timeout(900000)},async sandbox=>{
        await stageWorkspace(sandbox,staged.archive);
        if(data.length){await sandbox.files.write('/tmp/qualification.diff',data);await sandbox.commands.run(['git','apply','/tmp/qualification.diff'],{cwd:'/workspace/task'});}
        await sandbox.files.write('/tmp/check.cjs',await readFile(join(courseRoot,task.protectedChecker)));
        await sandbox.files.write('/tmp/poll.cjs',await readFile(join(courseRoot,'forge/graders/poll.cjs')));
        await writeJson(join(protectedDir,'command.json'),await sandbox.commands.run(['xvfb-run','-a','node','/tmp/check.cjs',task.gradeAs??task.id],{cwd:'/workspace/task',check:false,timeoutMs:240000}));
        const grade=JSON.parse(Buffer.from(await sandbox.files.read('/tmp/grade/result.json')).toString());
        await writeJson(evidence,grade);protectedPassed=grade.passed;
        for(const name of ['build.log','visible-answer.png','visible-answer.json','electron.png'])try{await writeFile(join(protectedDir,name),await sandbox.files.read('/tmp/grade/'+name));}catch{}
      });
      protectedCost=estimate(0,0,(Date.now()-started)/1000,p.pricing);
    }finally{await budget.settle(protectedId,protectedCost);}
    ids={services:randomUUID(),electron:randomUUID()};await budget.reserve(Object.fromEntries(Object.values(ids).map(id=>[id,0.5])));
    return {patch,sha256:createHash('sha256').update(data).digest('hex'),trialId:`fixture-${s.attempts}`,protectedGrade:{passed:protectedPassed,evidence}};
  },
  async verify(candidate,lane,s){
    const id=ids[lane],dir=join(root,`attempt-${s.attempts}-${lane}`);await mkdir(dir,{recursive:true});
    const start=Date.now();let cost:number|null=null;
    try {
      const staged=await stageTask(task,'graph',source);let passed=false;
      await withWorkspace({config:c,image:p.sandbox.image,trialId:id,evidenceDir:dir,signal:AbortSignal.timeout(900000)},async sandbox=>{
        await stageWorkspace(sandbox,staged.archive);const patch=await readFile(candidate.patch);
        if(patch.length){await sandbox.files.write('/tmp/qualification.diff',patch);await sandbox.commands.run(['git','apply','/tmp/qualification.diff'],{cwd:'/workspace/task'});}
        await sandbox.files.write('/tmp/graph-lane.cjs',await readFile(join(courseRoot,'forge/graders/graph-lane.cjs')));
        await sandbox.files.write('/tmp/poll.cjs',await readFile(join(courseRoot,'forge/graders/poll.cjs')));
        await writeJson(join(dir,'command.json'),await sandbox.commands.run(['xvfb-run','-a','node','/tmp/graph-lane.cjs',lane],{cwd:'/workspace/task',check:false,timeoutMs:180000}));
        const grade=JSON.parse(Buffer.from(await sandbox.files.read('/tmp/graph-grade.json')).toString());await writeJson(join(dir,'grade.json'),grade);passed=grade.passed;
        if(lane==='electron')try{await writeFile(join(dir,'electron.png'),await sandbox.files.read('/tmp/graph-electron.png'));}catch{}
      });
      cost=estimate(0,0,(Date.now()-start)/1000,p.pricing);
      return {lane,passed,evidence:join(dir,'grade.json')};
    }finally{await budget.settle(id,cost);}
  },
  async rollback(s){await writeJson(join(root,`rollback-${s.attempts}.json`),{discarded:s.candidate,restored:'frozen baseline',verification:s.verification});},
});
console.log(JSON.stringify(result,null,2));
