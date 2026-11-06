"""Validate canonical notebook sources and execute their unpaid saved-results view."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]

def validate(export=True):
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
        if saved != json.loads((ROOT / 'forge/results/snapshot.json').read_text()):
            raise RuntimeError(f'{source.name}: stale embedded evidence; regenerate notebooks')
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
            if 'Not launched' not in html or 'Saved results' not in html:
                raise RuntimeError(f'{source.name}: missing expected saved view')
            row.update(rendered=True, htmlSha256=hashlib.sha256(dest.read_bytes()).hexdigest())
        rows.append(row)
        print(source.name, 'passed', flush=True)
    (ROOT / 'forge/local-results/notebook-validation.json').write_text(json.dumps({'schemaVersion': 1, 'notebooks': rows}, indent=2) + '\n')
    return rows

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--syntax-only', action='store_true')
    validate(not parser.parse_args().syntax_only)
