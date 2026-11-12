"""Bind an observed notebook button run to its source, checkpoint and paid trial."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / 'forge/local-results'

def execution_hash(source):
    nodes = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)
             and 'subprocess.run(_command' in ast.unparse(n)]
    if len(nodes) != 1:
        raise RuntimeError('Expected one shared notebook execution cell')
    return hashlib.sha256(ast.dump(nodes[0]).encode()).hexdigest()

def build():
    file = LOCAL / 'notebook-rerun-qualification.json'
    receipt = json.loads(file.read_text())
    if receipt['status'] != 'runner_finished' or receipt['exitCode'] != 0:
        raise RuntimeError('No observed completed notebook action')
    source = Path(receipt['sourceFile']).read_bytes()
    if hashlib.sha256(source).hexdigest() != receipt['sourceSha256']:
        raise RuntimeError('Qualified notebook source changed')
    cell = execution_hash(source)
    canonical = (ROOT / 'forge/notebooks/07-bounded-loops.py').read_bytes()
    if cell != receipt['executionCellAstSha256'] or execution_hash(canonical) != cell:
        raise RuntimeError('Canonical execution cell differs from the tested action')
    checkpoint = json.loads(Path(receipt['checkpoint']).read_text())
    if checkpoint['sourceCommit'] != receipt['runnerCommit'] or checkpoint.get('pendingTrialId'):
        raise RuntimeError('Checkpoint source or pending launch is inconsistent')
    if len(checkpoint['rounds']) != 1 or checkpoint['status'] not in ['passed', 'round_limit', 'deadline']:
        raise RuntimeError('The one-round action did not reach its bounded stop')
    ledger = json.loads((LOCAL / 'budget.json').read_text())
    ids = []
    for round in checkpoint['rounds']:
        row = json.loads((LOCAL / round['trialId'] / 'trial.json').read_text())
        if (not row.get('finishedAt') or not row.get('wandbRunUrl') or not row.get('artifactUrl')
                or row['sourceCommit'] != receipt['runnerCommit']
                or row['outcome'] != round['outcome'] or row['id'] not in ledger['settled']):
            raise RuntimeError('Notebook checkpoint lacks completed, uploaded, settled trial evidence')
        ids.append(row['id'])
    ui = json.loads(Path(receipt['uiResult']).read_text())
    if ui.get('click') != 1 or ui.get('status') != 'Runner finished' or ui.get('exit_code') != 0 or not all(identifier in ui.get('stdout','') for identifier in ids):
        raise RuntimeError('Observed notebook UI result differs from trial evidence')
    screenshot = Path(receipt['screenshot']).read_bytes()
    receipt.update(verified=True, verifiedAt=datetime.now(timezone.utc).isoformat(),
                   trialIds=ids, stopReason=checkpoint['status'],
                   screenshotSha256=hashlib.sha256(screenshot).hexdigest(),
                   limitation='Executed through the notebook UI with an explicitly configured local shared coordinator; the hosted default has no mounted coordinator.')
    file.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'verified': True, 'trialIds': ids, 'stopReason': checkpoint['status']}))
    return receipt

if __name__ == '__main__':
    build()
