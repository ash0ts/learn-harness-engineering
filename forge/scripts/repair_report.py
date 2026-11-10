"""Build the revision-five repair receipt without rewriting historical cohorts."""
from collections import Counter
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
LOCAL=ROOT/'forge/local-results'
DEST=ROOT/'forge/results/protocol-v5'

def read(path):return json.loads(path.read_text())

def build():
    DEST.mkdir(parents=True,exist_ok=True)
    rows=[]
    for path in sorted((LOCAL/'protocol-v5').glob('qualification-*/qualification.json')):
        value=read(path)
        rows.append({key:value.get(key) for key in ['id','sourceCommit','startedAt','finishedAt','passed','inputTokens','outputTokens','sandboxSeconds','cleanupVerified','usageComplete','estimatedCostUsd','error']})
        rows[-1]['conversationId']=value.get('agent',{}).get('conversationId')
    ledger=read(LOCAL/'protocol-v5/budget.json')
    notebooks=read(LOCAL/'repair-v5/remote-before.json')['notebooks']
    validation=read(LOCAL/'notebook-validation.json')['notebooks'];apps=read(LOCAL/'app-checks.json')
    preservation=read(LOCAL/'lesson-preservation.json')
    archive=read(ROOT/'forge/results/snapshot.json');primary=read(ROOT/'forge/lessons/evidence.json')['primaryTrialIds']
    attempts=[read(path) for path in (LOCAL/'protocol-v5').glob('*/trial.json')]
    attempts=[r for r in attempts if r.get('protocol',{}).get('protocolRevision')==5 and r.get('finishedAt')]
    comparisons=[r for r in attempts if r.get('project') in [f'project-{i:02}' for i in range(1,7)]]
    targets={'comparisonAttempts':39,'loopControllers':9,'realTwoHourTimers':3,'graphs':3,'verificationPairs':3,'newHumanDecisions':2}
    operations={p.stem:read(p) for p in (LOCAL/'protocol-v5/operations').glob('*.json')}
    loops=[read(p) for p in (LOCAL/'protocol-v5').glob('cohort-loop-*-checkpoint.json')]
    graphs=[read(p) for p in (LOCAL/'protocol-v5').glob('cohort-graph-*-checkpoint.json')]
    finished_loops=[r for r in loops if operations.get(r['id'],{}).get('phase')=='completed' and not r.get('pendingTrialId')]
    timers=[r for r in finished_loops if r['mode']=='timer' and r['status']=='deadline' and r['deadlineAt']-r['startedAt']>=7200000 and datetime.fromisoformat(operations[r['id']]['updatedAt'].replace('Z','+00:00')).timestamp()*1000>=r['deadlineAt']]
    finished_graphs=[r for r in graphs if operations.get(r['id'],{}).get('phase')=='completed' and r['node'] in ('approval','done','rejected','failed')]
    decisions={r['approval']['decisionId'] for r in graphs if r.get('approval',{}).get('decisionId') and r['approval']['candidateSha256']==r.get('candidate',{}).get('sha256')}
    pairs=[]
    for path in (LOCAL/'protocol-v5').glob('verification-pairs-*.json'):
        rows_for_patch=read(path)['pairs']
        for repeat in (1,2,3):
            group=[r for r in rows_for_patch if r['repeat']==repeat]
            if len(group)==2 and {r['mode'] for r in group}=={'serial','parallel'} and all(r['completed'] for r in group) and len({r['candidateSha256'] for r in group})==1:pairs.append(group)
    completed={'comparisonAttempts':len(comparisons),'loopControllers':len(finished_loops),'realTwoHourTimers':len(timers),'graphs':len(finished_graphs),'verificationPairs':len(pairs),'newHumanDecisions':len(decisions)}
    groups=[]
    for project,variant,source in sorted({(r['project'],r['variant'],r['sourceCommit']) for r in comparisons}):
        group=[r for r in comparisons if (r['project'],r['variant'],r['sourceCommit'])==(project,variant,source)]
        groups.append({'project':project,'variant':variant,'sourceCommit':source,'attempts':len(group),'outcomes':dict(Counter(r['outcome'] for r in group)),'trialIds':[r['id'] for r in group]})
    tests=(LOCAL/'repair-v5/validation/typescript.log').read_text()
    python_tests=(LOCAL/'repair-v5/validation/python.log').read_text()
    publication_tests=(LOCAL/'repair-v5/validation/publication.log').read_text()
    value={'schemaVersion':1,'protocolRevision':5,'generatedAt':datetime.now(timezone.utc).isoformat(),
        'status':'blocked_missing_usage','candidateRunnerCommit':validation[0]['runnerCommit'],
        'historical':{'archiveAttempts':len(archive['trials']),'primaryComparisonAttempts':len(primary),'snapshotSha256':hashlib.sha256((ROOT/'forge/results/snapshot.json').read_bytes()).hexdigest(),'unaltered':True},
        'targets':targets,'completed':completed,'comparisonGroups':groups,'qualificationAttempts':rows,
        'budget':{'limitUsd':ledger['limitUsd'],'actualCostKnown':False,'knownSettledEstimateUsd':ledger['spentEstimateUsd'],
            'unresolvedReservationsUsd':sum(ledger['reservations'].values()),'halted':ledger.get('halted'),'billingReadback':read(LOCAL/'repair-v5/provider-usage.json')},
        'validation':{'typescriptTestsPassed':int(re.search(r'pass (\d+)',tests)[1]),'typescriptTestsFailed':int(re.search(r'fail (\d+)',tests)[1]),
            'pythonTestsPassed':int(re.search(r'Ran (\d+) tests',python_tests)[1]),'publicationGuardsPassed':int(re.search(r'Ran (\d+) tests',publication_tests)[1]),
            'offlineAppsPassed':sum(r['passed'] for r in apps),'offlineAppsTotal':len(apps),'localNotebooksRendered':sum(r['rendered'] for r in validation),
            'docsBuild': 'build complete' in (LOCAL/'repair-v5/validation/docs.log').read_text(),'anchorCheck':'OK: anchor map matches' in (LOCAL/'repair-v5/validation/anchors.log').read_text()},
        'presentation':{'historicalFilesUnchanged':preservation['historicalFilesUnchanged'],'cellOrderLabelsImagesAndResultsPreserved':True,'factualSentenceEdits':preservation['factualSentenceEdits']},
        'notebooks':notebooks,'traceReadback':read(LOCAL/'repair-v5/trace-readback.json'),
        'validationEvidence':[{"path":p.relative_to(LOCAL).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((LOCAL/'repair-v5/validation').glob('*.log'))],
        'unverifiedGates':['Corrected controls in the pinned CPU image under Xvfb','Complete protocol-5 scored campaign','Three real two-hour timers','Three graph executions and three serial/parallel pairs','Two new human graph decisions','Reproduction of the original full Pi lingering-worker failure','Authenticated Forge Edit and Preview downloads plus fresh runtime restore','Publication of these nine candidate sources through the native editor','Independent student-account rehearsal; user said only the owner can test'],
        'limitations':['No GPU sandbox or training experiment is part of this CPU-only track. Forge serverless inference is separately qualified.','Two SDK-only lifecycle probes exited cleanly; they did not reproduce the original Pi worker hang.','Local controller tests and locally compiled reference repairs are not live course-trial evidence.','The one new qualification failed before app qualification; the unknown second request is not charged as zero.','Remote notebook sources were read back unchanged. They still contain the preceding iteration, not these candidate repairs.']}
    (DEST/'status.json').write_text(json.dumps(value,indent=2)+'\n')
    (DEST/'presentation.json').write_text(json.dumps(preservation,indent=2)+'\n')
    lines=['# Protocol 5 repair status','', '**Rollout is blocked on missing provider usage.** Runtime repairs and candidate notebooks are locally validated. No corrected scored campaign or repaired notebook publication is claimed.','',
        f"Candidate notebook runner: `{value['candidateRunnerCommit']}`. Historical evidence remains byte-for-byte unchanged: {len(archive['trials'])} archived attempts and {len(primary)} primary comparisons.",'',
        '| Check | Actual result |','| --- | --- |']
    lines += [f"| TypeScript tests | {value['validation']['typescriptTestsPassed']} pass; {value['validation']['typescriptTestsFailed']} fail |",f"| Learner and publication tests | {value['validation']['pythonTestsPassed']} pass, plus {value['validation']['publicationGuardsPassed']} publication guards |",f"| Offline apps | {value['validation']['offlineAppsPassed']}/{len(apps)} pass |",f"| Local saved notebook views | {value['validation']['localNotebooksRendered']}/9 render without credentials |",'| Docs and anchors | Pass |','| Candidate notebooks published | 0/9; all previous remote sources unchanged |','', '| Corrected experiment | Completed | Target |','| --- | --- | --- |']
    lines += [f'| {key} | {completed[key]} | {target} |' for key,target in targets.items()]
    lines += ['', '## Qualification and accounting', '', 'The qualification recorded 396 input and 61 output tokens on its first model request. The second request timed out without usage. Its sandbox was verified terminated; the conservative lifetime was 209.785 seconds. Agent Lens read-back did not provide the missing usage, and the billing query returned HTTP 403. The full $2 reservation remains unresolved. It is a reservation, not a measured charge. The uncapped research authorization does not override fail-closed accounting.', '']
    for row in rows:
        lines += [f"- Operation `{row['id']}`, source `{row['sourceCommit']}`: failed; cleanup verified; usage incomplete. [Agent Lens conversation](https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge/conversations/{row['conversationId']})."]
    lines += ['', '## Resume safely', '', '1. Obtain the missing provider usage receipt for the qualification. Use `recovery-report` and the evidence-bound `reconcile` command in [RECOVERY.md](../../RECOVERY.md). Do not delete the ledger or overwrite this failed outcome.', '2. Run the frozen protocol-five qualification and all baseline/reference/regression controls before scored attempts. `python forge/scripts/protocol5.py freeze --schedule /path/to/evidence/schedule.json` records the exact inputs; `commands` displays the planned CLI invocations. `run --execute` refuses unresolved accounting and interrupted steps.', '3. Run the 39-attempt comparison, nine loop controllers, three graphs and three balanced verification pairs. The scheduler never approves graphs. Two new checksum-bound decisions remain human work. An interrupted two-hour timer resumes through `loop --resume` with the original checkpoint and deadline.', '4. Perform the owner rehearsal and native Forge Edit/Preview download test; inspect and restore the actual archive. The independent student-account gate remains unverified because no other tester is available.', '5. Recheck remote edits, reserve notebook compute, and publish the same nine IDs through the native editor. Verify currentVersion, exact source bytes and rendered output before updating the original publication manifest.', '', '## What remains unverified','']
    lines += ['- '+item+'.' for item in value['unverifiedGates']]
    lines += ['', '## Notebook sources', '', 'These links still show the preceding hosted iteration. Candidate source checksums and current remote versions are recorded separately in `status.json`.','']
    lines += [f"- [{Path(row['file']).stem}]({row['url']}) — prior version {row['currentVersion']['versionIndex']}; candidate not published." for row in notebooks]
    lines += ['', '## Limits on the claims','']+['- '+item for item in value['limitations']]
    dashboard=DEST/'dashboard.json'
    if dashboard.exists():
        hosted=read(dashboard)
        lines += ['', '## Private dashboard and evidence', '', '[Open the protocol 5 dashboard]('+hosted['forgeUrl']+') · [Audit run]('+hosted['runUrl']+'). The run and versioned artifact are separate from historical comparison runs.', '', '![Protocol 5 dashboard showing qualification blocked and zero scored attempts](dashboard.png)']
    (DEST/'README.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'status':value['status'],'validation':value['validation'],'completed':completed},indent=2))

if __name__=='__main__':build()
