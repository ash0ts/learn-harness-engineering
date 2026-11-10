import {readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {runTrial} from './trial.js';
import {writeJson} from './records.js';
import {updateOperation} from './operations.js';

const input=JSON.parse(process.argv[2]??'{}');
const ledger=JSON.parse(await readFile(input.ledger,'utf8'));
if(ledger.halted||(process.env.FORGE_BUDGET_MODE!=='incremental'&&!(ledger.reservations[input.id]>0)))throw new Error('Worker has no active budget reservation');
const receipt=join(input.output,input.id,'worker-finalization.json');
await runTrial(input);
await writeJson(receipt,{phase:'grading_complete',cleanExit:false,activeResources:process.getActiveResourcesInfo(),at:new Date().toISOString()});
// This unreferenced watchdog runs only when an owned resource keeps Node alive.
// Never disguise forced shutdown as a successful grading/publication lifecycle.
const watchdog=setTimeout(async()=>{
  await writeJson(receipt,{phase:'forced_shutdown',cleanExit:false,activeResources:process.getActiveResourcesInfo(),at:new Date().toISOString()});
  await updateOperation(input.output,input.id,op=>{op.phase='recoverable';op.events.push({event:'forced_worker_shutdown',at:new Date().toISOString()});});
  process.exit(1);
},30000);watchdog.unref();
process.once('beforeExit',async()=>{
  clearTimeout(watchdog);
  await writeJson(receipt,{phase:'terminated',cleanExit:true,activeResources:process.getActiveResourcesInfo(),at:new Date().toISOString()});
});
