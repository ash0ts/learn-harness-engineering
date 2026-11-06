import {readFile} from 'node:fs/promises';
import {runTrial} from './trial.js';

const input=JSON.parse(process.argv[2] ?? '{}');
const ledger=JSON.parse(await readFile(input.ledger,'utf8'));
if(ledger.halted || !(ledger.reservations[input.id]>0))throw new Error('Worker has no active budget reservation');
await runTrial(input);
