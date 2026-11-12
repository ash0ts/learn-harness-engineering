# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0", "wandb-workspaces==0.4.13"]
# ///
"""Publish the owner rollout receipt separately from comparison cohorts. No compute launches."""
import argparse
import json
import os
from pathlib import Path
import tempfile
import time
import wandb
import wandb_workspaces.expr as expr
import wandb_workspaces.reports.v2 as wr
import wandb_workspaces.workspaces as ws
from models import require_private_project, artifact_collection_exists
from publication import gql
from audit_artifact import snapshot, verify

ROOT=Path(__file__).resolve().parents[2]
DIRECTORY=ROOT/'forge/results/rollout-v5'
LOCAL=ROOT/'forge/local-results/rollout-v5'
MANIFEST=DIRECTORY/'dashboard.json'

def save(value):
    temporary=MANIFEST.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,indent=2)+'\n');temporary.replace(MANIFEST)

def publish():
    entity,project=require_private_project()
    data=json.loads((DIRECTORY/'status.json').read_text())
    previous=json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    metrics={**data['completed'],'rolloutEstimateUsd':data['budget']['rolloutEstimateUsd'],
             'earlierUnknownReservationUsd':2,'inputTokens':data['trial']['inputTokens'],
             'outputTokens':data['trial']['outputTokens']}
    files=[(DIRECTORY/p,p) for p in ('README.md','status.json')]
    files += [(LOCAL/p,'receipts/'+p) for p in ('budget.json','authorization.json','student-settlement.json',
              'trace-readback.json','trace-reconciled.json','checkpoint-verification.json',
              'final-sandbox-audit.json','cleanup-final.json','download-test.json','notebook-sessions/notebook-rollout-v5-scratch-final.json',
              'collected/checkpoint.tar.gz','collected/trial.json','collected/publication.json',
              'collected/save-receipt.json','python-tests-models.log','typescript-tests-final.log',
              'notebook-validation-models.log')]
    files += [(path,'screenshots/'+path.name) for path in sorted((DIRECTORY/'screenshots').glob('*.png'))]
    files += [(LOCAL/'download-rehearsal'/name,'fresh-restore/'+name) for name in ('checkpoint.tar.gz','checkpoint-verification.json','allowance.json')]
    files += [(LOCAL/'final-publication.log','receipts/final-publication.log'),(ROOT/'forge/publication-manifest.json','publication-manifest.json')]
    identifier='course-rollout5-owner-rehearsal';name='rollout5-owner-rehearsal'
    api=wandb.Api(timeout=60)
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary).resolve()
        digest,payload=snapshot(files,root/'upload',os.environ['WANDB_API_KEY'].encode())
        exists=artifact_collection_exists(entity,project,'course-rollout-audit',name)
        artifact=next((a for a in api.artifact_versions('course-rollout-audit',f'{entity}/{project}/{name}') if a.metadata.get('payloadSha256')==digest),None) if exists else None
        with wandb.init(entity=entity,project=project,id=identifier,resume='allow',job_type='course-rollout-audit',group='protocol-5-rollout',
                        config={'protocolRevision':5,'dashboardKind':'owner-rollout','candidateRunnerCommit':data['candidateRunnerCommit'],'executionSourceCommit':data['executionSourceCommit']},
                        settings=wandb.Settings(disable_git=True,disable_code=True,silent=True)) as run:
            run.summary.update({**metrics,'status':data['status'],'readyToShareLessonLinks':data['readyToShareLessonLinks'],'classroomAcceptanceComplete':data['classroomAcceptanceComplete'],'artifactPayloadSha256':digest})
            run.summary['acceptance']=wandb.Table(columns=['Check','Observed'],data=[[k,str(v)] for k,v in data['completed'].items()])
            run.summary['application_checks']=wandb.Table(columns=['Check','Passed','Error'],data=[[v['name'],v['passed'],v.get('error','')] for v in data['trial']['grade']['checks']])
            if artifact is None:
                new=wandb.Artifact(name,type='course-rollout-audit',metadata={'payloadSha256':digest,'protocolRevision':5})
                for entry in [*payload['files'],'receipt-manifest.json']:new.add_file(str(root/'upload'/entry),name=entry)
                artifact=run.log_artifact(new,aliases=['latest']).wait()
            run_url=run.url
        downloaded=Path(artifact.download(root=str(root/'readback')))
        verified=verify(downloaded,digest)
    view=ws.Workspace.from_url(previous['url']) if previous.get('url') else ws.Workspace(entity=entity,project=project)
    view.name='Forge lessons — owner rehearsal and publication gates'
    view.runset_settings=ws.RunsetSettings(filters=[expr.Config('protocolRevision')==5,expr.Config('dashboardKind')=='owner-rollout'],pinned_columns=['status','ownerStudentAttempts','finalCandidateNotebooksPublished'])
    panels=[('Student attempts completed','ownerStudentAttempts'),('Task failures retained','taskFailed'),('Protected controls qualified','project01ControlsQualified'),('Final notebooks published (target 9)','finalCandidateNotebooksPublished'),('Native downloads verified (target 2)','nativeDownloadsVerified'),('Conservative rollout estimate (USD)','rolloutEstimateUsd')]
    view.sections=[ws.Section(name='Nine lessons published — native download and student-account gates remain',is_open=True,panels=[wr.ScalarChart(title=t,metric=m,layout=wr.Layout(x=(i%2)*12,y=(i//2)*6,w=12,h=6)) for i,(t,m) in enumerate(panels)]),
        ws.Section(name='Actual application grade and remaining gates',is_open=True,panels=[wr.WeavePanelSummaryTable(table_name='application_checks',layout=wr.Layout(x=0,y=0,w=24,h=10)),wr.WeavePanelSummaryTable(table_name='acceptance',layout=wr.Layout(x=0,y=10,w=24,h=10))])]
    view.save()
    forge_url=view.url if '/wandb/wandb/' in view.url else view.url.replace('https://forge.coreweave.com/','https://forge.coreweave.com/wandb/',1)
    receipt={'schemaVersion':1,'url':view.url,'forgeUrl':forge_url,'runUrl':run_url,'artifact':artifact.qualified_name,'payloadSha256':digest,'verifiedEvidenceFiles':len(verified['files']),'readBackVerified':False}
    save(receipt)
    restored=ws.Workspace.from_url(view.url)
    if restored.name!=view.name or len(restored.sections)!=2:raise RuntimeError('Dashboard read-back mismatch')
    for _ in range(15):
        record=gql('query($e:String!,$p:String!,$n:String!){project(entityName:$e,name:$p){run(name:$n){summaryMetrics}}}',{'e':entity,'p':project,'n':identifier})
        summary=json.loads(record['project']['run']['summaryMetrics'])
        mismatch={k:summary.get(k) for k,v in metrics.items() if summary.get(k)!=v}
        if not mismatch:break
        time.sleep(2)
    if mismatch:raise RuntimeError('Run summary read-back mismatch: '+json.dumps(mismatch))
    receipt['readBackVerified']=True;save(receipt);print(json.dumps(receipt,indent=2))

def verify_saved():
    entity,project=require_private_project()
    receipt=json.loads(MANIFEST.read_text());data=json.loads((DIRECTORY/'status.json').read_text())
    view=ws.Workspace.from_url(receipt['url'])
    if view.name!='Forge lessons — owner rehearsal and publication gates' or len(view.sections)!=2:
        raise RuntimeError('Dashboard configuration differs from the saved receipt')
    raw=gql('query($e:String!,$p:String!,$n:String!){project(entityName:$e,name:$p){run(name:$n){summaryMetrics}}}',{'e':entity,'p':project,'n':'course-rollout5-owner-rehearsal'})
    summary=json.loads(raw['project']['run']['summaryMetrics'])
    expected={**data['completed'],'rolloutEstimateUsd':data['budget']['rolloutEstimateUsd'],'earlierUnknownReservationUsd':2,
              'inputTokens':data['trial']['inputTokens'],'outputTokens':data['trial']['outputTokens'],'artifactPayloadSha256':receipt['payloadSha256']}
    mismatch={k:summary.get(k) for k,v in expected.items() if summary.get(k)!=v}
    if mismatch:raise RuntimeError('Saved dashboard summary differs: '+json.dumps(mismatch))
    with tempfile.TemporaryDirectory() as temporary:
        artifact=wandb.Api(timeout=60).artifact(receipt['artifact'],type='course-rollout-audit')
        downloaded=Path(artifact.download(root=str(Path(temporary).resolve()/'readback')))
        verified=verify(downloaded,receipt['payloadSha256'])
    if len(verified['files'])!=receipt['verifiedEvidenceFiles']:raise RuntimeError('Evidence count changed')
    receipt['readBackVerified']=True;save(receipt);print(json.dumps(receipt,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    if args.verify:verify_saved()
    elif args.execute:publish()
    else:raise SystemExit('Use --execute to publish or --verify to recover read-back; no compute is launched')
