"""Native, explicitly submitted workbench controls for Projects 01–05."""

STATE = '''def _(mo):
    get_files_epoch, set_files_epoch = mo.state(0)
    get_workshop_save, set_workshop_save = mo.state(0)
    get_workshop_check, set_workshop_check = mo.state(0)
    get_workshop_start, set_workshop_start = mo.state(0)
    get_workshop_example, set_workshop_example = mo.state(0)
    get_workshop_import, set_workshop_import = mo.state(0)
    get_workshop_apply, set_workshop_apply = mo.state(0)
    get_workshop_candidate, set_workshop_candidate = mo.state(0)
    get_workshop_reload, set_workshop_reload = mo.state(0)
    return get_files_epoch, get_workshop_apply, get_workshop_candidate, get_workshop_check, get_workshop_example, get_workshop_import, get_workshop_reload, get_workshop_save, get_workshop_start, set_files_epoch, set_workshop_apply, set_workshop_candidate, set_workshop_check, set_workshop_example, set_workshop_import, set_workshop_reload, set_workshop_save, set_workshop_start'''

SPEC = '''def _(json):
    workshop_initial = json.loads(__WORKSHOP__)
    return (workshop_initial,)'''

SETUP = '''def _(mo, workshop_initial):
    learner_budget = mo.ui.number(start=5, stop=50, value=20, step=1, label="Spending limit for this copy (USD)")
    prepare_workspace = mo.ui.button(value=0, on_click=lambda v: v + 1, label="Prepare or restore my workspace", full_width=True)
    get_prepare_click, set_prepare_click = mo.state(0)
    mo.vstack([mo.md("## Your hands-on lab\\n\\n" + workshop_initial['manifest']['task'] + "\\n\\nThe checkpoint supplies the surrounding app. Your changes are the files below. **Save and check my edits** writes your draft, builds it and runs the focused checks without inference or a sandbox. A paid action freezes that saved draft and records exactly which code ran.\\n\\n**Use your own copy.** Choose **⋯ → Copy to project** and select a private project you can write to. Run the notebook cells with **▶**. Stay in Edit for the masked API-key prompt. Each copy has its own $20 estimate limit; this is separate from a classroom budget. No separate service deployment is needed."),
        mo.accordion({"Prepare the notebook workspace": mo.vstack([mo.md("Prepare installs the pinned runner and restores saved work. It starts no inference. Each one-hour CPU notebook session reserves an estimated $0.34. Keep the same limit when returning. Saved drafts and completed attempts are separate; a new copy starts a separate budget."), learner_budget, prepare_workspace])})])
    return get_prepare_click, learner_budget, prepare_workspace, set_prepare_click'''

PREPARE = '''def _(get_prepare_click, learner, learner_budget, mo, prepare_workspace, set_files_epoch, set_prepare_click):
    mo.stop(prepare_workspace.value <= get_prepare_click())
    set_prepare_click(prepare_workspace.value)
    try:
        with mo.status.spinner(title="Preparing your workspace"):
            learner.prepare(float(learner_budget.value))
        set_files_epoch(lambda v: v + 1)
        _message = mo.callout(mo.md("Workspace ready. Inspect the files, save your edits and run the local checks. Connect sandbox access when you are ready for a paid action."), kind="success")
    except Exception as _error:
        _message = mo.callout(mo.md("**Setup stopped.** " + learner.redact(_error)), kind="danger")
    _message
    return'''

