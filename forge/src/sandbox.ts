import {createSandboxClient} from '@coreweave/cwsandbox/wandb';
import type {Sandbox, SandboxClient} from '@coreweave/cwsandbox';
import {Type} from 'typebox';
import type {ToolDefinition} from '@earendil-works/pi-coding-agent';
import {mkdir, writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {writeJson} from './records.js';
import {acquireSlot} from './slots.js';
import {type Config, requireLive} from './config.js';
import {deadline} from './lifecycle.js';

export interface SandboxJournal {
  trialId: string;
  lookupTag?: string;
  sandboxId?: string;
  state: 'creating' | 'running' | 'terminated' | 'cleanup_failed' | 'creation_unknown';
  requestedAt?:string;runningAt?:string;terminatedAt?:string;
  recoveredSandboxIds?:string[];
}

/** Provider tags have a 59-character limit; durable operation IDs may be longer. */
export function sandboxLookupTag(id:string){
  return id.length<=59&&/^[A-Za-z0-9._-]*[A-Za-z0-9]$/.test(id)?id:`course-${createHash('sha256').update(id).digest('hex').slice(0,40)}`;
}

/** Adapter for pinned cwsandbox 1.0.0, which has no public client.dispose().
 * Close only this owner's sandbox channels and control transport, never the
 * module-global channel pool. An SDK shape change must fail visibly. */
export async function disposeSandboxClient(client:SandboxClient,ids:string[]) {
  const transport=(client as unknown as {transport?:{directDataPlane?:{discardSandbox:(id:string)=>void};clients?:{client?:{_transport?:{close:()=>void|Promise<void>}}}}}).transport;
  const control=transport?.clients?.client?._transport;
  if(!control?.close||!transport?.directDataPlane?.discardSandbox)throw new Error('Pinned sandbox transport disposal contract changed');
  for(const id of ids)transport.directDataPlane.discardSandbox(id);
  await deadline(Promise.resolve(control.close()),10000,'Sandbox transport shutdown');
}

export async function withWorkspace<T>(options: {
  config: Config; image: string; trialId: string; evidenceDir: string;
  signal?: AbortSignal; client?: SandboxClient; slotDir?: string;
  beforeLaunch?:()=>Promise<void>;
  onJournal?:(journal:SandboxJournal)=>Promise<void>;
}, action: (sandbox: Sandbox) => Promise<T>): Promise<T> {
  requireLive(options.config);
  if (!/@sha256:[a-f0-9]{64}$/.test(options.image)) throw new Error('Sandbox image must be pinned by digest');
  const lookupTag=sandboxLookupTag(options.trialId);
  const journal: SandboxJournal = {trialId: options.trialId, lookupTag, state: 'creating'};
  const journalFile = join(options.evidenceDir, 'sandbox.json');
  const save=async()=>{await writeJson(journalFile,journal);await options.onJournal?.(journal);};
  await save();
  const slot = await acquireSlot(options.trialId, options.slotDir, options.signal);
  const client = options.client ?? createSandboxClient({apiKey: options.config.apiKey, entity: options.config.entity, project: options.config.project});
  const ownedIds:string[]=[];let launched=false;
  try {
  await options.beforeLaunch?.();
  options.signal?.throwIfAborted();
  journal.requestedAt=new Date().toISOString();await save();launched=true;
  let sandbox: Sandbox;
  try {
    sandbox = await client.create({containerImage: options.image, resources: {cpu: '2', memory: '4Gi'},
      maxLifetimeSeconds: 1200, network: {denyEgress: true}, tags: ['harness-course', lookupTag],
      annotations: {'course.trial': options.trialId}, waitUntilRunning: false, timeoutMs: 60000, signal: options.signal});
  } catch (error) {
    journal.state = 'creation_unknown';
    await save();
    // A timed-out create can still launch a billed workload. Reconcile before retrying.
    const matches = await client.listAll({tags: [lookupTag], timeoutMs: 30000});
    for (const match of matches) {
      ownedIds.push(match.sandboxId);
      await match.stop({missingOk: true, timeoutMs: 30000});
      await match.wait({targetStatus: 'terminal', timeoutMs: 30000});
    }
    journal.recoveredSandboxIds=ownedIds;await save();
    throw error;
  }
  journal.sandboxId = sandbox.sandboxId;
  ownedIds.push(sandbox.sandboxId);
  try {
    await save();
    await sandbox.wait({targetStatus: 'running', timeoutMs: 180000, signal: options.signal});
    journal.state = 'running';
    journal.runningAt=new Date().toISOString();await save();
    return await action(sandbox);
  } finally {
    let collectionFailure:unknown;
    try {
      const patch = await sandbox.commands.run(['bash', '-lc', 'cd /workspace/task && git add -N . && git diff --binary HEAD'], {timeoutMs: 15000, check: false});
      await writeFile(join(options.evidenceDir, 'patch.diff'), patch.stdout);
    } catch (error) {
      try {await writeJson(join(options.evidenceDir, 'collection-error.json'), {error: String(error)});}
      catch(writeError){collectionFailure=writeError;}
    }
    try {
      await sandbox.stop({missingOk: true, timeoutMs: 30000, gracefulShutdownSeconds: 3});
      await sandbox.wait({targetStatus: 'terminal', timeoutMs: 30000});
      journal.state = 'terminated';
      journal.terminatedAt=new Date().toISOString();
    } catch (error) {
      journal.state = 'cleanup_failed';
      await save();
      throw new Error(`Cleanup unverified for sandbox ${sandbox.sandboxId}; stop the campaign`, {cause: error});
    }
    await save();
    if(collectionFailure)throw collectionFailure;
  }
  } finally {
    // Unknown creation/cleanup retains the slot until an operator proves termination.
    try {if (journal.state === 'terminated'||!launched) await slot.release();}
    finally {if(!options.client)await disposeSandboxClient(client,ownedIds);}
  }
}

export async function stageWorkspace(sandbox: Sandbox, archive: Uint8Array) {
  await sandbox.files.write('/tmp/task.tar', archive);
  await sandbox.commands.run(['bash', '-lc', 'mkdir -p /workspace/task && tar -xf /tmp/task.tar -C /workspace/task && cd /workspace/task && cp -as /opt/app/node_modules . && printf "\\nnode_modules/\\ndist/\\n" >> .gitignore && git init -q && git config user.email learner@example.invalid && git config user.name Learner && git add . && git commit -qm baseline'], {timeoutMs: 60000});
}

const terminateCommandGroup = `import json,os,signal,subprocess,sys,time
from pathlib import Path
marker=Path(sys.argv[1])
value=marker.read_text().strip()
if value.startswith('done:'):
    print(json.dumps({'terminated':True,'reason':'command already exited'}));sys.exit(0)
group=int(value)
def live():
    rows=subprocess.check_output(['ps','-eo','pgid=,stat='],text=True).splitlines()
    return [r for r in rows if len(r.split())==2 and int(r.split()[0])==group and not r.split()[1].startswith('Z')]
for sig in [signal.SIGTERM,signal.SIGKILL]:
    try:os.killpg(group,sig)
    except ProcessLookupError:pass
    for _ in range(30):
        if not live():break
        time.sleep(0.1)
    if not live():break
if live():raise RuntimeError('Remote command group remains active')
marker.unlink(missing_ok=True)
print(json.dumps({'terminated':True,'processGroup':group}))
`;

/** SDK cancel closes the stream only. Kill and verify our remote process group too. */
export async function runSandboxCommand(sandbox:Sandbox,command:string,options:{timeoutMs:number;signal?:AbortSignal;cancellationEvidence?:string}) {
  const marker=`/tmp/forge-command-${randomUUID()}.pid`;
  await sandbox.files.write(marker,'pending');
  const wrapper='setsid bash -lc "$2" & child=$!; echo "$child" > "$1"; wait "$child"; result=$?; echo "done:$result" > "$1"; exit "$result"';
  const process=await sandbox.commands.start(['bash','-lc',wrapper,'forge-bounded-command',marker,command],{cwd:'/workspace/task',check:false,bufferedMaxKiB:64,timeoutMs:options.timeoutMs,signal:options.signal});
  try {return await process.wait({timeoutMs:options.timeoutMs,signal:options.signal});}
  catch(error) {
    let streamError:string|undefined;
    try {await process.cancel({timeoutMs:10000});}catch(e){streamError=String(e);}
    // Cleanup uses a fresh deadline, never the aborted task signal.
    try {
      const cleanup=await sandbox.commands.run(['python3','-c',terminateCommandGroup,marker],{check:false,timeoutMs:15000});
      if(options.cancellationEvidence)await writeJson(options.cancellationEvidence,{error:String(error),streamError,cleanup});
      if(cleanup.exitCode!==0)throw new Error('Remote group remains active or unknown');
    } catch(cleanupError) {
      await sandbox.stop({missingOk:true,timeoutMs:30000});
      await sandbox.wait({targetStatus:'terminal',timeoutMs:30000});
      throw new Error('Remote command cancellation unverified; workspace terminated',{cause:cleanupError});
    }
    throw error;
  }
}

export function sandboxTools(sandbox: Sandbox, evidenceDir: string): ToolDefinition[] {
  let sequence = 0;
  return [{name: 'sandbox_command', label: 'Sandbox command',
    description: 'Run a shell command in the isolated task workspace. Use this to inspect, edit files, and run tests. Network access is disabled.',
    parameters: Type.Object({command: Type.String({maxLength: 20000})}),
    async execute(_id, parameters, signal) {
      const command = (parameters as {command: string}).command;
      const number=++sequence;
      try {
        const result = await runSandboxCommand(sandbox,command,{timeoutMs:90000,signal,cancellationEvidence:join(evidenceDir,`cancel-${number}.json`)});
        const record = {command, exitCode: result.exitCode, stdout: result.stdout, stderr: result.stderr, truncated: result.stdoutTruncated || result.stderrTruncated};
        await mkdir(evidenceDir, {recursive: true});
        await writeJson(join(evidenceDir, `tool-${number}.json`), record);
        // Preserve complete captured output in evidence; avoid consuming the model's
        // context with repeated whole-tree reads. The actor can request narrower ranges.
        const excerpt = (value: string) => value.length <= 12000 ? value : value.slice(0,8000) + '\n[output excerpted; inspect narrower file/line ranges]\n' + value.slice(-4000);
        return {content: [{type: 'text' as const, text: JSON.stringify({...record, stdout:excerpt(record.stdout), stderr:excerpt(record.stderr), truncated:record.truncated || record.stdout.length>12000 || record.stderr.length>12000})}], details: {exitCode: result.exitCode}};
      } catch (error) {
        await writeJson(join(evidenceDir,`tool-${number}.json`),{command,error:String(error)});
        throw error;
      }
    },
  }];
}
