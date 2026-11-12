import {mkdir, rm} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';
import {writeJson} from './records.js';

const packageRoot = fileURLToPath(new URL(existsSync(new URL('../package.json', import.meta.url)) ? '../' : '../../', import.meta.url));
export const slotDirectory = join(process.env.FORGE_RESULTS_DIR??join(packageRoot,'local-results'), '.sandbox-slots');
/** Cross-process capacity shared by qualifications, campaigns and graph lanes.
 * Never reclaim an orphan automatically: its remote sandbox may still be billed. */
export async function acquireSlot(owner: string, directory = slotDirectory, signal?: AbortSignal, timeoutMs = 1200000) {
  await mkdir(directory, {recursive:true});
  const started = Date.now();
  for (;;) {
    signal?.throwIfAborted();
    for (let slot = 0; slot < 2; slot++) {
      const path = join(directory, String(slot));
      try {await mkdir(path);}
      catch(error) {if ((error as NodeJS.ErrnoException).code === 'EEXIST') continue; throw error;}
      try {await writeJson(join(path, 'owner.json'), {owner, pid:process.pid, acquiredAt:new Date().toISOString()});}
      catch(error) {await rm(path, {recursive:true}); throw error;}
      let released = false;
      return {path, async release() {if (!released) {await rm(path, {recursive:true}); released=true;}}};
    }
    if (Date.now() - started >= timeoutMs) throw new Error('Two sandbox slots are occupied; reconcile recorded owners before retrying');
    await delay(100, undefined, {signal});
  }
}