def editor_cells(files):
    """Give each editor an independent reactive identity.

    Marimo 0.25.1 coalesces queued updates by the parent UI element ID.
    Dictionary children can therefore drop all but the last edited file while
    a check/save is busy. Independent roots retain every file's pending value.
    The second cell reads those roots explicitly so dirty state stays reactive.
    """
    names = [f"workshop_editor_{i}" for i in range(len(files))]
    lines = ["def _(get_files_epoch, learner, mo, workshop_initial):",
             "    get_files_epoch()",
             "    workshop_loaded = learner.workshop_files() or workshop_initial",
             "    _languages = {'.ts':'typescript', '.tsx':'typescript', '.md':'markdown', '.json':'json', '.py':'python'}"]
    for name, path in zip(names, files):
        language = path.rsplit('.', 1)[-1]
        lines.append(f"    {name} = mo.ui.code_editor(value=workshop_loaded['files'][{path!r}], language=_languages.get('.{language}', 'text'), label={path!r}, min_height=220, max_height=440, debounce=False)")
    tabs = ', '.join(f'{path!r}: {name}' for path, name in zip(files, names))
    explanation = "### 1. Inspect and edit your implementation\n\nThe deliberate gaps are in the files below. Open each file tab. Typing changes only the draft in this editor; it cannot launch work. Use Save and check my edits before executing. Files outside this list belong to the supplied checkpoint."
    lines.append(f"    mo.vstack([mo.md({explanation!r}), mo.ui.tabs({{{tabs}}})])")
    lines.append('    return ' + ', '.join([*names, 'workshop_loaded']))
    values = ', '.join(f'{path!r}: {name}.value' for path, name in zip(files, names))
    value_cell = 'def _(' + ', '.join(names) + '):\n    workshop_editors = {' + values + '}\n    return (workshop_editors,)'
    return ['\n'.join(lines), value_cell]

EDIT_BUTTONS = '''def _(mo):
    workshop_save = mo.ui.button(value=0, on_click=lambda v:v+1, label="Save and check my edits")
    workshop_reload = mo.ui.button(value=0, on_click=lambda v:v+1, label="Load my saved files")
    workshop_check = mo.ui.button(value=0, on_click=lambda v:v+1, label="Check my edits (no inference)")
    mo.hstack([workshop_save, workshop_check, workshop_reload], justify="start")
    return workshop_check, workshop_reload, workshop_save'''

SAVE = '''def _(get_workshop_save, learner, mo, set_workshop_save, workshop_editors, workshop_save):
    mo.stop(workshop_save.value <= get_workshop_save())
    set_workshop_save(workshop_save.value)
    try:
        with mo.status.spinner(title="Saving your source snapshot and verifying the private checkpoint"):
            _saved = learner.save_edits(workshop_editors)
        _message = mo.callout(mo.md("Saved snapshot `" + _saved['snapshot']['id'] + "` · SHA-256 `" + _saved['snapshot']['sha256'] + "`. Run the checks next."), kind="success")
    except Exception as _error:
        _message = mo.callout(mo.md("**Edits not saved.** " + learner.redact(_error)), kind="warn")
    _message
    return'''

DIRTY = '''def _(get_workshop_save, learner, mo, workshop_editors, workshop_loaded):
    get_workshop_save()
    _current = learner.workshop_files() or workshop_loaded
    _changed = [_name for _name, _text in workshop_editors.items() if _current['files'].get(_name) != _text]
    _state = learner.state.get('workshop', {})
    mo.md(("**Unsaved edits:** " + ", ".join("`" + _name + "`" for _name in _changed) + ". Save and check my edits before executing." if _changed else "**Editor matches the saved files.**") + (" Your last saved snapshot is `" + _state['draftSnapshot'] + "`." if _state.get('draftSnapshot') else " Save once to create your first snapshot."))
    return'''

RELOAD = '''def _(get_workshop_reload, mo, set_files_epoch, set_workshop_reload, workshop_reload):
    mo.stop(workshop_reload.value <= get_workshop_reload())
    set_workshop_reload(workshop_reload.value)
    set_files_epoch(lambda v:v+1)
    mo.md("Loaded the saved files. Unsaved editor contents were replaced.")
    return'''

CHECK = '''def _(get_workshop_check, learner, mo, set_workshop_check, workshop_check):
    mo.stop(workshop_check.value <= get_workshop_check())
    set_workshop_check(workshop_check.value)
    try:
        with mo.status.spinner(title="Building and checking the saved snapshot"):
            _result = learner.check_edits()
        _logs = {}
        for _label, _file in [('Build output','build.log'),('Focused check output','checks.log')]:
            try: _text=learner.projection(learner.workshop_evidence(_result['id'],_file).decode(errors='replace'))[-18000:]
            except FileNotFoundError: _text='This step did not run; inspect the preceding failure.'
            _logs[_label]=mo.md("```text\\n"+_text+"\\n```")
        _display = mo.vstack([mo.md("**" + _result['outcome'].replace('_',' ') + "** · snapshot `" + _result['snapshotId'] + "`"), mo.ui.table(_result['checks'], selection=None, pagination=False), mo.accordion(_logs)])
    except Exception as _error:
        _display = mo.callout(mo.md("**Check stopped.** " + learner.redact(_error)), kind="warn")
    _display
    return'''

