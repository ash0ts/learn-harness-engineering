"""Snapshot coordinator-confirmed trials for a running dashboard, never launch work.

The completed report supersedes this snapshot automatically. Only the coordinator's
post-settlement, post-upload log entries are eligible; unfinished workers are absent.
"""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]
LOCAL=ROOT/'forge/local-results'

def build(plan_file, log_file):
    plan=json.loads(Path(plan_file).read_text())
    log=Path(log_file).read_bytes()
    completed={}
    for line in log.decode().splitlines():
        try: entry=json.loads(line)
        except json.JSONDecodeError: continue
        if not isinstance(entry,dict) or not {'id','project','variant','outcome','cost'}<=entry.keys(): continue
        record=json.loads((LOCAL/entry['id']/'trial.json').read_text())
        if not record.get('finishedAt') or not record.get('wandbRunUrl'):
            raise RuntimeError('Coordinator entry lacks completed uploaded evidence')
        if record['sourceCommit']!=plan['sourceCommit'] or record['protocol']!=plan['protocol']:
            raise RuntimeError('Progress log belongs to another frozen cohort')
        if any(entry[k]!=record[k] for k in ['id','project','variant','outcome']) or entry['cost']!=record['estimatedCostUsd']:
            raise RuntimeError('Coordinator log differs from original trial record')
        completed[record['id']]=record
    result={**plan,'completed':list(completed.values()),'completedTrials':len(completed),
            'progressSnapshot':True,'capturedAt':datetime.now(timezone.utc).isoformat(),
            'coordinatorLogSha256':hashlib.sha256(log).hexdigest()}
    path=LOCAL/('dashboard-progress-'+plan['campaignId']+'.json')
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(f'{len(completed)} coordinator-confirmed trials; complete blocks only will appear in dashboards')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('plan');parser.add_argument('log')
    args=parser.parse_args();build(args.plan,args.log)
