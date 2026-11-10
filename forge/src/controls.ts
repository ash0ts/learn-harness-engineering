import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {mkdtemp,mkdir,readFile,writeFile,rm,readdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,dirname} from 'node:path';
import {createHash,randomUUID} from 'node:crypto';
import {courseRoot,frozenFile,readTask,stageTask} from './staging.js';
import {protocol} from './trial.js';
import {withWorkspace,stageWorkspace} from './sandbox.js';
import {Execution} from './execution.js';
import {writeJson} from './records.js';
import {updateOperation,evidenceReference} from './operations.js';
import {requirePrivateProject,config} from './config.js';
const exec=promisify(execFile);

export async function controlFingerprint(project:string,source:string){
  const task=await readTask(project,source),hash=createHash('sha256');
  const staged=await stageTask(task,task.variants[0],source);hash.update(staged.applicationSha256).update(staged.fixtureSha256);
  for(const file of [`forge/tasks/${project}.json`,task.protectedChecker,'forge/graders/poll.cjs','forge/graders/benchmark-probe.cjs','forge/graders/controls/App.tsx','forge/graders/controls/benchmark.cjs','forge/src/staging.ts','forge/src/controls.ts'])hash.update(file).update(await frozenFile(source,file));
  hash.update(JSON.stringify(await protocol()));return hash.digest('hex');
}
export async function requireControls(output:string,projects:string[],source:string){
  const candidates=await readdir(output).catch(()=>[]),proofs:any[]=[];
  for(const name of candidates.filter(n=>n.startsWith('control-')))try{proofs.push(JSON.parse(await readFile(join(output,name,'control.json'),'utf8')));}catch{}
  for(const project of projects){const fingerprint=await controlFingerprint(project,source);
    for(const kind of ['baseline','reference','regression'])if(!proofs.some(p=>p.project===project&&p.kind===kind&&p.qualified&&p.inputsSha256===fingerprint))throw new Error(`Missing qualified ${kind} control for ${project}; paid agent trials are blocked`);
  }
}

