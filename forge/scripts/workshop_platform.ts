/** Offline release qualification; examples are explicitly assisted controls. */
import {mkdir,readFile,writeFile,symlink} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {initWorkshop,workshopCourseRoot,snapshotWorkshop} from '../src/workshop-workspace.js';
import {writeWorkshopEdits} from '../src/workshop-contract.js';
const exec=promisify(execFile),root=join(workshopCourseRoot,'forge/local-results','platform-'+process.platform);
for(const project of ['project-01','project-05'] as const){
  const workspace=join(root,project,'workspace'),out=join(root,project,'evidence');
  await mkdir(out,{recursive:true});
  const manifest=await initWorkshop(project,workspace,process.env.WORKSHOP_SOURCE);
  await writeWorkshopEdits(workspace,manifest,JSON.parse(await readFile(join(workshopCourseRoot,'forge/workshop/examples',project,'files.json'),'utf8')));
  await symlink(join(workshopCourseRoot,'forge/workshop/base/node_modules'),join(workspace,'node_modules'),process.platform==='win32'?'junction':'dir');
  const snapshot=await snapshotWorkshop(workspace,out,{assisted:true});
  const scenario=join(out,'scenario.json');
  await writeFile(scenario,JSON.stringify({project,snapshotId:snapshot.id,snapshotSha256:snapshot.sha256,live:false,scenario:project==='project-05'?'clear-history':'restart',fixture:'long'}));
  try{
    const result=await exec(process.execPath,[resolve('forge/graders/workshop.cjs'),scenario],{cwd:workspace,env:{...process.env,WORKSHOP_GRADE_DIR:out},timeout:240000,maxBuffer:2_000_000});
    await writeFile(join(out,'command.log'),result.stdout+result.stderr);
  }catch(error:any){await writeFile(join(out,'command.log'),String(error.stdout??'')+String(error.stderr??'')+String(error));throw error;}
  console.log(project,process.platform,'Electron checks passed',snapshot.sha256);
}
