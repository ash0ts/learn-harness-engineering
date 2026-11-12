"""Generate self-contained, native Marimo course lessons and evidence browsers."""
from pathlib import Path
import argparse
import ast
import base64
import hashlib
import json
import subprocess
import urllib.parse
import textwrap
import lesson_cells as lc
import learner_cells as learner
import workshop_cells as workshop
from course_packets import ORIGINAL, SLUGS, packet

ROOT = Path(__file__).resolve().parents[2]
TITLES = [
    ('00-overview.py', 'overview', 'Forge track: evidence before conclusions', 'In each of eight projects on one small app, you change what surrounds a coding agent, then check what it delivered.'),
    ('01-minimal-harness.py', 'project-01', '01 · Minimal instructions and explicit harnesses', 'Ask an agent to build the app shell twice, once with only the task and once with a small harness, and compare what you get.'),
    ('02-workspace-docs.py', 'project-02', '02 · An agent-readable workspace', 'Give an agent one task across two sessions, with and without workspace docs, and see what the second session can recover from the files.'),
    ('03-session-recovery.py', 'project-03', '03 · Interrupted-session recovery', 'Break the work into one feature, one check and one commit at a time, then restart from a clean state.'),
    ('04-runtime-feedback.py', 'project-04', '04 · Runtime evidence and the seeded defect', 'Find a planted indexing defect, with and without feedback from the running app, and repair only what is broken.'),
    ('05-role-separation.py', 'project-05', '05 · One feature, three role arrangements', 'Build one feature three ways on the same budget: with one agent, with a maker and a checker, and with a planner, maker and checker.'),
    ('06-capstone.py', 'project-06', '06 · Capstone reliability', 'Run a fixed set of tasks with your full harness, clean up, rerun, then remove one piece at a time to see what each is for.'),
    ('07-bounded-loops.py', 'project-07', '07 · Goal, timer and maker-checker loops', 'Let a loop keep the agent working: a goal loop, a two-hour monitor, and a maker and checker run by a controller.'),
    ('08-state-machine.py', 'project-08', '08 · Checkpointed graphs and human approval', 'Turn the loop into an explicit graph with saved state, parallel checks, rollback, and a pause for a human decision.'),
]
# What each treatment actually stages; see forge/src/staging.ts and trial.ts.
NOTES = {
    'minimal': 'the agent gets the task and the unfinished app, with no instructions file.',
    'explicit': 'adds a short `AGENTS.md` and a one-paragraph architecture note. The rules include: inspect before editing, keep the main, preload and renderer boundaries, work one acceptance criterion at a time, test the real services and Electron, and record unfinished work honestly.',
    'workspace-docs': 'adds `AGENTS.md`, an architecture note, and a rule to write `session-handoff.md` before a session ends and read it first on resume.',
    'recovery': 'adds `AGENTS.md`, an architecture note, and a rule to write `session-handoff.md` before a session ends and read it first on resume.',
    'runtime-feedback': 'adds `AGENTS.md`, an architecture note, and a small script the agent can run to see the real chunks and indexing status.',
    'single-role': 'one agent plans, edits and checks with all 24 model calls, and no instructions file.',
    'gen-eval': 'a maker (10 model calls), a read-only checker (4), then a maker revision (10), with `AGENTS.md` and an architecture note.',
    'plan-gen-eval': 'a read-only planner (4 model calls), a maker (8), a read-only checker (4), then a maker revision (8), with `AGENTS.md` and an architecture note.',
    'capstone': 'adds `AGENTS.md`, an architecture note, and a rule to write `session-handoff.md` before a session ends and read it first on resume.',
    'goal': 'one attempt by the agent. In the lab a goal loop retries until the check passes or a limit is reached; here it stops after this one round.',
    'timer': 'the same single attempt as goal, after which the loop waits for its ten-minute deadline before it finishes.',
    'maker-checker': 'one round of a maker (10 model calls), a read-only checker (4), then a maker revision (10).',
    'graph': 'a planned, checkpointed route with up to three candidates. Each is graded, then verified in two separate sandboxes, one for the services and one for the app window. The graph pauses for your approval when a candidate passes.',
}
TWO_SESSIONS = {'project-02', 'project-03'}

