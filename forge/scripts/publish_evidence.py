# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0"]
# ///
"""Upload existing evidence and exact source archives; launches no inference or sandbox."""
from pathlib import Path
import hashlib
import json
import subprocess
import wandb
from models import require_private_project

ROOT=Path(__file__).resolve().parents[2]
LOCAL=ROOT/'forge/local-results'

def publish():
    entity,project=require_private_project()
    saved=json.loads((ROOT/'forge/results/snapshot.json').read_text())
    ledger=json.loads((LOCAL/'budget.json').read_text())
    sources=LOCAL/'audit-sources';sources.mkdir(exist_ok=True)
    commits=sorted({r['sourceCommit'] for r in saved['trials']+saved['qualifications']})
    archives=[]
    for commit in commits:
        path=sources/(commit+'.tar.gz')
        subprocess.run(['git','archive','--format=tar.gz','-o',str(path),commit,'forge','projects'],cwd=ROOT,check=True)
        archives.append({'sourceCommit':commit,'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (sources/'manifest.json').write_text(json.dumps(archives,indent=2)+'\n')
    with wandb.init(entity=entity,project=project,id='course-audit-20261106',resume='allow',job_type='qualification-audit',name='Forge course qualification and blocked campaign',config={'protocol':json.loads((ROOT/'forge/protocol.json').read_text()),'upstreamCommit':'a9342ff471f2c0e60be0c08b9f4a7c502df4e442'},settings=wandb.Settings(disable_git=True,disable_code=True)) as run:
        run.log({'qualificationAttempts':len(saved['qualifications']),'qualificationPassed':sum(r['passed'] for r in saved['qualifications']),'codingTrialAttempts':len(saved['trials']),'passedCodingTrials':sum(r['outcome']=='passed' for r in saved['trials']),'completeComparisonBlocks':0,'knownEstimatedSpendUsd':ledger['spentEstimateUsd'],'unresolvedReservationsUsd':sum(ledger['reservations'].values()),'budgetHalted':bool(ledger.get('halted'))})
        table=wandb.Table(columns=['id','kind','outcome','original_estimate_usd','audited_estimate_usd','source_commit'])
        for row in saved['qualifications']:
            table.add_data(row['id'],'qualification','passed' if row['passed'] else 'failed',row.get('estimatedCostUsd'),ledger['settled'].get(row['id']),row['sourceCommit'])
        for row in saved['trials']:
            table.add_data(row['id'],'coding-trial',row['outcome'],row.get('estimatedCostUsd'),ledger['settled'].get(row['id']),row['sourceCommit'])
        run.log({'attempts':table})
        artifact=wandb.Artifact('forge-course-qualification-evidence',type='course-evidence',metadata={'schemaVersion':1,'status':'paid-launches-halted','completedComparisonBlocks':0})
        for row in saved['qualifications']:
            directory=LOCAL/row['id']
            for path in sorted(directory.rglob('*')):
                if path.is_file() and path.suffix in {'.json','.diff','.txt'}:
                    artifact.add_file(str(path),name=str(path.relative_to(LOCAL)))
        for path in sorted(sources.iterdir()):artifact.add_file(str(path),name='source-archives/'+path.name)
        for filename in ['budget.json','app-checks.json','notebook-validation.json','project-07-real-timer.json']:
            path=LOCAL/filename
            if path.exists():artifact.add_file(str(path),name=filename)
        for path in sorted((ROOT/'forge/results').glob('*')):
            if path.is_file():artifact.add_file(str(path),name='results/'+path.name)
        artifact.add_file(str(ROOT/'forge/publication-manifest.json'),name='publication-manifest.json')
        committed=run.log_artifact(artifact).wait()
        receipt={'schemaVersion':1,'runId':run.id,'runUrl':run.url,'artifact':f'{entity}/{project}/{committed.name}','artifactUrl':f'https://wandb.ai/{entity}/{project}/artifacts/course-evidence/{committed.name}','sourceArchives':archives}
    api=wandb.Api();remote=api.artifact(receipt['artifact'],type='course-evidence')
    receipt['artifactFileCount']=len(list(remote.files()))
    receipt['verifiedRunBudgetHalted']=api.run(f'{entity}/{project}/{receipt["runId"]}').summary.get('budgetHalted')
    (ROOT/'forge/results/evidence-publication.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':publish()
