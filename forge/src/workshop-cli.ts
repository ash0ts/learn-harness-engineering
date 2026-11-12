import {parseArgs} from 'node:util';
import {readFile,mkdir,mkdtemp,rm} from 'node:fs/promises';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {randomUUID} from 'node:crypto';
import {initWorkshop,readManifest,snapshotWorkshop,workshopDiff,workshopTemplate,workshopCourseRoot} from './workshop-workspace.js';
import {writeWorkshopEdits,readWorkshopFiles,validateSnapshot,sha256,type WorkshopProject} from './workshop-contract.js';
import {importWorkshop} from './workshop-workspace.js';
import {checkWorkshop} from './workshop-local.js';
import {config} from './config.js';
import {createOperation,updateOperation,operationFile,evidenceReference} from './operations.js';
import {workshopProtocol} from './workshop-protocol.js';
import {boundedChild} from './lifecycle.js';
import {publishTrial} from './campaign.js';
import {writeJson} from './records.js';
import {Execution} from './execution.js';

import {workshopAttempt} from './workshop-attempt.js';
import {workshopGraph,decideWorkshopGraph} from './workshop-graph.js';
import {workshopLoop} from './workshop-loop.js';

export async function workshopCLI(args:string[]){
  const command=args[0];
  const {values:v}=parseArgs({args:args.slice(1),options:{project:{type:'string'},workspace:{type:'string'},source:{type:'string'},output:{type:'string'},input:{type:'string'},artifact:{type:'string'},candidate:{type:'boolean'},edits:{type:'string'},parent:{type:'string'},snapshot:{type:'string'},'operation-id':{type:'string'},scenario:{type:'string'},fixture:{type:'string'},question:{type:'string'},execute:{type:'boolean'},live:{type:'boolean'},apply:{type:'boolean'},assisted:{type:'boolean'},'single-role':{type:'boolean'},'no-publish':{type:'boolean'},controller:{type:'string'},decision:{type:'string'},sha256:{type:'string'},actor:{type:'string'},reason:{type:'string'},parallel:{type:'boolean'}}});
  if(!v.workspace)throw new Error('workshop requires --workspace DIRECTORY');
  const workspace=resolve(v.workspace),output=resolve(v.output??join(workspace,'.workshop-evidence'));
  if(command==='init'){if(!v.project)throw new Error('Choose --project project-01 through project-08');return initWorkshop(v.project as WorkshopProject,workspace,v.source);}
  const manifest=await readManifest(workspace);
  if(command==='inspect')return {manifest,files:await readWorkshopFiles(workspace,manifest)};
  if(command==='import'){
    if(v.artifact){
      if(v.input)throw new Error('Choose --artifact or --input');
      const temp=await mkdtemp(join(tmpdir(),'workshop-retrieve-'));
      try{
        const file=join(temp,'snapshot.json');
        await promisify(execFile)('uv',['run','--script',join(workshopCourseRoot,'forge/scripts/workshop_artifact.py'),v.artifact,v.candidate?'candidate.json':'submission.json',file],{cwd:workshopCourseRoot,timeout:120000,maxBuffer:1_000_000});
        // The same allowlist, source revision and checksum validation applies
        // to local uploads and authenticated artifact retrieval.
        return await importWorkshop(workspace,file,v.apply);
      }finally{await rm(temp,{recursive:true,force:true});}
    }
    if(!v.input)throw new Error('import requires --input snapshot.json or --artifact trial-ID:vN');
    return importWorkshop(workspace,resolve(v.input),v.apply);
  }
  if(command==='save'){
    if(!v.edits)throw new Error('save requires --edits FILE containing edited file contents');
    const edits=JSON.parse(await readFile(resolve(v.edits),'utf8'));await writeWorkshopEdits(workspace,manifest,edits);
  }
  const snapshot=v.snapshot?validateSnapshot(JSON.parse(await readFile(resolve(v.snapshot),'utf8')),manifest):await snapshotWorkshop(workspace,output,{parent:v.parent,assisted:v.assisted});
  if(['save','export'].includes(command)){
    if(command==='export'&&!v.input)throw new Error('export requires --input DESTINATION.json');
    if(command==='export')await writeJson(resolve(v.input!),snapshot);
    return {snapshot,diff:await workshopDiff(workspace,snapshot)};
  }
  if(command==='graph')return workshopGraph(workspace,output,manifest,snapshot,v);
  if(command==='decide')return decideWorkshopGraph(output,v.controller??'',v.decision??'',v.sha256??'',v.actor??'',v.reason??'');
  if(command==='loop')return workshopLoop(workspace,output,manifest,snapshot,v);
  if(command==='check')return checkWorkshop(snapshot,manifest,output);
  if(!['scenario','agent','resume'].includes(command))throw new Error('workshop: init | inspect | save | check | scenario | agent | resume | export | import');
  return workshopAttempt(workspace,output,manifest,snapshot,command,v);
}
