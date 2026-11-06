# /// script
# requires-python = ">=3.11"
# dependencies = ["wandb==0.31.0", "wandb-workspaces==0.4.13"]
# ///
"""Publish private, reproducible course dashboards from completed comparison blocks.

Aggregate runs are derived views, never coding attempts. Source trial IDs and
checksums make every displayed numerator/denominator independently recoverable.
Existing view IDs are reused. Original trial summaries and outcomes are untouched.
"""
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import sys
import wandb
import wandb_workspaces.expr as expr
import wandb_workspaces.reports.v2 as wr
import wandb_workspaces.workspaces as ws
from models import require_private_project
from evidence_reports import read_reports
from measurement import qualified, reason, HISTORY_SELECTOR_NOTE, HISTORY_SELECTOR_SOURCE

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "forge/local-results"
MANIFEST = ROOT / "forge/results/dashboards.json"

class ReadableLayout(ws.SectionLayoutSettings):
    """Pinned SDK adapter: expose its FlowConfig.box_height for 13 labeled bars."""
    def _to_model(self):
        model = super()._to_model()
        model.box_height = 520
        return model

def forge_url(url):
    # The workspace SDK uses the W&B app root; Forge embeds it under /wandb.
    return url.replace('https://forge.coreweave.com/', 'https://forge.coreweave.com/wandb/', 1)

def aggregates():
    groups = defaultdict(dict)
    for report in read_reports(LOCAL):
        for block in report["blocks"]:
            project = block["project"]
            if project not in [f"project-0{i}" for i in range(1, 7)]:
                continue
            expected = set(json.loads((ROOT / "forge/tasks" / (project + ".json")).read_text())["variants"])
            rows = [r for r in report["completed"] if r["project"] == project and r["trial"] == block["repeat"]]
            if set(r["variant"] for r in rows) != expected:
                continue
            for row in rows:
                original = json.loads((LOCAL / row["id"] / "trial.json").read_text())
                if not original.get("finishedAt"):
                    raise RuntimeError("Incomplete trial in completed block")
                if original['outcome'] == 'passed' and not all(c['passed'] for c in original['grade']['checks']):
                    raise RuntimeError('Passing outcome disagrees with protected check evidence')
                key = (report["protocolSha256"], report["sourceCommit"], project, row["variant"])
                groups[key][row["id"]] = original
    output = []
    for key, indexed in sorted(groups.items()):
        protocol, source, project, treatment = key
        rows = list(indexed.values())
        checks = [c for r in rows for c in r.get("grade", {}).get("checks", [])]
        ui = [c for c in checks if c["name"].startswith("Electron")]
        service = [c for c in checks if c["name"].startswith(("real import", "actual indexing", "actual retrieval"))]
        outcomes = [r["outcome"] for r in rows]
        metrics = {"attempts": len(rows), "passes": outcomes.count("passed"),
                   "passRate": outcomes.count("passed") / len(rows),
                   "taskFailures": outcomes.count("task_failed"),
                   "infrastructureFailures": outcomes.count("infrastructure_failed"),
                   "missingTelemetry": outcomes.count("telemetry_missing"),
                   "uiChecksExecuted": len(ui), "uiChecksPassed": sum(c["passed"] for c in ui),
                   "serviceChecksExecuted": len(service), "serviceChecksPassed": sum(c["passed"] for c in service),
                   "unknownCostAttempts": sum(r.get("estimatedCostUsd") is None for r in rows),
                   "knownEstimatedCostUsd": sum(r.get("estimatedCostUsd") or 0 for r in rows),
                   "inputTokens": sum(r.get("inputTokens") or 0 for r in rows),
                   "outputTokens": sum(r.get("outputTokens") or 0 for r in rows)}
        revision = rows[0]["protocol"]["protocolRevision"]
        output.append({"id": "course-view-" + hashlib.sha256(json.dumps(key).encode()).hexdigest()[:16],
                       "config": {"dashboardKind": "comparison-aggregate", "protocolRevision": revision,
                                  "protocolSha256": protocol, "sourceCommit": source, "project": project,
                                  "variant": treatment, "label": f"r{revision} {project[8:]} {treatment}",
                                  "trialIds": sorted(indexed), "acceptanceQualified": all(qualified(r) for r in rows),
                                  "measurementNote": reason(rows[0]), "lastTrialFinishedAt": max(r["finishedAt"] for r in rows)}, "metrics": metrics})
    latest = {}
    for row in output:
        c = row['config']
        if c['acceptanceQualified']:
            prior = latest.get(c['project'])
            if prior is None or c['lastTrialFinishedAt'] > prior[0]:
                latest[c['project']] = (c['lastTrialFinishedAt'], c['sourceCommit'])
    for row in output:
        c = row['config']
        c['primaryComparison'] = c['acceptanceQualified'] and latest.get(c['project'], (None,None))[1] == c['sourceCommit']
    return output

