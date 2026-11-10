"""Native lesson controls. No HTML imports and no paid work on opening a lesson."""

INIT = '''def _(LessonWorkspace, project_id, runner_commit):
    learner = LessonWorkspace(runner_commit, project_id)
    return (learner,)'''

SETUP = '''def _(mo, project_id, run_facts):
    learner_budget = mo.ui.number(start=5, stop=50, value=20, step=1, label="Spending limit for this copy (USD)")
    prepare_workspace = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Prepare or restore my workspace", full_width=True)
    get_prepare_click, set_prepare_click = mo.state(0)
    _typical = (f"The recorded attempts for this lesson took {run_facts['minMinutes']} to {run_facts['maxMinutes']} minutes and an estimated ${run_facts['minUsd']:.2f} to ${run_facts['maxUsd']:.2f} each. " if run_facts else "")
    _where = "On this overview page the controls run the Project 01 exercise. If you are going to do Project 01, run it from the Project 01 notebook instead, so your attempts sit beside its lesson.\\n\\n" if project_id == "overview" else ""
    mo.vstack([
        mo.md("## Run this lesson yourself\\n\\nYou have read the lab and looked at recorded attempts. Now run one of your own and compare. Work through the six steps in order, and stay in the editor view: the API key prompt in step 3 does not appear in Preview.\\n\\n" + _where + _typical + "Running an attempt is optional and costs money on your project. The spending limit below caps this copy's own estimate of what it has spent. Before each sandbox or model request the copy sets aside its maximum estimated cost, and it stops before an operation that would pass the limit, so leave the limit at $20 unless you have a reason to lower it. Your project's own billing shows the real charge.\\n\\n**1. Use your own copy.** If you have not copied this notebook yet, open the **⋯** menu at the top right and choose **Copy to project**, then pick a private project you can write to. Come back to that same copy next time. A new copy starts with no saved work and a new spending limit.\\n\\n**2. Prepare your workspace.** This installs the course runner inside the notebook and restores anything this copy saved before. It takes a few minutes and starts no model call or coding attempt. Each notebook session also counts about $0.34 of notebook compute against your limit, so **My work** shows $0.34 as soon as setup finishes. A notebook session lasts one hour. Keep the same spending limit each time you return."),
        learner_budget, prepare_workspace
    ])
    return get_prepare_click, learner_budget, prepare_workspace, set_prepare_click'''

PREPARE = '''def _(get_prepare_click, learner, learner_budget, mo, prepare_workspace, set_prepare_click):
    mo.stop(prepare_workspace.value <= get_prepare_click())
    set_prepare_click(prepare_workspace.value)
    try:
        with mo.status.spinner(title="Preparing your workspace. This takes a few minutes."):
            learner.prepare(float(learner_budget.value))
        _message = mo.callout(mo.md("**Workspace ready.** Go on to step 3 and connect your sandbox access."), kind="success")
    except Exception as _error:
        _message = mo.callout(mo.md("**Setup stopped.** " + learner.redact(_error)), kind="danger")
    _message
    return'''

CONNECT = '''def _(mo):
    connect_sandbox = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Connect my sandbox access")
    get_connect_click, set_connect_click = mo.state(0)
    mo.vstack([mo.md("**3. Connect your sandbox access.** Each attempt runs in a fresh sandbox, and starting one needs your own W&B API key. Copy it from [your API key page](https://wandb.ai/authorize). Click the button, then paste the key into the masked box that appears just below it and press Enter.\\n\\nThe box appears **only in the editor view**. If you are in Preview and nothing appears, switch back to the editor and the box will be there. Use your own key, never someone else's. It is kept in this session's memory only: it is not written to the notebook, your saved progress or your downloads. You will need to connect again whenever the notebook session restarts."), connect_sandbox])
    return connect_sandbox, get_connect_click, set_connect_click'''

