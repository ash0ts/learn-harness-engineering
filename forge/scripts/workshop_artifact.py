# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0"]
# ///
"""Retrieve one committed source snapshot; no archive extraction or paid work."""
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import wandb
from models import require_private_project


def fetch(name, member, destination):
    if not re.fullmatch(r"trial-[A-Za-z0-9-]+:v[0-9]+", name):
        raise ValueError("Use an immutable trial-ID:vN artifact version")
    if member not in {"submission.json", "candidate.json"}:
        raise ValueError("Choose submission.json or candidate.json")
    entity, project = require_private_project()
    artifact = wandb.Api(timeout=60).artifact(f"{entity}/{project}/{name}", type="course-evidence")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(artifact.get_path(member).download(root=directory))
        data = path.read_bytes()
    if len(data) > 8_000_000 or os.environ['WANDB_API_KEY'].encode() in data:
        raise ValueError("Unsafe snapshot payload")
    snapshot = json.loads(data)
    if snapshot.get('protocol') != 'workshop-v1':
        raise ValueError("Artifact is not a workshop snapshot")
    with Path(destination).open('xb') as stream:
        stream.write(data)


if __name__ == '__main__':
    fetch(*sys.argv[1:])
