"""Read-only acceptance qualifications; original trial grades remain immutable."""
import json
from pathlib import Path

POLICY = json.loads((Path(__file__).resolve().parents[2] / 'forge/measurement-notes.json').read_text())
HISTORY_SELECTOR_SOURCE = POLICY['exclusions'][0]['sourceCommit']
HISTORY_SELECTOR_NOTE = ' '.join(item['reason'] for item in POLICY['exclusions'])

def qualified(row):
    revision = row.get('protocolRevision', row.get('protocol', {}).get('protocolRevision', 1))
    return revision >= POLICY['minimumUiProtocolRevision'] and not any(
        row['project'] == item['project'] and row['sourceCommit'] == item['sourceCommit']
        for item in POLICY['exclusions']
    )

def reason(row):
    revision = row.get('protocolRevision', row.get('protocol', {}).get('protocolRevision', 1))
    if revision < POLICY['minimumUiProtocolRevision']:
        return 'Historical asynchronous UI waits do not establish visible-answer acceptance.'
    for item in POLICY['exclusions']:
        if row['project'] == item['project'] and row['sourceCommit'] == item['sourceCommit']:
            return item['reason']
    return 'Protected service checks and awaited visible-answer Electron acceptance.'
