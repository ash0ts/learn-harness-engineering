export interface Config {
  entity: string;
  project: string;
  model: string;
  inferenceUrl: string;
  apiKey?: string;
  budgetUsd: number;
  maxTurns: number;
  maxOutputTokens: number;
  maxInputBytes: number;
}

export function config(env: NodeJS.ProcessEnv = process.env): Config {
  const budgetUsd = env.FORGE_BUDGET_USD === 'unlimited' ? Infinity : Number(env.FORGE_BUDGET_USD ?? 50);
  if (env.FORGE_BUDGET_USD !== 'unlimited' && (!Number.isFinite(budgetUsd) || budgetUsd <= 0 || budgetUsd > 50)) {
    throw new Error('FORGE_BUDGET_USD must be positive and at most $50, or explicitly unlimited');
  }
  return {
    entity: env.WANDB_ENTITY ?? '',
    project: env.WANDB_PROJECT ?? 'learn-harness-engineering-forge',
    model: env.FORGE_MODEL ?? 'Qwen/Qwen3.6-35B-A3B',
    inferenceUrl: env.FORGE_INFERENCE_URL ?? 'https://api.inference.wandb.ai/v1',
    apiKey: env.WANDB_API_KEY, budgetUsd, maxTurns: 24, maxOutputTokens: 4096, maxInputBytes: 524288,
  };
}

export function requireLive(c: Config): asserts c is Config & {apiKey: string} {
  if (!c.entity || !c.apiKey) throw new Error('Live mode requires WANDB_ENTITY and WANDB_API_KEY');
  if (new URL(c.inferenceUrl).protocol !== 'https:') throw new Error('Live inference requires HTTPS');
}

/** Check the destination before reserving or launching paid work. */
export async function requirePrivateProject(c:Config,request:typeof fetch=fetch) {
  requireLive(c);
  const response=await request('https://api.wandb.ai/graphql',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Basic '+Buffer.from('api:'+c.apiKey).toString('base64')},
    body:JSON.stringify({query:'query($e:String!,$p:String!){project(entityName:$e,name:$p){access}}',variables:{e:c.entity,p:c.project}}),signal:AbortSignal.timeout(30000)});
  if(!response.ok)throw new Error(`Private project preflight HTTP ${response.status}`);
  const body=await response.json() as {errors?:unknown;data?:{project?:{access:string}|null}};
  if(body.errors||body.data?.project?.access!=='PRIVATE')throw new Error('Paid work requires an accessible PRIVATE W&B project');
}

export function publicConfig(c: Config) {
  const {apiKey: _, ...safe} = c;
  return {...safe, budgetUsd:Number.isFinite(c.budgetUsd)?c.budgetUsd:'unlimited'};
}
