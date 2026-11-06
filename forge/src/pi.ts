import {mkdtemp, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, dirname} from 'node:path';
import {createRequire} from 'node:module';
import {createAgentSession, DefaultResourceLoader, ModelRuntime, SessionManager, SettingsManager, type ToolDefinition, type ExtensionFactory} from '@earendil-works/pi-coding-agent';
import {init, createOtelExtension, flushOTel} from 'weave';
import type {Tracer} from '@opentelemetry/api';
import {type Config, requireLive} from './config.js';

export interface AgentRequest {
  prompt: string;
  role: string;
  attributes: Record<string, string | number>;
  tools: ToolDefinition[];
  signal?: AbortSignal;
}

export async function runPi(c: Config, request: AgentRequest) {
  requireLive(c);
  const directory = await mkdtemp(join(tmpdir(), 'forge-pi-'));
  await init(`${c.entity}/${c.project}`);
  // Weave 0.16.11 exposes metadata injection only through the extension's tracer.
  const require = createRequire(import.meta.url);
  const {getWeaveTracer} = require(join(dirname(require.resolve('weave')), 'genai/provider.js')) as {getWeaveTracer: (name: string) => Tracer};
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
    models: [{id: c.model, name: c.model, reasoning: false, input: ['text'], contextWindow: 32768, maxTokens: c.maxOutputTokens,
      cost: {input: 0.25, output: 1.25, cacheRead: 0.25, cacheWrite: 0.25}}],
  });
  const model = runtime.getModel('forge', c.model);
  if (!model) throw new Error(`Forge model unavailable: ${c.model}`);
  const settingsManager = SettingsManager.inMemory({compaction: {enabled: false}, retry: {enabled: false}});
  const loader = new DefaultResourceLoader({cwd: directory, agentDir: directory, settingsManager,
    noExtensions: true, noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true,
    extensionFactories: [createOtelExtension({tracer, captureContent: true}) as ExtensionFactory],
    systemPrompt: `You are the ${request.role} in a harness engineering exercise. Work only through the provided sandbox tools. Read AGENTS.md when present. Verify changes before claiming success. Never request secrets or access reference solutions.`,
  });
  await loader.reload();
  const {session, modelFallbackMessage} = await createAgentSession({cwd: directory, agentDir: directory, modelRuntime: runtime, model,
    settingsManager, resourceLoader: loader, sessionManager: SessionManager.inMemory(directory),
    noTools: 'builtin', tools: request.tools.map(t => t.name), customTools: request.tools, thinkingLevel: 'off'});
  if (modelFallbackMessage) throw new Error(modelFallbackMessage);
  let turns = 0;
  let exhausted = false;
  session.subscribe(event => {
    if (event.type === 'turn_end' && ++turns >= c.maxTurns) { exhausted = true; void session.abort(); }
  });
  const abort = () => { void session.abort(); };
  request.signal?.addEventListener('abort', abort, {once: true});
  try {
    request.signal?.throwIfAborted();
    await session.bindExtensions({});
    await session.prompt(request.prompt);
    const stats = session.getSessionStats();
    const errors = session.messages.filter(m => m.role === 'assistant' && (m.stopReason === 'error' || m.stopReason === 'aborted'));
    const text = session.messages.filter(m => m.role === 'assistant').flatMap(m => m.content.filter(p => p.type === 'text').map(p => p.text)).join('\n');
    return {conversationId: session.sessionId, inputTokens: stats.tokens.input + stats.tokens.cacheRead + stats.tokens.cacheWrite,
      outputTokens: stats.tokens.output, turns, text, completed: !exhausted && errors.length === 0 && !request.signal?.aborted,
      errors: errors.map(m => m.role === 'assistant' ? m.errorMessage : undefined)};
  } finally {
    request.signal?.removeEventListener('abort', abort);
    session.dispose();
    await flushOTel();
    await rm(directory, {recursive: true, force: true});
  }
}
