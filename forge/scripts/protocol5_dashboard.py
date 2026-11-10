# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0", "wandb-workspaces==0.4.13"]
# ///
"""Publish the separate revision-five audit; no inference or notebook session."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import wandb
import wandb_workspaces.expr as expr
import wandb_workspaces.reports.v2 as wr
import wandb_workspaces.workspaces as ws
from models import require_private_project

ROOT=Path(__file__).resolve().parents[2]
DIRECTORY=ROOT/'forge/results/protocol-v5'
MANIFEST=DIRECTORY/'dashboard.json'

def save(value):
    temporary=MANIFEST.with_suffix('.tmp');temporary.write_text(json.dumps(value,indent=2)+'\n');temporary.replace(MANIFEST)

def publish():
    entity,project=require_private_project();data=json.loads((DIRECTORY/'status.json').read_text())
    content=(DIRECTORY/'status.json').read_bytes();digest=hashlib.sha256(content).hexdigest()
    previous=json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    identifier='course-protocol5-repair-audit'
    metrics={**data['completed'], 'unresolvedReservationsUsd':data['budget']['unresolvedReservationsUsd'],
        'qualificationAttempts':len(data['qualificationAttempts']), 'notebooksPublished':sum(row['candidatePublished'] for row in data['notebooks']),
        'offlineAppsPassed':data['validation']['offlineAppsPassed'], 'localNotebooksRendered':data['validation']['localNotebooksRendered']}
    api=wandb.Api(timeout=60)
    name='protocol5-repair-audit'
    collections=api.artifact_collections(project_name=f'{entity}/{project}',type_name='course-repair-audit')
    collection=next((c for c in collections if c.name==name),None)
    existing=next((a for a in api.artifact_versions('course-repair-audit',f'{entity}/{project}/{name}') if a.metadata.get('sha256')==digest),None) if collection else None
    with wandb.init(entity=entity,project=project,id=identifier,resume='allow',job_type='course-repair-audit',group='protocol-5',
                    config={'protocolRevision':5,'dashboardKind':'repair-audit','candidateRunnerCommit':data['candidateRunnerCommit']},
                    settings=wandb.Settings(disable_git=True,disable_code=True,silent=True)) as run:
        run.summary.update({**metrics,'status':data['status'],'sourceEvidenceSha256':digest,'actualCostKnown':False})
        run.summary['completion'] = wandb.Table(columns=['Exercise','Completed','Target'], data=[[key,metrics[key],target] for key,target in data['targets'].items()])
        if existing is None:
            artifact=wandb.Artifact(name,type='course-repair-audit',metadata={'sha256':digest,'protocolRevision':5})
            artifact.add_file(str(DIRECTORY/'status.json'),name='status.json')
            artifact.add_file(str(DIRECTORY/'README.md'),name='README.md')
            evidence=ROOT/'forge/local-results'
            files=[(evidence/row['path'],'validation/'+Path(row['path']).name) for row in data['validationEvidence']]
            files += [(evidence/'repair-v5/trace-readback.json','qualification/trace-readback.json'),(evidence/'repair-v5/provider-usage.json','qualification/provider-usage.json')]
            for qualification in data['qualificationAttempts']:
                directory=evidence/'protocol-v5'/qualification['id']
                files += [(path,'qualification/'+qualification['id']+'/'+path.relative_to(directory).as_posix()) for path in directory.rglob('*.json')]
            secret=os.environ.get('WANDB_API_KEY','').encode()
            for path,name in files:
                if path.is_symlink() or secret and secret in path.read_bytes():raise RuntimeError('Unsafe evidence or credential in private artifact')
                artifact.add_file(str(path),name=name)
            existing=run.log_artifact(artifact,aliases=['latest']).wait()
        run_url=run.url
    with tempfile.TemporaryDirectory() as temporary:
        remote=Path(existing.get_entry('status.json').download(root=temporary)).read_bytes()
        if hashlib.sha256(remote).hexdigest()!=digest:raise RuntimeError('Audit artifact read-back mismatch')
    view=ws.Workspace.from_url(previous['url']) if previous.get('url') else ws.Workspace(entity=entity,project=project)
    view.name='Forge course — protocol 5 repair and qualification status'
    view.runset_settings=ws.RunsetSettings(filters=[expr.Config('protocolRevision')==5,expr.Config('dashboardKind')=='repair-audit'],pinned_columns=['status','comparisonAttempts','qualificationAttempts'])
    specs=[('Scored P01–06 attempts (target 39)','comparisonAttempts'),('Real two-hour timers (target 3)','realTwoHourTimers'),
        ('Graph executions (target 3)','graphs'),('New human decisions (target 2)','newHumanDecisions'),
        ('Local notebooks rendered','localNotebooksRendered'),('New notebooks published','notebooksPublished'),
        ('Unknown-usage reservation retained (USD)','unresolvedReservationsUsd'),('Qualification attempts, separate from scores','qualificationAttempts')]
    view.sections=[ws.Section(name='Qualification blocked — no treatment ranking or pass rate claimed',is_open=True,
        panels=[wr.ScalarChart(title=title,metric=metric,layout=wr.Layout(x=(i%2)*12,y=(i//2)*6,w=12,h=6)) for i,(title,metric) in enumerate(specs)]),
        ws.Section(name='Actual counts and targets — historical cohorts excluded',is_open=True,panels=[wr.WeavePanelSummaryTable(table_name='completion',layout=wr.Layout(x=0,y=0,w=24,h=10))])]
    view.save()
    state={'schemaVersion':1,'protocolRevision':5,'url':view.url,'forgeUrl':view.url.replace('https://forge.coreweave.com/','https://forge.coreweave.com/wandb/',1),'runUrl':run_url,'artifact':existing.qualified_name,'sourceSha256':digest,'readBackVerified':False}
    save(state)
    restored=ws.Workspace.from_url(view.url)
    if restored.name!=view.name or len(restored.sections)!=2:raise RuntimeError('Dashboard read-back mismatch')
    summary=wandb.Api(timeout=60).run(f'{entity}/{project}/{identifier}').summary
    if any(summary.get(key)!=value for key,value in metrics.items()):raise RuntimeError('Audit summary read-back mismatch')
    state['readBackVerified']=True;save(state);print(json.dumps(state,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:raise SystemExit('Use --execute to publish the private audit dashboard; no paid compute is launched')
    publish()