HINTS = '''def _(mo, workshop_initial):
    workshop_example = mo.ui.button(value=0, on_click=lambda v:v+1, label="Reveal the worked example (mark my work assisted)")
    mo.accordion({"Progressive hints": mo.vstack([mo.accordion({"Hint " + str(_i+1):mo.md(_hint)}) for _i,_hint in enumerate(workshop_initial['manifest']['hints'])] + [mo.md("The worked example is separate from your executed files. Revealing it marks subsequent snapshots as assisted; it does not overwrite your code."), workshop_example])})
    return (workshop_example,)'''

EXAMPLE = '''def _(get_workshop_example, learner, mo, set_workshop_example, workshop_example):
    mo.stop(workshop_example.value <= get_workshop_example())
    set_workshop_example(workshop_example.value)
    try:
        _example = learner.reveal_example()
        _display = mo.accordion({_name:mo.md("```\\n" + _text + "\\n```") for _name,_text in _example.items()})
    except Exception as _error:
        _display = mo.md(learner.redact(_error))
    _display
    return'''

ACTIONS = '''def _(mo, project_id, workshop_initial):
    _actions = {
        'project-01':{'Exercise import, questions and restart (CPU sandbox)':'offline-app', 'Run my Forge request and inspect its answers':'live-app'},
        'project-02':{'Run my sandbox command and inspect the detail view':'offline-app', 'Give Pi my documented document-detail task':'agent'},
        'project-03':{'Check metadata in the running app':'offline-app', 'Run the first bounded metadata session':'agent', 'Resume in a fresh session from my saved handoff':'resume'},
        'project-04':{'Inspect my chunks and the indexing defect':'offline-app', 'Run my instrumentation and Forge Q&A':'live-app'},
        'project-05':{'Inspect conversation history in the app':'offline-app', 'Run my maker, checker and revision prompts':'agent'}
    }[project_id]
    workshop_action = mo.ui.dropdown(options=_actions, value=next(iter(_actions)), label="Lesson action")
    workshop_scenario = mo.ui.dropdown(options=workshop_initial['manifest']['scenarios'], value='clear-history' if project_id=='project-05' else 'restart', label="App scenario")
    workshop_fixture = mo.ui.dropdown(options=['short','long'], value='long', label="Document fixture")
    workshop_question = mo.ui.text(value="What units are documents indexed into?", label="Supported question", full_width=True)
    workshop_single = mo.ui.checkbox(label="Optional comparison: give one role all 24 calls (Project 05)")
    workshop_consent = mo.ui.checkbox(label="Run this saved snapshot using my project's paid CPU/inference budget")
    workshop_start = mo.ui.button(value=0, on_click=lambda v:v+1, label="Execute my saved snapshot", full_width=True)
    learner_cancel = mo.ui.button(value=0, on_click=lambda v:v+1, label="Cancel the running action")
    get_cancel_click, set_cancel_click = mo.state(0)
    mo.vstack([mo.md("### 2. Exercise the app and inspect the consequences\\n\\nEvery action starts a fresh CPU sandbox, stages your saved files, collects evidence and verifies termination. **CPU sandbox actions cost money even in offline inference mode.** Live app actions issue at most two model requests; the second question is deliberately unsupported by the document. A surprising answer remains evidence to explain. Pi actions have a 24-call total allowance; each Project 03 session has 12 calls. Project 05 divides its 24 calls into maker 10, checker 4 and revision 10.\\n\\nChoose **import**, **index**, **ask**, or **restart** to stop at a particular app step. Screenshots come from your build under Xvfb. The optional laptop workflow below gives you full mouse-and-keyboard interaction."), workshop_action, mo.hstack([workshop_scenario, workshop_fixture]), workshop_question, workshop_single if project_id=='project-05' else mo.md(''), workshop_consent, workshop_start, learner_cancel])
    return get_cancel_click, learner_cancel, set_cancel_click, workshop_action, workshop_consent, workshop_fixture, workshop_question, workshop_scenario, workshop_single, workshop_start'''

