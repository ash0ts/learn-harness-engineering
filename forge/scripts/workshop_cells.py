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
    mo.vstack([mo.md("## Your hands-on lab\\n\\n" + workshop_initial['manifest']['task'] + "\\n\\nThe checkpoint supplies the surrounding app. Your changes are the files below. **Save these edits** writes your draft; **Check my edits** builds and tests it without inference or a sandbox. A paid action freezes that saved draft and records exactly which code ran.\\n\\n**Use your own copy.** Choose **⋯ → Copy to project** and select a private project you can write to. Run the notebook cells with **▶**. Stay in Edit for the masked API-key prompt. Each copy has its own $20 estimate limit; this is separate from a classroom budget. No separate service deployment is needed."),
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

EDITORS = '''def _(get_files_epoch, learner, mo, workshop_initial):
    get_files_epoch()
    workshop_loaded = learner.workshop_files() or workshop_initial
    _languages = {".ts":"typescript", ".tsx":"typescript", ".md":"markdown", ".json":"json", ".py":"python"}
    workshop_editors = mo.ui.dictionary({_name: mo.ui.code_editor(value=_text, language=_languages.get("." + _name.rsplit(".",1)[-1], "text"), label=_name, min_height=220, max_height=440, debounce=False) for _name, _text in workshop_loaded['files'].items()})
    mo.vstack([mo.md("### 1. Inspect and edit your implementation\\n\\nThe deliberate gaps are marked `TODO(workshop)`. Open each file tab. Typing changes only the draft in this editor; it cannot launch work. Save before checking or executing. Files outside this list belong to the supplied checkpoint."), mo.ui.tabs({_name:workshop_editors[_name] for _name in workshop_loaded['files']})])
    return workshop_editors, workshop_loaded'''

EDIT_BUTTONS = '''def _(mo):
    workshop_save = mo.ui.button(value=0, on_click=lambda v:v+1, label="Save these edits")
    workshop_reload = mo.ui.button(value=0, on_click=lambda v:v+1, label="Load my saved files")
    workshop_check = mo.ui.button(value=0, on_click=lambda v:v+1, label="Check my edits (no inference)")
    mo.hstack([workshop_save, workshop_check, workshop_reload], justify="start")
    return workshop_check, workshop_reload, workshop_save'''

SAVE = '''def _(get_workshop_save, learner, mo, set_workshop_save, workshop_editors, workshop_save):
    mo.stop(workshop_save.value <= get_workshop_save())
    set_workshop_save(workshop_save.value)
    try:
        _saved = learner.save_edits(workshop_editors.value)
        _message = mo.callout(mo.md("Saved snapshot `" + _saved['snapshot']['id'] + "` · SHA-256 `" + _saved['snapshot']['sha256'] + "`. Run the checks next."), kind="success")
    except Exception as _error:
        _message = mo.callout(mo.md("**Edits not saved.** " + learner.redact(_error)), kind="warn")
    _message
    return'''

DIRTY = '''def _(get_workshop_save, learner, mo, workshop_editors, workshop_loaded):
    get_workshop_save()
    _current = learner.workshop_files() or workshop_loaded
    _changed = [_name for _name, _text in workshop_editors.value.items() if _current['files'].get(_name) != _text]
    _state = learner.state.get('workshop', {})
    mo.md(("**Unsaved edits:** " + ", ".join("`" + _name + "`" for _name in _changed) + ". Save these edits before executing." if _changed else "**Editor matches the saved files.**") + (" Your last saved snapshot is `" + _state['draftSnapshot'] + "`." if _state.get('draftSnapshot') else " Save once to create your first snapshot."))
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
        if learner.workshop_files()['files'] != workshop_editors.value:
            raise RuntimeError("There are unsaved edits. Save these edits first.")
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
        _stale = _r.get('snapshotSha256') != _work.get('draftSha256') or (learner.workshop_files() or {}).get('files') != workshop_editors.value
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
    mo.accordion({'Continue from a Pi candidate or a laptop edit':mo.vstack([mo.md('Preview the diff first, then apply it explicitly. Applying updates the saved workspace; **Load my saved files** refreshes the editors and replaces unsaved text. Save these edits again before execution. Project 03 resumes only from a recorded first-session candidate: add your handoff to its files, then choose the fresh-session action. Your earlier snapshots remain intact.'), workshop_candidate, workshop_candidate_preview, workshop_upload, workshop_import, workshop_apply])})
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
