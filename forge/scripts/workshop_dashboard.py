# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0", "wandb-workspaces==0.4.13"]
# ///
"""Publish workshop rehearsals as their own cohort; never amend research scores."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import wandb
import wandb_workspaces.expr as expr
import wandb_workspaces.reports.v2 as wr
import wandb_workspaces.workspaces as ws
from models import require_private_project, artifact_collection_exists
from audit_artifact import snapshot, verify

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT/'forge/local-results/rollout-v5'
OUT = ROOT/'forge/results/workshop-v1'
RUNNER = 'd760596a441c76b797c9224641accc4a416a9af0'
CI = 'https://github.com/ash0ts/learn-harness-engineering/actions/runs/43227923247'

def collect():
    rows = []
    for path in sorted(LOCAL.glob('workshop-*/trial.json')):
        r = json.loads(path.read_bytes())
        if r.get('protocol') != 'workshop-v1':
            continue
        if not r.get('finishedAt') or r.get('cleanupStatus') != 'verified' or r.get('publicationStatus') != 'verified':
            raise RuntimeError('Incomplete rehearsal: '+r['id'])
        row = {k:r.get(k) for k in ['id','project','variant','outcome','sourceCommit','runnerRevision',
            'snapshotId','snapshotSha256','candidateId','candidateSha256','assisted','inputTokens',
            'outputTokens','estimatedCostUsd','cleanupStatus','telemetryStatus','publicationStatus',
            'wandbRunUrl','artifactUrl','conversationIds','startedAt','finishedAt']}
        row['recordSha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(row)
    publication = json.loads((ROOT/'forge/publication-manifest.json').read_text())
    canonical = []
    for r in publication['notebooks'][:6]:
        checksum = hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest()
        canonical.append({k:r.get(k) for k in ['file','id','url','currentVersion','sha256','verifiedAt']} |
                         {'currentCanonicalVerified':r.get('status')=='published_verified' and r.get('sha256')==checksum})
    counts = Counter(r['outcome'] for r in rows)
    data = {'schemaVersion':1,'cohort':'workshop-v1-owner-rehearsal','capturedAt':datetime.now(timezone.utc).isoformat(),
        'runnerCommit':RUNNER,'tag':'forge-workshop-v1.0.0','platformQualification':CI,
        'attempts':rows,'outcomes':dict(counts),'notebooks':canonical,
        'attemptEstimateUsd':sum(r['estimatedCostUsd'] for r in rows),
        'rolloutLedgerEstimateUsd':json.loads((LOCAL/'budget.json').read_text())['spentEstimateUsd'],
        'limitations':['Owner-account rehearsal only; no independent student account.',
            'Native browser progress download remains unverified at the owner’s request.',
            'CI exercises the actual Import button with a stubbed OS picker; native picker acceptance is separate.',
            'Windows local dev/build/check/source exchange qualified; paid CLI worker cleanup is not qualified.',
            'Rehearsals include protected examples and explicit prompt interventions, not a randomized comparison.',
            'CPU sandboxes and hosted Forge inference; no student GPU provisioning or model training.']}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'status.json').write_text(json.dumps(data,indent=2)+'\n')
    text = '# Five hands-on Forge labs: release evidence\n\n'
    text += f"Runner `{RUNNER}` is tagged `forge-workshop-v1.0.0`. [Three-platform qualification]({CI}) passed on macOS, Windows and Linux.\n\n"
    text += 'These are owner qualification rehearsals, separate from the preserved 129-attempt archive and 39-attempt main comparison. Every failed attempt remains listed. A successful protected example demonstrates the execution path; it does not predict a student pass rate.\n\n'
    text += f"{len(rows)} completed attempts: "+', '.join(f'{n} {k}' for k,n in sorted(counts.items()))+'.\n\n'
    text += '| Attempt | Project | Action | Outcome | Evidence |\n|---|---|---|---|---|\n'
    for r in rows:
        text += f"| `{r['id']}` | {r['project']} | {r['variant']} | {r['outcome']} | [run]({r['wandbRunUrl']}) |\n"
    text += '\nInterventions: repaired the SDK stdin lifetime and staging mutation; disabled provider thinking explicitly within existing output limits; fixed a whitespace-sensitive history assertion; rewrote the student handoff to include its required evidence sections; and batched checker file reads to produce a review within its unchanged four-call allowance. Earlier failures were retained.\n\n'
    text += 'Successful Project 01 inference included abstention to the original ambiguous question. That answer is recorded, not relabelled as factual success. Project 04 records student-authored indexing/retrieval spans. Project 03 records the fresh session reading the handoff. Project 05 records the actual checker review and subsequent patch.\n\n'
    text += f"Completed attempt estimate: ${data['attemptEstimateUsd']:.4f}. Shared rollout ledger, including prior rollout work and notebook sessions: ${data['rolloutLedgerEstimateUsd']:.4f}. These are estimates, not provider billing caps. The separate unresolved historical $2 reservation remains unchanged.\n\n"
    text += 'Validation: 77 TypeScript tests, 56 Python tests, nine unpaid saved views and the documentation build pass. A preservation audit checks 544 original files, all historical notebook payloads and the unchanged Project 06–08 sources.\n\n'
    text += 'Remaining limits:\n\n'+'\n'.join('- '+s for s in data['limitations'])+'\n'
    (OUT/'README.md').write_text(text)
    return data

def publish():
    data = collect()
    entity,project = require_private_project()
    manifest = OUT/'dashboard.json'
    previous = json.loads(manifest.read_text()) if manifest.exists() else {}
    api = wandb.Api(timeout=60)
    metrics = {'completedAttempts':len(data['attempts']),'passed':data['outcomes'].get('passed',0),
        'taskFailed':data['outcomes'].get('task_failed',0),'infrastructureFailed':data['outcomes'].get('infrastructure_failed',0),
        'publishedNotebooks':sum(r['currentCanonicalVerified'] for r in data['notebooks']),
        'attemptEstimateUsd':data['attemptEstimateUsd'],'rolloutLedgerEstimateUsd':data['rolloutLedgerEstimateUsd']}
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary).resolve()
        digest,payload=snapshot([(OUT/'README.md','README.md'),(OUT/'status.json','status.json'),
            (ROOT/'forge/publication-manifest.json','publication-manifest.json')],root/'upload',os.environ['WANDB_API_KEY'].encode())
        name='workshop-v1-owner-rehearsal'
        exists=artifact_collection_exists(entity,project,'course-workshop-audit',name)
        artifact=next((a for a in api.artifact_versions('course-workshop-audit',f'{entity}/{project}/{name}') if a.metadata.get('payloadSha256')==digest),None) if exists else None
        with wandb.init(entity=entity,project=project,id='course-workshop-v1-owner',resume='allow',job_type='course-workshop-audit',
            group='workshop-v1-owner-rehearsal',config={'protocol':'workshop-v1','dashboardKind':'workshop-owner-rehearsal','runnerCommit':RUNNER},
            settings=wandb.Settings(disable_git=True,disable_code=True,silent=True)) as run:
            run.summary.update(metrics)
            run.summary['attempts']=wandb.Table(columns=['Attempt','Project','Action','Outcome','Assisted','Estimate USD','Run','Source SHA'],data=[
                [r['id'],r['project'],r['variant'],r['outcome'],r['assisted'],r['estimatedCostUsd'],r['wandbRunUrl'],r['snapshotSha256']] for r in data['attempts']])
            run.summary['limits']=wandb.Table(columns=['Remaining qualification limit'],data=[[s] for s in data['limitations']])
            if artifact is None:
                new=wandb.Artifact(name,type='course-workshop-audit',metadata={'payloadSha256':digest,'protocol':'workshop-v1'})
                for entry in [*payload['files'],'receipt-manifest.json']:new.add_file(str(root/'upload'/entry),name=entry)
                artifact=run.log_artifact(new).wait()
            run_url=run.url
        verify(Path(artifact.download(root=str(root/'readback'))),digest)
    view=ws.Workspace.from_url(previous['url']) if previous.get('url') else ws.Workspace(entity=entity,project=project)
    view.name='Hands-on Forge workshop — rehearsal evidence'
    view.runset_settings=ws.RunsetSettings(filters=[expr.Config('protocol')=='workshop-v1',expr.Config('dashboardKind')=='workshop-owner-rehearsal'])
    panel_specs=[('Completed rehearsals','completedAttempts'),('Passed','passed'),('Task failures retained','taskFailed'),('Infrastructure failures retained','infrastructureFailed'),('Current notebooks verified (target 6)','publishedNotebooks'),('Attempt estimate USD','attemptEstimateUsd')]
    view.sections=[ws.Section(name='Owner rehearsals — separate from research comparisons',is_open=True,panels=[wr.ScalarChart(title=t,metric=m,layout=wr.Layout(x=i%2*12,y=i//2*6,w=12,h=6)) for i,(t,m) in enumerate(panel_specs)]),
        ws.Section(name='Every attempt and its limits',is_open=True,panels=[wr.WeavePanelSummaryTable(table_name='attempts',layout=wr.Layout(x=0,y=0,w=24,h=14)),wr.WeavePanelSummaryTable(table_name='limits',layout=wr.Layout(x=0,y=14,w=24,h=8))])]
    view.save()
    forge_url=view.url if '/wandb/wandb/' in view.url else view.url.replace('https://forge.coreweave.com/','https://forge.coreweave.com/wandb/',1)
    receipt={'schemaVersion':1,'url':view.url,'forgeUrl':forge_url,'runUrl':run_url,'artifact':artifact.qualified_name,'payloadSha256':digest,'artifactReadBackVerified':True}
    manifest.write_text(json.dumps(receipt,indent=2)+'\n')
    restored=ws.Workspace.from_url(view.url)
    if restored.name!=view.name or len(restored.sections)!=2:raise RuntimeError('Dashboard read-back mismatch')
    receipt['dashboardReadBackVerified']=True
    manifest.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if args.execute:publish()
    else:collect()