export async function controlPatch(project:string,source:string){
  const task=await readTask(project,source),staged=await stageTask(task,task.variants[0],source);
  const directory=await mkdtemp(join(tmpdir(),'protected-control-'));
  try{
    await writeFile(join(directory,'base.tar'),staged.archive);await exec('tar',['-xf','base.tar'],{cwd:directory});await rm(join(directory,'base.tar'));
    await exec('git',['init','-q'],{cwd:directory});await exec('git',['add','.'],{cwd:directory});await exec('git',['-c','user.email=control@example.invalid','-c','user.name=Control','commit','-qm','baseline'],{cwd:directory});
    const baseProject=['project-07','project-08'].includes(project)?'project-04':project;
    const solution=`projects/${baseProject}/solution${project==='project-05'?'/plan-gen-eval':''}`;
    const files=(await exec('git',['ls-tree','-r','--name-only',source,'--',`${solution}/src`],{cwd:courseRoot})).stdout.trim().split('\n');
    for(const file of files){const target=join(directory,file.slice(solution.length+1));await mkdir(dirname(target),{recursive:true});await writeFile(target,await frozenFile(source,file));}
    await writeFile(join(directory,'src/renderer/App.tsx'),await frozenFile(source,'forge/graders/controls/App.tsx'));
    const handlers=join(directory,'src/main/ipc-handlers.ts');let ipc=await readFile(handlers,'utf8');
    ipc="import {dialog,app} from 'electron';\nimport * as fsControl from 'node:fs';\nimport * as pathControl from 'node:path';\n"+ipc;
    ipc=ipc.replace(/(export function registerIpcHandlers\([^)]*\)[^{]*\{)/,'$1\n'+`
  const root=pathControl.join(app.getPath('userData'),'knowledge-base-data');
  ipcMain.handle('control:pick-import',async()=>{const result=await dialog.showOpenDialog({properties:['openFile']});return result.canceled?null:services.documentService.importDocument(result.filePaths[0]);});
  ipcMain.handle('control:content',async(_event,id:string)=>services.documentService.getDocumentContent(id));
  ipcMain.handle('control:clear',async()=>{fsControl.writeFileSync(pathControl.join(root,'qa-history.json'),'[]');});
  ipcMain.handle('control:reset',async()=>{fsControl.rmSync(root,{recursive:true,force:true});fsControl.mkdirSync(root,{recursive:true});});
`);
    if(project==='project-06'){
      ipc=ipc.replace(/ipcMain.handle\(IPC_CHANNELS.SUBMIT_FEEDBACK,[\s\S]*?\n  \}\);/,`ipcMain.handle(IPC_CHANNELS.SUBMIT_FEEDBACK,async(_event,value:{question:string;answer:string;rating:string;comment?:string})=>{const file=pathControl.join(root,'feedback.json');const entries=fsControl.existsSync(file)?JSON.parse(fsControl.readFileSync(file,'utf8')):[];entries.push(value);fsControl.writeFileSync(file,JSON.stringify(entries));return value;});`);
    }
    await writeFile(handlers,ipc);
    const preload=join(directory,'src/preload/preload.ts');let bridge=await readFile(preload,'utf8');
    bridge=bridge.replace('documents: {',"documents: {\n    pickImport:()=>ipcRenderer.invoke('control:pick-import'),");
    if(!bridge.includes('getContent:'))bridge=bridge.replace('documents: {',"documents: {\n    getContent:(id:string)=>ipcRenderer.invoke('control:content',id),");
    bridge=bridge.replace('qa: {',"qa: {\n    clear:()=>ipcRenderer.invoke('control:clear'),");
    if(bridge.includes('app: {'))bridge=bridge.replace('app: {',"app: {\n    reset:()=>ipcRenderer.invoke('control:reset'),");else bridge=bridge.replace('const api = {',"const api = {\n  app:{reset:()=>ipcRenderer.invoke('control:reset')},");
    if(project==='project-06')bridge=bridge.replace(/submit:[\s\S]*?ipcRenderer\.invoke\(IPC_CHANNELS.SUBMIT_FEEDBACK[^;]*?\),/,"submit:(...args:unknown[])=>ipcRenderer.invoke(IPC_CHANNELS.SUBMIT_FEEDBACK,...args),");
    await writeFile(preload,bridge);
    if(['project-04','project-07','project-08'].includes(project)){
      await mkdir(join(directory,'scripts'),{recursive:true});await writeFile(join(directory,'scripts/check-architecture.sh'),"#!/usr/bin/env bash\nset -eu\nif grep -REn \"(from|require[[:space:]]*\\()?[[:space:]]*['\\\"](node:|fs['\\\"]|path['\\\"]|electron['\\\"])\" src/renderer; then exit 1; fi\n");
    }
    if(project==='project-06'){
      await mkdir(join(directory,'scripts'),{recursive:true});await writeFile(join(directory,'scripts/benchmark.sh'),'#!/usr/bin/env bash\nset -eu\nnode scripts/benchmark.cjs\n');
      await writeFile(join(directory,'scripts/benchmark.cjs'),(await frozenFile(source,'forge/graders/controls/benchmark.cjs')).replaceAll('../../dist/','../dist/'));
    }
    await exec('git',['add','-N','.'],{cwd:directory});return (await exec('git',['diff','--binary','HEAD'],{cwd:directory,maxBuffer:10e6})).stdout;
  }finally{await rm(directory,{recursive:true,force:true});}
}

