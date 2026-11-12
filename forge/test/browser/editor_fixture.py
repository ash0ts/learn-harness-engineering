"""Generate a credential-free browser regression for the actual workbench cells.

python forge/test/browser/editor_fixture.py /tmp/workshop-editor-check.py
uv run --with marimo==0.25.1 marimo run /tmp/workshop-editor-check.py --port 4278

Click Save, then edit both tabs while the simulated checkpoint takes eight
seconds. Both files must remain dirty afterwards. Save again and confirm both
values in the saved-files output. No inference, sandbox, or W&B call is made.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import workshop_cells as workshop

files = ['first.ts', 'second.md']
setup = '''def _():
    import marimo as mo
    import hashlib
    import json
    import time
    class FakeWorkspace:
        def __init__(self):
            self.files = {'first.ts': 'export const first = 0;', 'second.md': '# Second draft'}
            self.state = {'workshop': {}}
        def workshop_files(self):
            return {'files': self.files.copy()}
        def save_edits(self, values):
            self.files = values.copy()
            _hash = hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
            self.state['workshop']['draftSnapshot'] = _hash[:12]
            time.sleep(8)
            return {'snapshot': {'id': _hash[:12], 'sha256': _hash}}
        def redact(self, error):
            return str(error)
    learner = FakeWorkspace()
    workshop_initial = learner.workshop_files()
    return learner, mo, workshop_initial
'''
readback = '''def _(get_workshop_save, learner, mo):
    get_workshop_save()
    mo.md('Saved files: ' + repr(learner.workshop_files()['files']))
    return
'''
cells = [setup, workshop.STATE, *workshop.editor_cells(files), workshop.EDIT_BUTTONS,
         workshop.SAVE, workshop.DIRTY, workshop.RELOAD, readback]
source = 'import marimo\napp = marimo.App()\n\n' + '\n\n'.join('@app.cell\n' + cell for cell in cells) + '\n\nif __name__ == "__main__": app.run()\n'
Path(sys.argv[1]).write_text(source)
