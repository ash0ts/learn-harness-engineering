import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, readFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import type {SandboxClient, Sandbox} from '@coreweave/cwsandbox';
import {withWorkspace,runSandboxCommand,disposeSandboxClient} from '../src/sandbox.js';
import {config} from '../src/config.js';

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
  const sandbox={files:{write:async()=>{}},commands:{start:async()=>({wait:async()=>{throw new Error('wait timed out');},cancel:async()=>{calls.push('stream cancel');}}),run:async(command:string[],options:{signal?:AbortSignal})=>{calls.push(command[0]);assert.equal(options.signal,undefined);return {exitCode:0};}}} as unknown as Sandbox;
  await assert.rejects(runSandboxCommand(sandbox,'sleep 60',{timeoutMs:1}),/wait timed out/);
  assert.deepEqual(calls,['stream cancel','python3']);
});

test('failed remote cancellation cannot be reported as a completed command',async()=>{
  const calls:string[]=[];
  const sandbox={files:{write:async()=>{}},commands:{start:async()=>({wait:async()=>{throw new Error('timeout');},cancel:async()=>{}}),run:async()=>({exitCode:1})},stop:async()=>{calls.push('stop');},wait:async()=>{calls.push('terminal');}} as unknown as Sandbox;
  await assert.rejects(runSandboxCommand(sandbox,'sleep 60',{timeoutMs:1}),/cancellation unverified/);
  assert.deepEqual(calls,['stop','terminal']);
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
