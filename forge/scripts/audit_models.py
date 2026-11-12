# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0"]
# ///
"""Read W&B Models runs and committed trial artifacts back without launching work."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import wandb
from models import require_private_project

ROOT=Path(__file__).resolve().parents[2]
LOCAL=ROOT/'forge/local-results'

def audit(record,entity,project):
    result={'trialId':record['id'],'sourceCommit':record['sourceCommit'],'verified':False,'errors':[]}
    try:
        api=wandb.Api(timeout=30)
        run=api.run(f"{entity}/{project}/{record['wandbRunId']}")
        for key in ['sourceCommit','model','variant','trial','protocol','applicationSha256','checkerSha256']:
            if key in record and run.config.get(key)!=record[key]:result['errors'].append('Run configuration differs: '+key)
        for key in ['outcome','inputTokens','outputTokens','estimatedCostUsd']:
            if record.get(key) is not None and run.summary.get(key)!=record[key]:result['errors'].append('Run summary differs: '+key)
        artifacts=[a for a in run.logged_artifacts() if a.type=='course-evidence' and a.name.startswith('trial-'+record['id']+':')]
        if len(artifacts)!=1:raise RuntimeError('Expected one versioned trial evidence artifact')
        artifact=artifacts[0]
        if artifact.metadata.get('sourceCommit')!=record['sourceCommit']:result['errors'].append('Artifact source revision differs')
        directory=LOCAL/'models-readback'/record['id'];directory.mkdir(parents=True,exist_ok=True)
        downloaded=Path(artifact.get_entry('trial.json').download(root=str(directory)))
        stored=json.loads(downloaded.read_text())
        for key in ['id','project','variant','trial','sourceCommit','outcome','inputTokens','outputTokens','estimatedCostUsd','conversationIds','grade']:
            if stored.get(key)!=record.get(key):result['errors'].append('Committed trial artifact differs: '+key)
        result.update(runId=run.id,runUrl=run.url,artifact=artifact.qualified_name,committedTrialSha256=hashlib.sha256(downloaded.read_bytes()).hexdigest(),verified=not result['errors'])
    except Exception as error:result['errors'].append(str(error))
    return result

def build():
    entity,project=require_private_project()
    records=[r for p in sorted(LOCAL.glob('*/trial.json')) if (r:=json.loads(p.read_text())).get('finishedAt')]
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda row:audit(row,entity,project),records))
    report={'schemaVersion':1,'verifiedAt':datetime.now(timezone.utc).isoformat(),'verified':bool(results) and all(r['verified'] for r in results),'trials':results}
    (LOCAL/'models-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'trials':len(results),'verified':sum(r['verified'] for r in results),'errors':[r for r in results if not r['verified']]},indent=2))
    return report

if __name__=='__main__':build()
