"""Generate self-contained, native Marimo course lessons and evidence browsers."""
from pathlib import Path
import argparse
import ast
import base64
import hashlib
import json
import subprocess
import urllib.parse
import lesson_cells as lc
from course_packets import ORIGINAL, SLUGS, packet

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
def assignments(path):
    return {n.targets[0].id:n.value for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}

def markdown_cell(text):
    return 'def _(mo):\n    mo.md(r\"\"\"\n'+''.join('    '+line+'\n' for line in text.splitlines())+'    \"\"\")\n    return'

def generate(runner_commit=None, projects=None, refresh_evidence=False):
    evidence=json.loads((ROOT/'forge/lessons/evidence.json').read_text())
    generated=[]
    for index,(filename,project,title,description) in enumerate(TITLES):
        if projects and project not in projects:continue
        dest=ROOT/'forge/notebooks'/filename
        previous=assignments(dest) if dest.exists() else {}
        if refresh_evidence or not previous:
            master=json.loads((ROOT/'forge/results/snapshot.json').read_text())
            saved=project_snapshot(master,project)
        else:
            saved=json.loads(ast.literal_eval(previous['saved'].args[0]))
        commit=runner_commit or (ast.literal_eval(previous['runner_commit']) if previous else subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
        lesson=(ROOT/'forge/lessons'/filename.replace('.py','.md')).read_text()
        sections=lesson.split('<!-- cell -->')
        nav=' · '.join(f'[{"Overview" if i==0 else f"{i:02}"}](https://forge.coreweave.com/notebooks/'+urllib.parse.quote('Tm90ZWJvb2s6MTUz'+['MTM=','MTQ=','MTU=','MTY=','MTc=','MTg=','MTk=','MjA=','MjE='][i],safe='')+')' for i in range(9))
        # Notebook IDs are stable; no notebook creation or HTML import is involved.
        intro='# '+title+'\n\n'+nav+'\n\n**Course lab + recorded Forge case.** Read and inspect saved evidence first. Coding trials require an explicit paid action; notebook runtime compute is separate.\n\n'+description
        cells=[lc.IMPORTS,lc.CONSTANTS,markdown_cell(intro)]
        cells += [markdown_cell(part.strip()) for part in sections[:-1]]
        for image in evidence['assets'][project]:
            path=ROOT/'forge/lessons/assets'/image['file']
            data=path.read_bytes()
            if hashlib.sha256(data).hexdigest()!=image['sha256']:raise RuntimeError('Visual provenance mismatch: '+str(path))
            mime='image/svg+xml' if path.suffix=='.svg' else 'image/jpeg' if path.suffix=='.jpg' else 'image/png'
            uri='data:'+mime+';base64,'+base64.b64encode(data).decode()
            cells.append('def _(mo):\n    mo.image('+repr(uri)+', alt='+repr(image['caption'])+', caption='+repr(image['caption'])+', width="100%")\n    return')
        cells += [lc.RESULTS,lc.SELECTOR,lc.DETAIL,lc.LIFECYCLE,markdown_cell(sections[-1].strip()),lc.WORKSHEET,lc.DOWNLOADS]
        original='https://github.com/walkinglabs/learn-harness-engineering/blob/'+ORIGINAL+'/docs/en/projects/'+(SLUGS[index]+'/' if index else '')+'index.md'
        article='https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/docs/en/forge/'+('index.md' if index==0 else filename.replace('.py','.md'))
        resources='## Sources and further inspection\n\n- [Frozen original course brief]('+original+') · upstream revision `'+ORIGINAL+'`.\n- [Long-form Forge case study]('+article+').\n- [Visual evidence workspace](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=su19wan3xra).\n- [Primary comparison dashboard](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=dfs83wdpatt).\n- [Execution and publication audit](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=l9e45ofb461).\n\nSaved-case runner revision: `'+commit+'`. Figures and captures are embedded native images with source checksums in `forge/lessons/evidence.json`; no website import is needed. Original records remain unchanged.'
        cells += [markdown_cell(resources),lc.CONTROLS,lc.EXECUTE,lc.STATUS]
        replacements={'__PROJECT__':repr(project),'__COMMIT__':repr(commit),'__SAVED__':repr(json.dumps(saved,ensure_ascii=False)),'__VARIANTS__':repr(VARIANTS[project]),'__PRIMARY__':repr(evidence['primaryTrialIds']),'__PACKET__':repr(json.dumps(packet(index,lesson),ensure_ascii=False))}
        text='''# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.25.1",
#     "wandb==0.31.0",
# ]
# ///
# Canonical course notebook. Edit forge/lessons/*.md and shared native cells.
# Generate with forge/scripts/create_notebooks.py; evidence refresh is explicit.
import marimo

__generated_with = "0.25.1"
app = marimo.App(width="normal")

'''
        for cell in cells:
            for key,value in replacements.items():cell=cell.replace(key,value)
            ast.parse(cell)
            text+='@app.cell(hide_code=True)\n'+cell+'\n\n\n'
        text+='if __name__ == "__main__":\n    app.run()\n'
        dest.write_text(text);generated.append(str(dest))
    subprocess.run(['uv','run','--with','marimo==0.25.1','marimo','check','--fix',*generated],check=True,cwd=ROOT)
    print('Generated',len(generated),'native course notebooks; saved evidence', 'refreshed' if refresh_evidence else 'preserved')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--runner-commit',help='Explicitly change the pinned coordinator revision')
    parser.add_argument('--project',action='append',choices=[r[1] for r in TITLES])
    parser.add_argument('--refresh-evidence',action='store_true',help='Replace embedded evidence from snapshot.json; otherwise preserve each notebook snapshot')
    args=parser.parse_args();generate(args.runner_commit,args.project,args.refresh_evidence)