export async function qualifyControl(project:string,source:string,output:string,kind:'baseline'|'reference'|'regression',operationId?:string){
  await requirePrivateProject(config());
  const p=await protocol(),task=await readTask(project,source),staged=await stageTask(task,task.variants[0],source);
  const id=operationId??`control-${project}-${kind}-${randomUUID()}`,dir=join(output,id);await mkdir(dir,{recursive:true});
  const execution=new Execution(output,id,p);await execution.begin('trial',source);if(!execution.incremental)await execution.budget.reserve({[id]:1});
  let grade:any=null,error:string|undefined;
  const candidate=kind==='baseline'?'':await controlPatch(project,source);await writeFile(join(dir,'candidate.diff'),candidate);
  try{
    await withWorkspace({config:execution.c,image:p.sandbox.image,trialId:id,evidenceDir:join(dir,'grader'),...execution.workspace('control',join(dir,'grader'))},async sandbox=>{
      await stageWorkspace(sandbox,staged.archive);
      if(candidate){await sandbox.files.write('/tmp/reference.diff',candidate);await sandbox.commands.run(['git','apply','/tmp/reference.diff'],{cwd:'/workspace/task'});}
      if(kind==='regression'){
        const target=project==='project-01'||project==='project-02'?'src/renderer/App.tsx':project==='project-06'?'src/preload/preload.ts':project==='project-05'?'src/renderer/App.tsx':'src/services/indexing-service.ts';
        let content=Buffer.from(await sandbox.files.read('/workspace/task/'+target)).toString('utf8');
        if(['project-01','project-02'].includes(project))content=content.replace('await api.documents.pickImport();','/* regression: import button disconnected */');
        else if(project==='project-06')content=content.replace("reset:()=>ipcRenderer.invoke('control:reset')","reset:async()=>undefined");
        else if(project==='project-05')content=content.replace('{item.response.answer}','{item.response.answer.slice(0,25)}');
        else content=content.replaceAll('buffer.trim()',"(content.length>1000?'':buffer.trim())");
        await sandbox.files.write('/workspace/task/'+target,content);
      }
      for(const file of ['check.cjs','poll.cjs','benchmark-probe.cjs'])await sandbox.files.write('/tmp/'+file,await frozenFile(source,'forge/graders/'+file));
      const command=await sandbox.commands.run(['xvfb-run','-a','node','/tmp/check.cjs',task.gradeAs??task.id],{cwd:'/workspace/task',timeoutMs:300000,check:false});await writeJson(join(dir,'command.json'),command);
      grade=JSON.parse(Buffer.from(await sandbox.files.read('/tmp/grade/result.json')).toString('utf8'));
      for(const name of ['result.json','build.log','ui-events.json','ui-failure.png','electron.png','logs.json','benchmark.json'])try{await writeFile(join(dir,name),await sandbox.files.read('/tmp/grade/'+name));}catch{}
    });
  }catch(e){error=String(e);}
  const accounting=await execution.finish(grade?.passed?'passed':'task_failed');if(!execution.incremental)await execution.budget.settle(id,accounting.estimatedCostUsd);
  const intended=kind==='regression'&&project==='project-03'?'actual indexing':project==='project-03'?'extracted metadata':['project-04','project-07','project-08'].includes(project)?'actual indexing':'Electron window';
  const target=grade?.checks.find((check:any)=>check.name.startsWith(intended));
  const result={schemaVersion:1,id,project,kind,sourceCommit:source,inputsSha256:await controlFingerprint(project,source),protocolSha256:createHash('sha256').update(JSON.stringify(p)).digest('hex'),candidateSha256:createHash('sha256').update(candidate).digest('hex'),applicationSha256:staged.applicationSha256,grade,error,...accounting,qualified:grade!=null&&grade.checks[0]?.passed&&(kind==='reference'?grade.passed:target?.passed===false)};
  await writeJson(join(dir,'control.json'),result);const ref=await evidenceReference(output,join(dir,'control.json'));await updateOperation(output,id,op=>{op.evidence.control=ref;op.publication='not_required';op.phase=accounting.cleanupVerified&&accounting.usageComplete?'completed':'blocked_unknown';});return result;
}
