import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, readFile, writeFile, access} from 'node:fs/promises';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {setTimeout as delay} from 'node:timers/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import type {SandboxClient, Sandbox} from '@coreweave/cwsandbox';
import {withWorkspace,runSandboxCommand,disposeSandboxClient,sandboxLookupTag,commandSupervisor,terminateCommandGroup,SandboxCommandError} from '../src/sandbox.js';
import {config} from '../src/config.js';

test('long control IDs use bounded stable lookup tags and retain their full identity',async()=>{
 const id='control-project-01-baseline-43c63357-a96b-437a-aa01-c832eebace8e',tag=sandboxLookupTag(id);
 assert.ok(tag.length<=59);assert.match(tag,/^[A-Za-z0-9._-]+$/);assert.equal(tag,sandboxLookupTag(id));assert.notEqual(tag,sandboxLookupTag(id+'x'));
 const dir=await mkdtemp(join(tmpdir(),'forge-tag-'));let created:any;
 const sandbox={sandboxId:'tag-test',wait:async()=>{},commands:{run:async()=>({stdout:''})},stop:async()=>{}} as unknown as Sandbox;
 await withWorkspace({config:config({WANDB_ENTITY:'test',WANDB_API_KEY:'test'}),image:`image@sha256:${'a'.repeat(64)}`,trialId:id,evidenceDir:dir,slotDir:join(dir,'slots'),client:{create:async(options:any)=>{created=options;return sandbox;}} as unknown as SandboxClient},async()=>{});
 assert.deepEqual(created.tags,['harness-course',tag]);assert.equal(created.annotations['course.trial'],id);
 assert.equal(created.dataPlaneMode,'gateway');
 assert.equal(JSON.parse(await readFile(join(dir,'sandbox.json'),'utf8')).lookupTag,tag);
});

test('failed tasks still collect patches and confirm termination', async () => {
  const evidenceDir = await mkdtemp(join(tmpdir(), 'forge-test-'));
  const calls: string[] = [];
  const sandbox = {sandboxId: 'sandbox-1', wait: async ({targetStatus}: {targetStatus: string}) => { calls.push(targetStatus); },
    commands: {run: async () => ({stdout: 'patch'})}, stop: async () => { calls.push('stop'); }} as unknown as Sandbox;
  const client = {create: async () => sandbox} as unknown as SandboxClient;
  await assert.rejects(withWorkspace({config: config({WANDB_ENTITY: 'test', WANDB_API_KEY: 'test'}),
    image: `example@sha256:${'a'.repeat(64)}`, trialId: 'trial', evidenceDir, slotDir:join(evidenceDir,'slots'), client}, async () => {throw new Error('task failed');}), /task failed/);
  assert.deepEqual(calls, ['running', 'stop', 'terminal']);
  assert.equal(JSON.parse(await readFile(join(evidenceDir, 'sandbox.json'), 'utf8')).state, 'terminated');
});

test('a timed-out stream also terminates its remote process group with an independent deadline',async()=>{
  const calls:string[]=[];
  const sandbox={files:{write:async()=>{},read:async()=>Buffer.from('{"state":"running","processGroup":42}')},commands:{start:async()=>({wait:async()=>{throw new Error('wait timed out');},cancel:async()=>{calls.push('stream cancel');}}),run:async(command:string[],options:{signal?:AbortSignal})=>{calls.push(command[0]);assert.equal(options.signal,undefined);return {exitCode:0,stdout:'{"terminated":true}'};}}} as unknown as Sandbox;
  await assert.rejects(runSandboxCommand(sandbox,'sleep 60',{timeoutMs:1}),/wait timed out/);
  assert.deepEqual(calls,['stream cancel','python3']);
});

test('failed remote cancellation cannot be reported as a completed command',async()=>{
  const calls:string[]=[];
  const sandbox={files:{write:async()=>{},read:async()=>Buffer.from('{"state":"running","processGroup":42}')},commands:{start:async()=>({wait:async()=>{throw new Error('timeout');},cancel:async()=>{}}),run:async()=>({exitCode:1})},stop:async()=>{calls.push('stop');},wait:async()=>{calls.push('terminal');}} as unknown as Sandbox;
  await assert.rejects(runSandboxCommand(sandbox,'sleep 60',{timeoutMs:1}),/cancellation unverified/);
  assert.deepEqual(calls,['stop','terminal']);
});

test('execution deadline waits for the remote PID; slow gateway startup is not execution',async()=>{
 let reads=0;const waits:Array<any>=[];
 const sandbox={files:{write:async()=>{},read:async()=>Buffer.from(JSON.stringify(++reads===1?{state:'pending'}:{state:'running',processGroup:42}))},commands:{start:async(_command:any,options:any)=>{assert.ok(options.timeoutMs>30000);return {status:'running',wait:async(options:any)=>{waits.push(options);if(options)assert.equal(reads,2);return {exitCode:0};}};}}} as unknown as Sandbox;
 assert.equal((await runSandboxCommand(sandbox,'true',{timeoutMs:500})).exitCode,0);
 assert.equal(waits[1].timeoutMs,500);
});

