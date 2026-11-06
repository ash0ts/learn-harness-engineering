"""Rebuild the delivery report from recorded evidence without promoting failed trials."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[2]
LOCAL=ROOT/'forge/local-results'
def read(path): return json.loads(path.read_text())

def build():
    saved=read(ROOT/'forge/results/snapshot.json')
    ledger=read(LOCAL/'budget.json')
    notebooks=read(ROOT/'forge/publication-manifest.json')['notebooks']
    apps=read(LOCAL/'app-checks.json')
    validation=read(LOCAL/'notebook-validation.json')
    prs=sorted(read(ROOT/'forge/results/pull-requests.json'),key=lambda row:row['number'])
    expected='main'
    if len(prs)!=8: raise RuntimeError('Expected eight draft PRs')
    for pr in prs:
        if not pr['isDraft'] or pr['baseRefName']!=expected: raise RuntimeError('Incorrect draft PR chain')
        expected=pr['headRefName']
    rows=saved['trials'];blocks=saved.get('completedComparisonBlocks',[])
    published=sum(n['status']=='published_verified' for n in notebooks)
    timers=[s for s in saved.get('loops',[]) if s['mode']=='timer' and s['deadlineAt']-s['startedAt']>=7200000]
    real_timer=any(s['status']=='deadline' and not s.get('pendingTrialId') for s in timers)
    test_path=LOCAL/'forge-tests-final.log';test_text=test_path.read_text() if test_path.exists() else ''
    tests={key:int(value) for key,value in re.findall(r'(?:#|ℹ) (tests|pass|fail) (\d+)',test_text)}
    uncertain=sum(r['reservedEstimateUsd'] for r in ledger.get('uncertainEstimates',[]))
    trace_audit=read(LOCAL/'trace-audit.json') if (LOCAL/'trace-audit.json').exists() else {}
    conversations=trace_audit.get('conversations',[])
    sandbox_audit=read(LOCAL/'sandbox-final-audit.json') if (LOCAL/'sandbox-final-audit.json').exists() else {}
    local_checks=read(LOCAL/'local-checks.json') if (LOCAL/'local-checks.json').exists() else {}
    gates={'nineNotebooksVerified':published==9,'eighteenCompleteBlocks':len(blocks)>=18,'realTwoHourTimer':real_timer,
           'offlineApps':len(apps)==15 and all(a['passed'] for a in apps),'forgeTests':tests.get('fail')==0 and tests.get('pass',0)>0,
           'localNotebookRenders':len(validation['notebooks'])==9 and all(n['rendered'] for n in validation['notebooks']),
           'tracesReadBack':bool(conversations) and all(c['verified'] for c in conversations),
           'concurrentAppTraces':any(q['passed'] for q in saved.get('concurrencyQualifications',[])),
           'liveSandboxLifecycle':any(q['passed'] for q in saved.get('sandboxQualifications',[])),
           'graphApprovalPause':any(s.get('qualification') and any(t['to']=='approval' for t in s['transitions']) for s in saved.get('graphs',[])),
           'sandboxCleanup':bool(sandbox_audit.get('allTerminal')),'noUnsettledReservations':not ledger['reservations'] and not ledger.get('halted'),
           'documentationChecks':all(local_checks.get(k,{}).get('exitCode')==0 for k in ['anchors','docs'])}
    status='verified_delivery' if all(gates.values()) else 'verification_in_progress' 
    delivery={'schemaVersion':1,'generatedAt':datetime.now(timezone.utc).isoformat(),'status':status,'completionGates':gates,'traceAudit':{'conversations':len(conversations),'verified':sum(c['verified'] for c in conversations)},'sandboxAudit':sandbox_audit,'upstreamCommit':'a9342ff471f2c0e60be0c08b9f4a7c502df4e442','forkUrl':'https://github.com/ash0ts/learn-harness-engineering','targetRepeatsPerVariant':3,'trialAttempts':len(rows),'outcomes':dict(Counter(r['outcome'] for r in rows)),'passedTrials':sum(r['outcome']=='passed' for r in rows),'completedComparisonBlocks':blocks,'realTwoHourExerciseCompleted':real_timer,'loopStates':saved.get('loops',[]),'graphStates':saved.get('graphs',[]),'qualifications':{'attempted':len(saved['qualifications']),'passed':sum(r['passed'] for r in saved['qualifications'])},'budget':ledger,'knownAndAuditedEstimateUsd':ledger['spentEstimateUsd']-uncertain,'chargedUnknownReservationsUsd':uncertain,'checks':{'forgeTests':tests,'offlineAppsPassed':sum(a['passed'] for a in apps),'offlineAppsTotal':len(apps),'notebooksRenderedLocally':sum(n['rendered'] for n in validation['notebooks']),'notebooksPublishedVerified':published},'prs':[p['url'] for p in prs],'notebooks':notebooks,'trials':rows}
    (ROOT/'forge/results/delivery.json').write_text(json.dumps(delivery,indent=2)+'\n')
    lines=['# Forge course delivery and evidence','',f"Status: **{status.replace('_',' ')}**. All eight PRs remain drafts; none has been merged.",'',f"The [public personal fork]({delivery['forkUrl']}) preserves the offline course at upstream `{delivery['upstreamCommit']}`. Results and notebook sources belong to the private `wandb/learn-harness-engineering-forge` project.",'','## Actual execution','', '| Evidence | Recorded result |','| --- | --- |',f"| Existing offline app checks | {sum(a['passed'] for a in apps)}/{len(apps)} pass |",f"| Forge integration tests | {tests.get('pass','unavailable')} pass; {tests.get('fail','unavailable')} fail |",f"| Canonical notebooks | {sum(n['rendered'] for n in validation['notebooks'])}/9 render locally without inference credentials |",f"| Hosted notebook verification | {published}/9 |",f"| Qualification attempts | {delivery['qualifications']['passed']}/{delivery['qualifications']['attempted']} pass |",f"| Coding attempts | {len(rows)} completed; {delivery['outcomes']} |",f"| Complete comparison blocks | {len(blocks)} |",f"| Real two-hour timer | {'Completed' if real_timer else 'Not yet completed'} |",'', 'A completed comparison block contains every treatment for the same project, repeat and source revision. Completion does not imply a passing patch. The independent checker executes the exported patch in a fresh sandbox and distinguishes service behavior from Xvfb/Electron behavior. Source revisions and protocol hashes remain attached to each attempt.','', '## Comparison results','', '| Project | Treatment | Source | Attempts | Pass | Task failure | Infrastructure failure | Missing telemetry |','| --- | --- | --- | --- | --- | --- | --- | --- |']
    for key in sorted({(r['project'],r['variant'],r['sourceCommit']) for r in rows}):
        group=[r for r in rows if (r['project'],r['variant'],r['sourceCommit'])==key];c=Counter(r['outcome'] for r in group)
        lines.append(f"| {key[0]} | {key[1]} | `{key[2][:12]}` | {len(group)} | {c['passed']} | {c['task_failed']} | {c['infrastructure_failed']} | {c['telemetry_missing']} |")
    input_bound=sum(any('Frozen input byte budget' in str(phase.get('errors',[])) for phase in row.get('actorPhases',[])) for row in rows)
    lines += ['',f'**{input_bound}/{len(rows)} attempts** reached the local input-context guard. This is a bounded execution result, not evidence that the task is impossible. Original tool/error traces and unfinished patches remain available.']
    lines += ['', '## Independent check results','', '| Check | Passed | Executed |','| --- | --- | --- |']
    checks={}
    for row in rows:
        for check in (row.get('grade') or {}).get('checks',[]):
            counts=checks.setdefault(check['name'],[0,0]);counts[0]+=bool(check['passed']);counts[1]+=1
    lines += [f'| {name} | {counts[0]} | {counts[1]} |' for name,counts in sorted(checks.items())]
    lines += ['', 'A check omitted after compilation failed is not counted as an executed service or UI check. Shared failures can mask differences between treatments; the end-to-end outcome remains failed.', '', '## Instrumentation and execution qualification','',
              f"Agent Lens readback verified **{sum(c['verified'] for c in conversations)}/{len(conversations)} conversations**, including actual token usage and isolated span parentage. The readback includes **{sum(c.get('observedErrorSpans',0) for c in conversations)} error spans**; their errors remain visible rather than being counted as successful calls.", '']
    for q in saved.get('concurrencyQualifications',[]): lines.append(f"- Concurrent app tracing `{q['id']}`: {'passed' if q['passed'] else 'failed'}; {len(q.get('sessions',[]))} isolated conversations.")
    for q in saved.get('sandboxQualifications',[]): lines.append(f"- Sandbox lifecycle `{q['id']}`: {'passed' if q['passed'] else 'failed'}; {sum(c['passed'] for c in q.get('checks',[]))} live checks. {q.get('error','')}")
    lines += ['', 'Manual graph qualification candidates validate runner control flow and checker behavior. They are explicitly excluded from Pi trial counts and treatment comparisons.', '', '## Loops and graph states','']
    for state in saved.get('loops',[]): lines.append(f"- `{state['file']}`: **{state['status']}**, {len(state['rounds'])} recorded rounds; {len(state.get('interventions',[]))} entered/observed interventions.")
    for state in saved.get('graphs',[]): lines.append(f"- `{state['file']}`: **{state['node']}**, {state['attempts']} maker attempts, {len(state['transitions'])} durable transitions. An approval pause requires an explicit checksum-bound human decision.")
    lines += ['', '## Spend estimates','',f"Known/audited estimate: **${delivery['knownAndAuditedEstimateUsd']:.6f}**. Conservative charges for unknown usage: **${uncertain:.6f}**. Total charged estimate: **${ledger['spentEstimateUsd']:.6f}**. Active reservations: **${sum(ledger['reservations'].values()):.6f}**.",'', 'The original $50 application cap was removed after the user explicitly authorized an unlimited budget. Worker concurrency and lifetimes remain bounded. The timed-out qualification retains unknown token usage; its full $2 reservation was charged conservatively. Estimates are not provider invoices. Notebook EDIT compute is measured separately at the verified 2 CPU / 4 GiB rates ($0.3408/hour), including publication work. The durable ledger records authorizations and reconciliations. It must not be reset.','',saved.get('costScope',''),'', '## Draft PRs','']
    lines += [f"- [{p['title']}]({p['url']})" for p in prs]
    lines += ['', '## Notebooks','', '| Notebook | Publication status |','| --- | --- |']
    lines += [f"| [{n['title']}]({n['url']}) | {n['status']} |" for n in notebooks]
    lines += ['', 'The publication manifest binds each stable notebook ID to its canonical source commit, SHA-256, committed currentVersion, and rendered-output SHA-256. Verification compares rendered cell source and output code hashes, including when Forge omits its legacy lastStaticOutputAt timestamp. Opening the notebook renders saved evidence; paid reruns require an explicit action.','', '## Evidence and reproduction','']
    receipt_path=ROOT/'forge/results/evidence-publication.json'
    if receipt_path.exists():
        receipt=read(receipt_path);lines += [f"[W&B course audit]({receipt['runUrl']}) · [versioned evidence and exact source archives]({receipt['artifactUrl']})",'']
    lines += ['Per-trial W&B runs, artifacts and Agent Lens conversation links are in `snapshot.json` and the notebooks. Original failed attempts are retained alongside later qualification and comparison runs.','', '```sh','npm ci --prefix forge','npm run check --prefix forge','npm test --prefix forge','python3 forge/scripts/check_apps.py','npm run anchors:check','npm run docs:build','python3 forge/scripts/validate_notebooks.py','python3 forge/scripts/report.py','```','', 'Supply `WANDB_ENTITY`, `WANDB_PROJECT` and credentials externally. Use the existing shared ledger. `doctor --qualify --execute` qualifies the frozen protocol; `compare --repeats 3 --execute` schedules complete blocks. The Project 07 and 08 learning pages document loop, checkpoint and approval commands.','', 'Notebook publication uses the normal authenticated Forge EDIT/Marimo file editor and save workflow. Reserve compute using `forge/scripts/notebook_session.ts`, check for remote edits with `publication.py check-remote`, load canonical source, run saved-analysis cells, then verify committed source and rendered output with `publication.py verify`. Terminate and account for every editing session.','', '## Limits','', '- These are repeated runs of one frozen task per project, not a broad benchmark. Three repeats do not establish general treatment effects.', '- A task failure is evidence about this bounded attempt. Passing offline checks is not substituted for Electron or held-out service evidence.', '- The frozen comparison study and two-hour exercise use their recorded runner revision. Later cancellation and retry-diagnostic fixes are qualified separately; historical attempts are not rewritten or rescored.', '- Original early failures and audited accounting corrections are preserved. Missing usage is never reported as zero usage.', '- Hosted saved analysis is self-contained. Paid reruns require the configured shared coordinator checkout with Node, pinned dependencies, external credentials, qualification and the existing durable ledger; a fresh hosted runtime has no mounted coordinator by default.', '- The two-hour timer status above comes from its actual wall-clock checkpoint. Accelerated tests are reported separately.', '- Graph retries and rollback may end in failure. Human approval is never inferred from a test or automatically supplied by the agent.', '- No human time savings were inferred, no model training was performed, and only sample course data was used.','']
    (ROOT/'forge/results/README.md').write_text('\n'.join(lines));print('Report rebuilt:',status)
    return delivery
if __name__=='__main__':build()
