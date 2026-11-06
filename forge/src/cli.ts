import {config, publicConfig} from './config.js';
import {runServices} from './headless.js';
import {writeJson} from './records.js';
import {parseArgs} from 'node:util';

const command = process.argv[2] ?? 'help';
if (command === 'validate-notebooks') {
  const {spawnSync}=await import('node:child_process');
  const {courseRoot}=await import('./staging.js');
  const result=spawnSync('python3',[`${courseRoot}/forge/scripts/validate_notebooks.py`,...process.argv.slice(3)],{cwd:courseRoot,stdio:'inherit'});
  if(result.error)throw result.error;
  process.exitCode=result.status??1;
} else if (command === 'doctor' && process.argv.includes('--qualify')) {
  if(!process.argv.includes('--execute'))throw new Error('Qualification requires --execute');
  console.log(JSON.stringify(await (await import('./qualification.js')).qualify(),null,2));
} else if (command === 'doctor') {
  const c = config();
  console.log(JSON.stringify({node: process.version, config: publicConfig(c), credentialsConfigured: Boolean(c.apiKey), liveReady: Boolean(c.apiKey && c.entity)}, null, 2));
} else if (command === 'services') {
  const [app, output, ...fixtures] = process.argv.slice(3).filter(arg => arg !== '--live');
  if (!app || !output || !fixtures.length) throw new Error('services APP_DIR OUTPUT_JSON FIXTURE... [--live]');
  await writeJson(output, await runServices(app, fixtures, process.argv.includes('--live')));
} else if(command==='graph') {
  const {values}=parseArgs({args:process.argv.slice(3),options:{checkpoint:{type:'string'},execute:{type:'boolean'},resume:{type:'boolean'},decision:{type:'string'},actor:{type:'string'},sha256:{type:'string'}}});
  if(!values.checkpoint)throw new Error('graph requires --checkpoint');
  if(values.decision) {
    if(!['approve','reject'].includes(values.decision)||!values.actor||!values.sha256)throw new Error('Decision requires approve/reject, --actor and reviewed --sha256');
    console.log(JSON.stringify(await (await import('./graph.js')).decideGraph(values.checkpoint,values.decision as 'approve'|'reject',values.actor,values.sha256),null,2));
  } else console.log(JSON.stringify(await (await import('./graph-runner.js')).runGraph(values.checkpoint,!!values.execute,values.resume),null,2));
} else if(command==='loop') {
  const {values}=parseArgs({args:process.argv.slice(3),options:{mode:{type:'string'},checkpoint:{type:'string'},execute:{type:'boolean'},resume:{type:'boolean'},'duration-seconds':{type:'string'},'interval-seconds':{type:'string'},'max-rounds':{type:'string'}}});
  if(!values.mode||!values.checkpoint)throw new Error('loop requires --mode and --checkpoint');
  const abort=new AbortController();process.once('SIGINT',()=>abort.abort());process.once('SIGTERM',()=>abort.abort());
  console.log(JSON.stringify(await (await import('./loops.js')).runLoop({mode:values.mode as import('./loops.js').LoopMode,file:values.checkpoint,execute:!!values.execute,resume:values.resume,durationSeconds:values['duration-seconds']?Number(values['duration-seconds']):undefined,intervalSeconds:values['interval-seconds']?Number(values['interval-seconds']):undefined,maxRounds:values['max-rounds']?Number(values['max-rounds']):undefined},abort.signal),null,2));
} else if(command==='run'||command==='compare') {
  const {values}=parseArgs({args:process.argv.slice(3),options:{project:{type:'string'},variant:{type:'string'},repeats:{type:'string'},execute:{type:'boolean'},output:{type:'string'},source:{type:'string'}}});
  if(command==='run'&&(!values.project||!values.variant))throw new Error('run requires --project and --variant');
  const result=await (await import('./campaign.js')).compare({...values,repeats:command==='run'?1:values.repeats?Number(values.repeats):undefined});
  console.log(JSON.stringify(result,null,2));
} else {
  console.log('Forge course: doctor | services | run | compare | loop | graph | validate-notebooks. Paid run/compare require --execute.');
}