def run_facts(saved, primary):
    """Observed duration and estimated cost of this lesson's recorded attempts."""
    from datetime import datetime
    rows = [r for r in saved.get('trials', []) if r['id'] in primary] or saved.get('trials', [])
    # Attempts that stopped early or lack usage data do not describe a typical run.
    rows = [r for r in rows if r.get('outcome') in ('passed', 'task_failed')]
    minutes, costs = [], []
    for row in rows:
        try:
            minutes.append((datetime.fromisoformat(row['finishedAt'].replace('Z', '+00:00')) - datetime.fromisoformat(row['startedAt'].replace('Z', '+00:00'))).total_seconds() / 60)
        except (KeyError, TypeError, ValueError, AttributeError):
            pass
        cost = row.get('reconciledEstimateUsd') or row.get('estimatedCostUsd')
        if cost:
            costs.append(cost)
    if not minutes or not costs:
        return None
    return {'attempts': len(rows), 'minMinutes': max(1, round(min(minutes))), 'maxMinutes': max(1, round(max(minutes) + 0.5)), 'minUsd': round(min(costs), 2), 'maxUsd': round(max(costs) + 0.005, 2)}

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

def workshop_payload(project, commit):
    script = "import {workshopTemplate} from './forge/src/workshop-workspace.ts'; const {manifest,files}=await workshopTemplate(process.argv[1],process.argv[2]);console.log(JSON.stringify({manifest,files:Object.fromEntries(manifest.editable.map(name=>[name,files[name]]))}));"
    return subprocess.check_output(['node','--import',str(ROOT/'forge/node_modules/tsx/dist/loader.mjs'),'--input-type=module','-e',script,project,commit],cwd=ROOT,text=True)