EXECUTE = '''def _(get_workshop_start, learner, mo, set_workshop_start, workshop_action, workshop_consent, workshop_editors, workshop_fixture, workshop_question, workshop_scenario, workshop_single, workshop_start):
    mo.stop(workshop_start.value <= get_workshop_start())
    set_workshop_start(workshop_start.value)
    try:
        if not workshop_consent.value:
            raise RuntimeError("Confirm the paid action before executing.")
        if learner.workshop_files()['files'] != workshop_editors:
            raise RuntimeError("There are unsaved edits. Save and check my edits first.")
        _identifier = learner.start_workshop(workshop_action.value, workshop_scenario.value, workshop_fixture.value, workshop_question.value, workshop_single.value)
        _message = mo.callout(mo.md("Started execution `" + _identifier + "`. My work refreshes below. You can edit a new draft while it runs; the running snapshot cannot change."), kind="info")
    except Exception as _error:
        _message = mo.callout(mo.md("**Not started.** " + learner.redact(_error)), kind="warn")
    _message
    return'''

RESULTS = '''def _(base64, evidence_link, json, learner, learner_refresh, mo, workshop_editors):
    learner_refresh.value
    my_progress = learner.view()
    _work = learner.state.get('workshop', {})
    _trials = [r for r in my_progress['trials'] if r.get('protocol')=='workshop-v1']
    _rows = []
    _cards = []
    for _r in sorted(_trials, key=lambda r:r.get('startedAt',''), reverse=True):
        _stale = _r.get('snapshotSha256') != _work.get('draftSha256') or (learner.workshop_files() or {}).get('files') != workshop_editors
        _rows.append({'Execution':_r['id'], 'Snapshot':_r.get('snapshotId'), 'Action':_r.get('variant'), 'Outcome':_r.get('outcome'), 'Current draft':not _stale, 'Estimated USD':_r.get('estimatedCostUsd'), 'Publication':_r.get('publicationStatus')})
        _links = [f"[Conversation {_i+1}](https://forge.coreweave.com/agent-lens/{my_progress['destination']}/conversations/{_c})" for _i,_c in enumerate(_r.get('conversationIds',[]))]
        if _r.get('wandbRunUrl'):_links.append('[W&B run]('+_r['wandbRunUrl']+')')
        if _r.get('artifactUrl'):_links.append('[Source and evidence artifact]('+evidence_link(_r['artifactUrl'])+')')
        _parts = [mo.md('**'+_r['id']+' · '+_r.get('outcome','running')+'**'+(' — result is older than the current draft' if _stale else '')+'\\n\\nSnapshot `'+str(_r.get('snapshotId'))+'` · '+('assisted' if _r.get('assisted') else 'worked example not revealed')+'\\n\\n'+' · '.join(_links)), mo.ui.table(_r.get('checks',[]), selection=None, pagination=False)]
        try:
            _images = json.loads(learner.workshop_evidence(_r['id'],'grader/images.json'))
            for _image in _images:
                _bytes=learner.workshop_evidence(_r['id'],'grader/'+_image['file'])
                _parts.append(mo.image('data:image/png;base64,'+base64.b64encode(_bytes).decode(), alt=_image['step']+' from the student Electron build', caption=_image['step']+' · snapshot '+_image['snapshot'], width='100%'))
        except (OSError, ValueError):pass
        _details = {}
        for _name in ['grader/answers.json','grader/chunks.json','grader/ui-events.json','grader/app-evidence/app.json','grader/student-sdk.json','actor/review.json','actor/reads-1.json','actor/changes-1.json','actor/changes-3.json','student-evaluation.json']:
            try:_details[_name]=mo.md('```json\\n'+learner.projection(learner.workshop_evidence(_r['id'],_name).decode())[:24000]+'\\n```')
            except OSError:pass
        if _details:_parts.append(mo.accordion(_details))
        _cards.append(mo.accordion({_r.get('action','Execution')+' · '+_r['id'][:8]:mo.vstack(_parts)}))
    _budget=my_progress['budget']
    mo.vstack([mo.md('## My work\\n\\n**Status:** '+my_progress['status']+'\\n\\n**Sandbox access:** '+('connected for this session' if my_progress['sandboxConnected'] else 'not connected')+'\\n\\n**Spending:** $'+str(round(_budget.get('spentEstimateUsd',0),3))+' estimated of $'+str(_budget.get('limitUsd',20))+' for this copy. '+('**Paid work blocked:** '+str(_budget.get('halted')) if _budget.get('halted') else '')+'\\n\\nSaved source, Pi changes, app checks, usage, cleanup and publication are separate evidence. Workshop results do not change the historical comparisons below.'), mo.ui.table(_rows,selection=None,pagination=False) if _rows else mo.md('No workshop executions yet. Start with the deterministic check.'), *_cards, mo.accordion({'Saved source diff':mo.md('```json\\n'+json.dumps(_work.get('diff',[]),indent=2)+'\\n```'), 'Latest action log':mo.md('```text\\n'+my_progress['log']+'\\n```')})])
    return (my_progress,)'''