AUTHENTICATE = '''def _(connect_sandbox, get_connect_click, learner, mo, set_connect_click):
    mo.stop(connect_sandbox.value <= get_connect_click())
    set_connect_click(connect_sandbox.value)
    _state = learner.view()
    # Never ask for a key that cannot be used yet.
    if not _state["prepared"]:
        _message = mo.callout(mo.md("**Prepare your workspace first** (step 2). You have not been asked for your key."), kind="warn")
    elif _state["active"]:
        _message = mo.callout(mo.md(("**An action is still running.** Wait until **My work** shows it has finished, then connect." if _state["active"] else "**This copy is stopped** because an earlier action was interrupted, so a key cannot be used here.") + " You have not been asked for your key."), kind="warn")
    else:
        try:
            import getpass
            _key = getpass.getpass("Paste your W&B API key and press Enter (kept in session memory only): ")
            _text = learner.connect(_key)
            del _key
            _message = mo.callout(mo.md("**Connected.** " + _text + " Go on to step 4."), kind="success")
        except Exception as _error:
            _message = mo.callout(mo.md("**Connection stopped.** " + learner.redact(_error)), kind="danger")
        finally:
            _key = None
    _message
    return'''

CONTROLS = '''def _(mo, project_id, variant_notes, variants):
    learner_variant = mo.ui.dropdown(options=variants, value=variants[0], label="Treatment to try")
    learner_repeats = mo.ui.number(start=1, stop=3, value=1, label="Attempts in one go (each is paid)")
    _run_name = "Run the loop once" if project_id == "project-07" else "Run the graph" if project_id == "project-08" else "Run attempts"
    _actions = {"Check that everything works (small paid test)": "qualify", _run_name + " (paid)": "run"}
    if project_id == "project-08":
        _actions["Record my reviewed graph decision"] = "decision"
    learner_action = mo.ui.dropdown(options=_actions, value=next(iter(_actions)), label="What to do")
    learner_consent = mo.ui.checkbox(label="I understand this starts paid work on my project, counted against my spending limit")
    learner_launch = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Start", full_width=True)
    learner_cancel = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Cancel the running action")
    learner_decision = mo.ui.dropdown(options=["reject", "approve"], value="reject", label="Graph decision after reviewing the patch")
    learner_digest = mo.ui.text(label="Reviewed candidate SHA-256", full_width=True)
    get_action_click, set_action_click = mo.state(0)
    get_cancel_click, set_cancel_click = mo.state(0)
    _setups = "\\n".join(f"- **{_name}**: {variant_notes.get(_name, 'See the lesson above.')}" for _name in variants)
    _compare = "Run one attempt with each treatment, one after the other, so you have rows to compare under **My work**. **Attempts in one go** sets how many attempts one Start runs, one after another. Each is paid, so leave it at 1 unless you want repeats." if len(variants) > 1 else "This lesson has one treatment."
    _special = ""
    if project_id == "project-07":
        _compare = "Run goal and maker-checker, one after the other, so you have two different setups to compare under **My work**. In one round, timer gives the agent the same setup as goal."
        _special = "\\n\\nIn this notebook each loop runs exactly one round, so the repeating described in the lab does not happen here. Goal and maker-checker finish as soon as their round has been graded. Timer runs the same single attempt as goal and then keeps the action open until its ten-minute deadline. Start can run another completed treatment; each attempt keeps its own checkpoint. The full two-hour monitoring exercise in the lab needs a runner that outlives a one-hour notebook session."
    if project_id == "project-08":
        _special = "\\n\\nHere the run action runs the whole graph once: up to three candidates by the agent, each followed by two verification sandboxes, so allow about three times the time and cost shown above. The graph pauses when a candidate passes its checks, and nothing is accepted until you review that exact patch and record a decision in the panel below. If no candidate passes, the graph stops at `failed`. Start can run another graph after the current graph finishes or you decide its approval candidate."
    mo.vstack([
        mo.md("**5. Check that everything works, then run an attempt.** The first time, choose **Check that everything works**. It is a small paid test that the model, the sandbox and the tracing all respond, followed by checks that the unfinished app fails and the protected repair passes; it cleans up after itself. Its result appears under **My work**. If it does not pass, the reason is shown there, and a check that fails without reporting what it used stops this copy until your instructor has looked at it. Once it passes, choose **" + _run_name + "**.\\n\\nA treatment is the setup the agent starts with. In this lesson you can try:\\n\\n" + _setups + "\\n\\n" + _compare + " The coding agent gets at most ten minutes and 24 model calls per attempt, and one copy runs one action at a time. A notebook session lasts one hour, so click **Save my notes and progress** first to keep your prediction, and start only when there is time to finish. Keep this tab open while it runs: if the notebook session ends mid-run, use Prepare and Connect to inspect the saved work. **Cancel the running action** waits for cleanup; missing usage or unverified cleanup keeps new paid work blocked until your instructor can reconcile it. Count a failed attempt as a result to explain, and do not hide it." + _special),
        learner_action, learner_variant,
        learner_repeats if project_id not in ["project-07", "project-08"] else mo.md(""),
        mo.accordion({"Project 08: record your review decision": mo.vstack([mo.md("Under **My work**, open **Details: checkpoints and approval candidate** and find `project-08-graph-checkpoint.json`. You can record a decision only when its `node` is `approval`. There, `candidate.trialId` names the attempt to review and `candidate.sha256` is its checksum. Read that attempt's patch and both verification results, paste the full checksum below and choose approve or reject. Then set **What to do** to **Record my reviewed graph decision** and press **Start**. Recording a decision starts no paid work and needs no tick in the box. An approval of a different candidate does not count."), learner_decision, learner_digest])}) if project_id == "project-08" else mo.md(""),
        learner_consent, learner_launch, learner_cancel
    ])
    return get_action_click, get_cancel_click, learner_action, learner_cancel, learner_consent, learner_decision, learner_digest, learner_launch, learner_repeats, learner_variant, set_action_click, set_cancel_click'''

