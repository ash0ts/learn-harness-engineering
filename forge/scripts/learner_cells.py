"""Native lesson controls. No HTML imports and no paid work on opening a lesson."""

INIT = '''def _(LessonWorkspace, project_id, runner_commit):
    learner = LessonWorkspace(runner_commit, project_id)
    return (learner,)'''

SETUP = '''def _(mo):
    learner_budget = mo.ui.number(start=5, stop=50, value=20, step=1, label="Budget for this notebook copy (USD)")
    prepare_workspace = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Prepare or restore my workspace", full_width=True)
    get_prepare_click, set_prepare_click = mo.state(0)
    mo.vstack([
        mo.md("## Run this lesson yourself\\n\\n**1. Make your own copy.** In Forge, choose **Copy to project**, select a private project you can write to, and open your copy in **Edit**. Forge supplies your identity and session credential. You do not need a local checkout or an instructor coordinator.\\n\\n**2. Prepare your workspace.** This installs the pinned runner and restores this copy’s saved progress. It launches no model calls or coding trials. Notebook CPU compute is billed separately; this ledger conservatively allows $0.3408 for each one-hour CPU session. Your project’s billing controls remain authoritative.\\n\\nSaved work belongs to this notebook copy and your user. Keep the same copy when returning; making a new copy starts a separate lesson budget."),
        learner_budget, prepare_workspace
    ])
    return get_prepare_click, learner_budget, prepare_workspace, set_prepare_click'''

PREPARE = '''def _(get_prepare_click, learner, learner_budget, mo, prepare_workspace, set_prepare_click):
    mo.stop(prepare_workspace.value <= get_prepare_click())
    set_prepare_click(prepare_workspace.value)
    try:
        with mo.status.spinner(title="Preparing your personal workspace; this can take a few minutes"):
            learner.prepare(float(learner_budget.value))
        _message = "Workspace ready. Connect your own sandbox access below, then choose Check live access before your first exercise."
    except Exception as _error:
        _message = "Setup stopped: " + learner.redact(_error)
    mo.md(_message)
    return'''

CONNECT = '''def _(mo):
    connect_sandbox = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Connect my sandbox access")
    get_connect_click, set_connect_click = mo.state(0)
    mo.vstack([mo.md("**Connect sandbox access for this session.** Forge's injected notebook credential can save progress and use inference, but the Sandbox API currently requires your own W&B API key. Click below for a masked prompt. Use your own key from [API key settings](https://wandb.ai/authorize), never an instructor's key. It stays in this session's memory and is excluded from source, progress artifacts and downloads. Reconnect after opening a fresh runtime."), connect_sandbox])
    return connect_sandbox, get_connect_click, set_connect_click'''

AUTHENTICATE = '''def _(connect_sandbox, get_connect_click, learner, mo, set_connect_click):
    mo.stop(connect_sandbox.value <= get_connect_click())
    set_connect_click(connect_sandbox.value)
    try:
        import getpass
        _key = getpass.getpass("Your W&B API key (session memory only): ")
        _message = learner.connect(_key)
        del _key
    except Exception as _error:
        _message = "Connection stopped: " + learner.redact(_error)
    finally:
        _key = None
    mo.md(_message)
    return'''

CONTROLS = '''def _(mo, project_id, variants):
    learner_variant = mo.ui.dropdown(options=variants, value=variants[0], label="Treatment to try")
    learner_repeats = mo.ui.number(start=1, stop=3, value=1, label="Repeats (Projects 01–06)")
    _actions = {"Check live access (paid qualification)": "qualify", "Run exercise (paid)": "run"}
    if project_id in ["project-07", "project-08"]:
        _actions["Resume checkpoint (may launch paid work)"] = "resume"
    if project_id == "project-08":
        _actions["Record reviewed graph decision"] = "decision"
    learner_action = mo.ui.dropdown(options=_actions, value=next(iter(_actions)), label="Next action")
    learner_consent = mo.ui.checkbox(label="I authorize this action against my notebook budget and project billing")
    learner_launch = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Run selected action", full_width=True)
    learner_cancel = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Cancel active action")
    learner_decision = mo.ui.dropdown(options=["reject", "approve"], value="reject", label="Graph decision after reviewing the patch")
    learner_digest = mo.ui.text(label="Reviewed candidate SHA-256", full_width=True)
    get_action_click, set_action_click = mo.state(0)
    get_cancel_click, set_cancel_click = mo.state(0)
    mo.vstack([
        mo.md("**3. Check access, then run an exercise.** Qualification checks inference, Pi tools, app tracing, sandbox cancellation, and cleanup. It can incur charges. Once it passes, choose a treatment and **Run exercise**. A failed task is still useful evidence.\\n\\nThese controls execute the Forge adaptation described in this lesson. Project 07 runs a bounded one-round, ten-minute exercise; its original two-hour assignment needs a longer-lived coordinator. Project 08 stops for your checksum-bound approval. Notebook execution remains bounded to 50 minutes.\\n\\nOne copy supports one action at a time and at most two worker sandboxes. This is a per-copy application budget, not an organization-wide billing cap."),
        learner_action, learner_variant, learner_repeats,
        mo.accordion({"Project 08: explicit review decision": mo.vstack([learner_decision, learner_digest])}) if project_id == "project-08" else None,
        learner_consent, learner_launch, learner_cancel
    ])
    return get_action_click, get_cancel_click, learner_action, learner_cancel, learner_consent, learner_decision, learner_digest, learner_launch, learner_repeats, learner_variant, set_action_click, set_cancel_click'''