TRANSFER = '''def _(mo):
    workshop_upload = mo.ui.file(filetypes=['.json'], max_size=5000000, label="Upload a workspace snapshot from your laptop")
    workshop_import = mo.ui.button(value=0, on_click=lambda v:v+1, label="Preview uploaded source diff")
    workshop_apply = mo.ui.button(value=0, on_click=lambda v:v+1, label="Apply the previewed files")
    workshop_candidate = mo.ui.text(label="Candidate execution ID from My work", full_width=True)
    workshop_candidate_preview = mo.ui.button(value=0, on_click=lambda v:v+1, label="Preview this candidate's source diff")
    mo.accordion({'Continue from a Pi candidate or a laptop edit':mo.vstack([mo.md('Preview the diff first, then apply it explicitly. Applying updates the saved workspace; **Load my saved files** refreshes the editors and replaces unsaved text. Save and check my edits again before execution. Project 03 resumes only from a recorded first-session candidate: add your handoff to its files, then choose the fresh-session action. Your earlier snapshots remain intact.'), workshop_candidate, workshop_candidate_preview, workshop_upload, workshop_import, workshop_apply])})
    return workshop_apply, workshop_candidate, workshop_candidate_preview, workshop_import, workshop_upload'''

DOWNLOAD = '''def _(get_workshop_save, learner, mo, my_progress):
    get_workshop_save()
    _download=learner.export_workspace() if my_progress['prepared'] else None
    mo.download(data=_download,filename='workshop-workspace.json',mimetype='application/json',label='Download my editable workspace') if _download else mo.md('Save a draft to enable the workspace download. It remains unavailable while an action is unresolved.')
    return'''

IMPORT = '''def _(get_workshop_import, json, learner, mo, set_workshop_import, workshop_import, workshop_upload):
    mo.stop(workshop_import.value <= get_workshop_import())
    set_workshop_import(workshop_import.value)
    try:
        _data=workshop_upload.contents()
        if not _data:raise ValueError('Upload a workspace JSON file first')
        _result=learner.preview_workspace_import(_data)
        _display=mo.md('```json\\n'+json.dumps(_result,indent=2)+'\\n```')
    except Exception as _error:_display=mo.md(learner.redact(_error))
    _display
    return'''

CANDIDATE = '''def _(get_workshop_candidate, json, learner, mo, set_workshop_candidate, workshop_candidate, workshop_candidate_preview):
    mo.stop(workshop_candidate_preview.value <= get_workshop_candidate())
    set_workshop_candidate(workshop_candidate_preview.value)
    try:_display=mo.md('```json\\n'+json.dumps(learner.preview_candidate(workshop_candidate.value),indent=2)+'\\n```')
    except Exception as _error:_display=mo.md(learner.redact(_error))
    _display
    return'''

