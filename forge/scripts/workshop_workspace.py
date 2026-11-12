"""Notebook coordinator for the shared workshop CLI; no Python app implementation."""
from learner_workspace import LessonWorkspace
import hashlib
import json
from pathlib import Path
import uuid


class WorkshopWorkspace(LessonWorkspace):
    @property
    def student_workspace(self):
        return self.results / 'workshop' / 'workspace'

    def workshop_command(self, action, *args):
        return self.cli() + ['workshop', action, '--workspace', str(self.student_workspace),
                             '--output', str(self.results), *map(str, args)]

    def _prepare(self, limit):
        super()._prepare(limit)
        marker = self.root / '.workshop-dependencies'
        if not marker.exists():
            self.run_command(['npm', 'ci', '--ignore-scripts', '--prefix', 'forge/workshop/base'], cwd=self.root)
            marker.write_text(self.revision)
        self.run_command(self.workshop_command('init', '--project', self.project, '--source', self.revision), cwd=self.root)
        self.state.setdefault('workshop', {})['ready'] = True
        self.state['status'] = 'Workspace ready; inspect and edit the lesson files'
        self.persist()
        return self.view()

    def workshop_files(self):
        if not self.state.get('workshop', {}).get('ready'):
            return None
        manifest = json.loads((self.student_workspace / 'workshop.json').read_text())
        # Rendering is read-only and cheap. The CLI validates the authoritative
        # pinned manifest again before every save, import, check and execution.
        return {'manifest': manifest, 'files': {name: self.safe_path(self.student_workspace, name).read_text() for name in manifest['editable']}}

    def save_edits(self, files):
        with self.lock:
            if self.blocked():
                raise RuntimeError(self.blocked())
            target = self.results / 'workshop' / 'edited-files.json'
            encoded = json.dumps(files)
            if self.redact(encoded) != encoded:
                raise ValueError('Remove credentials from source before saving')
            target.write_text(encoded)
            args = ['--edits', str(target)]
            state = self.state.setdefault('workshop', {})
            if state.get('assisted'):
                args.append('--assisted')
            if state.get('parent'):
                args += ['--parent', state['parent']]
            value = json.loads(self.run_command(self.workshop_command('save', *args), cwd=self.root))
            state['draftSnapshot'] = value['snapshot']['id']
            state['draftSha256'] = value['snapshot']['sha256']
            state['diff'] = value['diff']
            self.persist()
            return value

    def check_edits(self):
        with self.lock:
            if self.blocked():
                raise RuntimeError(self.blocked())
            state = self.state.get('workshop', {})
            if not state.get('draftSnapshot'):
                raise RuntimeError('Save these edits first; the check runs the saved snapshot.')
            result = json.loads(self.run_command(self.workshop_command('check', '--snapshot', self.results / 'snapshots' / (state['draftSnapshot'] + '.json')), cwd=self.root, timeout=180))
            state['lastCheck'] = result
            self.persist()
            return result

    def start_workshop(self, action, scenario, fixture, question, single_role=False):
        with self.lock:
            if self.blocked():
                raise RuntimeError(self.blocked())
            if not self.connected:
                raise RuntimeError('Connect your own sandbox access before starting a paid action.')
            ledger = self.ledger()
            if ledger.get('halted') or ledger.get('reservations'):
                raise RuntimeError('An earlier cost or cleanup is unresolved. Prepare and Connect to recover it.')
            state = self.state.get('workshop', {})
            if not state.get('draftSnapshot'):
                raise RuntimeError('Save these edits first; execution uses that exact snapshot.')
            if action == 'resume' and not state.get('parent'):
                raise RuntimeError('Load a first-session candidate, then write and save its handoff before resuming.')
            if action not in ('offline-app', 'live-app', 'agent', 'resume'):
                raise ValueError('Unknown workshop action')
            identifier = str(uuid.uuid4())
            command = self.workshop_command('scenario' if action.endswith('-app') else action,
                '--snapshot', self.results / 'snapshots' / (state['draftSnapshot'] + '.json'),
                '--operation-id', identifier, '--scenario', scenario, '--fixture', fixture,
                '--question', question, '--execute')
            if action == 'live-app':
                command.append('--live')
            if single_role:
                command.append('--single-role')
            self.env['FORGE_BUDGET_USD'] = str(ledger['limitUsd'])
            self.state.update(status='Starting ' + action, pending={'id': identifier, 'operationIds': [identifier],
                'action': action, 'variant': 'workshop-v1', 'revision': self.revision,
                'snapshotId': state['draftSnapshot'], 'session': self.env.get('WANDB_NOTEBOOK_SESSION_ID'),
                'nextIndex': 0, 'launchStatus': 'not_created'})
            self._cached_checkpoint = None
            self.persist()
            self.launch([command], 0)
        return identifier

    def reveal_example(self):
        if self.blocked():
            raise RuntimeError(self.blocked())
        self.state.setdefault('workshop', {})['assisted'] = True
        self.persist()
        return json.loads((self.root / 'forge/workshop/examples' / self.project / 'files.json').read_text())

    def preview_workspace_import(self, data):
        if self.blocked():
            raise RuntimeError(self.blocked())
        if len(data) > 5_000_000:
            raise ValueError('Workspace source exceeds 5 MB')
        if any(secret and secret.encode() in data for secret in self.secrets):
            raise ValueError('Remove credentials from the uploaded source')
        target = self.results / 'workshop' / 'import.json'
        target.write_bytes(data)
        result = json.loads(self.run_command(self.workshop_command('import', '--input', target), cwd=self.root))
        incoming = json.loads(data)
        current = self.workshop_files()['files']
        result['diff'] = [{'path': name, 'before': current[name], 'after': incoming['files'][name]} for name in result['changes']]
        self.state.setdefault('workshop', {})['importSha256'] = hashlib.sha256(data).hexdigest()
        self.write()
        return result

    def apply_workspace_import(self):
        if self.blocked():
            raise RuntimeError(self.blocked())
        target = self.results / 'workshop' / 'import.json'
        state = self.state.setdefault('workshop', {})
        if hashlib.sha256(target.read_bytes()).hexdigest() != state.get('importSha256'):
            raise RuntimeError('Preview this uploaded snapshot before applying it')
        incoming = json.loads(target.read_bytes())
        result = json.loads(self.run_command(self.workshop_command('import', '--input', target, '--apply'), cwd=self.root))
        state['parent'] = incoming['id']
        state['assisted'] = bool(state.get('assisted') or incoming.get('assisted'))
        state.pop('draftSnapshot', None)
        self.persist()
        return result

    def preview_candidate(self, identifier):
        path = self.safe_path(self.results, identifier + '/candidate.json')
        return self.preview_workspace_import(path.read_bytes())

    def export_workspace(self):
        state = self.state.get('workshop', {})
        if self.blocked() or not state.get('draftSnapshot'):
            return None
        value = json.loads(self.safe_path(self.results, 'snapshots/' + state['draftSnapshot'] + '.json').read_text())
        value['notes'] = self.state.get('notes', {})
        value['evidenceReferences'] = [{'operationId': row['id'], 'snapshotId': row.get('snapshotId'),
            'runUrl': row.get('wandbRunUrl'), 'artifactUrl': row.get('artifactUrl')} for row in self.view()['trials'] if row.get('protocol') == 'workshop-v1']
        return self.projection(json.dumps(value, indent=2)).encode()

    def workshop_evidence(self, identifier, name):
        return self.safe_path(self.results, identifier + '/' + name).read_bytes()