EXECUTE = '''def _(get_action_click, learner, learner_action, learner_consent, learner_decision, learner_digest, learner_launch, learner_repeats, learner_variant, mo, set_action_click):
    mo.stop(learner_launch.value <= get_action_click())
    set_action_click(learner_launch.value)
    try:
        if learner_action.value != "decision" and not learner_consent.value:
            raise RuntimeError("Tick the box above to confirm the paid work, then press Start again.")
        learner.start(learner_action.value, learner_variant.value, int(learner_repeats.value), learner_decision.value, learner_digest.value.strip())
        _message = mo.callout(mo.md("**Started.** Watch **My work** below; it refreshes by itself. Keep this tab open until the status says it has finished."), kind="info")
    except Exception as _error:
        _message = mo.callout(mo.md("**Not started.** " + learner.redact(_error)), kind="warn")
    _message
    return'''

CANCEL = '''def _(get_cancel_click, learner, learner_cancel, mo, set_cancel_click):
    mo.stop(learner_cancel.value <= get_cancel_click())
    set_cancel_click(learner_cancel.value)
    learner.cancel()
    mo.callout(mo.md("**Cancel requested.** Wait until the status under **My work** shows the action has finished or failed before closing this tab. If an attempt or check had already started, its cost is now unknown, so this copy will not start anything else until your instructor has checked it."), kind="warn")
    return'''

REFRESH = '''def _(mo):
    learner_refresh = mo.ui.refresh(options=[5, 15, 30], default_interval=15, label="Refresh my results")
    learner_refresh
    return (learner_refresh,)'''

