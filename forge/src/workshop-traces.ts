import {readFile,readdir} from 'node:fs/promises';
import {join} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';
import type {Config} from './config.js';
import type {WorkshopResult} from './workshop-contract.js';
import {writeJson,redact} from './records.js';

export function inspectWorkshopSpans(spans:any[],expected:{conversationId:string;sourceCommit:string;inputTokens:number;outputTokens:number;studentTools?:boolean}){
  const errors:string[]=[],byId=new Map(spans.map(s=>[s.span_id,s]));
  if(!spans.length)errors.push('Conversation has not appeared in Agent Lens');
  if(byId.size!==spans.length)errors.push('Duplicate spans');
  const models=spans.filter(s=>s.operation_name==='chat');
  const input=models.reduce((n,s)=>n+(s.input_tokens??0)+(s.cache_read_input_tokens??0)+(s.cache_creation_input_tokens??0),0);
  const output=models.reduce((n,s)=>n+(s.output_tokens??0),0);
  if(input!==expected.inputTokens||output!==expected.outputTokens)errors.push('Model span usage differs from request receipts');
  const names:string[]=[];
  for(const s of spans){
    if(s.conversation_id!==expected.conversationId)errors.push('Conversation contamination');
    if(s.parent_span_id&&byId.get(s.parent_span_id)?.trace_id!==s.trace_id)errors.push('Missing or cross-trace parent');
    const raw=typeof s.raw_span_dump==='string'?JSON.parse(s.raw_span_dump):s.raw_span_dump;
    names.push(raw?.attributes?.gen_ai?.tool?.name??'');
    if(raw?.attributes?.course?.source_commit!==expected.sourceCommit)errors.push('Source revision mismatch');
  }
  if(expected.studentTools)for(const name of ['student.indexing.start','student.retrieval.chunks','student.retrieval.ranked'])if(!names.includes(name))errors.push('Missing student-authored span: '+name);
  return {verified:!errors.length,errors:[...new Set(errors)],spanCount:spans.length,modelCalls:models.length,inputTokens:input,outputTokens:output,toolNames:names.filter(Boolean)};
}

/** Read only, after sandbox cleanup. Trace failures never repeat agent work. */
export async function verifyWorkshopTraces(dir:string,record:WorkshopResult,c:Config){
  const expected:Array<{conversationId:string;sourceCommit:string;inputTokens:number;outputTokens:number;studentTools?:boolean}>=[];
  for(const name of await readdir(join(dir,'actor')).catch(()=>[]))if(/^phase-\d+\.json$/.test(name)){
    const phase=JSON.parse(await readFile(join(dir,'actor',name),'utf8'));
    expected.push({conversationId:phase.conversationId,sourceCommit:record.sourceCommit,inputTokens:phase.inputTokens,outputTokens:phase.outputTokens});
  }
  try{
    const app=JSON.parse(await readFile(join(dir,'grader/app-evidence/app.json'),'utf8'));
    expected.push({conversationId:app.conversationId,sourceCommit:record.sourceCommit,...app.usage,studentTools:record.project==='project-04'});
  }catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
  const conversations=[];
  for(const entry of expected){
    let result:any;
    for(let attempt=0;attempt<3;attempt++){
      try{
        const response=await fetch('https://trace.wandb.ai/agents/spans/query',{method:'POST',signal:AbortSignal.timeout(15000),headers:{'Content-Type':'application/json',Authorization:'Basic '+Buffer.from('api:'+c.apiKey).toString('base64')},body:JSON.stringify({project_id:c.entity+'/'+c.project,query:{$expr:{$eq:[{$getField:'conversation_id'},{$literal:entry.conversationId}]}},include_details:true,limit:1000})});
        if(!response.ok)throw new Error('Agent Lens read-back HTTP '+response.status);
        const payload:any=await response.json();
        if((payload.total_count??0)>1000)throw new Error('Conversation needs pagination');
        result={conversationId:entry.conversationId,...inspectWorkshopSpans(payload.spans??[],entry)};
        await writeJson(join(dir,'trace-'+entry.conversationId+'.json'),payload);
        if(result.verified)break;
      }catch(error){result={conversationId:entry.conversationId,verified:false,errors:[redact(String(error),[c.apiKey??''])]};}
      if(attempt<2)await delay(2500);
    }
    conversations.push(result);
  }
  const result={verified:conversations.every(c=>c.verified),conversations,verifiedAt:new Date().toISOString()};
  await writeJson(join(dir,'trace-readback.json'),result);return result;
}
