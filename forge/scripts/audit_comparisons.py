"""Reconcile each completed treatment block with its frozen control contract."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from evidence_reports import read_reports

ROOT=Path(__file__).resolve().parents[2]
LOCAL=ROOT/'forge/local-results'

def build():
    results=[]
    for report in read_reports(LOCAL):
        for block in report['blocks']:
            project=block['project']
            if project not in [f'project-0{i}' for i in range(1,7)]:continue
            expected=set(json.loads((ROOT/'forge/tasks'/f'{project}.json').read_text())['variants'])
            rows=[r for r in report['completed'] if r['project']==project and r['trial']==block['repeat']]
            if set(r['variant'] for r in rows)!=expected:continue
            originals=[json.loads((LOCAL/r['id']/'trial.json').read_text()) for r in rows]
            errors=[]
            if len(rows)!=len(expected):errors.append('Duplicate treatment in block')
            for key in ['applicationSha256','checkerSha256']:
                values={r.get(key) for r in originals}
                if len(values)!=1 or None in values:errors.append(f'Treatments do not share a recorded {key}')
            for row in originals:
                if row['sourceCommit']!=report['sourceCommit'] or row['protocol']!=report['protocol']:
                    errors.append('Frozen source or generation settings differ')
                digest=hashlib.sha256(json.dumps(row['protocol'],separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
                if digest!=report['protocolSha256']:errors.append('Protocol checksum differs')
                if not row.get('finishedAt') or not row.get('wandbRunUrl') or not row.get('artifactUrl'):
                    errors.append('Incomplete or unpublished trial in block')
                if row['outcome']=='passed' and not all(c['passed'] for c in row['grade']['checks']):
                    errors.append('Passing outcome disagrees with protected checks')
            results.append({'campaignId':report['campaignId'],'project':project,'repeat':block['repeat'],
                            'sourceCommit':report['sourceCommit'],'protocolSha256':report['protocolSha256'],
                            'applicationSha256':originals[0].get('applicationSha256'),
                            'checkerSha256':originals[0].get('checkerSha256'),
                            'trialIds':[r['id'] for r in originals],'verified':not errors,'errors':sorted(set(errors))})
    result={'schemaVersion':1,'verifiedAt':datetime.now(timezone.utc).isoformat(),'blocks':results,
            'verified':bool(results) and all(r['verified'] for r in results),
            'note':'Matching frozen inputs establish local controls, not broad causal treatment effects.'}
    (LOCAL/'comparison-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'blocks':len(results),'verified':sum(r['verified'] for r in results),'errors':[r for r in results if not r['verified']]},indent=2))
    return result

if __name__=='__main__':build()
