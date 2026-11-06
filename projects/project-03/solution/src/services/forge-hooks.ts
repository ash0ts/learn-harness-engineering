// Canonical dependency-free service seam, copied into each standalone exercise.
import type {Citation} from '../shared/types';

export interface ForgeHooks {
  answer(question: string, citations: Citation[]): Promise<string>;
  turn<T>(question: string, work: () => Promise<T>): Promise<T>;
  tool<T>(name: string, input: unknown, work: () => T): T;
  shutdown(): Promise<void>;
}

let hooks: ForgeHooks | undefined;
export function setForgeHooks(value?: ForgeHooks) { hooks = value; }
export function forgeEnabled() { return hooks !== undefined; }
export function forgeAnswer(question: string, citations: Citation[], mock: () => string) {
  return hooks ? hooks.answer(question, citations) : Promise.resolve(mock());
}
export function forgeTurn<T>(question: string, work: () => Promise<T>) {
  return hooks ? hooks.turn(question, work) : work();
}
export function forgeTool<T>(name: string, input: unknown, work: () => T): T {
  return hooks ? hooks.tool(name, input, work) : work();
}

export async function initializeForgeHooks(appVariant: string) {
  if (!process.env.FORGE_APP_MODE || process.env.FORGE_APP_MODE === 'offline') return;
  if (process.env.FORGE_APP_MODE !== 'live') throw new Error('Unknown FORGE_APP_MODE');
  const adapter = process.env.FORGE_APP_ADAPTER;
  if (!adapter?.startsWith('file:///')) throw new Error('Live mode requires a file URL in FORGE_APP_ADAPTER');
  // Preserve native ESM import when the course compiles this file to CommonJS.
  const load = new Function('specifier', 'return import(specifier)') as
    (specifier: string) => Promise<{createAppHooks: (variant: string) => Promise<ForgeHooks>}>;
  setForgeHooks(await (await load(adapter)).createAppHooks(appVariant));
}
export async function shutdownForgeHooks() { await hooks?.shutdown(); }
