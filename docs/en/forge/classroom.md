# Run the Forge lessons yourself

Projects **01–08 now use the [hands-on workbench](./workshop)**: edit files, save a snapshot, check it, then execute it. Use that guide for the three-hour workshop and local Electron setup. The numbered run-and-compare flow below remains the guide for older notebook copies.

::: info What has been checked
The shared learner workflow passed a live owner-account rehearsal and a
fresh-runtime progress restore. We have not yet rehearsed it with a student
account. The [publication manifest](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/forge/publication-manifest.json)
records which published notebook versions match the committed source. See the
[validation record](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/forge/lessons/self-service-validation.md).
:::

Open the [overview](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTM%3D),
then start with Project 01. Each lesson is its own notebook. The steps below
match the numbered steps in older notebook copies.

**Before the numbered steps**

- **Copy the lesson.** Open the **⋯** menu at the top right, choose **Copy to
  project**, and pick a **private** project where you can create notebooks, runs,
  artifacts and sandboxes and use hosted inference. Your copy opens by itself in
  the editor. The picker lists every project you can write to and does not mark
  which are private; a non-private one is refused later, at step 2.
- **Load the page.** Click the yellow **▶** button at the bottom right of the
  editor. Until the cells have run you see only the lesson text: the figures,
  tables, worksheet and run controls are missing. Running them starts no model
  call and no coding attempt.
- **Read first.** Read the lab, then open a recorded attempt under **Inspect one
  attempt** and follow its link into Agent Lens to see what the agent did.

**The six steps under "Run this lesson yourself"**

1. **Use your own copy.** Return to the same copy every time. A new copy starts
   with no saved work and a new spending limit.
2. **Prepare your workspace.** Choose a spending limit and click **Prepare or
   restore my workspace**. Setup installs the exact course revision and pinned
   Node dependencies inside the notebook and restores this copy's saved
   progress. It takes a few minutes and needs outbound access to GitHub, Node's
   official distribution, Debian package repositories, npm and W&B.
3. **Connect your sandbox access.** Click the button and paste your own W&B API
   key into the masked box that appears below it. **Stay in the editor view:
   the box does not appear in Preview**, and the notebook then waits on a prompt
   you cannot see. The notebook's own session credential cannot start sandboxes
   yet, so you need your own key. It stays in session memory, never in
   the notebook source or saved progress. Connect again after a fresh runtime.
4. **Write your prediction** before you run anything.
5. **Check that everything works, then run.** The check is a small paid test
   of inference, sandbox tools, app tracing and cleanup; its result appears
   under **My work**, and nothing else will start until it has passed. Then
   choose the run action (**Run attempts** in Projects 01 to 06) and run one
   attempt with each treatment so you have something to compare. The runner
   stages a clean task, lets Pi work for at most ten minutes and 24 model calls,
   exports its patch, and grades it in a fresh sandbox with real service and
   Electron checks. Save your prediction first with **Save my notes and
   progress**, and keep the tab open while the attempt runs.
6. **Explain what happened.** Under **My work**, read the checks, look at the
   app window the grader captured, and open the agent's conversation in Agent
   Lens. Fill in the worksheet, click **Save my notes and progress**, and
   download your notes and progress. If a check failed, explain that result
   instead of replacing the evidence with a nicer score. Blank worksheet fields
   never overwrite notes you saved earlier.

You don't need a local checkout or an instructor's runner for a notebook
attempt. It is a smaller version of the lab. Each lesson still describes the
full lab and what to hand in, and finishing a notebook attempt doesn't complete it.

## Costs, progress and interrupted work

The default is a $20 application budget for one learner's notebook copy, adjustable
from $5 to $50 before first setup. The copy reserves estimated costs before work,
uses at most two worker sandboxes at a time, and blocks further paid launches if
usage or cleanup is uncertain. The ledger conservatively counts $0.3408 per
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
If a runtime disappears with a pending marker, the next session stops and will not
start new work. Earlier results stay visible under **My work**, but the progress
download is withheld, because the interrupted action's log was never scrubbed of
the learner's key. The instructor inspects the recorded trial IDs, sandbox state,
reservations and logs in the learner's project before reconciling it. There is no
in-notebook reconcile action yet. Creating a fresh ledger would hide unfinished
work and cost.

Three other things stop a copy in the same way, and the notebook says so at the
point where each can happen:

- **Cancel the running action**, once an attempt or check has started, leaves its
  cost unknown. Wait until **My work** shows the action has finished or failed
  before closing the tab.
- A **Check that everything works** that fails without reporting what it used.
- An attempt that does not report its usage.

Before each attempt the copy sets aside a worst case of about $4.20 and refuses
to start if that would pass the limit. On the $5 minimum that happens after a
few attempts or in a second session, so leave the limit at $20.

A notebook runtime lasts one hour. Start an attempt only when it can finish
inside the hour.

## Loops and graph decisions

Project 07's run action is **Run the loop once**. Each loop runs exactly one
round, so goal and timer give the agent the same single attempt, and timer then
waits out its ten-minute deadline. Each treatment runs once per copy. The lab's
two-hour monitor and five-round assignment need the longer-lived coordinator
described in [Running experiments](./running.md), because the notebook runtime
lasts one hour.

Project 08's run action is **Run the graph**. One run makes up to three
candidates, each followed by two verification sandboxes, so allow about three
times the time and cost of a single attempt. The graph runs once per copy and
pauses only if a candidate passes. To record a decision, find the candidate's
checksum under **My work** in **Details: checkpoints and approval candidate**,
paste it into the decision panel, choose approve or reject, then set **What to
do** to **Record my reviewed graph decision** and press **Start**. That step
starts no paid work. An approval of another candidate does not apply.

## Teaching a group

Give students view-only access to the source lessons and a writable private
destination. Do not give them edit rights on the course project: opening an
original in the editor with edit rights can save a new version of it.
Verify copying, setup and qualification from an actual student account before
class. A copied notebook includes its saved tables and images; linked historical
private traces and artifacts still require separate access to their original project.

For a first session, use pairs and Project 01. Spend ten minutes predicting failure,
fifteen inspecting the task, thirty-five running and examining conditions, twenty
reviewing patches and checks, and ten comparing explanations. These are suggested
timeboxes, not measured execution times. A notebook runtime lasts one hour, so
the 90 minutes span two notebook sessions: have pairs save their notes before
the hour is up, and prepare and connect again afterwards. Submit the observation JSON, patch or
commit, run link and test evidence through your normal class submission channel.
There is no automatic LMS submission or original-course certification.

W&B Models stores each learner's experiment evidence and progress run, and the saved
progress link appears under **My work**. In a shared project you can filter progress runs
by the `self-service-lessons` group. Team administrators manage access and
organization-wide concurrency; the notebook limits only its own workers.
