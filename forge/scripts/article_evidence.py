# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib==3.10.8"]
# ///
"""Build article figures and an allowlisted index from recorded evidence; no paid work.

uv run forge/scripts/article_evidence.py --reports forge/results
Inputs are immutable report snapshots plus their original local-results files.
Raw conversations, credentials, and unpublished fixture contents are not exported.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "forge/local-results"
ASSETS = ROOT / "docs/en/forge/assets"
PUBLIC = ROOT / "docs/public/forge/evidence"
INK, MUTED, BG = "#242722", "#62665e", "#faf9f6"
PASS, FAIL, ABSENT = "#176c59", "#b33f2b", "#e7e6e0"
LABELS = {"minimal": "Minimal", "explicit": "Explicit rules", "workspace-docs": "Workspace docs",
          "recovery": "Recovery files", "runtime-feedback": "Runtime feedback", "single-role": "Single role",
          "gen-eval": "Maker / checker", "plan-gen-eval": "Planner / maker / checker", "capstone": "Capstone"}
CHECKS = [
    ("strict compile and renderer build", "Build"),
    ("real import and persistence after reconstruction", "Import"),
    ("actual indexing keeps every nonempty paragraph", "Chunks"),
    ("extracted metadata", "Metadata"),
    ("single-document indexing is reflected in status", "Status"),
    ("actual retrieval and Q&A persist two turns", "Q&A"),
    ("architecture checker rejects a seeded boundary violation", "Guard"),
    ("Electron window, preload, import, indexing and question UI under Xvfb", "Electron"),
]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": INK,
    "figure.facecolor": BG, "axes.facecolor": BG, "svg.fonttype": "none",
    "svg.hashsalt": "forge-course-visual-evidence-v1", "savefig.dpi": 180})

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text())
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
def safe_text(value):
    return re.sub(r"/Users/[^\s\"']+", "[local path]", str(value))
def artifact_path(value):
    return value.split("/forge/local-results/", 1)[-1] if value else None
def ordered(rows):
    order = list(LABELS)
    return sorted(rows, key=lambda t: (t["project"], order.index(t["variant"]) if t["variant"] in order else 99, t["trial"], t["id"]))
def save(fig, name):
    for ext in ["svg", "png"]:
        fig.savefig(ASSETS / "figures" / f"{name}.{ext}", bbox_inches="tight", metadata={"Date": None} if ext == "svg" else {})
    plt.close(fig)

def overview(rows):
    groups = defaultdict(list)
    for row in ordered(rows): groups[(row["project"], row["variant"])].append(row)
    fig, ax = plt.subplots(figsize=(8.2, 8.3))
    ax.set(xlim=(0, 8.2), ylim=(len(groups)+1.6, -1.3)); ax.axis("off")
    ax.text(0, -0.75, "39 attempts, one task per project", size=19, weight="bold")
    ax.text(0, -0.1, "Each square is one attempt. 19 passed the complete protected grade.", size=10.5, color=MUTED)
    for j in range(3): ax.text(5.15+j*.73, .6, f"R{j+1}", ha="center", size=10, color=MUTED)
    ax.text(7.55, .6, "Passed", ha="center", size=10, color=MUTED)
    for i, ((project, variant), group) in enumerate(groups.items(), 1):
        assert len(group) == 3 and {x['trial'] for x in group} == {1,2,3}
        ax.text(0, i+.27, f"{project[-2:]}  {LABELS[variant]}", size=11.5)
        for j, row in enumerate(group):
            ok=row["outcome"]=="passed"
            ax.add_patch(Rectangle((4.85+j*.73, i-.05), .59, .6, color=PASS if ok else FAIL))
            ax.text(5.15+j*.73, i+.27, "P" if ok else "F", color="white", ha="center", va="center", weight="bold")
        ax.text(7.55, i+.27, f"{sum(x['outcome']=='passed' for x in group)}/3", ha="center", weight="bold")
    ax.text(0, len(groups)+1.2, "P = passed · F = task failed. Source revisions differ between projects; no pooled treatment ranking.", size=9.1, color=MUTED)
    save(fig,"primary-outcomes")

def check_matrix(project, rows):
    rows=ordered(rows)
    present={c["name"] for r in rows for c in r["checks"]}
    columns=[c for c in CHECKS if c[0] in present]
    unknown=present-{c[0] for c in CHECKS}
    if unknown: raise ValueError(f"Unmapped checker labels: {unknown}")
    n=len(rows); width=max(8.1,3.6+len(columns)*.78)
    fig,ax=plt.subplots(figsize=(width,2.8+n*.46))
    ax.set(xlim=(0,width),ylim=(n+2.3,-1.8));ax.axis('off')
    passed=sum(r['outcome']=='passed' for r in rows)
    ax.text(0,-1.15,f"Project {project[-2:]} · {passed}/{n} complete passes",size=18,weight='bold')
    ax.text(0,-.45,"Recorded checks in the primary cohort; a blank is not a pass.",size=10.5,color=MUTED)
    start=3.1; step=(width-start)/len(columns)
    for j,(_,label) in enumerate(columns): ax.text(start+j*step+step/2,.35,label,ha='center',size=10)
    for i,row in enumerate(rows,1):
        label=f"{LABELS[row['variant']]} · {row['trial']}"
        ax.text(0,i+.24,label,size=10.3)
        checks={c['name']:c['passed'] for c in row['checks']}
        for j,(name,_) in enumerate(columns):
            status=checks.get(name); color=ABSENT if status is None else PASS if status else FAIL
            ax.add_patch(Rectangle((start+j*step+.04,i-.12),step-.08,.65,facecolor=color,edgecolor=BG))
            ax.text(start+j*step+step/2,i+.22,"—" if status is None else "P" if status else "F",ha='center',va='center',color=MUTED if status is None else 'white',weight='bold')
    ax.text(0,n+1.25,"P = passed · F = failed · — = not executed (not measured)",size=10,color=MUTED)
    ax.text(0,n+1.85,"A failed build skips later checks. The explorer retains exact errors and trial IDs.",size=9.7,color=MUTED)
    save(fig,project+'-checks')

def roles():
    fig,ax=plt.subplots(figsize=(8.1,3.7))
    allocations=[('Single role',[(24,'Maker',PASS)]),('Maker / checker',[(10,'Maker',PASS),(4,'Check','#ad6530'),(10,'Revise','#527f9e')]),('Planner / maker / checker',[(4,'Plan','#74618b'),(8,'Maker',PASS),(4,'Check','#ad6530'),(8,'Revise','#527f9e')])]
    for i,(name,parts) in enumerate(allocations):
        left=0
        for count,label,color in parts:
            ax.barh(i,count,left=left,height=.64,color=color)
            ax.text(left+count/2,i,f'{label}\n{count}',ha='center',va='center',color='white',size=10);left+=count
    ax.set_yticks(range(3),[r[0] for r in allocations]);ax.invert_yaxis();ax.set_xlim(0,24);ax.set_xticks([0,4,8,12,16,20,24]);ax.set_xlabel('Maximum model calls per attempt (not tokens or dollars)')
    ax.set_title('A reviewer spends part of the 24-call allowance',loc='left',pad=17,size=16,weight='bold')
    for spine in ax.spines.values():spine.set_visible(False)
    save(fig,'role-allowances')

def timer(snapshot,by_id):
    loop=next(x for x in snapshot['loops'] if x['file']=='project-07-real-timer-qualified.json')
    start=loop['startedAt']/1000;duration=(loop['deadlineAt']-loop['startedAt'])/60000
    fig,ax=plt.subplots(figsize=(8.1,4.6))
    for i,round_ in enumerate(loop['rounds']):
        t=by_id[round_['trialId']];a=datetime.fromisoformat(t['startedAt'].replace('Z','+00:00')).timestamp();b=datetime.fromisoformat(t['finishedAt'].replace('Z','+00:00')).timestamp()
        ax.barh(i,(b-a)/60,left=(a-start)/60,height=.6,color=FAIL)
        ax.text((b-start)/60+1,i,'Failed',va='center',size=9.5,color=FAIL)
    ax.axvline(duration,color=INK,lw=1.2,linestyle='--')
    for event in loop['interventions']:
        minute=(datetime.fromisoformat(event['at'].replace('Z','+00:00')).timestamp()-start)/60
        ax.axvline(minute,color='#986822',linestyle=':',lw=1.5)
    ax.set_yticks(range(8),[f'Round {i+1}' for i in range(8)]);ax.invert_yaxis();ax.set_xlim(0,128);ax.set_xticks([0,15,30,45,60,75,90,105,120]);ax.set_xlabel('Minutes from the original start · bars show trial elapsed time, not billed occupancy')
    ax.set_title('Eight rounds across a real two-hour window',loc='left',pad=17,size=17,weight='bold')
    ax.text(.01,1.02,'Dotted line: one recorded intervention. Dashed line: original deadline.',transform=ax.transAxes,color=MUTED,size=9.5)
    for spine in ax.spines.values():spine.set_visible(False)
    save(fig,'timer-timeline')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reports',type=Path,default=ROOT/'forge/results');args=parser.parse_args()
    reports=args.reports.resolve();snapshot=read(reports/'snapshot.json');delivery=read(reports/'delivery.json')
    publication=read(reports/'evidence-publication.json');dashboards=read(reports/'dashboards.json');approval=read(reports/'qualification-approval.json')
    for name in ['captures','figures']:(ASSETS/name).mkdir(parents=True,exist_ok=True)
    PUBLIC.mkdir(parents=True,exist_ok=True)
    primary=set(delivery['primaryComparisons']['trialIds']);rows=[];assets=[]
    def copy_capture(source,name,kind,source_url,**extra):
        dest=ASSETS/'captures'/name;shutil.copyfile(source,dest)
        entry={'file':'captures/'+name,'kind':kind,'sha256':digest(dest),'bytes':dest.stat().st_size,
            'originalArtifactPath':str(source.relative_to(LOCAL)),'sourceUrl':source_url,'transformation':'none',**extra}
        assets.append(entry);return entry
    for t in ordered(snapshot['trials']):
        folder=LOCAL/t['id'];original=read(folder/'trial.json')
        row={k:t.get(k) for k in ['id','project','variant','trial','sourceCommit','outcome','inputTokens','outputTokens','estimatedCostUsd','reconciledEstimateUsd','chargedUnknownReservationUsd','conversationIds','wandbRunUrl','artifactUrl','startedAt','finishedAt','actorCompleted','protocolRevision','protocolSha256']}
        row['primary']=t['id'] in primary;row['checks']=[{**c,**({'error':safe_text(c['error'])} if 'error' in c else {})} for c in (t.get('grade') or {}).get('checks',[])]
        row['actorError']=safe_text(t['error']) if t.get('error') else None
        row['protocol']=original.get('protocol');row['applicationSha256']=original.get('applicationSha256');row['checkerSha256']=original.get('checkerSha256')
        row['agentLensUrls']=['https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge/conversations/'+c for c in t['conversationIds']]
        row['actorPhases']=t.get('actorPhases',[])
        patch=folder/'candidate.diff';row['patchSha256']=digest(patch) if patch.exists() else None
        row['changedFiles']=re.findall(r'^\+\+\+ b/(.*)$',patch.read_text(),re.M) if patch.exists() else []
        row['evidenceFiles']=[{'path':str(p.relative_to(LOCAL)),'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(folder.rglob('*')) if p.is_file() and p.suffix in {'.json','.diff','.txt','.log','.png'}]
        row['captures']=[]
        for image in sorted(folder.rglob('*.png')):
            name=t['id']+'-'+str(image.relative_to(folder)).replace('/','-')
            row['captures'].append(copy_capture(image,name,'trial-screenshot',t['artifactUrl'],trialId=t['id'],primary=row['primary'],trialFinishedAt=t['finishedAt']))
        rows.append(row)
    assert len(rows)==129 and len(primary)==39 and sum(r['primary'] and r['outcome']=='passed' for r in rows)==19
    captures=[('overview-final.jpg','00-overview'),('project01-revision4.jpg','01'),('project02-revision4.jpg','02'),('project03-revision4.jpg','03'),('project04-revision4.jpg','04'),('project05-qualified.jpg','05'),('project06-qualified.jpg','06'),('project07-revision4.jpg','07'),('project08-final.jpg','08')]
    notebook_ids=['Tm90ZWJvb2s6MTUzMTM%3D','Tm90ZWJvb2s6MTUzMTQ%3D','Tm90ZWJvb2s6MTUzMTU%3D','Tm90ZWJvb2s6MTUzMTY%3D','Tm90ZWJvb2s6MTUzMTc%3D','Tm90ZWJvb2s6MTUzMTg%3D','Tm90ZWJvb2s6MTUzMTk%3D','Tm90ZWJvb2s6MTUzMjA%3D','Tm90ZWJvb2s6MTUzMjE%3D']
    for (filename,project),notebook in zip(captures,notebook_ids):
        copy_capture(LOCAL/'publication'/filename,'notebook-'+project+'.jpg','notebook-screenshot','https://forge.coreweave.com/notebooks/'+notebook,captureDate='2026-11-06',snapshotNote='Saved publication view; may include older cohorts. Predates the later manual graph approval.')
    for filename in ['dashboard-comparisons-final.jpg','dashboard-operations-final.jpg','dashboard-source-evidence-final.jpg','dashboard-loop-evidence-final.jpg','dashboard-graph-evidence-final.jpg']:
        url=dashboards['primary' if 'comparisons' in filename or 'source-evidence' in filename else 'operations']['forgeUrl']
        copy_capture(LOCAL/'publication'/filename,filename,'dashboard-screenshot',url,captureDate='2026-11-06',snapshotNote='Original saved view. Run-list counts include derived aggregate runs; they are not coding-attempt counts. Predates later manual approval.')
    trace_captures=[('agent-lens-agent-revision4.jpg','01a1b0aa-ff8b-71d2-a2f0-9f7999092eed','coding-agent'),('agent-lens-revision4.jpg','app-bace80b4-24a6-4c67-bc75-def5cd385a2d','application')]
    audit=read(LOCAL/'trace-audit.json')
    for filename,conversation,role in trace_captures:
        entry=next(c for c in audit['conversations'] if c['conversationId']==conversation)
        assert entry['verified']
        copy_capture(LOCAL/'publication'/filename,filename,'trace-screenshot',entry['url'],captureDate='2026-11-06',conversationId=conversation,role=role,trialId=entry.get('trialId'),traceReadbackVerified=True)
    # Supplemental UI qualifications and graph lanes are not coding attempts.
    # Keep their captures separate, including failed diagnostic checks.
    trial_ids={r['id'] for r in rows}
    for image in sorted(LOCAL.rglob('*.png')):
        relative=image.relative_to(LOCAL)
        if image.name not in {'electron.png','visible-answer.png','history-diagnostic.png'} or relative.parts[0] in trial_ids: continue
        if not relative.parts[0].startswith(('graph-','visible-ui-','history-diagnostic-','checker-diagnostic-')): continue
        copy_capture(image,'supplemental-'+str(relative).replace('/','-'),'supplemental-screenshot',publication['artifactUrl'],
            qualificationId=relative.parts[0],snapshotNote='Independent verification, manual qualification, or checker diagnostic. Excluded from coding-attempt counts; consult the adjacent archived result before interpreting the image.')
    loops=[]
    for loop in snapshot['loops']:
        loops.append({k:loop[k] for k in ['file','id','mode','sourceCommit','startedAt','deadlineAt','status','rounds','interventions'] if k in loop})
    graphs=[]
    for graph in snapshot['graphs']:
        candidate=graph.get('candidate') or {}
        graphs.append({**{k:graph[k] for k in ['file','id','sourceCommit','node','attempts','transitions','qualification'] if k in graph},
            'candidateSha256':candidate.get('sha256'),'trialId':candidate.get('trialId'),
            'verification':[{'lane':v['lane'],'passed':v['passed'],'artifactPath':artifact_path(v.get('evidence'))} for v in graph.get('verification',[])],
            'protectedGradePassed':(graph.get('lastProtectedGrade') or {}).get('passed')})
    data={'schemaVersion':1,'capturedAt':snapshot['capturedAt'],'sourceReportCommit':'258cf51fdc692f9be60952d8dd811de90588a0c4',
        'inputs':{p.name:digest(p) for p in [reports/'snapshot.json',reports/'delivery.json',reports/'evidence-publication.json',reports/'qualification-approval.json']},
        'definitions':{'primary':'39 attempts, 13 treatments, 3 repeats each. One task per project; source revisions kept separate.',
            'other':'Historical, diagnostic, loop and graph attempts; not extra primary repeats. Native grades retained.',
            'notExecuted':'No corresponding check in the recorded grade. Not counted as pass or fail.',
            'screenshots':'Original unmodified captures. A screenshot records one UI state; the protected grade establishes the tested assertions.'},
        'primaryTrialIds':sorted(primary),'trials':rows,'loops':loops,'graphs':graphs,
        'manualApproval':{k:approval[k] for k in ['checkpointId','sourceCommit','previousNode','node','approval','verifiedLanes','protectedGradeInOriginalCheckpoint','excludedFromCodingTrialCounts','note']},
        'evidenceArtifact':{k:publication[k] for k in ['artifact','artifactUrl','artifactFileCount','sourceArchives']},
        'dashboards':{k:dashboards[k]['forgeUrl'] for k in ['primary','operations']},
        'audit':{'conversationsVerified':delivery['traceAudit']['verified'],'trialArtifactsVerified':delivery['modelsAudit']['verified'],
            'cleanupRecordsVerified':delivery['sandboxAudit']['recordedWorkers'],'activeWorkers':len(delivery['sandboxAudit']['active']),
            'chargedEstimateUsd':delivery['budget']['spentEstimateUsd'],'unknownUsageChargesUsd':delivery['chargedUnknownReservationsUsd'],
            'notebooksVerified':9,'qualifiedVisibleAnswerPasses':delivery['verifiedUiPasses'],'qualifiedVisibleAnswerAttempts':delivery['verifiedUiAttempts']},
        'qualifications':[{**{k:q.get(k) for k in ['id','passed','sourceCommit','startedAt','finishedAt','inputTokens','outputTokens','estimatedCostUsd','reconciledEstimateUsd','chargedUnknownReservationUsd','agentConversationId','appConversationId']},'error':safe_text(q['error']) if q.get('error') else None} for q in snapshot['qualifications']],
        'assets':assets}
    write(PUBLIC/'catalog.json',data)
    with (PUBLIC/'trials.csv').open('w',newline='') as file:
        fields=['id','project','variant','trial','primary','sourceCommit','protocolSha256','outcome','inputTokens','outputTokens','reconciledEstimateUsd','patchSha256','wandbRunUrl','artifactUrl']
        writer=csv.DictWriter(file,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    primary_rows=[r for r in rows if r['primary']];overview(primary_rows)
    for i in range(1,7):check_matrix(f'project-{i:02}',[r for r in primary_rows if r['project']==f'project-{i:02}'])
    roles();timer(snapshot,{r['id']:r for r in rows})
    print(json.dumps({'trials':len(rows),'primary':len(primary_rows),'captures':len(assets),'figures':9,'evidenceFiles':sum(len(r['evidenceFiles']) for r in rows)},indent=2))

if __name__=='__main__': main()
