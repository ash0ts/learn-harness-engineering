# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0"]
# ///
"""Create notebook records and verify normal-editor publication. Never uploads source.

Commands: ensure (metadata only), check-remote FILE (before editing), verify FILE.
The authenticated Forge EDIT/Marimo save workflow performs the source commit.
"""
import argparse
import ast
import base64
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import textwrap
import urllib.parse
import urllib.request

from create_notebooks import TITLES
from validate_notebooks import validate_course_view

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'forge/publication-manifest.json'
FIELDS = 'id name lastSourceEditedAt lastStaticOutputAt staticOutputUrl viewerPermissions currentVersion {artifactTypeName artifactCollectionName versionIndex sourceFileName}'

def now():
    return datetime.now(timezone.utc).isoformat()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def save(manifest):
    temporary = MANIFEST.with_suffix('.tmp')
    temporary.write_text(json.dumps(manifest, indent=2) + '\n')
    temporary.replace(MANIFEST)

def gql(query, variables=None):
    key = os.environ.get('WANDB_API_KEY')
    if not key:
        raise RuntimeError('Supply WANDB_API_KEY externally')
    request = urllib.request.Request('https://api.wandb.ai/graphql', data=json.dumps({'query': query, 'variables': variables or {}}).encode(), headers={'Content-Type':'application/json','Authorization':'Basic '+base64.b64encode(('api:'+key).encode()).decode()})
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError(str(result['errors']))
    return result['data']

def load():
    entity = os.environ['WANDB_ENTITY']
    project = os.environ.get('WANDB_PROJECT', 'learn-harness-engineering-forge')
    project_data = gql('query($e:String!,$p:String!){project(entityName:$e,name:$p){access}}', {'e':entity,'p':project})['project']
    if not project_data or project_data['access'] != 'PRIVATE':
        raise RuntimeError('Publication requires an existing PRIVATE project')
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {'schemaVersion':1,'entity':entity,'project':project,'notebooks':[]}
    if (manifest['entity'],manifest['project']) != (entity,project):
        raise RuntimeError('Destination differs from existing manifest; do not recreate notebook IDs')
    return manifest

def remote(notebook_id):
    data = gql('query($id:ID!){notebook(id:$id){'+FIELDS+'}}', {'id':notebook_id})['notebook']
    if not data or 'EDIT' not in data['viewerPermissions']:
        raise RuntimeError('Notebook missing or EDIT permission unavailable')
    return data

def source_bytes(manifest, notebook):
    import wandb
    version = notebook['currentVersion']
    if not version or version['sourceFileName'] != 'notebook.py':
        raise RuntimeError('No recognized committed source version')
    name = f"{manifest['entity']}/{manifest['project']}/{version['artifactCollectionName']}:v{version['versionIndex']}"
    artifact = wandb.Api().artifact(name, type=version['artifactTypeName'])
    destination = ROOT / 'forge/local-results/publication' / hashlib.sha256(notebook['id'].encode()).hexdigest()[:16]
    destination.mkdir(parents=True, exist_ok=True)
    downloaded = artifact.get_entry('notebook.py').download(root=str(destination))
    return Path(downloaded).read_bytes()

def ensure(manifest):
    for filename, project, title, _ in TITLES:
        file = 'forge/notebooks/' + filename
        row = next((r for r in manifest['notebooks'] if r['file']==file), None)
        if row and row.get('id'):
            print(filename, 'reusing', row['id'], flush=True)
            continue
        if row:
            raise RuntimeError(f'{filename}: previous creation is uncertain; reconcile remote inventory before retrying')
        canonical = ROOT / file
        revision = subprocess.check_output(['git','log','-1','--format=%H','--',file],cwd=ROOT,text=True).strip()
        if not revision:
            raise RuntimeError('Commit canonical notebook before creating its remote record')
        row = {'file':file,'project':project,'title':title,'sourceCommit':revision,'sha256':digest(canonical.read_bytes()),'id':None,'url':None,'status':'creating','createdAt':now()}
        manifest['notebooks'].append(row); save(manifest)
        created = gql('mutation($i:CreateNotebookInput!){createNotebook(input:$i){notebook{'+FIELDS+'}}}', {'i':{'entityName':manifest['entity'],'projectName':manifest['project'],'template':'BASIC'}})['createNotebook']['notebook']
        row.update(id=created['id'],url='https://forge.coreweave.com/notebooks/'+urllib.parse.quote(created['id'],safe=''),status='created_basic_not_uploaded')
        save(manifest)  # Persist ID before rename so retries never duplicate it.
        renamed = gql('mutation($i:RenameNotebookInput!){renameNotebook(input:$i){notebook{'+FIELDS+'}}}', {'i':{'id':row['id'],'name':title}})['renameNotebook']['notebook']
        row['expectedRemoteVersion'] = renamed['currentVersion']
        row['expectedRemoteEditedAt'] = renamed['lastSourceEditedAt']
        row['expectedRemoteSha256'] = digest(source_bytes(manifest,renamed)) if renamed['currentVersion'] else None
        row['publicationBlocker'] = 'Canonical source awaits a reserved authenticated EDIT session and verification'
        save(manifest); print(filename, row['status'], flush=True)
    return manifest

