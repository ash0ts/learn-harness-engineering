import type {Sandbox} from '@coreweave/cwsandbox';
/** The coordinator creates, stages, journals, and terminates this owned sandbox. */
export async function inspectWorkspace(sandbox:Sandbox) {
  return sandbox.commands.run(['npm','run','check'],{cwd:'/workspace/task',timeoutMs:60000,check:false});
}
