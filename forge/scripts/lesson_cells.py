"""Native Marimo cells shared by the course notebooks; no HTML import layer."""

IMPORTS = r'''def _():
    import marimo as mo
    import base64
    import io
    import json
    import os
    import subprocess
    import uuid
    import zipfile
    from pathlib import Path
    from collections import Counter
    return Counter, Path, base64, io, json, mo, os, subprocess, uuid, zipfile'''

CONSTANTS = r'''def _(json):
    project_id = __PROJECT__
    runner_commit = __COMMIT__
    saved = json.loads(__SAVED__)
    variants = __VARIANTS__
    primary_ids = __PRIMARY__
    lesson_files = json.loads(__PACKET__)
    return lesson_files, primary_ids, project_id, runner_commit, saved, variants'''

RESULTS = r'''def _(Counter, mo, primary_ids, project_id, saved):
    rows = [row for row in saved.get("trials", []) if project_id == "overview" or row["project"] == project_id]
    primary_rows = [row for row in rows if row["id"] in primary_ids]
    _primary = []
    for _task, _variant in sorted({(r["project"], r["variant"]) for r in primary_rows}):
        _group = [r for r in primary_rows if (r["project"], r["variant"]) == (_task, _variant)]
        _primary.append({"Project": _task, "Treatment": _variant, "Passed": sum(r["outcome"] == "passed" for r in _group), "Attempts": len(_group), "Other outcomes": ", ".join(f"{v} {k}" for k, v in Counter(r["outcome"] for r in _group if r["outcome"] != "passed").items()) or "None"})
    _history = []
    for _task, _variant, _source in sorted({(r["project"], r["variant"], r["sourceCommit"]) for r in rows}):
        _group = [r for r in rows if (r["project"], r["variant"], r["sourceCommit"]) == (_task, _variant, _source)]
        _counts = Counter(r["outcome"] for r in _group)
        _history.append({"project": _task, "variant": _variant, "source_commit": _source, "attempts": len(_group), "passed": _counts["passed"], "task_failed": _counts["task_failed"], "infrastructure_failed": _counts["infrastructure_failed"], "telemetry_missing": _counts["telemetry_missing"], "known_estimate_usd": round(sum(r.get("reconciledEstimateUsd", r.get("estimatedCostUsd")) or 0 for r in _group), 6), "unknown_cost_attempts": sum(r.get("estimatedCostUsd") is None and r.get("reconciledEstimateUsd") is None for r in _group)})
    mo.vstack([
        mo.md("## Saved results\n\nThese are recorded Forge adaptations. The lab above states the original assignment and the coverage gaps. Scores are not learner completion records."),
        mo.ui.table(_primary, selection=None, pagination=False, show_column_summaries=False) if _primary else mo.md("This project has dependent loop/graph evidence, not a primary three-repeat comparison. Inspect its checkpoints below."),
        mo.md("The primary cohort is frozen before this notebook revision. Earlier protocols and diagnostic attempts remain in the archive with their original grades; they are not extra primary repeats."),
        mo.accordion({"Historical outcomes by source revision": mo.vstack([mo.md(saved.get("status", "Saved evidence")), mo.ui.table(_history, selection=None, pagination=False, show_column_summaries=False)]), "Measurement limitations": mo.md("\n\n".join(item["reason"] for item in saved.get("measurementPolicy", {}).get("exclusions", []) if project_id in ["overview", item["project"]]) or "Read the project-specific limitations above. Human time savings are unmeasured unless explicitly recorded.")})
    ])
    return primary_rows, rows'''

SELECTOR = r'''def _(mo, primary_rows, rows):
    _ordered = primary_rows + [r for r in rows if r not in primary_rows]
    _options = {f"{'Primary' if r in primary_rows else 'Archive'} · {r['project']} · {r['variant']} · repeat {r['trial']} · {r['outcome']} · {r['id'][:8]}": r["id"] for r in _ordered}
    selected_trial = mo.ui.dropdown(options=_options, value=next(iter(_options), None), searchable=True, full_width=True, label="Choose a recorded attempt")
    mo.vstack([mo.md("## Inspect one attempt\n\nStart with the independent grade. Open its patch and trace to explain the result. The run and artifact links require private-project access."), selected_trial])
    return (selected_trial,)'''