APPLY = '''def _(get_workshop_apply, learner, mo, set_workshop_apply, workshop_apply):
    mo.stop(workshop_apply.value <= get_workshop_apply())
    set_workshop_apply(workshop_apply.value)
    try:
        learner.apply_workspace_import()
        _display=mo.md('Applied the previewed source. Click **Load my saved files**, then save and check your edits.')
    except Exception as _error:_display=mo.md(learner.redact(_error))
    _display
    return'''

# Guided workshop interface. Each button has an independent identity and counter;
# reactive refreshes never reset a paid action's click receipt.
GUIDANCE = '''def _(learner, learner_refresh, mo, workshop_editors):
    learner_refresh.value
    mo.callout(mo.md("**Next step:** " + learner.workshop_next_step(workshop_editors)), kind="info")
    return'''

SOURCE = '''def _(mo, workshop_initial):
    workshop_source = mo.ui.dropdown(options=list(workshop_initial['referenceFiles']), value=next(iter(workshop_initial['referenceFiles'])), label="Read the supplied code (not editable here)")
    mo.accordion({"How this checkpoint works":mo.vstack([mo.md("The Notebook edits and freezes your source. A separate CPU Sandbox builds it and runs Pi or Electron. Forge inference handles model requests; Agent Lens records their conversations. W&B stores checks, usage and source artifacts. Credentials stay in the service/runner process. These are the supplied files from this lesson's pinned revision."),workshop_source])})
    return (workshop_source,)'''

SOURCE_VIEW = '''def _(mo, workshop_initial, workshop_source):
    mo.accordion({"Read " + workshop_source.value: mo.md("```typescript\\n" + workshop_initial['referenceFiles'][workshop_source.value] + "\\n```")})
    return'''

ACTION_SETTINGS = '''def _(mo, project_id):
    workshop_fixture = mo.ui.radio(options=['short','long'], value='long', label="Document fixture")
    workshop_question = mo.ui.text(value="What units are documents indexed into?", label="Question for the app", full_width=True)
    workshop_single = mo.ui.checkbox(label="Optional Project 05 comparison: one role uses all 24 calls")
    workshop_consent = mo.ui.checkbox(label="Use my project's paid CPU/inference budget for the action I click")
    learner_cancel = mo.ui.button(value=0, on_click=lambda v:v+1, label="Cancel the running action")
    get_cancel_click, set_cancel_click = mo.state(0)
    mo.vstack([mo.md("### Execute and inspect\\n\\nEach named action below freezes your saved source. **Sandbox CPU costs money, including offline-inference actions.** Live app runs make at most two requests. Pi has at most 24 calls per ordinary task, or 12 per loop/graph repair round. The $20 estimate limit applies to this notebook copy.\\n\\nSave and check first. Connect your sandbox access once per session. Choose the action only after its prerequisites are satisfied; the adjacent result explains any blocked launch."),mo.accordion({"Fixture and question":mo.vstack([workshop_fixture,workshop_question,workshop_single if project_id=='project-05' else mo.md('')])}),workshop_consent,learner_cancel])
    return get_cancel_click, learner_cancel, set_cancel_click, workshop_consent, workshop_fixture, workshop_question, workshop_single'''

