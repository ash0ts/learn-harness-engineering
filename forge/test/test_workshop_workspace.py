"""Exercise the real notebook-to-TypeScript edit boundary without paid services."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'forge/scripts'))
from workshop_workspace import WorkshopWorkspace


class WorkshopNotebookTest(unittest.TestCase):
    def test_edit_check_export_import_and_duplicate_start(self):
        with tempfile.TemporaryDirectory() as directory:
            learner = WorkshopWorkspace.__new__(WorkshopWorkspace)
            learner.root = ROOT
            learner.results = Path(directory) / 'evidence'
            learner.results.mkdir()
            learner.base = Path(directory)
            learner.revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            learner.project = 'project-01'
            learner.env = dict(os.environ)
            learner.secrets = {'private-test-credential'}
            learner.state = {'prepared': True, 'workshop': {'ready': True}, 'notes': {}, 'actions': []}
            learner.process = None
            learner.connected = True
            learner.lock = threading.Lock()
            learner.persist = lambda: None
            learner.write = lambda: None
            learner.view = lambda: {'trials': []}
            learner.ledger = lambda: {'limitUsd': 20, 'spentEstimateUsd': 4, 'reservations': {}}
            learner.run_command(learner.workshop_command('init', '--project', 'project-01', '--source', learner.revision), cwd=ROOT)
            initial = learner.workshop_files()
            self.assertEqual(len(initial['files']), 2)
            with self.assertRaises(ValueError):
                learner.save_edits({**initial['files'], 'workshop/inference.ts': 'private-test-credential'})
            saved = learner.save_edits(initial['files'])
            self.assertEqual(learner.check_edits()['outcome'], 'task_failed')
            example = json.loads((ROOT / 'forge/workshop/examples/project-01/files.json').read_text())
            completed = learner.save_edits(example)
            self.assertNotEqual(saved['snapshot']['sha256'], completed['snapshot']['sha256'])
            self.assertEqual(learner.check_edits()['outcome'], 'passed')
            exported = learner.export_workspace()
            self.assertNotIn(b'private-test-credential', exported)
            self.assertNotIn(b'/Users/', exported)
            preview = learner.preview_workspace_import(exported)
            self.assertEqual(preview['changes'], [])
            learner.apply_workspace_import()
            self.assertEqual(learner.state['workshop']['parent'], completed['snapshot']['id'])
            learner.save_edits(example)
            launches = []
            learner.launch = lambda commands, index: launches.append(commands[index])
            identifier = learner.start_workshop('offline-app', 'restart', 'short', 'question')
            self.assertIn('--snapshot', launches[0])
            self.assertEqual(learner.state['pending']['id'], identifier)
            with self.assertRaises(RuntimeError):
                learner.start_workshop('offline-app', 'restart', 'short', 'question')
            self.assertEqual(len(launches), 1)
            self.assertIsNone(learner.export_workspace())


if __name__ == '__main__':
    unittest.main()