DETAIL = r'''def _(json, mo, rows, selected_trial):
    _row = next((r for r in rows if r["id"] == selected_trial.value), None)
    if _row is None:
        _view = mo.md("No recorded attempt selected.")
    else:
        _links = []
        if _row.get("wandbRunUrl"):
            _links.append(f"[W&B run]({_row['wandbRunUrl']})")
        if _row.get("artifactUrl"):
            _links.append(f"[Patch, logs and grade artifact]({_row['artifactUrl']})")
        for _i, _conversation in enumerate(_row.get("conversationIds", []), 1):
            _links.append(f"[Agent Lens conversation {_i}](https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge/conversations/{_conversation})")
        _checks = [{"Check": c["name"], "Result": "Pass" if c["passed"] else "Fail", "Detail": c.get("error", "")} for c in (_row.get("grade") or {}).get("checks", [])]
        _view = mo.vstack([
            mo.md(f"**{_row['project']} · {_row['variant']} · {_row['outcome']}**\n\n" + " · ".join(_links)),
            mo.ui.table(_checks, selection=None, pagination=False, wrapped_columns=["Check", "Detail"], show_column_summaries=False) if _checks else mo.md("No protected grade was recorded for this attempt. Read the error and telemetry before drawing a conclusion."),
            mo.md(f"Source: `{_row['sourceCommit']}` · protocol revision {_row.get('protocolRevision', 1)}. Input/output tokens: {_row.get('inputTokens', 'unknown')} / {_row.get('outputTokens', 'unknown')}. Token counts are not measurements of human effort."),
            mo.accordion({"Complete trial record": mo.md("```json\n" + json.dumps(_row, indent=2) + "\n```")})
        ])
    _view
    return'''

LIFECYCLE = r'''def _(json, mo, project_id, saved):
    _states = []
    if project_id in ["overview", "project-07"]:
        _states += saved.get("loops", [])
    if project_id in ["overview", "project-08"]:
        _states += saved.get("graphs", [])
    _items = {state["file"]: mo.md("```json\n" + json.dumps(state, indent=2) + "\n```") for state in _states}
    mo.vstack([mo.md("## Checkpoints and decisions\n\nThese are saved states, not a request to resume. Loop rounds depend on prior work. A manual qualification approval does not approve a different Pi patch."), mo.accordion(_items)]) if _items else None
    return'''

WORKSHEET = r'''def _(mo):
    prediction = mo.ui.text_area(label="Before running: what do you predict, and why?", rows=3, full_width=True)
    observation = mo.ui.text_area(label="What did you observe? Include the command, revision, and evidence link.", rows=5, full_width=True)
    limitation = mo.ui.text_area(label="What does that evidence leave unresolved? What will you check next?", rows=3, full_width=True)
    measured_minutes = mo.ui.text(value="", label="Observed human effort in minutes (leave blank if unmeasured)")
    mo.vstack([mo.md("## Your observation worksheet\n\nUse a running notebook session to fill this in and download it below. Entries are not automatically submitted or saved as a course result. Saved-view readers can download the blank lab packet. This activity launches no inference or coding trial."), prediction, observation, limitation, measured_minutes])
    return limitation, measured_minutes, observation, prediction'''

DOWNLOADS = r'''def _(io, json, lesson_files, limitation, measured_minutes, mo, observation, prediction, project_id, runner_commit, zipfile):
    _notes = {"project": project_id, "runnerRevisionForSavedCase": runner_commit, "prediction": prediction.value, "observation": observation.value, "limitationsAndNextCheck": limitation.value, "observedHumanMinutes": measured_minutes.value or None, "status": "learner notes; not an independently verified grade"}
    _buffer = io.BytesIO()
    with zipfile.ZipFile(_buffer, "w", zipfile.ZIP_DEFLATED) as _zip:
        for _name, _content in lesson_files.items():
            _zip.writestr(_name, _content)
    mo.vstack([mo.download(data=json.dumps(_notes, indent=2).encode(), filename=project_id + "-observations.json", mimetype="application/json", label="Download my observations"), mo.download(data=_buffer.getvalue(), filename=project_id + "-lab-packet.zip", mimetype="application/zip", label="Download lab brief and submission templates")])
    return'''
