import {mkdir, writeFile, rename} from 'node:fs/promises';
import {dirname} from 'node:path';
import {randomUUID} from 'node:crypto';

export type Outcome = 'passed' | 'task_failed' | 'infrastructure_failed' | 'telemetry_missing' | 'budget_exhausted' | 'awaiting_approval';
export interface TrialRecord {
  schemaVersion: 1;
  id: string;
  project: string;
  variant: string;
  trial: number;
  sourceCommit: string;
  model: string;
  startedAt: string;
  finishedAt?: string;
  outcome: Outcome;
  sandboxId?: string;
  conversationIds: string[];
  wandbRunId?: string;
  inputTokens: number | null;
  outputTokens: number | null;
  estimatedCostUsd: number | null;
  evidence: string[];
  error?: string;
}

export async function writeJson(file: string, data: unknown) {
  await mkdir(dirname(file), {recursive: true});
  const temporary = `${file}.${randomUUID()}.tmp`;
  await writeFile(temporary, JSON.stringify(data, null, 2) + '\n', {mode: 0o600});
  await rename(temporary, file);
}

export function redact(value: string, secrets: string[] = []) {
  let text = value.replace(/(?:Bearer|Basic)\s+[A-Za-z0-9+/=_-]+/gi, '[redacted authorization]');
  for (const secret of secrets.filter(Boolean)) text = text.split(secret).join('[redacted]');
  return text;
}