def panels(revision, acceptance_qualified=True):
    specs = [("End-to-end pass rate (visible answers verified)" if revision >= 4 and acceptance_qualified else "Recorded native pass rate — see qualification notes", "passRate"),
             ("Completed attempts — denominator", "attempts"),
             ("Electron checks passed", "uiChecksPassed"),
             ("Service checks passed", "serviceChecksPassed"),
             ("Task failures", "taskFailures"),
             ("Known estimated cost (USD)", "knownEstimatedCostUsd")]
    return [wr.BarPlot(title=title, metrics=[metric], groupby=wr.Config("label"),
                       groupby_aggfunc="sum", groupby_rangefunc="none", max_runs_to_show=100,
                       max_bars_to_show=100, range_x=(0, 1) if metric == "passRate" else (0, None),
                       layout=wr.Layout(x=(i % 2) * 12, y=(i // 2) * 10, w=12, h=10))
            for i, (title, metric) in enumerate(specs)]

def evidence_report(entity, project, rows, views, operations, primary, previous):
    notebooks = json.loads((ROOT / 'forge/publication-manifest.json').read_text())['notebooks']
    ledger = json.loads((LOCAL / 'budget.json').read_text())
    old = previous.get('report')
    report = wr.Report.from_url(old['url']) if old else wr.Report(entity=entity, project=project)
    report.title = 'Forge harness course — verified execution and comparison evidence'
    report.description = 'Frozen cohorts, protected service and Electron checks, Agent Lens traces, W&B artifacts and nine saved notebooks.'
    lines = ['# What completed, and what passed',
             'Revision 4 requires every protected check plus observed, rendered answers in a fresh grading sandbox. '
             'Revision 2 and 3 have an asynchronous UI-wait defect: their native grades are preserved as historical results, not verified UI acceptance. '
             'The tables below include completed comparison blocks only. Aggregate runs are derived views, not additional trials. '
             'A service check is not UI evidence. Repeated attempts of one task do not establish a general treatment ranking. Protected app checks execute the actual services with deterministic course Q&A defaults; the live Forge app adapter is qualified separately. These checks do not measure production answer quality.', '',
             '[Execution and publication dashboard](' + forge_url(operations.url) + ')', '',
             '## Qualified comparison results', '', HISTORY_SELECTOR_NOTE, '', '[Open the primary qualified dashboard](' + forge_url(primary.url) + ')', '', '| Project | Treatment | Pass / attempts | Source |', '| --- | --- | --- | --- |']
    selected=[r for r in rows if r['config']['primaryComparison']]
    for row in sorted(selected,key=lambda r:(r['config']['project'],r['config']['variant'])):
        c,m=row['config'],row['metrics']
        lines.append(f"| {c['project']} | {c['variant']} | {m['passes']}/{m['attempts']} | `{c['sourceCommit'][:12]}` |")
    lines += ['', f"Qualified complete-block attempts: **{sum(r['metrics']['passes'] for r in selected)}/{sum(r['metrics']['attempts'] for r in selected)} pass**. Source revisions differ only where a checker correction required a new frozen comparison; compare treatments within each project, not across projects.", '', '## Archived frozen comparison cohorts']
    for view in views:
        cohort = [r for r in rows if r['config']['protocolRevision'] == view['protocolRevision'] and r['config']['sourceCommit'] == view['sourceCommit']]
        count = sum(r['metrics']['attempts'] for r in cohort)
        passes = sum(r['metrics']['passes'] for r in cohort)
        label = 'native checker passes; see qualification notes above'
        lines += [f"### Revision {view['protocolRevision']}: {passes}/{count} {label}", '',
                  f"Source `{view['sourceCommit']}`. [Open interactive comparison dashboard]({view['forgeUrl']}).", '',
                  '| Project | Treatment | Recorded grade pass / attempts | Electron check pass / executed | Service pass / executed | Known cost (USD) |',
                  '| --- | --- | --- | --- | --- | --- |']
        for row in sorted(cohort, key=lambda r:(r['config']['project'], r['config']['variant'])):
            c, m = row['config'], row['metrics']
            link=f'https://forge.coreweave.com/wandb/{entity}/{project}/runs/{row["id"]}'
            lines.append(f"| {c['project']} | [{c['variant']}]({link}) | {m['passes']}/{m['attempts']} | {m['uiChecksPassed']}/{m['uiChecksExecuted']} | {m['serviceChecksPassed']}/{m['serviceChecksExecuted']} | {m['knownEstimatedCostUsd']:.4f} |")
        lines += ['']
    lines += ['## What changed in revision 3',
              'The shared Forge build now bundles the learner preload for Electron’s sandboxed module loader. '
              'Offline starter exercises retain their gaps. Actor-visible command output is bounded while full captured logs remain saved; '
              'the provider payload cap is 524,288 bytes. The app inference timeout is 120 seconds with no automatic retries. '
              'The model, 24-call trial budget, task assertions and image remain fixed. '
              'These changes are a new protocol cohort, not an isolated causal test of any single change.', '',
              '## What changed in revision 4',
              'A separate visible-answer acceptance check exposed the asynchronous polling bug. Revision 3 launches were halted; active attempts finished and remain recorded. '
              'Revision 4 awaits resolved IPC values in Node and then requires the actual answer text in the renderer before saving screenshots. '
              'Negative regression tests reject a predicate that resolves false. Old native grades are not rewritten or pooled with this corrected cohort.', '',
              '## Evidence navigation',
              'Open any treatment run above and its **sourceEvidenceV2** table for original trial runs, artifacts, outcomes and conversation IDs. '
              f'[Agent Lens traces](https://forge.coreweave.com/wandb/{entity}/{project}/weave/traces) retain coding-agent and app conversations separately.', '',
              '## Saved course notebooks',
              'These nine source-verified notebooks retain the evidence snapshot recorded in their committed source. '
              'Their capture timestamps identify historical snapshots; the dashboards above cover later completed campaigns. '
              'Opening a notebook launches no coding or inference work.']
    lines += [f"- [{n['title']}]({n['url']})" for n in notebooks]
    saved=json.loads((ROOT/'forge/results/snapshot.json').read_text())
    lines += ['', '## Bounded loops and checkpointed graphs', '',
              '| Loop checkpoint | Mode | Stop state | Rounds | Observed interventions |',
              '| --- | --- | --- | --- | --- |']
    for state in saved.get('loops',[]):
        lines.append(f"| `{state['file']}` | {state['mode']} | {state['status']} | {len(state['rounds'])} | {len(state.get('interventions',[]))} |")
    lines += ['', '| Graph checkpoint | Kind | State | Maker attempts |', '| --- | --- | --- | --- |']
    for state in saved.get('graphs',[]):
        lines.append(f"| `{state['file']}` | {'Manual control-flow qualification' if state.get('qualification') else 'Pi coding graph'} | {state['node']} | {state['attempts']} |")
    lines += ['', 'An approval state is a durable pause, not an accepted patch. Manual control-flow qualifications are excluded from Pi comparisons. The operations dashboard includes the underlying checkpoint tables.']
    unknown = sum(r['reservedEstimateUsd'] for r in ledger.get('uncertainEstimates', []))
    lines += ['', '## Accounting and limits',
              f"Charged estimate as of this report: **${ledger['spentEstimateUsd']:.6f}**, including **${unknown:.2f}** conservatively charged for unknown usage. "
              f"Active reservations: **${sum(ledger['reservations'].values()):.6f}**. These are application estimates, not provider invoices.",
              'The real two-hour exercise and original unsuccessful attempts remain recorded. '
              'Human approval pauses remain explicit; a passing candidate is not automatically accepted. '
              'No human time savings were inferred and no models were trained.']
    report.blocks = [wr.MarkdownBlock('\n'.join(lines))]
    report.save()
    restored = wr.Report.from_url(report.url)
    if restored.title != report.title or not restored.blocks:
        raise RuntimeError('Report readback mismatch')
    return {'url':report.url, 'forgeUrl':forge_url(report.url), 'title':report.title, 'readBackVerified':True}

def publish():
    entity, project = require_private_project()
    previous = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    rows = aggregates()
    recorded = {r['id']:r for r in previous.get('aggregateRuns',[])}
    pending = [r for r in rows if previous.get('evidenceTableVersion')!=2 or recorded.get(r['id'])!=r]
    for row in ([] if '--views-only' in sys.argv else pending):
        with wandb.init(entity=entity, project=project, id=row["id"], resume="allow",
                        job_type="course-dashboard-aggregate", name=row["config"]["label"],
                        config=row["config"], allow_val_change=True,
                        settings=wandb.Settings(disable_git=True, disable_code=True)) as run:
            run.log(row["metrics"])
            table = wandb.Table(columns=["project", "treatment", "repeat", "outcome", "run", "artifact", "agent_lens", "other_trace_ids", "trial_id"], data=[])
            for trial_id in row["config"]["trialIds"]:
                trial = json.loads((LOCAL / trial_id / "trial.json").read_text())
                traces=trial['conversationIds']
                trace_url=f'https://forge.coreweave.com/agent-lens/{entity}/{project}/conversations/{traces[0]}' if traces else None
                table.add_data(trial['project'],trial['variant'],trial['trial'],trial['outcome'],
                               trial.get("wandbRunUrl"),trial.get("artifactUrl"),trace_url,json.dumps(traces[1:]),trial_id)
            run.log({"sourceEvidenceV2": table})
    views = []
    cohorts = {(r["config"]["protocolRevision"], r["config"]["sourceCommit"]) for r in rows}
    for plan_file in LOCAL.glob('campaign-*.json'):
        plan = json.loads(plan_file.read_text())
        if plan['protocol'].get('protocolRevision', 1) >= 3 and len(plan['blocks']) == 18 and len({b['project'] for b in plan['blocks']}) == 6:
            cohorts.add((plan['protocol']['protocolRevision'], plan['sourceCommit']))
    for revision, source in sorted(cohorts):
        prior = next((v for v in previous.get("views", []) if v.get("protocolRevision") == revision and v.get("sourceCommit", source) == source), None)
        view = ws.Workspace.from_url(prior["url"]) if prior else ws.Workspace(entity=entity, project=project)
        view.name = f"Forge course — revision {revision} comparisons · {source[:8]}"
        view.runset_settings = ws.RunsetSettings(filters=[expr.Config("dashboardKind") == "comparison-aggregate", expr.Config("protocolRevision") == revision, expr.Config("sourceCommit") == source],
                                                pinned_columns=["config:label", "passRate", "attempts"])
        view.settings = ws.WorkspaceSettings(max_runs=100)
        view.sections = [ws.Section(name=("Archived grades · Project 05–06 checker defects" if source==HISTORY_SELECTOR_SOURCE else "Verified task outcomes and execution evidence") if revision >= 4 else "Historical checker outcomes — UI acceptance unqualified", panels=panels(revision,source!=HISTORY_SELECTOR_SOURCE), is_open=True,
                                    layout_settings=ReadableLayout(columns=2, rows=1)),
                         ws.Section(name="Original trial runs, traces and artifacts", is_open=True,
                                    panels=[wr.WeavePanelSummaryTable(table_name='sourceEvidenceV2',layout=wr.Layout(x=0,y=0,w=24,h=10))],
                                    layout_settings=ReadableLayout(columns=1,rows=1))]
        view.save()
        restored = ws.Workspace.from_url(view.url)
        if restored.name != view.name or len(restored.sections)!=2 or len(restored.sections[0].panels) != 6 or len(restored.sections[1].panels)!=1:
            raise RuntimeError("Dashboard readback mismatch")
        views.append({"protocolRevision": revision, "sourceCommit": source, "url": view.url, "forgeUrl": forge_url(view.url), "name": view.name, "readBackVerified": True})
    prior = previous.get('primary')
    primary = ws.Workspace.from_url(prior['url']) if prior else ws.Workspace(entity=entity,project=project)
    primary.name = 'Forge course — qualified end-to-end comparisons'
    primary.runset_settings = ws.RunsetSettings(filters=[expr.Config('dashboardKind') == 'comparison-aggregate',expr.Config('primaryComparison') == True],pinned_columns=['config:label','passRate','attempts'])
    primary.settings = ws.WorkspaceSettings(max_runs=100)
    primary.sections = [ws.Section(name='Qualified outcomes · three repeats per treatment',panels=panels(4),is_open=True,layout_settings=ReadableLayout(columns=2,rows=1)),
                        ws.Section(name='Original trial runs, traces and artifacts',is_open=True,panels=[wr.WeavePanelSummaryTable(table_name='sourceEvidenceV2',layout=wr.Layout(x=0,y=0,w=24,h=10))],layout_settings=ReadableLayout(columns=1,rows=1))]
    primary.save()
    restored=ws.Workspace.from_url(primary.url)
    if restored.name!=primary.name or len(restored.sections)!=2: raise RuntimeError('Primary dashboard readback mismatch')
    previous['primary']={'url':primary.url,'forgeUrl':forge_url(primary.url),'name':primary.name,'readBackVerified':True}
    prior = previous.get("operations")
    operations = ws.Workspace.from_url(prior["url"]) if prior else ws.Workspace(entity=entity, project=project)
    operations.name = "Forge course — execution and publication audit"
    operations.runset_settings = ws.RunsetSettings(query="Forge course execution and publication evidence")
    operations.sections = [ws.Section(name="Qualification, publication and accounting", is_open=True, panels=[
        wr.ScalarChart(title=title, metric=metric, layout=wr.Layout(x=(i%3)*8,y=(i//3)*6,w=8,h=6))
        for i,(title,metric) in enumerate([
            ("All completed coding attempts", "codingTrialAttempts"), ("Verified visible-answer passes", "verifiedUiPasses"),
            ("Verified notebooks", "notebooksPublishedVerified"), ("Charged estimate (USD)", "totalChargedEstimateUsd"),
            ("Unknown-usage charges (USD)", "chargedUnknownReservationsUsd"), ("Unresolved reservations (USD)", "unresolvedReservationsUsd"),
            ("Agent Lens conversations verified", "agentLensConversationsVerified"), ("W&B trial artifacts verified", "modelsTrialArtifactsVerified"),
            ("Cleanup records verified", "cleanupRecordsVerified"), ("Active course workers", "activeCourseWorkers")])])]
    operations.sections += [ws.Section(name='Project 07–08 execution states',is_open=True,panels=[
        wr.ScalarChart(title=title,metric=metric,layout=wr.Layout(x=(i%2)*12,y=(i//2)*6,w=12,h=6))
        for i,(title,metric) in enumerate([
            ('Real two-hour timers completed','realTwoHourTimersCompleted'),('Goal loops passed','goalLoopsPassed'),
            ('Pi graphs awaiting human approval','piGraphApprovalPauses'),('Manual graph controls awaiting approval','manualGraphApprovalPauses')])]),
        ws.Section(name='Loop checkpoints and observed interventions',is_open=True,panels=[wr.WeavePanelSummaryTable(table_name='loopEvidence',layout=wr.Layout(x=0,y=0,w=24,h=10))],layout_settings=ReadableLayout(columns=1,rows=1)),
        ws.Section(name='Graph checkpoints · manual controls labeled separately',is_open=True,panels=[wr.WeavePanelSummaryTable(table_name='graphEvidence',layout=wr.Layout(x=0,y=0,w=24,h=10))],layout_settings=ReadableLayout(columns=1,rows=1))]
    operations.save()
    previous.update(views=views, operations={"url":operations.url, "forgeUrl":forge_url(operations.url), "name":operations.name})
    # Preserve newly created IDs even if a later readback is unavailable.
    MANIFEST.write_text(json.dumps(previous, indent=2) + "\n")
    # Eventual consistency: verify every summary against the local source after finish.
    for attempt in range(20):
        api = wandb.Api()
        verified = True
        for row in rows:
            run = api.run(f"{entity}/{project}/{row['id']}")
            verified &= all(run.summary.get(k) == v for k, v in row["metrics"].items())
            verified &= all(run.config.get(k) == v for k, v in row["config"].items())
            verified &= bool(run.summary.get("sourceEvidenceV2"))
        if verified: break
        time.sleep(2)
    if not verified: raise RuntimeError("Dashboard aggregate readback mismatch")
    report = evidence_report(entity, project, rows, views, operations, primary, previous)
    result = {"schemaVersion": 1, "generatedAt": datetime.now(timezone.utc).isoformat(),
              "primary": previous["primary"], "views": views, "operations": {"url": operations.url, "forgeUrl": forge_url(operations.url), "name": operations.name},
              "aggregateRuns": rows, "aggregateReadBackVerified": True, "evidenceTableVersion": 2,
              "report": report,
              "note": "Derived aggregate runs are not coding trials. Revisions are separate cohorts. Missing usage is not zero."}
    MANIFEST.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"views": views, "operations": result["operations"]}, indent=2))

if __name__ == "__main__":
    publish()
