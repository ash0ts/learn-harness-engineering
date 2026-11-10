import {mkdtemp, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, dirname} from 'node:path';
import {createRequire} from 'node:module';
import {createAgentSession, DefaultResourceLoader, ModelRuntime, SessionManager, SettingsManager, type ToolDefinition, type ExtensionFactory} from '@earendil-works/pi-coding-agent';
import {init, createOtelExtension, flushOTel, flush} from 'weave';
import type {Tracer} from '@opentelemetry/api';
import {type Config, requireLive} from './config.js';
import {deadline} from './lifecycle.js';

export interface RequestUsage {request:number;payloadBytes:number;inputTokens:number;outputTokens:number;complete:boolean}

export interface AgentRequest {
  prompt: string;
  role: string;
  attributes: Record<string, string | number>;
  tools: ToolDefinition[];
  signal?: AbortSignal;
  /** Persist/reserve before dispatch. Rejection prevents the external request. */
  beforeRequest?: (request:number,payloadBytes:number)=>Promise<void>;
  /** Awaited before the next request, including failed model responses. */
  afterRequest?: (usage:RequestUsage)=>Promise<void>;
  finalInstruction?: string;
}

export async function runPi(c: Config, request: AgentRequest) {
  requireLive(c);
  const directory = await mkdtemp(join(tmpdir(), 'forge-pi-'));
  try {
  await init(`${c.entity}/${c.project}`);
  // Weave 0.16.11 exposes metadata injection only through the extension's tracer.
  const require = createRequire(import.meta.url);
  const {getWeaveTracer,getWeaveTracerProvider,clearWeaveTracerProvider} = require(join(dirname(require.resolve('weave')), 'genai/provider.js')) as {getWeaveTracer: (name: string) => Tracer;getWeaveTracerProvider:()=>{shutdown:()=>Promise<void>}|null;clearWeaveTracerProvider:()=>void};
  const base = getWeaveTracer('harness-course');
  const tracer = new Proxy(base, {get(target, property) {
    if (property === 'startSpan') return (name: string, options: Parameters<Tracer['startSpan']>[1], context: Parameters<Tracer['startSpan']>[2]) =>
      target.startSpan(name, {...options, attributes: {...options?.attributes, ...request.attributes, 'course.role': request.role}}, context);
    const value = Reflect.get(target, property);
    return typeof value === 'function' ? value.bind(target) : value;
  }});
  const runtime = await ModelRuntime.create({authPath: join(directory, 'auth.json'), modelsPath: null, allowModelNetwork: false});
  runtime.registerProvider('forge', {
    baseUrl: c.inferenceUrl, apiKey: c.apiKey, api: 'openai-completions',
    headers: {'OpenAI-Project': `${c.entity}/${c.project}`},
    models: [{id: c.model, name: c.model, reasoning: false, input: ['text'], contextWindow: 262144, maxTokens: c.maxOutputTokens,
      cost: {input: 0.25, output: 1.25, cacheRead: 0.25, cacheWrite: 0.25}}],
  });
  const model = runtime.getModel('forge', c.model);
  if (!model) throw new Error(`Forge model unavailable: ${c.model}`);
  const settingsManager = SettingsManager.inMemory({compaction: {enabled: false}, retry: {enabled: false}, cacheWarming: 'off'});
  const loader = new DefaultResourceLoader({cwd: directory, agentDir: directory, settingsManager,
    noExtensions: true, noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true,
    extensionFactories: [createOtelExtension({tracer, captureContent: true}) as ExtensionFactory],
    systemPrompt: `You are the ${request.role} in a harness engineering exercise. All commands run in /workspace/task inside the sandbox. Use relative task paths there, and keep command output concise. Work only through the provided sandbox tools. Read AGENTS.md when present. Verify changes before claiming success. Never request secrets or access reference solutions.`,
  });
  await loader.reload();
  const {session, modelFallbackMessage} = await createAgentSession({cwd: '/workspace/task', agentDir: directory, modelRuntime: runtime, model,
    settingsManager, resourceLoader: loader, sessionManager: SessionManager.inMemory('/workspace/task'),
    noTools: 'builtin', tools: request.tools.map(t => t.name), customTools: request.tools, thinkingLevel: 'off'});
  if (modelFallbackMessage) { session.dispose(); throw new Error(modelFallbackMessage); }
  // Enforce limits at the provider boundary. Extension errors are swallowed by Pi,
  // so an extension callback alone cannot enforce a billing reservation.
  const stream = session.agent.streamFunction;
  let requests = 0;
  let settlement:Promise<void>=Promise.resolve();
  session.agent.streamFunction = async (model, context, options) => {
    await settlement;
    if (requests >= c.maxTurns) throw new Error('Model-call budget exhausted');
    if (Buffer.byteLength(JSON.stringify(context), 'utf8') > c.maxInputBytes - 8192) {
      throw new Error('Frozen input byte budget exceeded');
    }
    const finalContext=request.finalInstruction&&requests===c.maxTurns-1?
      {...context,tools:[],messages:[...context.messages,{role:'user' as const,content:request.finalInstruction,timestamp:Date.now()}]}:context;
    let dispatched=0,payloadBytes=0;
    const response=await stream(model, finalContext, {...options, temperature: 0, maxTokens: c.maxOutputTokens, maxRetries: 0,
      onPayload: async payload => {
        const changed = await options?.onPayload?.(payload, model);
        const final = changed ?? payload;
        payloadBytes=Buffer.byteLength(JSON.stringify(final),'utf8');
        if (payloadBytes > c.maxInputBytes) throw new Error('Frozen provider payload byte budget exceeded');
        await request.beforeRequest?.(requests+1,payloadBytes);
        requests++; // Only requests that pass the local gate can incur inference cost.
        dispatched=requests;
        return final;
      },
    });
    settlement=response.result().then(async message=>{
      if(!dispatched)return;
      const inputTokens=message.usage.input+message.usage.cacheRead+message.usage.cacheWrite,outputTokens=message.usage.output;
      await request.afterRequest?.({request:dispatched,payloadBytes,inputTokens,outputTokens,complete:inputTokens+outputTokens>0});
    });
    // Keep the rejection observed while Pi consumes the stream. It is rethrown
    // at the next request or final settlement, never swallowed by an extension.
    void settlement.catch(()=>{});
    return response;
  };
  let turns = 0;
  session.subscribe(event => {
    if (event.type === 'turn_end') turns++;
  });
  const abort = () => { void session.abort(); };
  request.signal?.addEventListener('abort', abort, {once: true});
  try {
    request.signal?.throwIfAborted();
    await session.bindExtensions({});
    await session.prompt(request.prompt);
    await settlement;
    const stats = session.getSessionStats();
    const errors = session.messages.filter(m => m.role === 'assistant' && (m.stopReason === 'error' || m.stopReason === 'aborted'));
    const text = session.messages.filter(m => m.role === 'assistant').flatMap(m => m.content.filter(p => p.type === 'text').map(p => p.text)).join('\n');
    const assistantMessages = session.messages.filter(m => m.role === 'assistant');
    const telemetryComplete = assistantMessages.filter(m => m.usage.input + m.usage.output + m.usage.cacheRead + m.usage.cacheWrite > 0).length === requests;
    return {conversationId: session.sessionId, telemetryComplete, requests, inputTokens: stats.tokens.input + stats.tokens.cacheRead + stats.tokens.cacheWrite,
      outputTokens: stats.tokens.output, turns, text, finalText:assistantMessages.at(-1)?.content.filter(p=>p.type==='text').map(p=>p.text).join('\n')??'', completed: errors.length === 0 && !request.signal?.aborted,
      errors: errors.map(m => m.role === 'assistant' ? m.errorMessage : undefined)};
  } finally {
    request.signal?.removeEventListener('abort', abort);
    session.dispose();
    const cleanup=await Promise.allSettled([
      deadline(settlement,30000,'request settlement'),
      deadline(flushOTel(),30000,'Pi trace flush'),
      deadline(flush(),30000,'Pi Weave flush'),
    ]);
    const provider=getWeaveTracerProvider();
    if(provider)cleanup.push(...await Promise.allSettled([deadline(provider.shutdown(),30000,'Pi trace shutdown')]));
    clearWeaveTracerProvider();
    const failures=cleanup.filter((r):r is PromiseRejectedResult=>r.status==='rejected');
    if(failures.length)throw new AggregateError(failures.map(r=>r.reason),'Pi finalization failed');
  }
  } finally {
    await rm(directory, {recursive: true, force: true});
  }
}
