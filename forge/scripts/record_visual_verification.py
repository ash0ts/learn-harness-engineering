# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0"]
# ///
"""Archive actual authenticated browser observations after visual inspection.

This does not infer UI success from upload completion. The operator supplies an
observations.json alongside the original browser captures, after inspecting them.
"""
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import wandb
from models import require_private_project

ROOT=Path(__file__).resolve().parents[2]
DIRECTORY=ROOT/'forge/local-results/article-visual-publication'
RECEIPT=ROOT/'forge/results/article-visual-publication.json'

def main():
    entity,project=require_private_project()
    publication=json.loads(RECEIPT.read_text())
    observation=json.loads((DIRECTORY/'observations.json').read_text())
    assert observation['verified'] and observation['forgeUrl']==publication['forgeUrl']
    assert observation['sourceArtifact']==publication['artifact']
    captures=[]
    for name in observation['captures']:
        path=DIRECTORY/name
        assert path.is_file() and path.parent==DIRECTORY and path.suffix in {'.jpg','.png'}
        captures.append({'path':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
    artifact=wandb.Artifact('forge-article-visual-browser-proof',type='course-evidence',metadata={'sourceArtifact':publication['artifact'],'sourceCommit':publication['sourceCommit'],'workspaceUrl':publication['forgeUrl']})
    for name in ['observations.json',*[c['path'] for c in captures]]:artifact.add_file(str(DIRECTORY/name),name=name)
    with wandb.init(entity=entity,project=project,id=publication['runId'],resume='must',settings=wandb.Settings(disable_git=True,disable_code=True)) as run:
        published=run.log_artifact(artifact,aliases=['latest']).wait()
        artifact_name=published.name
    remote=wandb.Api().artifact(f'{entity}/{project}/{artifact_name}')
    for name in remote.manifest.entries:
        digest=base64.b64encode(hashlib.md5((DIRECTORY/name).read_bytes()).digest()).decode()
        assert remote.manifest.entries[name].digest==digest,name
    publication['browserVerification']={**observation,'recordedAt':datetime.now(timezone.utc).isoformat(),'captures':captures,'proofArtifact':f'{entity}/{project}/{artifact_name}','proofArtifactUrl':f'https://wandb.ai/{entity}/{project}/artifacts/course-evidence/{artifact_name}','artifactFilesVerified':len(remote.manifest.entries)}
    RECEIPT.write_text(json.dumps(publication,indent=2)+'\n')
    print(json.dumps(publication['browserVerification'],indent=2))

if __name__=='__main__':main()
