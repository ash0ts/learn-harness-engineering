# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0"]
# ///
"""Idempotent publication: read back a stable run/artifact before retrying writes."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import urllib.request
import wandb


def require_private_project():
    entity, project = os.environ['WANDB_ENTITY'], os.environ['WANDB_PROJECT']
    payload = {'query': 'query($e:String!,$p:String!){project(name:$p,entityName:$e){name access}}', 'variables': {'e': entity, 'p': project}}
    authorization = base64.b64encode(('api:' + os.environ['WANDB_API_KEY']).encode()).decode()
    request = urllib.request.Request('https://api.wandb.ai/graphql', data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json', 'Authorization': 'Basic ' + authorization})
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get('data', {}).get('project', {}).get('access') != 'PRIVATE':
        raise RuntimeError('An existing PRIVATE project is required')
    return entity, project


def projection(record):
    value = {k: v for k, v in record.items() if k not in {'wandbRunUrl', 'artifactUrl', 'publicationStatus'}}
    text = json.dumps(value, sort_keys=True)
    # Protected raw evidence stays local/private; dashboard projections are portable.
    return json.loads(re.sub(r'/(?:Users|home)/[^/"\\\s]+/', '[local]/', text))


def payload(file):
    record = json.loads(file.read_text())
    projected = projection(record)
    canonical = json.dumps(projected, sort_keys=True, separators=(',', ':')).encode()
    entries = {'trial.json': canonical}
    for path in sorted(file.parent.rglob('*')):
        if path.is_symlink():
            raise RuntimeError('Evidence symlink rejected')
        if not path.is_file() or path.name in {'trial.json', 'models.log', 'publication.json', 'publication-child.json', 'recovery-accounting.json'}:
            continue
        entries[path.relative_to(file.parent).as_posix()] = path.read_bytes()
    secret = os.environ.get('WANDB_API_KEY', '').encode()
    if secret and any(secret in data for data in entries.values()):
        raise RuntimeError('Credential detected in evidence; publication stopped')
    fingerprint = hashlib.sha256()
    for name, data in sorted(entries.items()):
        fingerprint.update(name.encode() + b'\0' + hashlib.sha256(data).digest())
    return record, projected, entries, fingerprint.hexdigest()


def artifact_collection_exists(entity, project, type_name, name, request=None):
    query = 'query($e:String!,$p:String!,$t:String!,$n:String!){project(entityName:$e,name:$p){access artifactType(name:$t){artifactCollection(name:$n){id}}}}'
    payload = {'query':query,'variables':{'e':entity,'p':project,'t':type_name,'n':name}}
    authorization = base64.b64encode(('api:' + os.environ['WANDB_API_KEY']).encode()).decode()
    req = urllib.request.Request('https://api.wandb.ai/graphql',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Basic '+authorization})
    with (request or urllib.request.urlopen)(req,timeout=30) as response:
        result=json.load(response)
    value=result.get('data',{}).get('project')
    if result.get('errors') or not value or value.get('access')!='PRIVATE' or 'artifactType' not in value:
        raise RuntimeError('Cannot verify private artifact collection; no write is authorized by this response')
    kind=value['artifactType']
    if kind is None:return False
    if 'artifactCollection' not in kind:raise RuntimeError('Artifact collection response is incomplete')
    return kind['artifactCollection'] is not None


def remote_artifact(api, entity, project, name, fingerprint):
    # The pinned SDK raises for a missing artifact type. Only an explicit GraphQL
    # null proves absence; network, parse and authorization failures still stop.
    if not artifact_collection_exists(entity, project, 'course-evidence', name):
        return None
    versions = list(api.artifact_versions('course-evidence', f'{entity}/{project}/{name}'))
    match = next((a for a in versions if a.metadata.get('evidenceSha256') == fingerprint), None)
    if match is None and versions:
        raise RuntimeError('Stable artifact ID already contains different evidence; reconcile before publishing')
    return match


def log_trial(file):
    record, projected, entries, fingerprint = payload(file)
    entity, project = require_private_project()
    api = wandb.Api(timeout=60)
    name = 'trial-' + record['id']
    artifact = remote_artifact(api, entity, project, name, fingerprint)
    existing = next(iter(api.runs(f'{entity}/{project}', filters={'name': record['wandbRunId']})), None)
    if existing and existing.summary.get('evidenceSha256') not in (None, fingerprint):
        raise RuntimeError('Stable run ID contains different evidence')
    if artifact is None or existing is None or existing.summary.get('evidenceSha256') != fingerprint:
        with wandb.init(entity=entity, project=project, id=record['wandbRunId'], resume='allow', job_type='course-trial',
                        group=f"protocol-{record.get('protocol', {}).get('protocolRevision', 'unknown')}-{record['project']}",
                        name=f"{record['project']}-{record['variant']}-{record['trial']}",
                        config={key: projected[key] for key in ['sourceCommit', 'model', 'variant', 'trial', 'configuration', 'protocol', 'applicationSha256', 'checkerSha256'] if key in projected},
                        settings=wandb.Settings(disable_git=True, disable_code=True)) as run:
            metrics = {'passed': int(record['outcome'] == 'passed'), 'outcome': record['outcome'], 'protocolRevision': record.get('protocol', {}).get('protocolRevision')}
            for key in ['inputTokens', 'outputTokens', 'estimatedCostUsd', 'sandboxSecondsUpperBound']:
                if record.get(key) is not None:
                    metrics[key] = record[key]
            metrics['completedChecks'] = sum(c['passed'] for c in record.get('grade', {}).get('checks', []))
            # Summary replacement is idempotent; retries never append another row.
            run.summary.update(metrics)
            run.summary['acceptance_checks'] = wandb.Table(columns=['check', 'passed', 'error'], data=[
                [c.get('name'), bool(c.get('passed')), c.get('error')] for c in record.get('grade', {}).get('checks', [])])
            if artifact is None:
                artifact = wandb.Artifact(name, type='course-evidence', metadata={'schemaVersion': 2, 'sourceCommit': record['sourceCommit'], 'evidenceSha256': fingerprint})
                with tempfile.TemporaryDirectory() as directory:
                    for relative, data in entries.items():
                        target = Path(directory, relative)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(data)
                        artifact.add_file(str(target), name=relative)
                    run.log_artifact(artifact).wait()
            run.summary['evidenceSha256'] = fingerprint
    # Verify committed bytes, not merely a successful upload response.
    api = wandb.Api(timeout=60)
    remote = remote_artifact(api, entity, project, name, fingerprint)
    if remote is None:
        raise RuntimeError('Artifact read-back missing')
    with tempfile.TemporaryDirectory() as directory:
        downloaded = Path(remote.download(root=directory))
        for relative, data in entries.items():
            if hashlib.sha256((downloaded / relative).read_bytes()).digest() != hashlib.sha256(data).digest():
                raise RuntimeError('Artifact read-back checksum mismatch: ' + relative)
    run = api.run(f"{entity}/{project}/{record['wandbRunId']}")
    if run.summary.get('evidenceSha256') != fingerprint:
        raise RuntimeError('Run summary read-back mismatch')
    record['wandbRunUrl'] = run.url
    record['artifactUrl'] = f'https://wandb.ai/{entity}/{project}/artifacts/course-evidence/{remote.name}'
    record['publicationStatus'] = 'verified'
    for target, value in [(file, record), (file.parent / 'publication.json', {'schemaVersion': 2, 'operationId': record['id'], 'runId': record['wandbRunId'], 'artifactId': remote.id, 'artifactVersion': remote.name, 'evidenceSha256': fingerprint, 'verified': True, 'runUrl': run.url, 'artifactUrl': record['artifactUrl']})]:
        temporary = target.with_suffix('.tmp')
        temporary.write_text(json.dumps(value, indent=2) + '\n')
        temporary.replace(target)


if __name__ == '__main__':
    log_trial(Path(sys.argv[1]).resolve())