EXECUTE = '''def _(get_action_click, learner, learner_action, learner_consent, learner_decision, learner_digest, learner_launch, learner_repeats, learner_variant, mo, set_action_click):
    mo.stop(learner_launch.value <= get_action_click())
    set_action_click(learner_launch.value)
    try:
        if not learner_consent.value:
            raise RuntimeError("Confirm the action and billing above before launching")
        learner.start(learner_action.value, learner_variant.value, int(learner_repeats.value), learner_decision.value, learner_digest.value.strip())
        _message = "Action started. Results below refresh while it runs. Keep this editor session open."
    except Exception as _error:
        _message = "Action stopped: " + learner.redact(_error)
    mo.md(_message)
    return'''

CANCEL = '''def _(get_cancel_click, learner, learner_cancel, mo, set_cancel_click):
    mo.stop(learner_cancel.value <= get_cancel_click())
    set_cancel_click(learner_cancel.value)
    learner.cancel()
    mo.md("Cancellation requested. Check the status and cleanup evidence before closing this session.")
    return'''

REFRESH = '''def _(mo):
    learner_refresh = mo.ui.refresh(options=[5, 15, 30], default_interval=15, label="Refresh my results")
    learner_refresh
    return (learner_refresh,)'''

RESULTS = '''def _(json, learner, learner_refresh, mo):
    learner_refresh.value
    my_progress = learner.view()
    _rows = [{"Attempt": r["id"], "Treatment": r["variant"], "Outcome": r["outcome"], "Input tokens": r.get("inputTokens"), "Output tokens": r.get("outputTokens"), "Estimated USD": r.get("estimatedCostUsd")} for r in my_progress["trials"]]
    _links = []
    for _r in my_progress["trials"]:
        _parts = [f"**{_r['id'][:8]} · {_r['outcome']}**"]
        if _r.get("wandbRunUrl"):
            _parts.append(f"[Run]({_r['wandbRunUrl']})")
        if _r.get("artifactUrl"):
            _parts.append(f"[Patch and test evidence]({_r['artifactUrl']})")
        for _i, _conversation in enumerate(_r.get("conversationIds", []), 1):
            _parts.append(f"[Agent Lens {_i}](https://forge.coreweave.com/agent-lens/{my_progress['destination']}/conversations/{_conversation})")
        _links.append(" · ".join(_parts))
    _budget = my_progress["budget"]
    mo.vstack([
        mo.md("## My work\\n\\n**Status:** " + my_progress["status"] + "\\n\\nDestination: `" + (my_progress["destination"] if my_progress["destination"] != "/" else "Open your own Forge copy in Edit") + "`. These are your attempts; the historical tables above stay frozen."),
        mo.md(f"Budget: ${_budget.get('limitUsd', 0)} · accounted estimate: ${_budget.get('spentEstimateUsd', 0):.4f}. Sandbox access: " + ("connected for this session. " if my_progress["sandboxConnected"] else "not connected. ") + ("**Stopped:** " + _budget["halted"] if _budget.get("halted") else "")),
        mo.ui.table(_rows, selection=None, pagination=False, show_column_summaries=False) if _rows else mo.md("No personal trials yet. Prepare your workspace and check live access first."),
        mo.md("\\n\\n".join(_links)) if _links else None,
        mo.md(f"[Saved progress and dashboard]({my_progress['progressUrl']})") if my_progress.get("progressUrl") else None,
        mo.accordion({"Qualification results": mo.md("```json\\n" + json.dumps(my_progress["qualifications"], indent=2) + "\\n```"), "Checkpoints and approval candidate": mo.md("```json\\n" + json.dumps(my_progress["checkpoints"], indent=2) + "\\n```"), "Latest action log": mo.md("```text\\n" + my_progress["log"] + "\\n```"), "Saved observations": mo.md("```json\\n" + json.dumps(my_progress["notes"], indent=2) + "\\n```")}),
        mo.md("**4. Explain what happened.** Fill in the observation worksheet, save it below, and download your checkpoint before leaving. Return to this same notebook copy and choose **Prepare or restore my workspace** to recover the ledger, evidence and notes. A lost session with unfinished paid work stops for reconciliation; it never silently starts over.")
    ])
    return (my_progress,)'''

SAVE = '''def _(mo):
    learner_save = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Save my observations and progress")
    get_save_click, set_save_click = mo.state(0)
    learner_save
    return get_save_click, learner_save, set_save_click'''

PERSIST = '''def _(get_save_click, learner, learner_save, limitation, mo, observation, prediction, set_save_click):
    mo.stop(learner_save.value <= get_save_click())
    set_save_click(learner_save.value)
    try:
        learner.save_notes(prediction.value, observation.value, limitation.value)
        _message = "Observations and progress saved to your private project."
    except Exception as _error:
        _message = "Save stopped: " + learner.redact(_error)
    mo.md(_message)
    return'''

DOWNLOAD = '''def _(learner, mo, my_progress):
    if my_progress["prepared"] and not my_progress["pending"]:
        _download = mo.download(data=learner.bundle(), filename="my-lesson-checkpoint.tar.gz", mimetype="application/gzip", label="Download my progress and evidence")
    else:
        _download = mo.md("Your checkpoint download becomes available after setup and after an active action finishes. Results are saved privately after every completed action.")
    _download
    return'''

CELLS = [INIT, SETUP, PREPARE, CONNECT, AUTHENTICATE, CONTROLS, EXECUTE, CANCEL, REFRESH, RESULTS, SAVE, PERSIST, DOWNLOAD]
