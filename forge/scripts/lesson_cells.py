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
    variant_notes = __NOTES__
    run_facts = __FACTS__

    def phase_labels(variant, count):
        """Name each coding-agent conversation by the role that produced it."""
        if variant in ("gen-eval", "maker-checker") and count == 3:
            return ["Maker", "Checker (read-only)", "Maker revision"]
        if variant == "plan-gen-eval" and count == 4:
            return ["Planner (read-only)", "Maker", "Checker (read-only)", "Maker revision"]
        if count == 1:
            return ["Coding agent"]
        return [f"Session {index}" for index in range(1, count + 1)]

    def evidence_link(url):
        """Forge opens an evidence version at .../name/v0. The recorded .../name:v0 form lands on a different artifact."""
        url = str(url or "")
        head, colon, version = url.rpartition(":v")
        if colon and version.isdigit() and "/artifacts/" in head:
            url = head + "/v" + version
        return url.replace("https://wandb.ai/", "https://forge.coreweave.com/wandb/", 1)

    return evidence_link, lesson_files, phase_labels, primary_ids, project_id, run_facts, runner_commit, saved, variant_notes, variants'''



RESULTS = r'''def _(Counter, mo, primary_ids, project_id, saved):
    rows = [row for row in saved.get("trials", []) if project_id == "overview" or row["project"] == project_id]
    primary_rows = [row for row in rows if row["id"] in primary_ids]
    _primary = []
    for _task, _variant in sorted({(r["project"], r["variant"]) for r in primary_rows}):
        _group = [r for r in primary_rows if (r["project"], r["variant"]) == (_task, _variant)]
        _primary.append({"Project": _task, "Treatment": _variant, "Passed": sum(r["outcome"] == "passed" for r in _group), "Attempts": len(_group), "Other outcomes": ", ".join(f"{v} {k.replace('_', ' ')}" for k, v in Counter(r["outcome"] for r in _group if r["outcome"] != "passed").items()) or "None"})
    _history = []
    for _task, _variant, _source in sorted({(r["project"], r["variant"], r["sourceCommit"]) for r in rows}):
        _group = [r for r in rows if (r["project"], r["variant"], r["sourceCommit"]) == (_task, _variant, _source)]
        _counts = Counter(r["outcome"] for r in _group)
        _history.append({"project": _task, "variant": _variant, "source_commit": _source, "attempts": len(_group), "passed": _counts["passed"], "task_failed": _counts["task_failed"], "infrastructure_failed": _counts["infrastructure_failed"], "telemetry_missing": _counts["telemetry_missing"], "known_estimate_usd": round(sum(r.get("reconciledEstimateUsd", r.get("estimatedCostUsd")) or 0 for r in _group), 6), "unknown_cost_attempts": sum(r.get("estimatedCostUsd") is None and r.get("reconciledEstimateUsd") is None for r in _group)})
    mo.vstack([
        mo.md("## Saved results\n\nWe recorded these attempts while building the course. They ran a smaller version of the lab above, so treat them as worked examples, not as your grade."),
        mo.ui.table(_primary, selection=None, pagination=False, show_column_summaries=False) if _primary else mo.md("This project has no three-attempt comparison. " + ("Its recorded attempts are candidates in a graph. Each candidate starts again from the unchanged starter and is given the grader's feedback on the one before." if project_id == "project-08" else "Its recorded attempts are rounds of a loop, where a round can start from the patch of the round before.") + " Read their saved states below."),
        mo.md("The table counts the main comparison only: three attempts per treatment, where a treatment is the setup the agent starts with. Earlier trial runs and diagnostics are kept below with their original grades and are not counted here.") if _primary else mo.md(""),
        mo.accordion({"All recorded attempts, grouped by source revision": mo.vstack([mo.md(f"This notebook has {len(rows)} recorded attempts, captured on {str(saved.get('capturedAt', ''))[:10]}. That includes failed attempts" + (" and earlier trial runs that the main comparison leaves out." if _primary else ".")), mo.ui.table(_history, selection=None, pagination=False, show_column_summaries=False)]), "What these results do not measure": mo.md("\n\n".join(item["reason"] for item in saved.get("measurementPolicy", {}).get("exclusions", []) if project_id in ["overview", item["project"]]) or "Nothing here measures how much of your own time a harness saves. Where a time or effort number is missing, it was not measured.")})
    ])
    return primary_rows, rows'''

SELECTOR = r'''def _(mo, primary_rows, rows):
    _ordered = primary_rows + [r for r in rows if r not in primary_rows]
    _options = {f"{'Main comparison' if r in primary_rows else 'Archive'} · {r['project']} · {r['variant']} · attempt {r['trial']} · {str(r['outcome']).replace('_', ' ')} · {r['id'][:8]}": r["id"] for r in _ordered}
    selected_trial = mo.ui.dropdown(options=_options, value=next(iter(_options), None), searchable=True, full_width=True, label="Choose a recorded attempt")
    mo.vstack([mo.md("## Inspect one attempt\n\nPick a recorded attempt. Read its checks first: they were run by a separate process on the patch the agent delivered. Then open the agent's conversation in Agent Lens to see how it got there."), selected_trial])
    return (selected_trial,)'''

DETAIL = r'''def _(evidence_link, json, mo, phase_labels, rows, selected_trial):
    _row = next((r for r in rows if r["id"] == selected_trial.value), None)
    if _row is None:
        _view = mo.md("No recorded attempt selected.")
    else:
        _lens = "https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge"
        _phases = {p.get("conversationId"): p for p in (_row.get("actorPhases") or [])}
        _steps = []
        for _label, _conversation in zip(phase_labels(_row.get("variant"), len(_row.get("conversationIds", []))), _row.get("conversationIds", [])):
            _phase = _phases.get(_conversation, {})
            _ended = "yes" if _phase.get("completed") else ("no: " + str((_phase.get("errors") or ["it reached its limit"])[0]).lower()) if _phase.get("completed") is False else "not recorded"
            _steps.append(f"| {_label} | [Open in Agent Lens]({_lens}/conversations/{_conversation}) | {_phase.get('requests', 'not recorded')} | {_ended} |")
        _other = []
        if _row.get("artifactUrl"):
            _other.append(f"[Patch, logs and grade]({evidence_link(_row['artifactUrl'])})")
        if _row.get("wandbRunUrl"):
            _other.append(f"[Run record]({_row['wandbRunUrl']})")
        _checks = [{"Check": c["name"], "Result": "Pass" if c["passed"] else "Fail", "Detail": c.get("error", "")} for c in (_row.get("grade") or {}).get("checks", [])]
        _view = mo.vstack([
            mo.md(f"**{_row['project']} · {_row['variant']} · {str(_row['outcome']).replace('_', ' ')}**"),
            mo.ui.table(_checks, selection=None, pagination=False, wrapped_columns=["Check", "Detail"], show_column_summaries=False) if _checks else mo.md("No independent grade was recorded for this attempt. Read the error in the full record below before drawing a conclusion."),
            mo.md("### What the agent did\n\nAgent Lens keeps the whole conversation behind this attempt. The **Thread** tab shows the task the agent was given, then each step: what it reasoned, the command or edit it made, and what came back. **Timeline** shows where the time went, and the token totals are at the top right.\n\n| Step | Conversation | Model calls | Finished on its own |\n|---|---|---|---|\n" + "\n".join(_steps) + "\n\nIn the last column, \"model-call budget exhausted\" means the agent used every model call it was allowed in that step, which is 24 for a whole attempt. It has nothing to do with money.\n\nAs you read, answer three questions. What did the agent look at before its first edit? Did it build or launch the app before it stopped? If it finished on its own, does its last message agree with the checks above, and if it was stopped at its limit, what was it in the middle of? The conversation shows what the agent did, but only the checks show whether the app worked. The patch is `candidate.diff` behind **Patch, logs and grade**.") if _steps else mo.md("No agent conversation was recorded for this attempt."),
            mo.md(" · ".join(_other) + ("\n\n" if _other else "") + "These links open the course's own project, `wandb/learn-harness-engineering-forge`. If one says you do not have access, ask your instructor. Your own attempts open in your own project, under **My work**."),
            mo.md(f"Source `{_row['sourceCommit']}` · protocol revision {_row.get('protocolRevision', 1)} · tokens in/out: {_row.get('inputTokens', 'unknown')} / {_row.get('outputTokens', 'unknown')}."),
            mo.accordion({"Full record for this attempt": mo.md("```json\n" + json.dumps(_row, indent=2) + "\n```")})
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
    mo.vstack([mo.md("## Checkpoints and decisions\n\nEach entry shows where a recorded loop or graph stopped and why. They are records to read and are not to be resumed. A loop round can start from the patch of the round before, a graph candidate starts again from the unchanged starter, and an approval applies only to the exact patch it names."), mo.accordion(_items)]) if _items else None
    return'''

PREDICTION = r'''def _(mo):
    prediction = mo.ui.text_area(label="My prediction, and why", rows=3, full_width=True)
    mo.vstack([mo.md("**4. Write your prediction.** Before you run anything, say what you expect to happen and where the agent is most likely to fall short. You will compare this with the result in step 6, so do not change it afterwards."), prediction])
    return (prediction,)'''

WORKSHEET = r'''def _(mo):
    observation = mo.ui.text_area(label="What happened? Name the treatment, the result, and the evidence you looked at.", rows=5, full_width=True)
    limitation = mo.ui.text_area(label="What does that evidence not tell you? What would you check next?", rows=3, full_width=True)
    measured_minutes = mo.ui.text(value="", label="Minutes you spent, if you timed it (leave blank otherwise)")
    mo.vstack([mo.md("## Your observation worksheet\n\n**6. Explain what happened.** Look at your attempt under **My work**: its checks, the app window, and the agent's conversation in Agent Lens. Compare it with your prediction, then fill this in. If you only read the recorded attempts, write about one of those instead.\n\n**Save my notes and progress** keeps your notes with this copy. **Download my notes** gives you a file to hand in, since nothing is submitted for you."), observation, limitation, measured_minutes])
    return limitation, measured_minutes, observation'''

DOWNLOADS = r'''def _(io, json, lesson_files, limitation, measured_minutes, mo, observation, prediction, project_id, runner_commit, zipfile):
    _notes = {"project": project_id, "runnerRevisionForSavedCase": runner_commit, "prediction": prediction.value, "observation": observation.value, "limitationsAndNextCheck": limitation.value, "observedHumanMinutes": measured_minutes.value or None, "status": "learner notes; not an independently verified grade"}
    _buffer = io.BytesIO()
    with zipfile.ZipFile(_buffer, "w", zipfile.ZIP_DEFLATED) as _zip:
        for _name, _content in lesson_files.items():
            _zip.writestr(_name, _content)
    mo.vstack([mo.download(data=json.dumps(_notes, indent=2).encode(), filename=project_id + "-observations.json", mimetype="application/json", label="Download my notes"), mo.download(data=_buffer.getvalue(), filename=project_id + "-lab-packet.zip", mimetype="application/zip", label="Download the lab brief and templates")])
    return'''
