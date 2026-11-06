import {createSandboxClient} from '@coreweave/cwsandbox/wandb';
import type {Sandbox, SandboxClient} from '@coreweave/cwsandbox';
import {Type} from 'typebox';
import type {ToolDefinition} from '@earendil-works/pi-coding-agent';
import {mkdir, writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {writeJson} from './records.js';
import {type Config, requireLive} from './config.js';

export interface SandboxJournal {
  trialId: string;
  sandboxId?: string;
  state: 'creating' | 'running' | 'terminated' | 'cleanup_failed' | 'creation_unknown';
}

export async function withWorkspace<T>(options: {
  config: Config; image: string; trialId: string; evidenceDir: string;
  signal?: AbortSignal; client?: SandboxClient;
}, action: (sandbox: Sandbox) => Promise<T>): Promise<T> {
  requireLive(options.config);
  if (!/@sha256:[a-f0-9]{64}$/.test(options.image)) throw new Error('Sandbox image must be pinned by digest');
  const client = options.client ?? createSandboxClient({apiKey: options.config.apiKey, entity: options.config.entity, project: options.config.project});
  const journal: SandboxJournal = {trialId: options.trialId, state: 'creating'};
  const journalFile = join(options.evidenceDir, 'sandbox.json');
  await writeJson(journalFile, journal);
  let sandbox: Sandbox;
  try {
    sandbox = await client.create({containerImage: options.image, resources: {cpu: '2', memory: '4Gi'},
      maxLifetimeSeconds: 1200, network: {denyEgress: true}, tags: ['harness-course', options.trialId],
      annotations: {'course.trial': options.trialId}, waitUntilRunning: false, timeoutMs: 60000, signal: options.signal});
  } catch (error) {
    journal.state = 'creation_unknown';
    await writeJson(journalFile, journal);
    // A timed-out create can still launch a billed workload. Reconcile before retrying.
    const matches = await client.listAll({tags: [options.trialId], timeoutMs: 30000});
    for (const match of matches) {
      await match.stop({missingOk: true, timeoutMs: 30000});
      await match.wait({targetStatus: 'terminal', timeoutMs: 30000});
    }
    throw error;
  }
  journal.sandboxId = sandbox.sandboxId;
  await writeJson(journalFile, journal);
  try {
    await sandbox.wait({targetStatus: 'running', timeoutMs: 180000, signal: options.signal});
    journal.state = 'running';
    await writeJson(journalFile, journal);
    return await action(sandbox);
  } finally {
    try {
      const patch = await sandbox.commands.run(['bash', '-lc', 'cd /workspace/task && git add -N . && git diff --binary HEAD'], {timeoutMs: 15000, check: false});
      await writeFile(join(options.evidenceDir, 'patch.diff'), patch.stdout);
    } catch (error) {
      await writeJson(join(options.evidenceDir, 'collection-error.json'), {error: String(error)});
    }
    try {
      await sandbox.stop({missingOk: true, timeoutMs: 30000, gracefulShutdownSeconds: 3});
      await sandbox.wait({targetStatus: 'terminal', timeoutMs: 30000});
      journal.state = 'terminated';
    } catch (error) {
      journal.state = 'cleanup_failed';
      await writeJson(journalFile, journal);
      throw new Error(`Cleanup unverified for sandbox ${sandbox.sandboxId}; stop the campaign`, {cause: error});
    }
    await writeJson(journalFile, journal);
  }
}

export async function stageWorkspace(sandbox: Sandbox, archive: Uint8Array) {
  await sandbox.files.write('/tmp/task.tar', archive);
  await sandbox.commands.run(['bash', '-lc', 'mkdir -p /workspace/task && tar -xf /tmp/task.tar -C /workspace/task && cd /workspace/task && cp -as /opt/app/node_modules . && printf "\\nnode_modules/\\ndist/\\n" >> .gitignore && git init -q && git config user.email learner@example.invalid && git config user.name Learner && git add . && git commit -qm baseline'], {timeoutMs: 60000});
}

export function sandboxTools(sandbox: Sandbox, evidenceDir: string): ToolDefinition[] {
  let sequence = 0;
  return [{name: 'sandbox_command', label: 'Sandbox command',
    description: 'Run a shell command in the isolated task workspace. Use this to inspect, edit files, and run tests. Network access is disabled.',
    parameters: Type.Object({command: Type.String({maxLength: 20000})}),
    async execute(_id, parameters, signal) {
      const command = (parameters as {command: string}).command;
      const process = await sandbox.commands.start(['bash', '-lc', command], {cwd: '/workspace/task', check: false, bufferedMaxKiB: 64, timeoutMs: 90000, signal});
      try {
        const result = await process.wait({timeoutMs: 90000, signal});
        const record = {command, exitCode: result.exitCode, stdout: result.stdout, stderr: result.stderr, truncated: result.stdoutTruncated || result.stderrTruncated};
        await mkdir(evidenceDir, {recursive: true});
        await writeJson(join(evidenceDir, `tool-${++sequence}.json`), record);
        return {content: [{type: 'text' as const, text: JSON.stringify(record)}], details: {exitCode: result.exitCode}};
      } catch (error) {
        await process.cancel({timeoutMs: 10000});
        throw error;
      }
    },
  }];
}
