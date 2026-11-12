import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('audit_artifact', Path(__file__).parents[1] / 'scripts/audit_artifact.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AuditArtifactTests(unittest.TestCase):
    def test_changed_evidence_changes_identity_even_when_status_is_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            status, log = root / 'status.json', root / 'log.txt'
            status.write_text('{}'); log.write_text('first')
            first, _ = module.snapshot([(status, 'status.json'), (log, 'validation/log.txt')], root / 'first')
            module.verify(root / 'first', first)
            log.write_text('second')
            second, _ = module.snapshot([(status, 'status.json'), (log, 'validation/log.txt')], root / 'second')
            self.assertNotEqual(first, second)
            (root / 'first/validation/log.txt').write_text('corrupted')
            with self.assertRaisesRegex(RuntimeError, 'read-back mismatch'):
                module.verify(root / 'first', first)

    def test_snapshot_rejects_credentials_traversal_duplicates_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); source = root / 'source'; source.write_bytes(b'private-secret')
            link = root / 'link'; link.symlink_to(source)
            for files, secret in [([(source, '../escape')], b''), ([(source, 'safe')], b'private-secret'), ([(link, 'safe')], b''), ([(source, 'same'), (source, 'same')], b'')]:
                with self.assertRaises(ValueError): module.snapshot(files, root / 'output', secret)

    def test_readback_rejects_missing_and_unexpected_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); source = root / 'source'; source.write_text('evidence')
            digest, _ = module.snapshot([(source, 'evidence')], root / 'output')
            (root / 'output/extra').write_text('not in receipt')
            with self.assertRaisesRegex(RuntimeError, 'Unexpected'): module.verify(root / 'output', digest)
            (root / 'output/extra').unlink(); (root / 'output/evidence').unlink()
            with self.assertRaises(FileNotFoundError): module.verify(root / 'output', digest)


if __name__ == '__main__': unittest.main()