test('ambiguous start failure still cancels the durable pending launch',async()=>{
 let cleaned=false;
 const sandbox={files:{write:async()=>{}},commands:{start:async()=>{throw new Error('gateway unavailable');},run:async()=>{cleaned=true;return {exitCode:0,stdout:'{"terminated":true,"started":false}'};}}} as unknown as Sandbox;
 await assert.rejects(runSandboxCommand(sandbox,'sleep 60',{timeoutMs:500}),e=>e instanceof SandboxCommandError&&!e.started&&e.cancellationVerified);
 assert.equal(cleaned,true);
});

const python=promisify(execFile);
test('pending cancellation prevents a delayed real supervisor from launching',async()=>{
 const root=await mkdtemp(join(tmpdir(),'forge-pending-')),marker=join(root,'marker'),proof=join(root,'launched');
 await writeFile(marker,JSON.stringify({state:'pending'}));
 const cleanup=await python('python3',['-c',terminateCommandGroup,marker]);
 assert.equal(JSON.parse(cleanup.stdout).started,false);
 await assert.rejects(python('python3',['-c',commandSupervisor,marker,`touch '${proof}'`]),(e:any)=>e.code===125);
 await assert.rejects(access(proof));
});

test('real running command and descendants terminate and repeated cleanup is safe',async()=>{
 const root=await mkdtemp(join(tmpdir(),'forge-running-')),marker=join(root,'marker');
 await writeFile(marker,JSON.stringify({state:'pending'}));
 const child=python('python3',['-c',commandSupervisor,marker,'sleep 60 & wait']).then(()=>null,e=>e);
 try{
  for(let i=0;i<100&&JSON.parse(await readFile(marker,'utf8')).state==='pending';i++)await delay(20);
  assert.equal(JSON.parse(await readFile(marker,'utf8')).state,'running');
  const cleanup=await python('python3',['-c',terminateCommandGroup,marker]);
  assert.equal(JSON.parse(cleanup.stdout).started,true);
  assert.equal(JSON.parse(cleanup.stdout).terminated,true);
  assert.equal(JSON.parse((await python('python3',['-c',terminateCommandGroup,marker])).stdout).terminated,true);
 }finally{await python('python3',['-c',terminateCommandGroup,marker]);await child;}
});

test('unverified cleanup overrides a successful task', async () => {
  const evidenceDir = await mkdtemp(join(tmpdir(), 'forge-test-'));
  const sandbox = {sandboxId: 'sandbox-2', wait: async () => {}, commands: {run: async () => ({stdout: ''})},
    stop: async () => {throw new Error('gateway offline');}} as unknown as Sandbox;
  await assert.rejects(withWorkspace({config: config({WANDB_ENTITY: 'test', WANDB_API_KEY: 'test'}),
    image: `example@sha256:${'a'.repeat(64)}`, trialId: 'trial', evidenceDir, slotDir:join(evidenceDir,'slots'),
    client: {create: async () => sandbox} as unknown as SandboxClient}, async () => 'pass'), /Cleanup unverified/);
});

test('only the owned sandbox channels and transport are closed',async()=>{
  const calls:string[]=[];
  const client={transport:{directDataPlane:{discardSandbox:(id:string)=>calls.push(id)},clients:{client:{_transport:{close:()=>{calls.push('control');}}}}}} as unknown as SandboxClient;
  await disposeSandboxClient(client,['owned']);assert.deepEqual(calls,['owned','control']);
  await assert.rejects(disposeSandboxClient({} as SandboxClient,[]),/contract changed/);
});

test('a journal failure after creation still terminates the sandbox',async()=>{
  const evidenceDir=await mkdtemp(join(tmpdir(),'forge-journal-'));let stopped=false;
  const sandbox={sandboxId:'journal-failure',commands:{run:async()=>({stdout:''})},stop:async()=>{stopped=true;},wait:async()=>{}} as unknown as Sandbox;
  await assert.rejects(withWorkspace({config:config({WANDB_ENTITY:'test',WANDB_API_KEY:'test'}),image:`example@sha256:${'a'.repeat(64)}`,trialId:'journal-failure',evidenceDir,slotDir:join(evidenceDir,'slots'),client:{create:async()=>sandbox} as unknown as SandboxClient,onJournal:async j=>{if(j.sandboxId&&j.state==='creating')throw new Error('disk unavailable');}},async()=>{}),/disk unavailable/);
  assert.equal(stopped,true);
  assert.equal(JSON.parse(await readFile(join(evidenceDir,'sandbox.json'),'utf8')).state,'terminated');
});
