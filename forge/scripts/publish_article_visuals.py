# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0", "wandb-workspaces==0.4.13", "pillow==13.0.0"]
# ///
"""Publish the allowlisted article visuals; never launch or rescore coding trials."""
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
import wandb
import wandb_workspaces.expr as expr
import wandb_workspaces.reports.v2 as wr
import wandb_workspaces.workspaces as ws
from models import require_private_project

ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'docs/public/forge/evidence'
ASSETS=ROOT/'docs/en/forge/assets'
RECEIPT=ROOT/'forge/results/article-visual-publication.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

class ReadableLayout(ws.SectionLayoutSettings):
    def _to_model(self):
        model=super()._to_model();model.box_height=560;return model

class SummaryLayout(ws.SectionLayoutSettings):
    def _to_model(self):
        model=super()._to_model();model.box_height=240;return model

def forge_url(url,entity):
    if url.startswith(f"https://forge.coreweave.com/wandb/{entity}/"):
        return url
    if url.startswith('https://forge.coreweave.com/'):
        return url.replace('https://forge.coreweave.com/','https://forge.coreweave.com/wandb/',1)
    return url

def main():
    entity,project=require_private_project()
    catalog=json.loads((PUBLIC/'catalog.json').read_text())
    validation=json.loads((PUBLIC/'validation.json').read_text())
    assert validation['verified'] and len(catalog['trials'])==129
    previous=json.loads(RECEIPT.read_text()) if RECEIPT.exists() else {}
    source=subprocess.check_output(['git','rev-parse','codex/forge-notebooks'],cwd=ROOT,text=True).strip()
    bundle_sha=sha(PUBLIC/'forge-visual-evidence.zip')
    run_id=previous.get('runId','course-article-evidence-20261106')
    columns=['project','treatment','repeat','primary','outcome','checksPassed','checksExecuted','screenshots','trialId','run','artifact','AgentLens','sourceCommit','patchSha256']
    rows=[[t['project'],t['variant'],t['trial'],t['primary'],t['outcome'],sum(c['passed'] for c in t['checks']),len(t['checks']),len(t['captures']),t['id'],t['wandbRunUrl'],t['artifactUrl'],'\n'.join(t['agentLensUrls']),t['sourceCommit'],t['patchSha256']] for t in catalog['trials']]
    captures=[]
    for asset in catalog['assets']:
        path=ASSETS/asset['file'];assert sha(path)==asset['sha256']
        captures.append([wandb.Image(str(path),caption=asset['originalArtifactPath']),asset['kind'],asset.get('trialId',asset.get('qualificationId','')),asset.get('primary'),asset['originalArtifactPath'],asset['sha256'],asset['sourceUrl']])
    figures=sorted((ASSETS/'figures').glob('*.png'))
    primary=[t for t in catalog['trials'] if t['primary']]
    metrics={'recordedAttempts':129,'primaryAttempts':len(primary),'primaryPasses':sum(t['outcome']=='passed' for t in primary),'originalCaptureCount':len(captures),'dataFigures':len(figures),'verifiedSourceFiles':validation['artifactReadback']['checkedFiles']}
    paths={p.name:p for p in PUBLIC.iterdir() if p.is_file() and p.suffix in {'.json','.csv','.zip'}}
    paths['README.md']=ROOT/'forge/ARTICLE-VISUALS.md'
    for p in sorted((ROOT/'docs/en/forge').rglob('*')):
        if p.is_file():paths['articles/'+str(p.relative_to(ROOT/'docs/en/forge'))]=p
    for p in sorted((ROOT/'docs/.vitepress/theme/components').glob('Forge*.vue')):paths['viewer/'+p.name]=p
    paths['scripts/publish_article_visuals.py']=Path(__file__)
    paths['scripts/publish_article_visuals.py.lock']=Path(__file__).with_suffix('.py.lock')
    artifact=wandb.Artifact('forge-article-visual-evidence',type='course-evidence',metadata={'sourceCommit':source,'sourceReportCommit':catalog['sourceReportCommit'],'bundleSha256':bundle_sha,'codingTrial':False,'rescore':False})
    for name,p in sorted(paths.items()):artifact.add_file(str(p),name=name)
    with wandb.init(entity=entity,project=project,id=run_id,resume='allow',job_type='article-evidence',name='Article visuals — saved evidence, no new trials',settings=wandb.Settings(disable_git=True,disable_code=True)) as run:
        run.config.update({'dashboardKind':'article-visual-evidence','codingTrial':False,'primaryComparison':False,'sourceCommit':source,'sourceReportCommit':catalog['sourceReportCommit'],'bundleSha256':bundle_sha},allow_val_change=True)
        run.log({**metrics,'attempts':wandb.Table(columns=columns,data=rows),'originalCaptures':wandb.Table(columns=['originalImage','kind','trialOrQualificationId','primary','artifactPath','sha256','source'],data=captures),**{'figures/'+p.stem:wandb.Image(str(p),caption=p.stem+' · derived from frozen recorded evidence; see source catalog') for p in figures}})
        run.summary.update({**metrics,'originalCaptureCount':len(captures),'bundleSha256':bundle_sha,'evidenceBoundary':'Derived publication run; excludes new coding, inference, grading, and sandbox execution. Primary 19/39; all 129 native outcomes retained.'})
        published=run.log_artifact(artifact,aliases=['latest']).wait()
        artifact_name=published.name
        run_url=run.url
    api=wandb.Api();remote=api.artifact(f'{entity}/{project}/{artifact_name}')
    checked=[]
    for name,p in sorted(paths.items()):
        digest=base64.b64encode(hashlib.md5(p.read_bytes()).digest()).decode()
        assert remote.manifest.entries[name].digest==digest,name
        checked.append({'path':name,'sha256':sha(p),'bytes':p.stat().st_size})
    # Download the portable artifact as well, so manifest agreement is not the only check.
    downloaded=Path(remote.get_entry('forge-visual-evidence.zip').download(root=str(ROOT/'forge/local-results/article-visual-readback')))
    assert sha(downloaded)==bundle_sha
    for _ in range(12):
        api.flush();stored=api.run(f'{entity}/{project}/{run_id}')
        if stored.summary.get('recordedAttempts')==129 and stored.summary.get('originalCaptures') and stored.summary.get('bundleSha256')==bundle_sha:break
        time.sleep(5)
    assert stored.summary['recordedAttempts']==129 and stored.summary['primaryPasses']==19
    assert stored.config['sourceCommit']==source
    assert stored.summary['attempts']['nrows']==129
    assert stored.summary['originalCaptures']['nrows']==123
    view=ws.Workspace.from_url(previous['workspaceUrl']) if previous.get('workspaceUrl') else ws.Workspace(entity=entity,project=project)
    view.name='Forge course — article visuals and full evidence'
    view.runset_settings=ws.RunsetSettings(filters=[expr.Config('dashboardKind')=='article-visual-evidence'],pinned_columns=['name'])
    view.settings=ws.WorkspaceSettings(max_runs=1)
    def section(name,panels):return ws.Section(name=name,panels=panels,is_open=True,layout_settings=SummaryLayout(columns=3,rows=2) if name.startswith('Saved evidence') else ReadableLayout(columns=1,rows=1))
    view.sections=[
        section('Saved evidence • derived publication, not another coding attempt',[wr.ScalarChart(title=title,metric=metric,legend_template='Saved evidence',layout=wr.Layout(x=(i%3)*8,y=(i//3)*5,w=8,h=5)) for i,(title,metric) in enumerate([('Completed attempts — all cohorts','recordedAttempts'),('Primary denominator','primaryAttempts'),('Primary passes','primaryPasses'),('Original captures','originalCaptureCount'),('Data figures','dataFigures'),('Source files matched to artifact','verifiedSourceFiles')])]),
        section('Recorded figures • primary checks, role allowances, two-hour timer',[wr.MediaBrowser(title=p.stem,media_keys=['figures/'+p.stem],num_columns=1,mode='gallery',gallery_axis='index',layout=wr.Layout(x=0,y=i*12,w=24,h=12)) for i,p in enumerate(figures)]),
        section('All 129 attempts • native outcomes, primary membership, source links',[wr.WeavePanelSummaryTable(table_name='attempts',layout=wr.Layout(x=0,y=0,w=24,h=12))]),
        section('123 originals • application, dashboard, notebook, trace and diagnostic captures',[wr.WeavePanelSummaryTable(table_name='originalCaptures',layout=wr.Layout(x=0,y=0,w=24,h=14))])]
    view.save()
    restored=ws.Workspace.from_url(view.url);assert len(restored.sections)==4
    receipt={'schemaVersion':1,'publishedAt':datetime.now(timezone.utc).isoformat(),'entity':entity,'project':project,'access':'PRIVATE','sourceCommit':source,'sourceReportCommit':catalog['sourceReportCommit'],'publisherSha256':sha(Path(__file__)),'runId':run_id,'runUrl':forge_url(run_url,entity),'workspaceUrl':view.url,'forgeUrl':forge_url(view.url,entity),'artifact':f'{entity}/{project}/{artifact_name}','artifactUrl':f'https://wandb.ai/{entity}/{project}/artifacts/course-evidence/{artifact_name}','bundleSha256':bundle_sha,'counts':metrics,'readback':{'verified':True,'files':len(checked),'downloadedBundleMatches':True,'attemptTableRows':129,'captureTableRows':123,'workspaceSections':4},'files':checked,'browserVerification':{'verified':False,'reason':'Pending authenticated native workspace inspection'}}
    RECEIPT.parent.mkdir(parents=True,exist_ok=True);RECEIPT.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['forgeUrl','artifactUrl','runUrl','readback']},indent=2))

if __name__=='__main__':main()