def action_cells(project):
    from workshop_teaching import LABS
    cells=[]
    for i,(action,label,description,scenario) in enumerate(LABS[project]['actions']):
        button=f'workshop_action_{i}'
        getter=f'get_workshop_action_{i}'
        setter=f'set_workshop_action_{i}'
        cells.append(f'''def _(mo):
    {button} = mo.ui.button(value=0, on_click=lambda v:v+1, label={label!r}, full_width=True)
    {getter}, {setter} = mo.state(0)
    mo.vstack([mo.md({('**'+str(i+1)+'. '+label+'**\n\n'+description)!r}), {button}])
    return {button}, {getter}, {setter}''')
        cells.append(f'''def _({getter}, learner, mo, {setter}, {button}, workshop_consent, workshop_editors, workshop_fixture, workshop_question, workshop_single):
    mo.stop({button}.value <= {getter}())
    {setter}({button}.value)
    try:
        if not workshop_consent.value:
            raise RuntimeError("Select the paid-budget checkbox above before this explicit action.")
        if not learner.workshop_files():
            raise RuntimeError("Prepare or restore my workspace first.")
        if learner.workshop_files()['files'] != workshop_editors:
            raise RuntimeError("The editor has unsaved changes. Use Save and check my edits first.")
        _id=learner.start_workshop({action!r},{scenario!r},workshop_fixture.value,workshop_question.value,workshop_single.value)
        _display=mo.callout(mo.md("Started `"+_id+"`. Follow this snapshot under **My work**. Editing a new draft cannot change the running snapshot."),kind="info")
    except Exception as _error:
        _display=mo.callout(mo.md("**Not started.** "+learner.redact(_error)),kind="warn")
    _display
    return''')
    return cells

CONTROLLER = '''def _(learner, learner_refresh, mo):
    learner_refresh.value
    workshop_controller = learner.workshop_controller()
    _display=mo.md('')
    if workshop_controller:
        _state=workshop_controller
        _candidate=_state.get('candidate') or {}
        _next=_state.get('node') or _state.get('status')
        _parts=[mo.md("### Your controller checkpoint\\n\\n**Current step:** "+str(_next)+" · execution `"+_state['id']+"`\\n\\nCandidate `"+str(_candidate.get('sha256','starting snapshot'))+"`. This checkpoint survives notebook restart. No node starts merely by opening it."),mo.ui.table(_state.get('rounds',_state.get('trials',[])),selection=None,pagination=False),mo.accordion({'Route decisions and feedback':mo.md('```json\\n'+learner.projection(json.dumps(_state.get('events',[]),indent=2))+'\\n```')})]
        if _state.get('deadline'):_parts.append(mo.md('Saved absolute deadline (Unix milliseconds): `'+str(_state['deadline'])+'`. The next explicit round uses the same deadline.'))
        if _next=='approval':_parts.append(mo.callout(mo.md('**Human decision required.** Inspect the verified candidate diff, checks, lane receipts and screenshots below. Record your own decision for the displayed checksum. This does not merge code.'),kind='warn'))
        _display=mo.vstack(_parts)
    _display
    return (workshop_controller,)'''.replace('def _(learner, learner_refresh, mo):','def _(json, learner, learner_refresh, mo):')

DECISION_CONTROLS = '''def _(mo, project_id):
    workshop_decision = mo.ui.radio(options={'Approve this candidate':'approve','Reject this candidate':'reject'}, label="My graph decision")
    workshop_reviewed = mo.ui.checkbox(label="I reviewed this candidate's diff, checks and screenshots")
    workshop_reason = mo.ui.text_area(label="Reason for my decision", full_width=True)
    workshop_decide = mo.ui.button(value=0,on_click=lambda v:v+1,label="Record my decision")
    get_workshop_decide,set_workshop_decide=mo.state(0)
    mo.accordion({'Review the graph candidate':mo.vstack([mo.md('These controls become actionable only when your graph pauses at approval. The decision is bound to the checksum shown in the checkpoint, and remains in its history.'),workshop_decision,workshop_reviewed,workshop_reason,workshop_decide])}) if project_id=='project-08' else mo.md('')
    return get_workshop_decide, set_workshop_decide, workshop_decide, workshop_decision, workshop_reason, workshop_reviewed'''

DECIDE = '''def _(get_workshop_decide, learner, mo, set_workshop_decide, workshop_controller, workshop_decide, workshop_decision, workshop_reason, workshop_reviewed):
    mo.stop(workshop_decide.value <= get_workshop_decide())
    set_workshop_decide(workshop_decide.value)
    try:
        if not workshop_reviewed.value or not workshop_decision.value:
            raise RuntimeError('Review the evidence and select your own decision first.')
        _receipt=learner.decide_workshop_graph(workshop_decision.value,(workshop_controller or {}).get('verifiedSha256'),workshop_reason.value)
        _display=mo.md('Recorded **'+_receipt['decision']+'** for `'+_receipt['candidateSha256']+'`. No merge or replacement execution was launched.')
    except Exception as _error:_display=mo.callout(mo.md(learner.redact(_error)),kind='warn')
    _display
    return'''

