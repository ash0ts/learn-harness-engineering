"""Generate the nine canonical, self-contained Marimo analysis notebooks."""
from pathlib import Path
import json
import subprocess
import argparse

ROOT = Path(__file__).resolve().parents[2]
TITLES = [
    ('00-overview.py', 'overview', 'Forge track: evidence before conclusions', 'Follow all eight projects from a frozen task to a sandbox patch, independent grading, Agent Lens conversation and W&B artifact.'),
    ('01-minimal-harness.py', 'project-01', '01 · Minimal instructions and explicit harnesses', 'Compare prompt-only work with explicit repository rules on identical application code. Verify the Electron shell and real service pipeline.'),
    ('02-workspace-docs.py', 'project-02', '02 · An agent-readable workspace', 'Compare two fresh coding sessions with and without workspace documentation. Measure recovered behavior, not inferred time saved.'),
    ('03-session-recovery.py', 'project-03', '03 · Interrupted-session recovery', 'Persist a patch, discard conversational context, and resume indexing and grounded Q&A from files. Inspect the handoff and held-out evidence.'),
    ('04-runtime-feedback.py', 'project-04', '04 · Runtime evidence and the seeded defect', 'Find the long-document empty-chunk defect using actual import, indexing and retrieval. Check architecture guardrails and Electron independently.'),
    ('05-role-separation.py', 'project-05', '05 · One feature, three role arrangements', 'Compare single role, generator/evaluator, and planner/generator/evaluator on the same ConversationHistory upgrade and total model-turn budget.'),
    ('06-capstone.py', 'project-06', '06 · Capstone reliability', 'Verify import, indexing, Q&A, feedback and reset with real services and Electron. Historical simulated benchmarks are not evidence in this track.'),
    ('07-bounded-loops.py', 'project-07', '07 · Goal, timer and maker-checker loops', 'Inspect durable checkpoints, separate review contexts, interventions and stop conditions. Accelerated timer tests are distinct from the real two-hour exercise.'),
    ('08-state-machine.py', 'project-08', '08 · Checkpointed graphs and human approval', 'Follow conditional routing, parallel verification, rollback and retry. A passing patch pauses at approval until a human submits a checksum-bound decision.'),
]
VARIANTS = {'overview':['minimal','explicit'],'project-01':['minimal','explicit'],'project-02':['minimal','workspace-docs'],'project-03':['minimal','recovery'],'project-04':['minimal','runtime-feedback'],'project-05':['single-role','gen-eval','plan-gen-eval'],'project-06':['minimal','capstone'],'project-07':['goal','timer','maker-checker'],'project-08':['graph']}

