import {config, publicConfig} from './config.js';
import {runServices} from './headless.js';
import {writeJson} from './records.js';
import {parseArgs} from 'node:util';

const command = process.argv[2] ?? 'help';
if(command==='workshop'){
  console.log(JSON.stringify(await (await import('./workshop-cli.js')).workshopCLI(process.argv.slice(3)),null,2));
} else if (command === 'doctor' && process.argv.includes('--qualify')) {
  if(!process.argv.includes('--execute'))throw new Error('Qualification requires --execute');
  const {values}=parseArgs({args:process.argv.slice(3),options:{qualify:{type:'boolean'},execute:{type:'boolean'},output:{type:'string'},'operation-id':{type:'string'}}});
  const result=await (await import('./qualification.js')).qualify(values.output,values['operation-id']);console.log(JSON.stringify(result,null,2));if(!result.passed)process.exitCode=1;
} else if(command==='controls'){
  const {values}=parseArgs({args:process.argv.slice(3),options:{output:{type:'string'},project:{type:'string'},kind:{type:'string'},execute:{type:'boolean'},source:{type:'string'},'operation-id':{type:'string'}}});
  if(!values.execute||!values.project||!['baseline','reference','regression'].includes(values.kind??''))throw new Error('controls --project project-NN --kind baseline|reference|regression --execute');
  const source=values.source??await (await import('./staging.js')).sourceHead();
  const result=await (await import('./controls.js')).qualifyControl(values.project,source,values.output??process.env.FORGE_RESULTS_DIR??'forge/local-results',values.kind as 'baseline'|'reference'|'regression',values['operation-id']);console.log(JSON.stringify(result,null,2));if(!result.qualified)process.exitCode=1;
} else if(['recovery-report','recover','reconcile'].includes(command)){
  const {values}=parseArgs({args:process.argv.slice(3),options:{output:{type:'string'},operation:{type:'string'},evidence:{type:'string'},publish:{type:'boolean'}}});
  const root=values.output??process.env.FORGE_RESULTS_DIR??'forge/local-results';
  const recovery=await import('./recovery.js');
  if(command!=='recovery-report'&&!values.operation)throw new Error('--operation is required');
  if(command==='reconcile'&&!values.evidence)throw new Error('--evidence must name a relative supporting receipt');
  console.log(JSON.stringify(command==='recovery-report'?await recovery.recoveryReport(root):command==='recover'?await recovery.recoverOperation(root,values.operation!,values.publish):await recovery.reconcileOperation(root,values.operation!,values.evidence!),null,2));
} else if (command === 'doctor') {
  const c = config();
  console.log(JSON.stringify({node: process.version, config: publicConfig(c), credentialsConfigured: Boolean(c.apiKey), liveReady: Boolean(c.apiKey && c.entity)}, null, 2));
} else if (command === 'services') {
  const [app, output, ...fixtures] = process.argv.slice(3).filter(arg => arg !== '--live');
  if (!app || !output || !fixtures.length) throw new Error('services APP_DIR OUTPUT_JSON FIXTURE... [--live]');
  await writeJson(output, await runServices(app, fixtures, process.argv.includes('--live')));
} else if(command==='run'||command==='compare') {
  const {values}=parseArgs({args:process.argv.slice(3),options:{project:{type:'string'},variant:{type:'string'},repeats:{type:'string'},execute:{type:'boolean'},output:{type:'string'},source:{type:'string'},'operation-id':{type:'string'}}});
  if(command==='run'&&(!values.project||!values.variant))throw new Error('run requires --project and --variant');
  const result=await (await import('./campaign.js')).compare({...values,operationId:values['operation-id'],repeats:command==='run'?1:values.repeats?Number(values.repeats):undefined});
  console.log(JSON.stringify(result,null,2));
} else {
  console.log('Forge course: doctor | services | run | compare. Paid run/compare require --execute.');
}