RESULTS = '''def _(base64, evidence_link, json, learner, learner_refresh, mo, phase_labels):
    learner_refresh.value
    my_progress = learner.view()
    _lens = "https://forge.coreweave.com/agent-lens/" + my_progress["destination"]
    _own = my_progress["destination"] != "/"
    _budget = my_progress["budget"]
    _checks = my_progress["qualifications"]
    if not _checks:
        _access = "not run yet"
    elif _checks[-1].get("passed"):
        _access = "**passed**. You can run an attempt."
    else:
        _access = "**did not pass**. " + learner.redact(_checks[-1].get("error") or "Open the details below for the reason.") + (" This copy has now stopped and will not start anything else until your instructor has checked it." if _budget.get("halted") or _budget.get("reservations") else " Run the check again once that is fixed.")
    # The check is the only time the app itself calls a model, so link both of its conversations.
    _traces = []
    if _checks and _own:
        _agent_id = (_checks[-1].get("agent") or {}).get("conversationId")
        _app_id = (_checks[-1].get("app") or {}).get("conversationId")
        if _agent_id:
            _traces.append(f"[the test agent's conversation]({_lens}/conversations/{_agent_id})")
        if _app_id:
            _traces.append(f"[the app's own conversation]({_lens}/conversations/{_app_id})")
    if _traces:
        _access += " In Agent Lens you can open " + " and ".join(_traces) + ". The check is the only time the app itself calls a model, so this is where you can compare an app's conversation with an agent's."
    # The runner writes a placeholder outcome before the agent starts; do not show it as a failure.
    _result = lambda r: str(r.get("outcome", "unknown")).replace("_", " ") if r.get("finishedAt") else ("still running" if my_progress["active"] else "interrupted before it finished")
    _rows = [{"Attempt": r["id"][:8], "Treatment": r.get("variant"), "Result": _result(r), "Checks passed": (str(sum(bool(c.get("passed")) for c in (r.get("grade") or {}).get("checks", []))) + " of " + str(len((r.get("grade") or {}).get("checks", [])))) if (r.get("grade") or {}).get("checks") else "not graded", "Estimated USD": round(r["estimatedCostUsd"], 3) if isinstance(r.get("estimatedCostUsd"), (int, float)) else None} for r in my_progress["trials"]]
    _cards = []
    for _r in my_progress["trials"]:
        _labels = phase_labels(_r.get("variant"), len(_r.get("conversationIds", [])))
        _parts = [f"[{_label} in Agent Lens]({_lens}/conversations/{_conversation})" for _label, _conversation in zip(_labels, _r.get("conversationIds", []))]
        if _r.get("artifactUrl"):
            _parts.append(f"[Patch and test evidence]({evidence_link(_r['artifactUrl'])})")
        if _r.get("wandbRunUrl"):
            _parts.append(f"[Run record]({_r['wandbRunUrl']})")
        _failed = [str(c.get("name")) + (" (" + str(c["error"]) + ")" if c.get("error") else "") for c in (_r.get("grade") or {}).get("checks", []) if not c.get("passed")]
        _summary = f"**Attempt {_r['id'][:8]} · {_r.get('variant')} · {_result(_r)}**" + ("\\n\\nFailed checks: " + learner.redact("; ".join(_failed)) + "." if _failed else "") + ("\\n\\nThe agent used all of its allowed time or turns before saying it was done. The grade above is from the independent check of its patch." if _r.get("actorCompleted") is False else "")
        _card = [mo.md(_summary), mo.md(" · ".join(_parts))]
        if _r["id"] in my_progress["captures"]:
            _shot = learner.capture(_r["id"])
            _card.append(mo.image(("data:image/jpeg;base64," if _shot[:2] == b"\\xff\\xd8" else "data:image/png;base64,") + base64.b64encode(_shot).decode(), alt="The app window from this attempt, captured by the independent check", caption="Your attempt's app window, captured by the independent check, not by the agent.", width="100%"))
        _cards.append(mo.vstack(_card))
    _notes = my_progress["notes"]
    _saved_notes = "\\n\\n".join(f"**{_title}**\\n\\n{_notes[_key]}" for _key, _title in [("prediction", "Your prediction"), ("observation", "What you observed"), ("limitation", "What is still unresolved"), ("observedHumanMinutes", "Your time in minutes")] if _notes.get(_key))
    mo.vstack([
        mo.md("## My work\\n\\n**Status:** " + my_progress["status"] + "\\n\\n**Check that everything works:** " + _access + "\\n\\n**Sandbox access:** " + ("connected for this session." if my_progress["sandboxConnected"] else "not connected.") + (f"\\n\\n**Spending:** an estimated ${_budget.get('spentEstimateUsd', 0):.2f} of your ${_budget['limitUsd']:g} limit." if _budget.get("limitUsd") else "\\n\\n**Spending:** nothing yet. You choose your limit in step 2.") + ("\\n\\n**Stopped:** " + str(_budget["halted"]) + ". Ask your instructor before continuing." if _budget.get("halted") else "\\n\\n**Stopped:** the cost of an earlier action is uncertain. Ask your instructor before continuing." if _budget.get("reservations") and not my_progress["active"] else "") + "\\n\\nSaved in `" + (my_progress["destination"] if _own else "your own copy, once you make one") + "`. These are your attempts. The recorded attempts above never change."),
        mo.ui.table(_rows, selection=None, pagination=False, show_column_summaries=False) if _rows else mo.md("No attempts of your own yet."),
        mo.vstack(_cards) if _cards else mo.md(""),
        mo.md(f"**See what the agent did.** Each attempt links to its conversation in Agent Lens: the prompt, every step the agent reasoned through, each command it ran and what came back. [Open all conversations in your project]({_lens}/conversations)." + (f" · [Saved progress run]({my_progress['progressUrl']})" if my_progress.get("progressUrl") else "")) if _own else mo.md(""),
        mo.md("### Your saved notes\\n\\n" + _saved_notes) if _saved_notes else mo.md(""),
        mo.accordion({"Details: check that everything works": mo.md("```json\\n" + json.dumps(_checks, indent=2) + "\\n```"), "Details: checkpoints and approval candidate": mo.md("```json\\n" + json.dumps(my_progress["checkpoints"], indent=2) + "\\n```"), "Details: latest action log": mo.md("```text\\n" + my_progress["log"] + "\\n```")})
    ])
    return (my_progress,)'''

