"""Audit the authorized workbench replacement against the preceding lessons."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import textwrap

ROOT = Path(__file__).resolve().parents[2]
BASELINE = '32942db5ec54bdd08c5c0c860443a4cd0c724ed9'

def original(path):
    return subprocess.check_output(['git', 'show', BASELINE + ':' + path], cwd=ROOT)

def assignments(tree):
    return {n.targets[0].id: n.value for n in ast.walk(tree)
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}

def validate():
    historical = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE,
        '--', 'forge/lessons', 'forge/results/snapshot.json', 'projects'], cwd=ROOT, text=True).splitlines()
    for name in historical:
        if original(name) != (ROOT/name).read_bytes():
            raise RuntimeError('Historical source or evidence changed: ' + name)
    rows = []
    for path in sorted((ROOT/'forge/notebooks').glob('*.py')):
        name = path.relative_to(ROOT).as_posix()
        before = original(name)
        old, new = ast.parse(before), ast.parse(path.read_text())
        a, b = assignments(old), assignments(new)
        for field in ['saved', 'primary_ids', 'lesson_files']:
            if ast.dump(a[field]) != ast.dump(b[field]):
                raise RuntimeError('Historical payload changed: ' + name + ':' + field)
        if int(path.name[:2]) >= 6 and before != path.read_bytes():
            raise RuntimeError('Project 06–08 changed: ' + name)
        # Each original narrative section must remain verbatim and in order.
        constants = [textwrap.dedent(n.value).strip() for n in ast.walk(new)
                     if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        sections = (ROOT/'forge/lessons'/path.name.replace('.py', '.md')).read_text().split('<!-- cell -->')
        indices = [constants.index(section.strip()) for section in sections if section.strip()]
        if indices != sorted(indices):
            raise RuntimeError('Historical narrative order changed: ' + name)
        old_images = [ast.dump(n) for n in ast.walk(old) if isinstance(n, ast.Call)
                      and isinstance(n.func, ast.Attribute) and n.func.attr == 'image']
        new_images = [ast.dump(n) for n in ast.walk(new) if isinstance(n, ast.Call)
                      and isinstance(n.func, ast.Attribute) and n.func.attr == 'image']
        if any(image not in new_images for image in old_images):
            raise RuntimeError('Historical image changed: ' + name)
        rows.append({'file': name, 'historicalPayloadsAndNarrativePreserved': True,
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    receipt = {'schemaVersion': 1, 'baselineCommit': BASELINE,
               'unchangedHistoricalFiles': len(historical), 'notebooks': rows,
               'authorizedChanges': 'forge/lessons/workshop-preservation.md'}
    output = ROOT/'forge/local-results/workshop-preservation.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2)+'\n')
    print(f'Preserved {len(historical)} historical files and all nine notebook evidence payloads')
    return receipt

if __name__ == '__main__':
    validate()
