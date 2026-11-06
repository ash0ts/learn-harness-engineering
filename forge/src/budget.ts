import {mkdir, readFile, rm} from 'node:fs/promises';
import {dirname} from 'node:path';
import {writeJson} from './records.js';

export interface Ledger {
  schemaVersion: 1; limitUsd: number; spentEstimateUsd: number;
  reservations: Record<string, number>; settled: Record<string, number>;
  halted?: string;
}
/** Shared, fail-closed reservation ledger. A stale lock requires explicit reconciliation. */
export class Budget {
  constructor(readonly file: string, readonly limitUsd = 50) {
    if (!Number.isFinite(limitUsd) || limitUsd <= 0 || limitUsd > 50) throw new Error('Invalid budget limit');
  }
  private async change<T>(fn: (ledger: Ledger) => T): Promise<T> {
    await mkdir(dirname(this.file), {recursive:true});
    const lock = `${this.file}.lock`;
    await mkdir(lock); // atomic across processes; never silently steal an uncertain reservation
    try {
      let ledger: Ledger;
      try { ledger = JSON.parse(await readFile(this.file,'utf8')); }
      catch (error) {
        if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
        ledger = {schemaVersion:1,limitUsd:this.limitUsd,spentEstimateUsd:0,reservations:{},settled:{}};
      }
      if (ledger.limitUsd !== this.limitUsd) throw new Error('Budget limit changed; use the original ledger');
      const result = fn(ledger); await writeJson(this.file, ledger); return result;
    } finally {await rm(lock, {recursive:true});}
  }
  async reserve(block: Record<string, number>) {
    return this.change(ledger => {
      if (ledger.halted) throw new Error(`Budget halted: ${ledger.halted}`);
      for (const [id, amount] of Object.entries(block)) {
        if (!Number.isFinite(amount) || amount <= 0) throw new Error('Missing/invalid pricing');
        if (id in ledger.reservations || id in ledger.settled) throw new Error(`Duplicate trial ${id}`);
      }
      const total = ledger.spentEstimateUsd + [...Object.values(ledger.reservations),...Object.values(block)].reduce((a,b)=>a+b,0);
      if (total > ledger.limitUsd) throw new Error('budget_exhausted: complete block does not fit');
      Object.assign(ledger.reservations,block);
    });
  }
  async settle(id: string, actual: number | null, haltReason?: string) {
    return this.change(ledger => {
      if (!(id in ledger.reservations)) throw new Error(`No reservation for ${id}`);
      if (actual === null || !Number.isFinite(actual) || actual < 0 || haltReason) {
        ledger.halted = haltReason || `Missing usage for ${id}`; return;
      }
      if (actual > ledger.reservations[id]) ledger.halted = `Reservation exceeded by ${id}`;
      ledger.spentEstimateUsd += actual; ledger.settled[id] = actual; delete ledger.reservations[id];
    });
  }
}

export function estimate(inputTokens: number, outputTokens: number, sandboxSeconds: number,
  prices: {inputPerMillionUsd: number; outputPerMillionUsd: number; cpuHourUsd: number; memoryGiBHourUsd: number}) {
  const values = [inputTokens,outputTokens,sandboxSeconds,...Object.values(prices)];
  if (values.some(v => !Number.isFinite(v) || v < 0)) throw new Error('Missing usage or pricing');
  return (inputTokens*prices.inputPerMillionUsd + outputTokens*prices.outputPerMillionUsd)/1e6 +
    sandboxSeconds/3600*(2*prices.cpuHourUsd+4*prices.memoryGiBHourUsd);
}