# Saving and checking is the main local action. Separate source-only save/load
# remain secondary for recovery and intentionally unfinished baselines.
EDIT_BUTTONS = '''def _(mo):
    workshop_save = mo.ui.button(value=0, on_click=lambda v:v+1, label="Save without checking")
    workshop_reload = mo.ui.button(value=0, on_click=lambda v:v+1, label="Load my saved files")
    workshop_check = mo.ui.button(value=0, on_click=lambda v:v+1, label="Save and check my edits", full_width=True)
    mo.vstack([workshop_check,mo.accordion({'Other source actions':mo.hstack([workshop_save,workshop_reload],justify='start')})])
    return workshop_check, workshop_reload, workshop_save'''
CHECK = CHECK.replace('workshop_check):','workshop_check, workshop_editors):').replace('            _result = learner.check_edits()','            learner.save_edits(workshop_editors)\n            _result = learner.check_edits()')

CANDIDATE_OPTIONS = '''def _(learner, learner_refresh, mo):
    learner_refresh.value
    _rows=[row for row in learner.view()['trials'] if row.get('protocol')=='workshop-v1' and row.get('candidateId') and row.get('cleanupStatus')=='verified']
    _options={row.get('action','execution')+' · '+row['id'][:8]+' · '+row['outcome']:row['id'] for row in _rows}
    workshop_candidate = mo.ui.dropdown(options=_options, label="Choose a saved candidate")
    mo.accordion({'Continue from a saved candidate':mo.vstack([mo.md('Choose an execution from your own evidence. Preview its source diff before applying it. The previous snapshot remains saved.'),workshop_candidate])})
    return (workshop_candidate,)'''
TRANSFER = TRANSFER.replace('    workshop_candidate = mo.ui.text(label="Candidate execution ID from My work", full_width=True)\n','').replace('), workshop_candidate, workshop_candidate_preview,', '), workshop_candidate_preview,').replace('workshop_apply, workshop_candidate, workshop_candidate_preview','workshop_apply, workshop_candidate_preview')
# No action selector remains: each lesson has named, independent submit actions.

# A source-version signal updates dirty/prerequisite messages after either save
# path without rebuilding editors or reusing a button's duplicate-click counter.
STATE = STATE.replace('    get_files_epoch, set_files_epoch = mo.state(0)', '    get_files_epoch, set_files_epoch = mo.state(0)\n    get_source_version, set_source_version = mo.state(0)').replace('    return get_files_epoch,', '    return get_source_version, set_source_version, get_files_epoch,')
SAVE = SAVE.replace('workshop_editors, workshop_save):','workshop_editors, workshop_save, set_source_version):').replace("            _saved = learner.save_edits(workshop_editors)","            _saved = learner.save_edits(workshop_editors)\n            set_source_version(lambda v:v+1)")
CHECK = CHECK.replace('workshop_check, workshop_editors):','workshop_check, workshop_editors, set_source_version):').replace('            learner.save_edits(workshop_editors)','            learner.save_edits(workshop_editors)\n            set_source_version(lambda v:v+1)')
DIRTY = DIRTY.replace('def _(get_workshop_save,','def _(get_source_version, get_workshop_save,').replace('    get_workshop_save()','    get_workshop_save()\n    get_source_version()')
GUIDANCE = GUIDANCE.replace('def _(learner,','def _(get_source_version, learner,').replace('    learner_refresh.value','    learner_refresh.value\n    get_source_version()')
CANDIDATE = CANDIDATE.replace("    try:_display=", "    try:\n        if not workshop_candidate.value:raise ValueError('Choose a saved execution above before previewing its candidate.')\n        _display=")
RESULTS = RESULTS.replace("'student-evaluation.json']", "'student-evaluation.json','grader/local-check.json','grader/lanes.json','loop-checkpoint.json','graph-checkpoint.json']")
