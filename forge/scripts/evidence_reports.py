"""Completed campaign reports supersede read-only progress snapshots by ID."""
import json

def read_reports(directory):
    reports={}
    for pattern in ['dashboard-progress-*.json','report-*.json']:
        for path in sorted(directory.glob(pattern)):
            report=json.loads(path.read_text())
            reports[report['campaignId']]=report
    return list(reports.values())
