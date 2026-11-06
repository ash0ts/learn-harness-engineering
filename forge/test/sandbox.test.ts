import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, readFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import type {SandboxClient, Sandbox} from '@coreweave/cwsandbox';
import {withWorkspace} from '../src/sandbox.js';
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

test('unverified cleanup overrides a successful task', async () => {
  const evidenceDir = await mkdtemp(join(tmpdir(), 'forge-test-'));
  const sandbox = {sandboxId: 'sandbox-2', wait: async () => {}, commands: {run: async () => ({stdout: ''})},
    stop: async () => {throw new Error('gateway offline');}} as unknown as Sandbox;
  await assert.rejects(withWorkspace({config: config({WANDB_ENTITY: 'test', WANDB_API_KEY: 'test'}),
    image: `example@sha256:${'a'.repeat(64)}`, trialId: 'trial', evidenceDir, slotDir:join(evidenceDir,'slots'),
    client: {create: async () => sandbox} as unknown as SandboxClient}, async () => 'pass'), /Cleanup unverified/);
});
