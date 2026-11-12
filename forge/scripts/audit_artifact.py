"""Snapshot and verify every byte in a recoverable audit artifact."""
import hashlib
import json
from pathlib import Path, PurePosixPath


def safe_name(name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or '..' in path.parts or ':' in name or '\\' in name or str(path) != name:
        raise ValueError('Unsafe artifact entry name')
    return path


def snapshot(files, destination, secret=b''):
    """Freeze bytes before upload; retries identify all content, not just metrics."""
    hashes = {}
    for source, name in files:
        safe_name(name)
        if name in hashes or name == 'receipt-manifest.json':
            raise ValueError('Duplicate or reserved artifact entry')
        if any(path.is_symlink() for path in (source, *source.parents)):
            raise ValueError('Symlink in artifact evidence')
        content = source.read_bytes()
        if secret and secret in content:
            raise ValueError('Credential in artifact evidence')
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        hashes[name] = hashlib.sha256(content).hexdigest()
    manifest = {'schemaVersion': 1, 'files': dict(sorted(hashes.items()))}
    encoded = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    (destination / 'receipt-manifest.json').write_bytes(encoded)
    return hashlib.sha256(encoded).hexdigest(), manifest


def verify(directory, expected_digest):
    receipt = directory / 'receipt-manifest.json'
    if receipt.is_symlink() or hashlib.sha256(receipt.read_bytes()).hexdigest() != expected_digest:
        raise RuntimeError('Artifact receipt mismatch')
    manifest = json.loads(receipt.read_bytes())
    if manifest.get('schemaVersion') != 1:
        raise RuntimeError('Unsupported artifact receipt')
    for name, digest in manifest['files'].items():
        safe_name(name)
        path = directory / name
        if any(parent.is_symlink() for parent in (path, *path.parents)) or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Artifact evidence read-back mismatch: ' + name)
    actual = {path.relative_to(directory).as_posix() for path in directory.rglob('*') if path.is_file()}
    if actual != set(manifest['files']) | {'receipt-manifest.json'}:
        raise RuntimeError('Unexpected artifact evidence entries')
    return manifest