DESIGNS = {
'overview': ('Which harness changes improve a bounded coding attempt?', 'Hold application code, fixture, model and generation settings fixed. Vary only the staged harness treatment.', 'Inspect complete treatment blocks, exported patches, protected service checks, Xvfb/Electron evidence, usage and traces. A completed trial can still fail.', 'Start with qualification, inspect one project, compare all three repeats, then follow the loop and graph checkpoints. Never treat historical simulated scores as live evidence.'),
'project-01': ('Do explicit acceptance criteria help the agent finish a usable shell?', 'Compare minimal instructions with explicit harness guidance from the same unfinished starter.', 'Check compilation, import persistence, indexing, grounded Q&A and an actual Electron window with a working typed preload bridge.', 'Open both patches and their Agent Lens tool calls. A service pass with a broken preload remains a failed application task.'),
'project-02': ('Can workspace documentation support a fresh coding session?', 'Compare minimal and workspace-docs treatments. Each attempt gets two fresh sessions sharing files, with the same total model-call allowance.', 'Check actual document import through the Electron UI, persisted contents, indexing and Q&A. Inspect whether session two discovers the relevant workspace files.', 'Treat each two-session attempt as one trial. Do not count its sessions as independent repeats or infer time saved.'),
'project-03': ('Does a written handoff preserve progress after context is discarded?', 'Compare minimal instructions with the recovery harness on identical unfinished code; persist the patch between two fresh Pi sessions.', 'Check document metadata, single-document indexing status, grounded citations, durable history and Electron behavior.', 'Read the checkpoint and handoff before inspecting the resumed conversation. Verify recovered behavior from held-out checks, not the final agent claim.'),
'project-04': ('Does runtime evidence expose a defect that superficial checks miss?', 'Compare minimal instructions with runtime-feedback guidance on the same seeded long-document chunking defect.', 'Import a document exceeding the defect threshold, inspect every nonempty chunk, retrieve source text and exercise Electron. The architecture guard must reject a seeded Node import.', 'Separate compilation, service and UI failures. A test script that prints success without executing these paths is not a passing result.'),
'project-05': ('Does role separation improve the same ConversationHistory feature?', 'Compare single-role, generator/evaluator and planner/generator/evaluator treatments from the same starter. Split the same 24-call allowance across roles; checker edits are discarded.', 'Check ordered full answers, confidence, expandable citations, clearing history and preserved app behavior under Electron.', 'Inspect what information crosses role boundaries. Extra roles receive a smaller share of the fixed allowance, not additional compute.'),
'project-06': ('Can the full harness deliver a reliable capstone workflow?', 'Compare minimal instructions with capstone guidance using identical unfinished code and fixtures.', 'Execute import, indexing, grounded Q&A, persisted feedback and reset. Verify services and Electron independently.', 'Use the exported patch and versioned evidence to reproduce failures. Keep this live study separate from the original lecture simulated benchmark examples.'),
'project-07': ('How do goal, timer and maker-checker stop conditions change execution?', 'Run bounded exercises with durable patches and checkpoints. Goal and maker-checker stop on success, no progress or a round bound; timer schedules bounded sessions over a real wall-clock window.', 'Inspect each round, isolated review context, recorded intervention and stop reason. Accelerated timer tests validate scheduling; they are not the real two-hour exercise.', 'Rounds depend on prior patches and are not independent repeats. A pending ambiguous launch requires reconciliation before resume. No human time savings are inferred.'),
'project-08': ('Can a durable graph route a real patch through verification and review?', 'Follow explicit plan, make, parallel verification, rollback/retry and approval states. Failed candidates are retained as evidence and discarded before the next attempt.', 'Grade services and Electron in separate fresh workspaces. Inspect checkpoint transitions, retry feedback, patch checksums and the maximum-attempt stop.', 'A passing candidate pauses at approval. Review the exact patch and evidence, then submit an explicit checksum-bound approve or reject decision. The runner never supplies that human decision.'),
}

TEMPLATE = '''# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.25.1",
#     "wandb==0.31.0",
# ]
# ///
# Canonical source: forge/notebooks/__FILE__
# Generated by forge/scripts/create_notebooks.py; edit that generator for shared cells.
import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")

@app.cell(hide_code=True)
 def_placeholder_imports

@app.cell(hide_code=True)
 def_placeholder_constants

@app.cell(hide_code=True)
 def_placeholder_intro

@app.cell(hide_code=True)
 def_placeholder_design

@app.cell(hide_code=True)
 def_placeholder_results

@app.cell(hide_code=True)
 def_placeholder_links

@app.cell(hide_code=True)
 def_placeholder_lifecycle

@app.cell(hide_code=True)
 def_placeholder_controls

@app.cell(hide_code=True)
 def_placeholder_execute

@app.cell(hide_code=True)
 def_placeholder_status

if __name__ == "__main__":
    app.run()
'''

