"""Package only the public article evidence allowlist, with deterministic ZIP paths."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'docs/public/forge/evidence'
ASSETS=ROOT/'docs/en/forge/assets'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
catalog=json.loads((PUBLIC/'catalog.json').read_text())
files={'catalog.json':PUBLIC/'catalog.json','trials.csv':PUBLIC/'trials.csv','README.md':ROOT/'forge/ARTICLE-VISUALS.md',
       'scripts/article_evidence.py':ROOT/'forge/scripts/article_evidence.py','scripts/article_diagrams.py':ROOT/'forge/scripts/article_diagrams.py',
       'scripts/package_article_evidence.py':Path(__file__).resolve()}
files['scripts/validate_article_visuals.mts']=ROOT/'forge/scripts/validate_article_visuals.mts'
if (PUBLIC/'validation.json').exists():files['validation.json']=PUBLIC/'validation.json'
lock=ROOT/'forge/scripts/article_evidence.py.lock'
if lock.exists():files['scripts/article_evidence.py.lock']=lock
for p in sorted(ASSETS.rglob('*')):
    if p.is_file() and p.suffix in {'.svg','.png','.jpg'}:files['assets/'+str(p.relative_to(ASSETS))]=p
audit_path=ROOT/'forge/local-results/article-editorial/visual-artifact-audit.json'
audit=json.loads(audit_path.read_text()) if audit_path.exists() else None
if audit and not audit['verified']:raise RuntimeError('Committed artifact byte verification failed')
manifest={'schemaVersion':1,'sourceReportCommit':catalog['sourceReportCommit'],'inputs':catalog['inputs'],
    'counts':{'attempts':len(catalog['trials']),'primaryAttempts':len(catalog['primaryTrialIds']),
        'originalCaptures':len(catalog['assets']),'figures':len(list((ASSETS/'figures').glob('*.svg'))),
        'workflowDiagrams':len(list((ASSETS/'diagrams').glob('*.svg'))),'indexedTrialFiles':sum(len(r['evidenceFiles']) for r in catalog['trials'])},
    'privateEvidenceArtifact':catalog['evidenceArtifact'],
    'artifactReadback':{k:audit[k] for k in ['artifact','artifactFiles','checkedFiles','verified']} if audit else {'verified':False,'reason':'Readback receipt not supplied'},
    'captures':catalog['assets'],'files':[{ 'path':name,'bytes':p.stat().st_size,'sha256':sha(p)} for name,p in sorted(files.items())]}
(PUBLIC/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
files['manifest.json']=PUBLIC/'manifest.json'
with zipfile.ZipFile(PUBLIC/'forge-visual-evidence.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
    for name,p in sorted(files.items()):
        entry=zipfile.ZipInfo(name,date_time=(2026,11,6,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o644<<16
        archive.writestr(entry,p.read_bytes())
print(json.dumps({'counts':manifest['counts'],'zipBytes':(PUBLIC/'forge-visual-evidence.zip').stat().st_size,'zipSha256':sha(PUBLIC/'forge-visual-evidence.zip')},indent=2))
