"""Validate canonical notebook sources and execute their unpaid saved-results view."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import os
import subprocess
from html.parser import HTMLParser
from collections import Counter
from create_notebooks import project_snapshot,TITLES
from workshop_teaching import LABS

ROOT = Path(__file__).resolve().parents[2]

def validate_course_view(session, tree):
    """Check the visible cohort independently and require native course assets."""
    assignments = {n.targets[0].id:n.value for n in ast.walk(tree)
                   if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
    saved=json.loads(ast.literal_eval(assignments['saved'].args[0]))
    primary_ids=ast.literal_eval(assignments['primary_ids'])
    files=json.loads(ast.literal_eval(assignments['lesson_files'].args[0]))
    if 'LAB.md' not in files or 'observations.csv' not in files or 'comparison.md' not in files:
        raise RuntimeError('Missing downloadable course submission material')
    class Content(HTMLParser):
        def __init__(self):
            super().__init__(); self.tables=[]; self.images=[]; self.downloads=[]
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='marimo-table':
                value=json.loads(attrs['data-data'])
                if isinstance(value,str):value=json.loads(value)
                self.tables.append(value)
            elif tag=='img':self.images.append(attrs)
            elif tag=='marimo-download':self.downloads.append(attrs)
    content=Content()
    for cell in session['cells']:
        for output in cell.get('outputs',[]):content.feed(output.get('data',{}).get('text/html',''))
    rows=[r for r in saved['trials'] if r['id'] in primary_ids]
    expected=[]
    for task,variant in sorted({(r['project'],r['variant']) for r in rows}):
        group=[r for r in rows if (r['project'],r['variant'])==(task,variant)]
        expected.append({'Project':task,'Treatment':variant,'Passed':sum(r['outcome']=='passed' for r in group),'Attempts':len(group),'Other outcomes':', '.join(f"{v} {k.replace('_',' ')}" for k,v in Counter(r['outcome'] for r in group if r['outcome']!='passed').items()) or 'None'})
    actual=[t for t in content.tables if isinstance(t,list) and t and isinstance(t[0],dict) and 'Treatment' in t[0]]
    if actual != ([expected] if expected else []):raise RuntimeError('Primary displayed cohort does not match recorded evidence')
    if not content.images or any(not i.get('alt') or not i.get('src','').startswith('data:image/') for i in content.images):
        raise RuntimeError('Native self-contained figures and alt text are required')
    if len(content.downloads)<2:raise RuntimeError('Worksheet and lab packet downloads were not rendered')
    return {'primaryGroups':len(expected),'nativeImages':len(content.images),'packetFiles':len(files)}

def validate(export=True,projects=None):
    sources = sorted((ROOT / 'forge/notebooks').glob('*.py'))
    if len(sources) != 9:
        raise RuntimeError('Expected overview plus eight project notebooks')
    output = ROOT / 'forge/local-results/notebook-html'
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for source in sources:
        tree = ast.parse(source.read_text())
        assignments = {node.targets[0].id: node.value for node in ast.walk(tree)
                       if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)}
        saved = json.loads(ast.literal_eval(assignments['saved'].args[0]))
        project=ast.literal_eval(assignments['project_id'])
        if projects and project not in projects:continue
        master=json.loads((ROOT / 'forge/results/snapshot.json').read_text())
        expected=project_snapshot(master,project)
        for key in ['trials','completedComparisonBlocks','loops','graphs','qualifications','concurrencyQualifications','sandboxQualifications','visibleUiQualifications']:
            if saved.get(key,[])!=expected.get(key,[]):
                raise RuntimeError(f'{source.name}: stale {key}; regenerate this notebook')
        # Earlier completed projects may be published while the timer runs.
        # Their budget snapshot retains its capture time; prior settlements must
        # still agree with the final ledger rather than being silently rewritten.
        for identifier,amount in saved.get('budget',{}).get('settled',{}).items():
            if master.get('budget',{}).get('settled',{}).get(identifier)!=amount:
                raise RuntimeError(f'{source.name}: historical budget settlement changed')
        subprocess.run(['uv', 'run', '--with', 'marimo==0.25.1', 'marimo', 'check', str(source)], check=True, cwd=ROOT)
        row = {'file': str(source.relative_to(ROOT)), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'runnerCommit': ast.literal_eval(assignments['runner_commit']), 'syntaxValidated': True, 'rendered': False}
        if export:
            dest = output / (source.stem + '.html')
            # A missing credential is intentional: the initial view must need no paid execution.
            env = {key: value for key, value in os.environ.items() if key not in {'WANDB_API_KEY', 'FORGE_RUNNER_ROOT'}}
            subprocess.run(['uv', 'run', '--with', 'marimo==0.25.1', 'marimo', 'export', 'html', str(source), '-o', str(dest), '--force', '--no-include-code'], cwd=ROOT, env=env, check=True, timeout=120)
            html = dest.read_text()
            marker = '"session": '
            session, _ = json.JSONDecoder().raw_decode(html[html.index(marker) + len(marker):])
            errors = [item for cell in session['cells'] for item in cell.get('outputs', [])
                      if item.get('type') == 'error' or 'application/vnd.marimo+error' in item.get('data', {})]
            if errors:
                raise RuntimeError(f'{source.name}: rendering errors: {errors}')
            if ('Not launched' not in html and not (project=='overview' and 'Eight hands-on labs' in html)) or 'Saved results' not in html:
                raise RuntimeError(f'{source.name}: missing expected saved view')
            if 'workshop_initial' in assignments and ('marimo-code-editor' not in html or 'Save and check my edits' not in html or 'Next step:' not in html):
                raise RuntimeError(f'{source.name}: missing native workshop workbench')
            if project in LABS:
                for _,label,_,_ in LABS[project]['actions']:
                    if label not in html:raise RuntimeError(source.name+': missing named activity '+label)
                if 'Lesson action' in html:raise RuntimeError('Obsolete action dropdown remains')
            row.update(rendered=True, htmlSha256=hashlib.sha256(dest.read_bytes()).hexdigest(),courseView=validate_course_view(session,tree))
        rows.append(row)
        print(source.name, 'passed', flush=True)
    (ROOT / 'forge/local-results/notebook-validation.json').write_text(json.dumps({'schemaVersion': 1, 'notebooks': rows}, indent=2) + '\n')
    return rows

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--syntax-only', action='store_true')
    parser.add_argument('--project',action='append',choices=[r[1] for r in TITLES])
    args=parser.parse_args();validate(not args.syntax_only,args.project)