CELLS = {
'imports': '''def _():
    import marimo as mo
    import json
    import os
    import subprocess
    import uuid
    from pathlib import Path
    from collections import Counter
    return Counter, Path, json, mo, os, subprocess, uuid''',
'constants': '''def _(json):
    project_id = __PROJECT__
    runner_commit = __COMMIT__
    saved = json.loads(__SAVED__)
    variants = __VARIANTS__
    return project_id, runner_commit, saved, variants''',
'intro': '''def _(mo, runner_commit):
    mo.md(__INTRO__ + f"\\n\\nRunner revision: `{runner_commit}`. Opening this notebook displays saved evidence and launches no inference or coding work.")
    return''',
'design': '''def _(json, mo):
    _question, _control, _checks, _reading = __DESIGN__
    _protocol = json.loads(__PROTOCOL__)
    mo.vstack([mo.md("## Experiment design\\n\\n" + _question + "\\n\\n**Control and treatment.** " + _control + "\\n\\n**Evidence to inspect.** " + _checks + "\\n\\n**How to read the result.** " + _reading), mo.md("### Frozen execution settings"), mo.ui.table([{"model": _protocol["model"], "temperature": _protocol["temperature"], "maximum_model_calls": _protocol["maxModelTurnsPerTrial"], "maximum_output_tokens_per_call": _protocol["maxOutputTokens"], "target_repeats": _protocol["repeats"], "sandbox_image": _protocol["sandbox"]["image"]}], selection=None)])
    return''',
'results': '''def _(Counter, mo, project_id, saved):
    rows = [row for row in saved.get("trials", []) if project_id == "overview" or row["project"] == project_id]
    counts = Counter((row["project"], row["variant"], row["sourceCommit"], row["outcome"]) for row in rows)
    aggregates = []
    for _project, _variant, _source in sorted({(row["project"], row["variant"], row["sourceCommit"]) for row in rows}):
        _group = [row for row in rows if (row["project"], row["variant"], row["sourceCommit"]) == (_project, _variant, _source)]
        aggregates.append({"project": _project, "variant": _variant, "source_commit": _source, "attempts": len(_group), "passed": counts[_project, _variant, _source, "passed"], "task_failed": counts[_project, _variant, _source, "task_failed"], "infrastructure_failed": counts[_project, _variant, _source, "infrastructure_failed"], "telemetry_missing": counts[_project, _variant, _source, "telemetry_missing"], "known_estimate_usd": round(sum(row.get("reconciledEstimateUsd", row.get("estimatedCostUsd")) or 0 for row in _group), 6), "unknown_cost_attempts": sum(row.get("estimatedCostUsd") is None and row.get("reconciledEstimateUsd") is None for row in _group)})
    mo.vstack([mo.md("## Saved results\\n\\n" + saved.get("status", "No campaign has been recorded.")), mo.ui.table(aggregates, selection=None) if aggregates else mo.md("No trials are recorded for this project. This is an explicit absence of evidence, not a zero score."), mo.md("Target: three repeats per automated variant. Show task failures, infrastructure failures and missing telemetry separately. Repeats of one task are not independent tasks. Rows are grouped by project, treatment and source revision. Cost sums include audited reconciliations where available; unknown token usage remains unknown even when a reservation is charged conservatively. Original outcomes are preserved; see the shared ledger for reservations and reconciliation evidence."), mo.ui.table(rows, selection=None) if rows else mo.md("No run rows to display."), mo.md("### Qualification and budget evidence"), mo.ui.table(saved.get("qualifications", []), selection=None), mo.md("```json\\n" + __import__("json").dumps({key: value for key, value in saved.get("budget", {}).items() if key != "settled"}, indent=2) + "\\n```")])
    return (rows,)''',
'links': '''def _(mo, rows, saved):
    _links = []
    for _row in rows:
        if _row.get("wandbRunUrl"):
            _links.append(f"- [{_row['id']} · W&B run]({_row['wandbRunUrl']})")
        for _conversation in _row.get("conversationIds", []):
            _links.append(f"- Agent Lens conversation [`{_conversation}`](https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge/conversations/{_conversation})")
        if _row.get("artifactUrl"):
            _links.append(f"- [Versioned trial evidence]({_row['artifactUrl']})")
    for _qualification in saved.get("qualifications", []):
        for _kind in ["agentConversationId", "appConversationId"]:
            _conversation = _qualification.get(_kind)
            if _conversation:
                _links.append(f"- Protocol qualification · {_kind}: [Agent Lens `{_conversation}`](https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge/conversations/{_conversation})")
    for _qualification in saved.get("concurrencyQualifications", []):
        for _session in _qualification.get("sessions", []):
            _conversation = _session.get("conversationId")
            if _conversation:
                _links.append(f"- Concurrent app qualification: [Agent Lens `{_conversation}`](https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge/conversations/{_conversation})")
    mo.md("## Evidence links\\n\\n" + ("\\n".join(_links) if _links else "Links appear only for recorded runs. No synthetic run URLs are generated."))
    return''',
'lifecycle': '''def _(json, mo, project_id, saved):
    _states = []
    if project_id in ["overview", "project-07"]:
        _states += saved.get("loops", [])
    if project_id in ["overview", "project-08"]:
        _states += saved.get("graphs", [])
    _parts = [mo.md("## Durable execution evidence\\n\\nLoop rounds are dependent attempts. Manual graph qualification candidates verify control flow and are excluded from Pi scores. Human decisions and observed interventions retain their original timestamps.")]
    for _state in _states:
        _parts.append(mo.md("### " + _state["file"] + "\\n\\n```json\\n" + json.dumps(_state, indent=2) + "\\n```"))
    if project_id == "overview":
        _parts.append(mo.md("### Live sandbox qualification\\n\\n```json\\n" + json.dumps(saved.get("sandboxQualifications", []), indent=2) + "\\n```"))
    mo.vstack(_parts) if _states or project_id == "overview" else None
    return''',
'controls': '''def _(mo, os, variants):
    runner_root = mo.ui.text(value=os.environ.get("FORGE_RUNNER_ROOT", ""), label="Shared coordinator checkout (absolute path)", full_width=True)
    entity = mo.ui.text(value="wandb", label="W&B team")
    result_project = mo.ui.text(value="learn-harness-engineering-forge", label="Private W&B project")
    treatment = mo.ui.dropdown(options=variants, value=variants[0], label="Harness treatment")
    repetitions = mo.ui.number(start=1, stop=3, value=1, label="Repeats for Projects 01–06")
    launch = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Launch bounded rerun · uses shared budget")
    get_execution, set_execution = mo.state({"click": 0, "status": "Not launched"})
    mo.vstack([mo.md("## Bounded rerun\\n\\nPaid work requires this explicit button. The coordinator needs Node, installed pinned dependencies, external credentials, a successful qualification, and the existing durable budget ledger. Hosted analysis works without that coordinator. Configure its mounted checkout to enable execution; this notebook never creates a fresh $50 ledger on opening. A failed or uncertain request stays recorded."), runner_root, mo.hstack([entity, result_project]), mo.hstack([treatment, repetitions]), launch])
    return entity, get_execution, launch, repetitions, result_project, runner_root, set_execution, treatment''',
'execute': '''def _(Path, entity, get_execution, json, launch, mo, os, project_id, repetitions, result_project, runner_commit, runner_root, set_execution, subprocess, treatment, uuid):
    mo.stop(launch.value <= get_execution()["click"])
    set_execution({"click": launch.value, "status": "Starting explicit request"})
    try:
        _root = Path(runner_root.value)
        if not runner_root.value or not _root.is_absolute():
            raise RuntimeError("Configure an absolute shared coordinator checkout first.")
        _actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_root, text=True).strip()
        if _actual != runner_commit:
            raise RuntimeError("The coordinator revision must match the pinned runner revision shown above.")
        _ledger = _root / "forge/local-results/budget.json"
        if not _ledger.exists():
            raise RuntimeError("A qualified, durable shared budget ledger is required; no new ledger is created here.")
        _budget = json.loads(_ledger.read_text())
        if _budget.get("halted"):
            raise RuntimeError("The shared ledger is halted; reconcile its recorded reason before launching.")
        _authorized_limit = _budget.get("limitUsd")
        if _authorized_limit is None and not _budget.get("authorizations"):
            raise RuntimeError("An unlimited ledger requires its recorded explicit authorization.")
        _env = dict(os.environ, WANDB_ENTITY=entity.value, WANDB_PROJECT=result_project.value, FORGE_BUDGET_USD="unlimited" if _authorized_limit is None else str(_authorized_limit))
        if not _env.get("WANDB_API_KEY"):
            raise RuntimeError("Supply credentials through the coordinator environment, never a notebook cell.")
        _command = ["node", "--import", str(_root / "forge/node_modules/tsx/dist/loader.mjs"), str(_root / "forge/src/cli.ts")]
        _checkpoint = str(_root / "forge/local-results" / ("notebook-" + uuid.uuid4().hex + ".json"))
        if project_id == "project-07":
            _command += ["loop", "--mode", treatment.value, "--checkpoint", _checkpoint, "--duration-seconds", "600", "--max-rounds", "1", "--execute"]
        elif project_id == "project-08":
            _command += ["graph", "--checkpoint", _checkpoint, "--execute"]
        else:
            _command += ["compare", "--project", "project-01" if project_id == "overview" else project_id, "--variant", treatment.value, "--repeats", str(int(repetitions.value)), "--source", runner_commit, "--execute"]
        _completed = subprocess.run(_command, cwd=_root, env=_env, text=True, capture_output=True, timeout=3500)
        set_execution({"click": launch.value, "status": "Runner finished", "exit_code": _completed.returncode, "stdout": _completed.stdout[-16000:], "stderr": _completed.stderr[-4000:]})
    except Exception as _error:
        set_execution({"click": launch.value, "status": "Not completed", "error": str(_error)})
    return''',
'status': '''def _(get_execution, mo):
    mo.md("## Last explicit action\\n\\n```json\\n" + __import__("json").dumps(get_execution(), indent=2) + "\\n```")
    return'''
}

