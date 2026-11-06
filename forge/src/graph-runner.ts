import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {compare} from './campaign.js';
import {driveGraph,newGraph,type GraphState} from './graph.js';
import {sourceHead,readTask,stageTask,courseRoot} from './staging.js';
import {protocol} from './trial.js';
import {config} from './config.js';
import {Budget,estimate} from './budget.js';
import {stageWorkspace,withWorkspace} from './sandbox.js';
import {writeJson,type TrialRecord} from './records.js';

export async function runGraph(file:string,execute:boolean,resume=false) {
  const state:GraphState=resume?JSON.parse(await readFile(file,'utf8')):newGraph(await sourceHead());
  if(!execute)return state;
  const c=config(),p=await protocol(),task=await readTask('project-08');
  const output=resolve(join(courseRoot,'forge/local-results'));const budget=new Budget(join(output,'budget.json'),c.budgetUsd);
  // Reserve both independent verification lanes together, before concurrent launch.
  let laneIds:Record<string,string>={};
  return driveGraph(file,state,{
    async plan(){return task.task;},
    async make(s){
      const result=await compare({project:'project-08',variant:'graph',repeats:1,execute:true,source:s.sourceCommit,output,resumePatch:s.previous?.patch});
      const record=(result as {completed?:TrialRecord[]}).completed?.[0];
      if(!record||['infrastructure_failed','telemetry_missing'].includes(record.outcome))throw new Error('Maker unavailable; retain trial evidence');
      const patch=join(output,record.id,'candidate.diff');const sha256=createHash('sha256').update(await readFile(patch)).digest('hex');
      laneIds={services:randomUUID(),electron:randomUUID()};const maximum=estimate(0,0,1200,p.pricing)*1.3;
      await budget.reserve(Object.fromEntries(Object.values(laneIds).map(id=>[id,maximum])));
      return {patch,sha256,trialId:record.id};
    },
    async verify(candidate,lane,s){
      const id=laneIds[lane];if(!id)throw new Error('Resume requires fresh verification reservations');
      const dir=join(output,`graph-${id}`);await mkdir(dir,{recursive:true});const start=Date.now();let cost:number|null=null;
      try{
        const staged=await stageTask(task,'graph',s.sourceCommit);
        let grade:{passed:boolean;error?:string}={passed:false};
        await withWorkspace({config:c,image:p.sandbox.image,trialId:id,evidenceDir:dir},async sandbox=>{
          await stageWorkspace(sandbox,staged.archive);await sandbox.files.write('/tmp/candidate.diff',await readFile(candidate.patch));
          if((await readFile(candidate.patch)).length)await sandbox.commands.run(['git','apply','/tmp/candidate.diff'],{cwd:'/workspace/task'});
          await sandbox.files.write('/tmp/graph-lane.cjs',await readFile(join(courseRoot,'forge/graders/graph-lane.cjs')));
          const command=await sandbox.commands.run(['xvfb-run','-a','node','/tmp/graph-lane.cjs',lane],{check:false,timeoutMs:180000,cwd:'/workspace/task'});await writeJson(join(dir,'command.json'),command);
          grade=JSON.parse(Buffer.from(await sandbox.files.read('/tmp/graph-grade.json')).toString());await writeJson(join(dir,'grade.json'),grade);
          if(lane==='electron')try{await writeFile(join(dir,'electron.png'),await sandbox.files.read('/tmp/graph-electron.png'));}catch{}
        });
        cost=estimate(0,0,(Date.now()-start)/1000,p.pricing);
        return {lane,passed:grade.passed,evidence:join(dir,'grade.json'),error:grade.error};
      }finally{await budget.settle(id,cost);}
    },
    async rollback(s){
      // Candidate remains an immutable artifact. The next fresh workspace starts
      // from the last verified patch (or baseline), so no failed edits survive.
      await writeJson(join(output,`rollback-${s.id}-${s.attempts}.json`),{discarded:s.candidate,restored:s.previous??'frozen baseline',verification:s.verification});
    },
  });
}