SAVE = '''def _(mo):
    learner_save = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Save my notes and progress")
    get_save_click, set_save_click = mo.state(0)
    learner_save
    return get_save_click, learner_save, set_save_click'''

PERSIST = '''def _(get_save_click, learner, learner_save, limitation, measured_minutes, mo, observation, prediction, set_save_click):
    mo.stop(learner_save.value <= get_save_click())
    set_save_click(learner_save.value)
    try:
        learner.save_notes(prediction.value, observation.value, limitation.value, measured_minutes.value)
        _message = mo.callout(mo.md("**Saved to your private project.** Anything you left blank keeps what you saved earlier."), kind="success")
    except Exception as _error:
        _message = mo.callout(mo.md("**Not saved.** " + learner.redact(_error).rstrip(".") + ". You can still use **Download my notes** below."), kind="warn")
    _message
    return'''

DOWNLOAD = '''def _(learner, mo, my_progress):
    _checkpoint = learner.cached_checkpoint_bytes()
    if _checkpoint is not None:
        _download = mo.download(data=_checkpoint, filename="my-lesson-checkpoint.tar.gz", mimetype="application/gzip", label="Download my progress and evidence")
    else:
        _download = mo.md("Your progress download appears here after setup, and again once a running action has finished. Results are saved to your project after every completed action.")
    _download
    return'''

# Order matters to a reader. The worksheet cells from lesson_cells are placed
# between these groups by create_notebooks.py.
SETUP_CELLS = [INIT, SETUP, PREPARE, CONNECT, AUTHENTICATE]
RUN_CELLS = [CONTROLS, EXECUTE, CANCEL, REFRESH, RESULTS]
SAVE_CELLS = [SAVE, PERSIST]
CELLS = [*SETUP_CELLS, *RUN_CELLS, *SAVE_CELLS, DOWNLOAD]