def project_snapshot(snapshot, project):
    saved=json.loads(json.dumps(snapshot))
    saved['scope']=project
    saved['trials']=[r for r in snapshot.get('trials',[]) if project=='overview' or r['project']==project]
    saved['completedComparisonBlocks']=[b for b in snapshot.get('completedComparisonBlocks',[]) if project=='overview' or b['project']==project]
    saved['loops']=snapshot.get('loops',[]) if project in ['overview','project-07'] else []
    saved['graphs']=snapshot.get('graphs',[]) if project in ['overview','project-08'] else []
    for key in ['qualifications','concurrencyQualifications','sandboxQualifications']:saved.setdefault(key,[])
    saved['status']=f"Saved at {snapshot.get('capturedAt','the recorded source revision')}: {len(saved['trials'])} completed coding attempts for {project}. Outcomes include unsuccessful attempts. No human time savings are inferred."
    if project not in ['project-07','project-08']:
        saved['status']+=f" Complete comparison blocks: {len(saved['completedComparisonBlocks'])}."
    return saved

def generate(runner_commit=None, projects=None):
    snapshot = ROOT / 'forge/results/snapshot.json'
    saved = json.loads(snapshot.read_text()) if snapshot.exists() else {'schemaVersion':1,'status':'Qualification in progress; no completed comparison campaign.','trials':[]}
    commit = runner_commit or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    generated=[]
    for filename,project,title,description in TITLES:
        if projects and project not in projects:continue
        evidence=project_snapshot(saved,project)
        source=TEMPLATE.replace('__FILE__',filename)
        for key,cell in CELLS.items():
            source=source.replace(' def_placeholder_'+key,cell)
        source=source.replace('__DESIGN__',repr(DESIGNS[project])).replace('__PROTOCOL__',repr((ROOT/'forge/protocol.json').read_text())).replace('__PROJECT__',repr(project)).replace('__COMMIT__',repr(commit)).replace('__VARIANTS__',repr(VARIANTS[project])).replace('__SAVED__',repr(json.dumps(evidence,ensure_ascii=False))).replace('__INTRO__',repr('# '+title+'\n\n'+description+'\n\nKeep the task, model and fixtures fixed. Inspect evidence before comparing scores.'))
        # Static Marimo exports retain only the current page of a paginated
        # table. The course overview must preserve every aggregate group.
        if project == 'overview':
            source=source.replace('mo.ui.table(aggregates, selection=None)', 'mo.ui.table(aggregates, selection=None, pagination=False)')
        (ROOT/'forge/notebooks'/filename).write_text(source)
        generated.append(str(ROOT/'forge/notebooks'/filename))
    # Forge's editor serializes source with its pinned Marimo version. Normalize
    # locally so the ordinary editor save retains the canonical byte checksum.
    subprocess.run(['uv', 'run', '--with', 'marimo==0.25.1', 'marimo', 'check', '--fix', *generated], check=True, cwd=ROOT)
    print('Generated',len(generated),'canonical notebooks at runner revision',commit)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runner-commit', help='Freeze runner revision when refreshing saved results')
    parser.add_argument('--project',action='append',choices=[r[1] for r in TITLES],help='Refresh only these project notebooks; other snapshots retain their capture time')
    args=parser.parse_args()
    generate(args.runner_commit,args.project)
