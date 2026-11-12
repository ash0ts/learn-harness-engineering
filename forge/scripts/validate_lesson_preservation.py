"""Audit the repair against the supplied lesson iteration, without changing it."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASELINE = 'a33df54f2ae2fef63dcdf9377a469ef02ee10971'
FACTUAL_EDITS = [
    ('Before each attempt the copy sets aside a worst case of about $4.20, and it will not start if that would pass the limit, so leave the limit at $20 unless you have a reason to lower it.', 'Before each sandbox or model request the copy sets aside its maximum estimated cost, and it stops before an operation that would pass the limit, so leave the limit at $20 unless you have a reason to lower it.'),
    ('Each treatment runs once per copy.', 'Start can run another completed treatment; each attempt keeps its own checkpoint.'),
    ('Either way the graph runs once per copy.', 'Start can run another graph after the current graph finishes or you decide its approval candidate.'),
    ('It is a small paid test that the model, the sandbox and the tracing all respond, and it cleans up after itself.', 'It is a small paid test that the model, the sandbox and the tracing all respond, followed by checks that the unfinished app fails and the protected repair passes; it cleans up after itself.'),
    ('if the notebook session ends mid-run, this copy stops until your instructor has checked it. **Cancel the running action** has the same effect once an attempt has started, because its cost is then unknown.', 'if the notebook session ends mid-run, use Prepare and Connect to inspect the saved work. **Cancel the running action** waits for cleanup; missing usage or unverified cleanup keeps new paid work blocked until your instructor can reconcile it.'),
    ('find `project-08-graph-checkpoint.json`', 'find the latest `project-08-graph-…-checkpoint.json`'),
]

def original(path):
    return subprocess.check_output(['git', 'show', BASELINE + ':' + path], cwd=ROOT)

def assignment(tree, name):
    return next(n.value for n in ast.walk(tree) if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name)

def cells(tree):
    return [n for n in tree.body if isinstance(n, ast.FunctionDef)]

def labels(tree):
    return [ast.literal_eval(k.value) for n in ast.walk(tree) if isinstance(n, ast.Call) for k in n.keywords if k.arg in ('label', 'caption', 'alt') and isinstance(k.value, ast.Constant)]

def validate():
    checks = []
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE, '--', 'forge/lessons', 'forge/results/snapshot.json'], cwd=ROOT, text=True).splitlines()
    for path in paths:
        if original(path) != (ROOT/path).read_bytes():
            raise RuntimeError('Historical lesson, screenshot, or evidence changed: ' + path)
    for path in sorted((ROOT/'forge/notebooks').glob('*.py')):
        before = ast.parse(original(path.relative_to(ROOT).as_posix()))
        after = ast.parse(path.read_text())
        if len(cells(before)) != len(cells(after)):
            raise RuntimeError('Cell count changed: ' + path.name)
        if labels(before) != labels(after):
            raise RuntimeError('Control labels or image captions changed: ' + path.name)
        for name in ('saved', 'primary_ids', 'lesson_files'):
            if ast.dump(assignment(before, name)) != ast.dump(assignment(after, name)):
                raise RuntimeError('Historical results or lesson packet changed: ' + path.name)
        markdown_before, markdown_after = [], []
        for old, new in zip(cells(before), cells(after)):
            # The coordinator is executable implementation, not lesson prose.
            if any(isinstance(n, ast.ClassDef) and n.name == 'LessonWorkspace' for n in ast.walk(old)):
                continue
            for target, cell in [(markdown_before, old), (markdown_after, new)]:
                target.extend(n.value for n in ast.walk(cell) if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value not in {'prepared','pending','active'})
        old_commit = ast.literal_eval(assignment(before, 'runner_commit'))[:12]
        new_commit = ast.literal_eval(assignment(after, 'runner_commit'))[:12]
        normalized = []
        for value in markdown_before:
            for old, new in FACTUAL_EDITS:
                value = value.replace(old, new)
            if value == ast.literal_eval(assignment(before, 'runner_commit')):
                value = ast.literal_eval(assignment(after, 'runner_commit'))
            elif 'Your own attempts in this copy run with course runner revision' in value:
                value = value.replace(old_commit, new_commit)
            normalized.append(value)
        if normalized != markdown_after:
            raise RuntimeError('Unlisted prose or heading/order change: ' + path.name)
        checks.append({'file':path.relative_to(ROOT).as_posix(),'cellCount':len(cells(after)), 'labelsAndImagesUnchanged':True, 'historicalResultsUnchanged':True, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    receipt = {'schemaVersion':1,'baselineCommit':BASELINE,'historicalFilesUnchanged':len(paths),'factualSentenceEdits':[{'before':a,'after':b} for a,b in FACTUAL_EDITS], 'notebooks':checks}
    (ROOT/'forge/local-results/lesson-preservation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'Preserved {len(paths)} lesson/evidence files and all {len(checks)} notebooks; {len(FACTUAL_EDITS)} factual substitutions allowed')
    return receipt

if __name__ == '__main__':
    validate()
