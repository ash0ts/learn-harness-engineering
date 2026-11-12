import {test} from 'node:test';
import assert from 'node:assert/strict';
import {inspectWorkshopSpans} from '../src/workshop-traces.js';
test('trace acceptance requires actual student spans, isolated parents and model-only usage',()=>{
  const expected={conversationId:'session',sourceCommit:'commit',inputTokens:5,outputTokens:2,studentTools:true};
  const span=(id:string,parent:string,operation:string,tool?:string)=>({span_id:id,parent_span_id:parent,trace_id:'trace',conversation_id:'session',operation_name:operation,input_tokens:5,output_tokens:2,raw_span_dump:JSON.stringify({attributes:{course:{source_commit:'commit'},gen_ai:{tool:{name:tool}}}})});
  const spans=[span('turn','','invoke_agent'),span('model','turn','chat'),...['indexing.start','retrieval.chunks','retrieval.ranked'].map((n,i)=>span('tool'+i,'turn','execute_tool','student.'+n))];
  assert.equal(inspectWorkshopSpans(spans,expected).verified,true);
  assert.equal(inspectWorkshopSpans(spans.filter(s=>s.span_id!=='tool0'),expected).verified,false);
  assert.equal(inspectWorkshopSpans(spans.filter(s=>s.span_id!=='turn'),expected).verified,false);
  assert.equal(inspectWorkshopSpans([...spans,spans[1]],expected).verified,false);
});
