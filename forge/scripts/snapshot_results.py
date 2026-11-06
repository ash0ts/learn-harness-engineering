"""Freeze completed evidence for notebook analysis; never count in-flight trial records."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LOCAL=ROOT/'forge/local-results'

def read(path): return json.loads(path.read_text())
def protocol_hash(value): return hashlib.sha256(json.dumps(value,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def build():
    ledger=read(LOCAL/'budget.json')
    audits={r['id']:r['estimatedUsd'] for r in ledger.get('reconciliations',[])}
    uncertain={r['id']:r['reservedEstimateUsd'] for r in ledger.get('uncertainEstimates',[])}
    trials=[]
    for path in sorted(LOCAL.glob('*/trial.json')):
        r=read(path)
        if not r.get('finishedAt'): continue
        keys=['id','project','variant','trial','sourceCommit','outcome','inputTokens','outputTokens','estimatedCostUsd','conversationIds','wandbRunUrl','artifactUrl','startedAt','finishedAt','actorCompleted','error']
        row={key:r.get(key) for key in keys}
        row.update(protocolSha256=protocol_hash(r['protocol']) if r.get('protocol') else None,
                   grade=r.get('grade'),reconciledEstimateUsd=audits.get(r['id'],r.get('estimatedCostUsd')),
                   chargedUnknownReservationUsd=uncertain.get(r['id']))
        trials.append(row)
    qualifications=[]
    for path in sorted(LOCAL.glob('qualification-*/qualification.json')):
        r=read(path)
        if not r.get('finishedAt'): continue
        keys=['id','passed','sourceCommit','protocolSha256','startedAt','finishedAt','inputTokens','outputTokens','estimatedCostUsd','error']
        row={key:r.get(key) for key in keys}
        row.update(reconciledEstimateUsd=audits.get(r['id'],r.get('estimatedCostUsd')),chargedUnknownReservationUsd=uncertain.get(r['id']),agentConversationId=r.get('agent',{}).get('conversationId'),appConversationId=r.get('app',{}).get('conversationId'))
        qualifications.append(row)
    blocks=[]
    for path in sorted(LOCAL.glob('report-*.json')):
        report=read(path)
        for block in report['blocks']:
            if block['project'] not in [f'project-0{i}' for i in range(1,7)]: continue
            expected=set(read(ROOT/'forge/tasks'/f"{block['project']}.json")['variants'])
            rows=[r for r in report['completed'] if r['project']==block['project'] and r['trial']==block['repeat']]
            if set(r['variant'] for r in rows)!=expected: continue
            blocks.append({'campaignId':report['campaignId'],'project':block['project'],'repeat':block['repeat'],'sourceCommit':report['sourceCommit'],'protocolSha256':report['protocolSha256'],'trialIds':[r['id'] for r in rows],'outcomes':dict(Counter(r['outcome'] for r in rows))})
    loops=[dict(file=p.name,**read(p)) for p in sorted(LOCAL.glob('project-07-*.json'))]
    graphs=[dict(file=p.name,**read(p)) for p in sorted(LOCAL.glob('project-08-*.json'))]
    concurrency=[read(p) for p in sorted(LOCAL.glob('concurrency-*/concurrency.json'))]
    sandboxes=[read(p) for p in sorted(LOCAL.glob('sandbox-qualification-*/sandbox-qualification.json'))]
    status=f"Recorded {len(trials)} completed coding attempts and {len(blocks)} complete comparison blocks. Outcomes include unsuccessful attempts; no human time savings are inferred."
    snapshot={'schemaVersion':1,'capturedAt':datetime.now(timezone.utc).isoformat(),'status':status,'trials':trials,'qualifications':qualifications,'concurrencyQualifications':concurrency,'sandboxQualifications':sandboxes,'completedComparisonBlocks':blocks,'loops':loops,'graphs':graphs,'budget':ledger,'costScope':'Budget snapshot as of capturedAt. Final publication/editor costs are recorded separately in the delivery report and W&B audit artifact.'}
    (ROOT/'forge/results/snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
    print(status)
    return snapshot

if __name__=='__main__': build()