WORKSHOP_ENTRY = '''## Five hands-on labs

Use **01, 02 and 04** for the three-hour workshop. **03 and 05** are complete extensions. Each lab starts from its own checkpoint, so nobody has to finish an earlier project to begin the next.

| Lab | Your edit | What you inspect |
| --- | --- | --- |
| [01 · Build and connect](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTQ%3D) | Typed import IPC and a Forge inference request | The app, actual answers, request/response and token usage |
| [02 · Give Pi a workspace](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTU%3D) | AGENTS.md, architecture, acceptance criteria and a sandbox SDK command | Staged files, Pi's file reads and the document-detail patch |
| [03 · Recover a session](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTY%3D) | Metadata code, a verification entry and your handoff | Two separate conversations and preserved earlier work |
| [04 · Instrument and diagnose](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTc%3D) | Forge SDK spans, chunk statistics and the indexing repair | Short/long fixtures, actual chunks, errors and Agent Lens |
| [05 · Make and check](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTg%3D) | Role prompts, a rubric, evaluation code and W&B logging | The checker's review, revision patch, UI and your metrics |

**How to begin:** open a lab, copy it into a private Forge project, run its cells with ▶, and use **Prepare or restore my workspace**. Edit the named files, **Save these edits**, then **Check my edits**. Connect your own sandbox-capable API key only when you are ready to execute. Opening a notebook starts no agent or inference request. A notebook's CPU session and later sandbox/model actions do cost money; the default $20 estimate limit belongs to that copy, not the whole class.

No separate service deployment is required. The notebook installs the runner and creates bounded sandboxes. To use the Electron app with your own mouse and keyboard, follow the [clone-and-run guide](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/docs/en/forge/workshop.md). Notebook and laptop edits use the same source files and checks.

| Time | Activity |
| --- | --- |
| 0:00–0:20 | Setup and inspect the starting app |
| 0:20–1:00 | Project 01 |
| 1:00–1:35 | Project 02; faster participants begin 03 |
| 1:35–1:45 | Break and save progress |
| 1:45–2:30 | Project 04; faster participants continue to 05 |
| 2:30–2:45 | Demonstrate and discuss 03 and 05 |
| 2:45–3:00 | Explain one edit, its observed effect, and its evidence |

The original lesson prose and historical comparisons follow. Workshop executions use a separate `workshop-v1` cohort. Projects 06–08 retain their existing course flow.
'''

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
        start=('**Start here**\n\n'
               '1. **Make your own copy.** Open the **⋯** menu at the top right, choose **Copy to project**, and pick a private project you can write to. Your copy opens by itself.\n'
               '2. **Load the page.** In your copy, click the yellow **▶** button at the bottom right of the editor. The figures, tables and controls below appear only after the cells have run. This makes no model call and starts no coding attempt.\n'
               '3. **Read, inspect, run.** Read the lab, open a recorded attempt in Agent Lens to see what the agent did, then run an attempt of your own.\n\n'
               'Jump to [recorded attempts](#inspect-one-attempt) · [run this lesson yourself](#run-this-lesson-yourself) · [my work](#my-work) · [my observations](#your-observation-worksheet). These links work once the cells have run.\n\n'
               'Each lesson is a separate notebook with its own copy and spending limit. The lesson links above open the course originals.')
        intro='# '+title+'\n\n'+nav+'\n\n'+description+'\n\n'+start
        practical = project in [f'project-{i:02}' for i in range(1,6)]
        if practical:
            intro=intro.replace('3. **Read, inspect, run.** Read the lab, open a recorded attempt in Agent Lens to see what the agent did, then run an attempt of your own.', '3. **Edit, check, execute.** Open the file tabs, save a small change, run its deterministic checks, then exercise that saved snapshot. The historical comparison follows the workbench.')
            intro=intro.replace('[run this lesson yourself](#run-this-lesson-yourself)','[your hands-on lab](#your-hands-on-lab)')
        elif project=='overview':
            intro='# '+title+'\n\n'+nav+'\n\n'+description+'\n\nStart with the lab links below. Copy the selected lab into your own private project; you do not need to copy this overview.'
        cells=[lc.IMPORTS,lc.CONSTANTS,markdown_cell(intro)]
        if practical:
            helper=(ROOT/'forge/scripts/learner_workspace.py').read_text()
            extension=(ROOT/'forge/scripts/workshop_workspace.py').read_text().replace('from learner_workspace import LessonWorkspace\n','')
            helper_cell='def _():\n    def _load_learner():\n'+textwrap.indent(helper+'\n'+extension,'        ')+'\n        return WorkshopWorkspace\n    LessonWorkspace = _load_learner()\n    return (LessonWorkspace,)'
            cells += [workshop.SPEC, helper_cell, learner.INIT, workshop.STATE, workshop.SETUP, workshop.PREPARE,
                      lc.PREDICTION.replace('**4. Write your prediction.**','**Write your prediction.**').replace('where the agent is most likely to fall short','which check or app behavior your edit should change').replace('in step 6','in your observation worksheet'), *workshop.editor_cells(json.loads(workshop_payload(project,commit))['manifest']['editable']), workshop.EDIT_BUTTONS, workshop.SAVE, workshop.DIRTY,
                      workshop.RELOAD, workshop.CHECK, workshop.HINTS, workshop.EXAMPLE,
                      learner.CONNECT, learner.AUTHENTICATE.replace('Go on to step 4.','Choose a lesson action below.'), workshop.ACTIONS, workshop.EXECUTE,
                      learner.CANCEL, learner.REFRESH, workshop.RESULTS, workshop.TRANSFER,
                      workshop.IMPORT, workshop.CANDIDATE, workshop.APPLY, workshop.DOWNLOAD,
                      markdown_cell('### Use the same app on your laptop\n\nFollow the [Mac, Windows and Linux setup guide](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/docs/en/forge/workshop.md). Initialize `'+project+'`, then run `npm ci` and `npm run dev` in that generated workspace. It starts in clearly labelled offline mode. Export your source with the workshop CLI and preview its diff here before applying it. No separate service is needed.\n\nThe recorded comparison below uses the original research treatments. This practical lab uses an independent supplied checkpoint of the same app. Your new attempts never change those recorded results.')]
        elif project=='overview':
            cells.append(markdown_cell(WORKSHOP_ENTRY))
        cells += [markdown_cell(part.strip()) for part in sections[:-1]]
        for image in evidence['assets'][project]:
            path=ROOT/'forge/lessons/assets'/image['file']
            data=path.read_bytes()
            if hashlib.sha256(data).hexdigest()!=image['sha256']:raise RuntimeError('Visual provenance mismatch: '+str(path))
            mime='image/svg+xml' if path.suffix=='.svg' else 'image/jpeg' if path.suffix=='.jpg' else 'image/png'
            uri='data:'+mime+';base64,'+base64.b64encode(data).decode()
            cells.append('def _(mo):\n    mo.image('+repr(uri)+', alt='+repr(image['caption'])+', caption='+repr(image['caption'])+', width="100%")\n    return')
        original='https://github.com/walkinglabs/learn-harness-engineering/blob/'+ORIGINAL+'/docs/en/projects/'+(SLUGS[index]+'/' if index else '')+'index.md'
        article='https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/docs/en/forge/'+('index.md' if index==0 else filename.replace('.py','.md'))
        guide='https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/docs/en/forge/classroom.md'
        workspace='https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge'
        resources=('## Sources and further reading\n\n'
                   '- [Step-by-step guide to running these lessons]('+guide+'), including costs and what to do if a session is interrupted.\n'
                   '- [All recorded agent conversations in Agent Lens](https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge/conversations).\n'
                   '- [The original course brief for this project]('+original+'), frozen at upstream revision `'+ORIGINAL[:12]+'`.\n'
                   '- [The long-form write-up of the recorded Forge case]('+article+').\n'
                   '- Dashboards for the recorded attempts: [evidence]('+workspace+'?nw=su19wan3xra) · [main comparison]('+workspace+'?nw=dfs83wdpatt) · [execution audit]('+workspace+'?nw=l9e45ofb461).\n\n'
                   'The Agent Lens and dashboard links open the course\'s private project, so you need view access to it. Your own attempts in this copy run with course runner revision `'+commit[:12]+'`. Each recorded attempt shows its own source revision under **Inspect one attempt**.')
        helper=(ROOT/'forge/scripts/learner_workspace.py').read_text()
        helper_cell='def _():\n    def _load_learner():\n'+textwrap.indent(helper,'        ')+'\n        return LessonWorkspace\n    LessonWorkspace = _load_learner()\n    return (LessonWorkspace,)'
        # Reading order: lab, recorded attempts, then the learner's own run with
        # the prediction before it and the explanation after it.
        if practical:
            cells += [lc.RESULTS,lc.SELECTOR,lc.DETAIL,lc.LIFECYCLE,lc.WORKSHEET.replace('**6. Explain what happened.**','**Explain what happened.**').replace("the agent's conversation",'the matching conversation'),*learner.SAVE_CELLS,lc.DOWNLOADS,learner.DOWNLOAD,markdown_cell(sections[-1].strip()),markdown_cell(resources)]
        elif project=='overview':
            overview_sheet=lc.WORKSHEET.replace('**6. Explain what happened.** Look at your attempt under **My work**: its checks, the app window, and the agent\'s conversation in Agent Lens.', '**Explain what happened.** Choose a recorded attempt above or an execution from your lab copy.').replace('**Save my notes and progress** keeps your notes with this copy. ', '')
            cells += [lc.RESULTS,lc.SELECTOR,lc.DETAIL,lc.LIFECYCLE,lc.PREDICTION.replace('**4. Write your prediction.**','**Write your prediction.**').replace('in step 6','in your observation worksheet'),overview_sheet,lc.DOWNLOADS,markdown_cell(sections[-1].strip()),markdown_cell(resources.replace('Your own attempts in this copy run with course runner revision','The hands-on labs link their pinned runner revisions; this overview records revision'))]
        else:
            cells += [lc.RESULTS,lc.SELECTOR,lc.DETAIL,lc.LIFECYCLE,helper_cell,*learner.SETUP_CELLS,lc.PREDICTION,*learner.RUN_CELLS,
                      lc.WORKSHEET,*learner.SAVE_CELLS,lc.DOWNLOADS,learner.DOWNLOAD,markdown_cell(sections[-1].strip()),markdown_cell(resources)]
        notes={name:(('two fresh sessions; ' if project in TWO_SESSIONS else '')+NOTES[name]) for name in VARIANTS[project]}
        replacements={'__PROJECT__':repr(project),'__COMMIT__':repr(commit),'__SAVED__':repr(json.dumps(saved,ensure_ascii=False)),'__VARIANTS__':repr(VARIANTS[project]),'__PRIMARY__':repr(evidence['primaryTrialIds']),'__PACKET__':repr(json.dumps(packet(index,lesson),ensure_ascii=False)),'__NOTES__':repr(notes),'__FACTS__':repr(run_facts(saved,evidence['primaryTrialIds']))}
        if practical:replacements['__WORKSHOP__']=repr(workshop_payload(project,commit))
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
