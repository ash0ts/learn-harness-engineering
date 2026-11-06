"""Read Agent Lens spans back and reconcile model-level usage, excluding turn rollups."""
import base64
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
LOCAL=ROOT/'forge/local-results'

def query(conversation):
    body={'project_id':os.environ['WANDB_ENTITY']+'/'+os.environ.get('WANDB_PROJECT','learn-harness-engineering-forge'),'query':{'$expr':{'$eq':[{'$getField':'conversation_id'},{'$literal':conversation}]}},'include_details':True,'limit':1000}
    request=urllib.request.Request('https://trace.wandb.ai/agents/spans/query',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Authorization':'Basic '+base64.b64encode(('api:'+os.environ['WANDB_API_KEY']).encode()).decode()})
    with urllib.request.urlopen(request,timeout=30) as response:result=json.load(response)
    directory=LOCAL/'trace-readback';directory.mkdir(exist_ok=True)
    (directory/(conversation+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    if result.get('total_count',len(result.get('spans',[])))>1000:raise RuntimeError('Trace audit requires pagination for this conversation')
    return result.get('spans',[])

def audit(entry):
    conversation=entry['conversationId'];spans=query(conversation);by_id={s['span_id']:s for s in spans}
    errors=[]
    if not spans:errors.append('Conversation missing from Agent Lens')
    if len(by_id)!=len(spans):errors.append('Duplicate span IDs')
    chats=[s for s in spans if s['operation_name']=='chat']
    # Pi reports uncached input separately from cache reads/writes. Parent turns
    # also carry rollups, so summing all spans would double-count usage.
    input_tokens=sum((s.get('input_tokens') or 0)+(s.get('cache_read_input_tokens') or 0)+(s.get('cache_creation_input_tokens') or 0) for s in chats)
    output_tokens=sum(s.get('output_tokens') or 0 for s in chats)
    for span in spans:
        if span['conversation_id']!=conversation:errors.append('Cross-conversation contamination')
        parent=span.get('parent_span_id')
        if parent and (parent not in by_id or by_id[parent]['trace_id']!=span['trace_id']):errors.append('Missing or cross-trace parent')
        raw=json.loads(span['raw_span_dump']);attrs=raw.get('attributes',{}).get('course',{})
        if entry.get('sourceCommit') and attrs.get('source_commit')!=entry['sourceCommit']:errors.append('Source metadata mismatch')
        if entry.get('variant') and attrs.get('variant')!=entry['variant']:errors.append('Variant metadata mismatch')
    if entry.get('telemetryComplete',True):
        if (input_tokens,output_tokens)!=(entry['inputTokens'],entry['outputTokens']):errors.append('Model-level usage differs from local evidence')
    counts=Counter(s['operation_name'] for s in spans)
    if entry.get('expectedTurns') is not None and counts['invoke_agent']!=entry['expectedTurns']:errors.append('Unexpected turn count')
    if entry.get('expectedModelCalls') is not None and counts['chat']!=entry['expectedModelCalls']:errors.append('Unexpected model count')
    return {**entry,'spanCount':len(spans),'operations':dict(counts),'readbackInputTokens':input_tokens,'readbackOutputTokens':output_tokens,'verified':not errors,'errors':sorted(set(errors)),'url':'https://forge.coreweave.com/agent-lens/'+os.environ['WANDB_ENTITY']+'/'+os.environ.get('WANDB_PROJECT','learn-harness-engineering-forge')+'/conversations/'+conversation}

def build():
    entries={}
    for path in LOCAL.glob('*/trial.json'):
        record=json.loads(path.read_text())
        if not record.get('finishedAt'):continue
        for phase in path.parent.glob('actor/phase-*.json'):
            item=json.loads(phase.read_text())
            entries[item['conversationId']]={k:item[k] for k in ['conversationId','inputTokens','outputTokens','telemetryComplete']}
            entries[item['conversationId']].update(sourceCommit=record['sourceCommit'],variant=record['variant'],trialId=record['id'],kind='coding-agent')
    for path in LOCAL.glob('qualification-*/qualification.json'):
        record=json.loads(path.read_text())
        if not record.get('passed'):continue
        agent=record['agent'];entries[agent['conversationId']]={k:agent[k] for k in ['conversationId','inputTokens','outputTokens','telemetryComplete']}
        entries[agent['conversationId']].update(sourceCommit=record['sourceCommit'],kind='agent-qualification')
        app=record['app'];entries[app['conversationId']]={'conversationId':app['conversationId'],**{k:app['usage'][k] for k in ['inputTokens','outputTokens']},'sourceCommit':record['sourceCommit'],'kind':'app-qualification','expectedTurns':4,'expectedModelCalls':2}
    for path in LOCAL.glob('concurrency-*/concurrency.json'):
        record=json.loads(path.read_text())
        if not record.get('passed'):continue
        for app in record['sessions']:
            entries[app['conversationId']]={'conversationId':app['conversationId'],**{k:app['usage'][k] for k in ['inputTokens','outputTokens']},'sourceCommit':record['sourceCommit'],'variant':app['attributes']['course.variant'],'kind':'concurrent-app','expectedTurns':2,'expectedModelCalls':2}
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(audit,entries.values()))
    result={'schemaVersion':1,'verifiedAt':datetime.now(timezone.utc).isoformat(),'conversations':results,'verified':all(r['verified'] for r in results),'note':'Usage totals include cache tokens at model spans only; parent-turn rollups are excluded.'}
    (LOCAL/'trace-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'conversations':len(results),'verified':sum(r['verified'] for r in results),'errors':[r for r in results if not r['verified']]},indent=2))
    return result
if __name__=='__main__':build()
