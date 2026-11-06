# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0"]
# ///
"""Upload existing evidence and exact source archives; launches no inference or sandbox."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import wandb
from models import require_private_project

ROOT=Path(__file__).resolve().parents[2]
LOCAL=ROOT/'forge/local-results'

def publish():
    entity,project=require_private_project()
    saved=json.loads((ROOT/'forge/results/snapshot.json').read_text())
    ledger=json.loads((LOCAL/'budget.json').read_text())
    sources=LOCAL/'audit-sources';sources.mkdir(exist_ok=True)
    concurrent=[json.loads(p.read_text()) for p in LOCAL.glob('concurrency-*/concurrency.json')]
    publications=json.loads((ROOT/'forge/publication-manifest.json').read_text())
    supplemental=saved.get('sandboxQualifications',[])+saved.get('graphs',[])+saved.get('loops',[])
    publisher_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    commits=sorted({publisher_commit}|{r['sourceCommit'] for r in saved['trials']+saved['qualifications']+concurrent+supplemental+publications['notebooks'] if r.get('sourceCommit')})
    archives=[]
    for commit in commits:
        path=sources/(commit+'.tar.gz')
        subprocess.run(['git','archive','--format=tar.gz','-o',str(path),commit,'forge','projects'],cwd=ROOT,check=True)
        archives.append({'sourceCommit':commit,'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (sources/'manifest.json').write_text(json.dumps(archives,indent=2)+'\n')
    blocks=len(saved.get('completedComparisonBlocks',[]))
    uncertain=sum(r['reservedEstimateUsd'] for r in ledger.get('uncertainEstimates',[]))
    verified_ui=[r for r in saved['trials'] if r.get('protocolRevision',1)>=4]
    audit_metrics={'qualificationAttempts':len(saved['qualifications']),'qualificationPassed':sum(r['passed'] for r in saved['qualifications']),'codingTrialAttempts':len(saved['trials']),'passedCodingTrials':sum(r['outcome']=='passed' for r in saved['trials']),'completeComparisonBlocks':blocks,'knownEstimatedSpendUsd':ledger['spentEstimateUsd']-uncertain,'chargedUnknownReservationsUsd':uncertain,'totalChargedEstimateUsd':ledger['spentEstimateUsd'],'unresolvedReservationsUsd':sum(ledger['reservations'].values()),'budgetHalted':bool(ledger.get('halted')),'notebooksPublishedVerified':sum(r['status']=='published_verified' for r in publications['notebooks'])}
    audit_metrics.update(verifiedUiAttempts=len(verified_ui),verifiedUiPasses=sum(r['outcome']=='passed' for r in verified_ui))
    with wandb.init(entity=entity,project=project,id='course-audit-20261106',resume='allow',job_type='qualification-audit',name='Forge course execution and publication evidence',config={'protocol':json.loads((ROOT/'forge/protocol.json').read_text()),'upstreamCommit':'a9342ff471f2c0e60be0c08b9f4a7c502df4e442'},settings=wandb.Settings(disable_git=True,disable_code=True)) as run:
        run.name='Forge course execution and publication evidence'
        run.log(audit_metrics)
        table=wandb.Table(columns=['id','kind','outcome','original_estimate_usd','audited_estimate_usd','source_commit'])
        for row in saved['qualifications']:
            table.add_data(row['id'],'qualification','passed' if row['passed'] else 'failed',row.get('estimatedCostUsd'),ledger['settled'].get(row['id']),row['sourceCommit'])
        for row in saved['trials']:
            table.add_data(row['id'],'coding-trial',row['outcome'],row.get('estimatedCostUsd'),ledger['settled'].get(row['id']),row['sourceCommit'])
        run.log({'attempts':table})
        artifact=wandb.Artifact('forge-course-qualification-evidence',type='course-evidence',metadata={'schemaVersion':1,'status':'recorded-evidence','completedComparisonBlocks':blocks,'publisherSourceCommit':publisher_commit})
        for row in saved['qualifications']+saved['trials']+concurrent+saved.get('sandboxQualifications',[]):
            directory=LOCAL/row['id']
            for path in sorted(directory.rglob('*')):
                if path.is_file() and path.suffix in {'.json','.diff','.txt','.log','.png'}:
                    artifact.add_file(str(path),name=str(path.relative_to(LOCAL)))
        for path in sorted(sources.iterdir()):artifact.add_file(str(path),name='source-archives/'+path.name)
        for filename in ['budget.json','app-checks.json','notebook-validation.json','trace-audit.json','models-audit.json','forge-tests-final.log','sandbox-final-audit.json','local-checks.json','docs-check.log','anchors-check.log']:
            path=LOCAL/filename
            if path.exists():artifact.add_file(str(path),name=filename)
        for pattern in ['project-07-*.json','project-08-*.json','rollback-*.json','report-*.json','graph-*/*.json','graph-*/*.png','notebook-sessions/*.json','trace-readback/*.json','reconciliations/*.json','publication/*/notebook.py','publication/*/rendered.html','publication/*.jpg']:
            for path in sorted(LOCAL.glob(pattern)):
                if path.is_file():artifact.add_file(str(path),name=str(path.relative_to(LOCAL)))
        for directory in sorted(LOCAL.glob('graph-qualification-*')):
            for path in sorted(directory.rglob('*')):
                if path.is_file() and path.suffix in {'.json','.diff','.png'}:
                    artifact.add_file(str(path),name=str(path.relative_to(LOCAL)))
        for path in sorted((ROOT/'forge/results').glob('*')):
            if path.name in {'README.md','evidence-publication.json'}:continue
            if path.is_file():artifact.add_file(str(path),name='results/'+path.name)
        for path in sorted((ROOT/'forge/notebooks').glob('*.py')):artifact.add_file(str(path),name='notebooks/'+path.name)
        artifact.add_file(str(ROOT/'forge/publication-manifest.json'),name='publication-manifest.json')
        committed=run.log_artifact(artifact).wait()
        receipt={'schemaVersion':1,'runId':run.id,'runUrl':run.url,'artifact':f'{entity}/{project}/{committed.name}','artifactUrl':f'https://wandb.ai/{entity}/{project}/artifacts/course-evidence/{committed.name}','publisherSourceCommit':publisher_commit,'sourceArchives':archives}
    api=wandb.Api();remote=api.artifact(receipt['artifact'],type='course-evidence')
    receipt['artifactFileCount']=len(list(remote.files()))
    # Run summary reads can briefly lag a successful finish. Require the final
    # values, with bounded retries, rather than recording a stale earlier state.
    for attempt in range(16):
        summary=wandb.Api().run(f'{entity}/{project}/{receipt["runId"]}').summary
        observed={key:summary.get(key) for key in audit_metrics}
        if observed==audit_metrics:break
        if attempt==15:raise RuntimeError('Final audit run summary does not match recorded evidence')
        time.sleep(2)
    receipt['verifiedRunSummary']=observed
    receipt['verifiedRunBudgetHalted']=observed['budgetHalted']
    readback=LOCAL/'evidence-readback';readback.mkdir(exist_ok=True)
    for source in archives:
        downloaded=Path(remote.get_entry('source-archives/'+source['file']).download(root=str(readback)))
        if hashlib.sha256(downloaded.read_bytes()).hexdigest()!=source['sha256']:
            raise RuntimeError('Committed source archive checksum mismatch: '+source['sourceCommit'])
    manifest_copy=Path(remote.get_entry('publication-manifest.json').download(root=str(readback)))
    if manifest_copy.read_bytes()!=(ROOT/'forge/publication-manifest.json').read_bytes():
        raise RuntimeError('Committed publication manifest differs from verified local manifest')
    receipt['sourceArchivesReadBackVerified']=True
    receipt['publicationManifestReadBackVerified']=True
    receipt['completedComparisonBlocks']=blocks
    receipt['completedCodingAttempts']=len(saved['trials'])
    (ROOT/'forge/results/evidence-publication.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':publish()
