## Teach the course by building the app

An agent says the job is done. The app opens. Then you ask a second question and the history disappears. Which of those observations belongs in the grade?

This course follows a small Electron knowledge-base app through eight projects. You will build its shell, teach an agent to navigate the workspace, resume unfinished work, diagnose a real defect, divide work between roles, and finally turn the process into loops and a graph. The application gives you something concrete to inspect whenever an agent claims success.

**Start here:** open Project 01, read its task, and write down what would convince you that the app works. Keep that prediction. At the end, compare it with what your checker actually observed.

These notebooks have two jobs. The **course lab** restores the original exercise and its submission requirements. The **recorded Forge case** lets you inspect experiments we already ran with Pi, hosted Qwen inference, CPU sandboxes, Agent Lens, and W&B Models. Those experiments adapted several original tasks. Their results are useful case studies, but they do not certify that every original exercise was completed.

<!-- cell -->
## A route through the eight projects

| Project | What you change | What you must bring back |
|---|---|---|
| 01 · Minimal harness | The instructions and workspace around the agent | Two isolated builds, launch evidence, and a comparison |
| 02 · Readable workspace | The files a fresh session uses to find its way | Working import/detail/persistence plus a usable handoff |
| 03 · Continuity | The unit of progress and its evidence | A feature ledger, feature-ID commits, and a clean restart |
| 04 · Runtime feedback | The observations available during debugging | A diagnosis, a narrow repair, and measured debugging notes |
| 05 · Roles | Who plans, implements, and checks the same feature | Three implementations and the same independent rubric |
| 06 · Capstone | The complete operating harness | A fixed task set, cleanup/rerun evidence, and ablations |
| 07 · Loops | Who decides when to continue or stop | Manual/goal comparison, a two-hour monitor, five review rounds |
| 08 · Graphs | The paths, state, concurrency, and approvals | A graph contract, serial/parallel comparison, two human reviews |

Work in this order for the full course. For a first class, teach Project 01 and inspect one Project 04 trace. Projects 07 and 08 need the artifacts from earlier work; treating them as isolated demos loses the lesson about durable state.

<!-- cell -->
## Run a class together

**Before class.** Share this notebook URL and the project notebook links below. They are in a private Forge project: students need an account and access to that project. Test access with a student account before the session. A link alone does not grant access. Each learner chooses **Copy to project**, selects a private project they can write to, and opens their own copy in **Edit**. Keep the instructor's canonical notebooks as the reference. Copying a notebook does not copy permissions to the historical private traces and artifacts.

For the notebook's Forge exercise, students choose **Prepare or restore my workspace**, connect their own sandbox access through the masked prompt, then choose **Check live access** and **Run exercise**. Setup installs the pinned runner automatically and uses the notebook's session credential for progress. Sandbox execution currently requires the learner's own API key, held only in session memory. It saves progress to a learner-specific artifact in the selected private project. The original course lab also needs a clean editable course workspace and evidence folder. Use the frozen original revision linked below when comparing with that course. Keep reference solutions out of the coding agent's workspace. For a controlled study, keep model settings, task, starter bytes, test fixtures, and budget fixed within each comparison.

**During a 90-minute first session:** spend 10 minutes predicting failures, 15 inspecting the starter and acceptance criteria, 35 running the two conditions, 20 inspecting the patches and checks, and 10 comparing observations. These are teaching timeboxes, not measured completion times. A slow run becomes a follow-up; do not call an unfinished attempt a failure merely because class ended.

**Before students leave.** Have each pair save its observations, download the progress checkpoint, and submit the actual patch, run log, and evidence alongside it. Return to the same copy next time and restore the workspace. A new copy has a separate budget; this is not a classroom-wide billing limit. Ask another pair to reproduce one claim. A screenshot without the command, fixture, revision, and check is a useful illustration, but weak evidence.

<!-- cell -->
## What runs here, and what needs a workspace

Forge can open these links in its editor when you have edit permission. Before teaching, open Marimo's command palette, choose **Run all stale cells**, and use the **preview** button to show the lesson. These cells load the saved evidence and enable the selector, worksheet, and downloads; they do not start inference or a coding trial. Notebook runtime compute can incur cost. The saved static output is verified separately from the live editor.

The original course lab runs in a student workspace with an editor, Git, Node, Electron, and the selected coding agent. The **Run this lesson yourself** section prepares a personal TypeScript coordinator inside the notebook, then launches the adapted Forge tasks in isolated CPU sandboxes. The lesson does not reimplement the app in Python. You can inspect your own results and trace links under **My work**, alongside the frozen historical examples. The one-round Project 07 exercise is bounded to ten minutes; the original two-hour exercise still requires a coordinator that outlives the notebook's one-hour session.

The saved campaign used CPU sandboxes to run Node, Python, Electron, and Xvfb. Model inference was served by Forge's hosted endpoint. **We did not provision or validate a GPU training job.** W&B Models records experiments and artifacts here; it does not mean that we trained a model. Lecture 13's GPU autoresearch example is a separate case study.

<!-- cell -->
## Read a result from the outside in

Start with the independently checked behavior. Then look at the patch, the agent's trace, and its final claim. This ordering helps you avoid accepting a plausible explanation for behavior that never worked.

The frozen primary comparison contains 39 attempts across Projects 01–06, with three repeats per treatment. Nineteen passed. The full archive contains 129 coding attempts, including historical protocols, diagnostics, and dependent loop/graph attempts. Those are different denominators. The selector below lets you inspect both without blending them into a single success rate.

Three repeats on one task do not establish a general advantage for a harness. A failure can still be a strong teaching example: Project 02's services passed while every UI import check timed out. Project 06's reset reached the service layer but left stale state on screen. The point of inspecting evidence is to discover exactly where a claim stops being supported.

**Discuss before reading the cases:** what would you refuse to conclude from a 3/3 versus 3/3 result? What additional task would give a repository rule a real opportunity to matter?

<!-- cell -->
## Instructor completion checklist

- Every learner can open the shared notebook and knows which account pays for any live work.
- Each comparison starts from isolated, identical application bytes with reference solutions excluded.
- A protected checker, separate from the coding agent, evaluates the exported patch.
- Service evidence and actual Electron/Xvfb evidence remain distinct.
- Unfinished work, infrastructure errors, missing usage, and failed application checks have separate labels.
- Human interventions and time are observed or entered by the learner; blank means unmeasured.
- Students submit their own original-course artifacts. The saved Forge case is not their completed assignment.

Use the project worksheets to collect the evidence. Keep unresolved limitations in the conclusion; they are often the most useful part of the class discussion.