def select(manifest, file):
    rows = [r for r in manifest['notebooks'] if Path(r['file']).name == Path(file).name]
    if len(rows) != 1 or not rows[0].get('id'):
        raise RuntimeError('Notebook is not in the publication manifest')
    return rows[0]

def check_remote(manifest, row):
    notebook = remote(row['id'])
    actual_hash = digest(source_bytes(manifest,notebook)) if notebook['currentVersion'] else None
    if (notebook['currentVersion'] != row.get('expectedRemoteVersion') or notebook['lastSourceEditedAt'] != row.get('expectedRemoteEditedAt') or actual_hash != row.get('expectedRemoteSha256')):
        raise RuntimeError('Remote edits detected; preserve and review remote source before replacing it')
    print('Remote source unchanged; normal authenticated EDIT workflow may proceed only with a reserved compute budget.')

def check_source(manifest, row):
    """Read back source after the edit runtime's final flush, before a clean render."""
    notebook = remote(row['id'])
    canonical = (ROOT/row['file']).read_bytes()
    revision = subprocess.check_output(['git','log','-1','--format=%H','--',row['file']],cwd=ROOT,text=True).strip()
    if subprocess.check_output(['git','show',revision+':'+row['file']],cwd=ROOT) != canonical:
        raise RuntimeError('Commit canonical source before publication')
    if source_bytes(manifest,notebook) != canonical:
        raise RuntimeError('Committed currentVersion source does not match canonical source')
    print(row['file'],'committed_source_verified','version',notebook['currentVersion']['versionIndex'],digest(canonical))

def verify_rendered_source(html, canonical):
    """Bind outputs to canonical cell code, including when Forge omits legacy timestamps."""
    text = html.decode()
    def embedded(name):
        marker = json.dumps(name) + ': '
        return json.JSONDecoder().raw_decode(text[text.index(marker)+len(marker):])[0]
    notebook, session = embedded('notebook'), embedded('session')
    expected = []
    source_lines = canonical.decode().splitlines(keepends=True)
    for node in ast.parse(canonical).body:
        if isinstance(node, ast.FunctionDef) and node.decorator_list:
            body = node.body[:-1] if isinstance(node.body[-1], ast.Return) else node.body
            # Marimo stores editor cells outside the generated function wrapper.
            # Dedent that source before parsing, including multiline Markdown
            # literals. Parsing the indented function first preserves four
            # wrapper spaces inside those literals and falsely rejects the
            # editor's normal serialization. Source bytes are checked separately.
            cell_source = textwrap.dedent(''.join(source_lines[body[0].lineno-1:body[-1].end_lineno])) if body else ''
            expected.append(ast.dump(ast.parse(cell_source)))
    cells = notebook['cells']
    actual = [ast.dump(ast.parse(cell['code'])) for cell in cells]
    if actual != expected:
        raise RuntimeError('Rendered cell source differs from canonical notebook')
    outputs = {cell['id']:cell for cell in session['cells']}
    if len(outputs) != len(cells):
        raise RuntimeError('Rendered session has missing or duplicate cells')
    for cell in cells:
        code_hash = hashlib.md5(cell['code'].encode(), usedforsecurity=False).hexdigest()
        if cell['code_hash'] != code_hash or outputs.get(cell['id'],{}).get('code_hash') != code_hash:
            raise RuntimeError('Rendered output belongs to different cell source')
        for output in outputs[cell['id']].get('outputs',[]):
            if output.get('type') == 'error' or 'application/vnd.marimo+error' in output.get('data',{}):
                raise RuntimeError('Hosted rendered output contains a cell error')
    return session

