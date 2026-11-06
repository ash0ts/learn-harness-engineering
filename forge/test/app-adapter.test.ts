import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createAppHooks} from '../src/app.js';

test('malformed inference, missing usage and tracing outages surface explicit failures',async()=>{
  const originalFetch=globalThis.fetch;
  const keys=['WANDB_API_KEY','WANDB_ENTITY','WANDB_PROJECT','WF_TRACE_SERVER_URL','FORGE_APP_EVIDENCE'];
  const saved=Object.fromEntries(keys.map(k=>[k,process.env[k]]));
  Object.assign(process.env,{WANDB_API_KEY:'offline-test-key',WANDB_ENTITY:'offline-tests',WANDB_PROJECT:'adapter-failures',WF_TRACE_SERVER_URL:'http://127.0.0.1:9'});
  delete process.env.FORGE_APP_EVIDENCE;
  try {
    for(const missingUsage of [false,true]) {
      // No provider request is sent: only the OpenAI response boundary is faked.
      globalThis.fetch=async()=>new Response(JSON.stringify({id:'fixture',created:0,model:'fixture',object:'chat.completion',choices:[{index:0,finish_reason:missingUsage?'stop':'length',message:{role:'assistant',content:missingUsage?'fixture':'partial'}}],...(missingUsage?{}:{usage:{prompt_tokens:4,completion_tokens:2,total_tokens:6}})}),{status:200,headers:{'Content-Type':'application/json'}});
      const hooks=await createAppHooks('offline-adapter-test');
      try {
        await assert.rejects(hooks.turn('fixture',()=>hooks.answer('fixture',[])),missingUsage?/telemetry_missing/:/Malformed or incomplete/);
      }finally {
        // A failed trace export must not silently turn the run into a success.
        await assert.rejects(hooks.shutdown());
      }
    }
  }finally {
    globalThis.fetch=originalFetch;
    for(const key of keys)if(saved[key]===undefined)delete process.env[key];else process.env[key]=saved[key];
  }
});
