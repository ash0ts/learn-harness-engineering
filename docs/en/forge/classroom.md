# Run the Forge lessons yourself

::: info Verified release
All nine master notebooks have matching committed source and saved output. The
shared learner workflow passed a live owner-account rehearsal and fresh-runtime
progress restore. See the [validation record](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-notebooks/forge/lessons/self-service-validation.md).
:::

Open the [overview](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTM%3D),
then start with Project 01. The nine notebooks are the reference lessons. Make
your own copy so your work and budget have a stable home.

1. Choose **Copy to project** in the notebook menu. Select a **private** Forge
   project where you can create notebooks, runs, artifacts, sandboxes, and use
   hosted inference. Your team must have the relevant entitlements.
2. Open the copy in **Edit**. In Marimo's **Config → Command palette**, choose
   **Re-run all cells** to initialize the lesson before preparing or launching an
   action. This displays the saved examples without starting a model call or coding trial.
3. Under **Run this lesson yourself**, choose a budget and click **Prepare or
   restore my workspace**. Setup installs the exact course revision and pinned
   Node dependencies inside the notebook. Forge supplies the session credential;
   do not paste a key into notebook source. Setup also restores this copy's saved
   progress. It requires outbound access to GitHub, Node's official distribution,
   Debian package repositories, npm and W&B.
4. Click **Connect my sandbox access** and enter your own W&B API key in the
   masked prompt beneath the running code cell. Keep Marimo in **Edit** view;
   Preview hides this prompt. The injected notebook credential currently cannot authenticate
   to the Sandbox API. Your key remains in session memory, never in source or
   progress artifacts. Reconnect after starting a fresh runtime.
5. Choose **Check live access**, authorize the action, and click **Run selected
   action**. This is paid qualification of inference, sandbox tools, app tracing,
   and cleanup. Read its result under **My work** before continuing.
6. Write a prediction in the observation worksheet. Choose **Run exercise**, a
   treatment and one repeat. The runner stages a clean task, lets Pi work, exports
   its patch, and grades it in a fresh sandbox with real service and Electron/Xvfb
   checks. Keep the editor open while the action runs.
7. Inspect your outcome, token usage, patch, test evidence and Agent Lens links
   under **My work**. Historical example tables stay frozen. A failed check is
   a result to explain, not a reason to replace the evidence with a nicer score.
8. Save your observations and download your progress checkpoint. Return to this
   same copy next time, select the original budget, and prepare/restore again.

No local checkout or instructor runner is required for these **adapted Forge
exercises**. The original assignments remain in each lesson with their own
deliverables. Completing a preset run does not certify the whole original lab.

## Costs, progress and interrupted work

The default is a $20 application budget for one learner's notebook copy, adjustable
from $5 to $50 before first setup. The copy reserves estimated costs before work,
uses at most two worker sandboxes at a time, and blocks further paid launches if
usage or cleanup is uncertain. The ledger conservatively accounts $0.3408 per
one-hour notebook CPU session at the verified 2-CPU/4-GiB rates. Provider pricing
and billing remain authoritative; this is not a guaranteed billing cap. Notebook
compute before setup, other notebooks, and other users are outside this ledger.

**Copying again creates another budget.** Use project/account billing controls for
an overall class limit. Do not put an instructor's credential in a student copy.
The destination remains the copy's project, and its saved state is keyed by
project, notebook collection and user. A partner should use the same designated
owner when working as a pair.

Progress is a versioned `course-learner-state` artifact. Before a paid action the
runner commits a pending marker; after completion it saves the ledger and evidence.
If a runtime disappears with a pending marker, the next session stops. Ask the
instructor to inspect the recorded trial IDs, sandbox state, reservations and logs
before reconciling it. Creating a fresh ledger would hide unfinished work and cost.
**Cancel active action** requests shutdown; wait for cleanup before closing Edit.

## Loops and graph decisions

Project 07's notebook control runs a one-round, ten-minute bounded exercise. Its
original two-hour monitor and five-round assignment require the longer-lived
coordinator described in [Running experiments](./running.md). The notebook cannot
promise a two-hour process inside a one-hour runtime.

Project 08 exposes a persistent graph checkpoint. Review the exported candidate
patch and both verification lanes. Paste the full displayed candidate SHA-256,
choose approve or reject, and explicitly run **Record reviewed graph decision**.
An approval from another candidate or an older qualification does not apply.

## Teaching a group

Give students access to the source lessons and a writable private destination.
Verify copying, setup and qualification from an actual student account before
class. A copied notebook includes its saved tables and images; linked historical
private traces and artifacts still require separate access to their original project.

For a first session, use pairs and Project 01. Spend ten minutes predicting failure,
fifteen inspecting the task, thirty-five running and examining conditions, twenty
reviewing patches and checks, and ten comparing explanations. These are suggested
timeboxes, not measured execution times. Submit the observation JSON, patch or
commit, run link and test evidence through your normal class submission channel.
There is no automatic LMS submission or original-course certification.

W&B Models stores each learner's experiment evidence and progress run. The saved
progress link appears under **My work**. A shared project can filter progress runs
by the `self-service-lessons` group. Access and organization-wide concurrency remain
team administration concerns; the notebook only limits its own workers.