def verify_rendered_aggregates(session, canonical):
    assignments={n.targets[0].id:n.value for n in ast.walk(ast.parse(canonical)) if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
    saved=json.loads(ast.literal_eval(assignments['saved'].args[0]))
    project=ast.literal_eval(assignments['project_id'])
    rows=[r for r in saved['trials'] if project=='overview' or r['project']==project]
    groups={}
    for row in rows:groups.setdefault((row['project'],row['variant'],row['sourceCommit']),[]).append(row)
    expected=[]
    for (task,variant,source),group in sorted(groups.items()):
        counts={outcome:sum(r['outcome']==outcome for r in group) for outcome in ['passed','task_failed','infrastructure_failed','telemetry_missing']}
        expected.append({'project':task,'variant':variant,'source_commit':source,'attempts':len(group),**counts,'known_estimate_usd':round(sum(r.get('reconciledEstimateUsd',r.get('estimatedCostUsd')) or 0 for r in group),6),'unknown_cost_attempts':sum(r.get('estimatedCostUsd') is None and r.get('reconciledEstimateUsd') is None for r in group)})
    class Tables(HTMLParser):
        tables=[]
        def handle_starttag(self,tag,attrs):
            if tag=='marimo-table':
                value=json.loads(dict(attrs)['data-data'])
                if isinstance(value,str):value=json.loads(value)
                if isinstance(value,list):self.tables.append(value)
    parser=Tables()
    for cell in session['cells']:
        for output in cell.get('outputs',[]):parser.feed(output.get('data',{}).get('text/html',''))
    aggregates=[table for table in parser.tables if table and isinstance(table[0],dict) and 'attempts' in table[0] and 'variant' in table[0]]
    if (expected and aggregates!=[expected]) or (not expected and aggregates):
        raise RuntimeError('Displayed aggregates do not reproduce the recorded trial evidence')
    return len(expected)

def verify(manifest, row):
    notebook = remote(row['id'])
    canonical = (ROOT/row['file']).read_bytes()
    if digest(source_bytes(manifest,notebook)) != digest(canonical):
        raise RuntimeError('Committed currentVersion source does not match canonical source')
    edited = notebook['lastSourceEditedAt']
    rendered = notebook['lastStaticOutputAt']
    if rendered and datetime.fromisoformat(rendered.replace('Z','+00:00')) < datetime.fromisoformat(edited.replace('Z','+00:00')):
        raise RuntimeError('Rendered output predates committed source')
    url = notebook['staticOutputUrl']
    if not url or urllib.parse.urlsplit(url).scheme != 'https':
        raise RuntimeError('Missing HTTPS rendered output')
    # The API returns a signed artifact URL. Never send the W&B credential to it.
    with urllib.request.urlopen(url, timeout=30) as response:
        html = response.read()
    session = verify_rendered_source(html, canonical)
    aggregate_groups=verify_rendered_aggregates(session,canonical)
    course_view=validate_course_view(session,ast.parse(canonical))
    rendered_text = json.dumps(session,ensure_ascii=False)
    idle_view = 'Not launched' in rendered_text or (row['project'] == 'overview' and 'Five hands-on labs' in rendered_text)
    if 'Saved results' not in rendered_text or not idle_view or row['title'] not in rendered_text:
        raise RuntimeError('Expected saved-results view and idle run control were not rendered')
    revision = subprocess.check_output(['git','log','-1','--format=%H','--',row['file']],cwd=ROOT,text=True).strip()
    committed_source = subprocess.check_output(['git','show',revision+':'+row['file']],cwd=ROOT)
    if committed_source != canonical:
        raise RuntimeError('Canonical source has uncommitted edits; commit it before recording publication')
    if remote(row['id'])['currentVersion'] != notebook['currentVersion']:
        raise RuntimeError('Remote source changed during verification')
    evidence = ROOT/'forge/local-results/publication'/hashlib.sha256(row['id'].encode()).hexdigest()[:16]
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence/'rendered.html').write_bytes(html)
    row.update(sourceCommit=revision,status='published_verified',sha256=digest(canonical),currentVersion=notebook['currentVersion'],expectedRemoteVersion=notebook['currentVersion'],expectedRemoteEditedAt=edited,expectedRemoteSha256=digest(canonical),renderedOutputSha256=digest(html),renderedCellSourceVerified=True,verifiedAggregateGroups=aggregate_groups,lastStaticOutputAt=rendered,verifiedAt=now())
    row.pop('publicationBlocker',None)
    row['verifiedCourseView'] = course_view
    save(manifest)
    print(row['file'],'published_verified',row['url'])

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['ensure','check-remote','check-source','verify'])
    parser.add_argument('file',nargs='?')
    args=parser.parse_args(); manifest=load()
    if args.command=='ensure': ensure(manifest)
    elif args.command=='check-remote': check_remote(manifest,select(manifest,args.file or ''))
    elif args.command=='check-source': check_source(manifest,select(manifest,args.file or ''))
    else: verify(manifest,select(manifest,args.file or ''))
