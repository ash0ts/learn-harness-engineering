# Five hands-on Forge labs

Students edit the app, its harness and its instrumentation. The notebook runs those saved files, shows their build and test output, then displays screenshots and traces from that execution. There is no separate service to deploy.

Start from the [workshop overview](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTM%3D). For a three-hour class, use **01, 02 and 04**. Offer **03 and 05** as extensions. Each lesson supplies its own documented checkpoint of the same knowledge-base app; completing Project 01 is not a prerequisite for Project 02.

## Before class

Each participant needs a Forge account, a writable **private** project, and their own W&B API key with sandbox access. Arrange project access before the workshop. Being able to view an instructor notebook does not establish sandbox entitlement. Results in the course's private project require view permission; a participant's new results are saved to their copy's destination.

The notebook copy defaults to a **$20 estimated limit**. Each copy has a separate ledger. This is not an overall classroom budget or a guaranteed billing cap. Notebook CPU time, sandbox CPU time and model usage count toward the estimate. A CPU-only app check in a sandbox still costs money; the deterministic **Check my edits** action launches no sandbox or inference. Unknown usage or unverified cleanup blocks further paid actions until recovered.

## Run a lesson in Forge

1. Open the selected lesson from the overview. Choose **⋯ → Copy to project**, then select your writable private project. Return to the same copy later.
2. In Edit, click **▶** to run the notebook cells. This displays the saved lesson, file editors and controls without starting an agent or inference call.
3. Open **Prepare the notebook workspace** and click **Prepare or restore my workspace**. Leave the limit at the value you used previously.
4. Open the file tabs under **Inspect and edit your implementation**. Change the `TODO(workshop)` gaps. The files outside this list are supplied prerequisites. Hints are separate; revealing the worked example marks subsequent snapshots as assisted.
5. Click **Save these edits**, then **Check my edits (no inference)**. Read the named failures and build output. Fix one problem and repeat. The saved diff is under **My work**.
6. Click **Connect my sandbox access**. Enter your own API key into the masked prompt in Edit. It stays in the session's process configuration; do not paste it into a code cell or source file.
7. Choose a **Lesson action**, fixture and app scenario. Confirm the paid action, then click **Execute my saved snapshot**. Unsaved editor changes cannot silently become the executed code.
8. Open that execution under **My work**. Compare its screenshots, actual chunks and answers, tool commands, review, source diff, Agent Lens conversations and W&B run. Each result names its snapshot. Editing again makes older results visibly stale.
9. Record what changed, what you observed and what remains unexplained. **Save my notes and progress** commits the checkpoint to your private project. Keep the tab open until work and publication finish.

Prepare and Connect inspect interrupted work; they do not automatically launch another agent. Do not make a new copy merely to clear an error or reset spending. Cancellation waits for resource cleanup. If publication failed after grading, recover the upload rather than rerunning the coding agent.

## What each lab teaches

| Lab | Work you do | Evidence to explain |
| --- | --- | --- |
| 01 | Complete the typed Import bridge and the Forge request, then change its instructions | A button-driven import, supported and unsupported questions, actual request/response, usage and persisted answers |
| 02 | Write `AGENTS.md`, architecture guidance and acceptance criteria; complete `sandbox.commands.run` | Staged-file hashes, the SDK command's output, what Pi read, and whether its document-detail patch works |
| 03 | Implement metadata, record its check and write a handoff | A saved first-session candidate, a genuinely fresh second conversation, its file reads and preservation of the earlier feature |
| 04 | Add Forge SDK spans and chunk statistics; repair the indexing defect | Short and long fixtures, nonempty chunks, student-authored tool spans, parent relationships and actual UI output |
| 05 | Edit maker/checker prompts and a rubric; calculate and log an evaluation | An actual checker review, separate role conversations, the maker's revision, full history and your `student/` W&B metrics |

Project 03's first agent action ends after its bounded session. Preview its candidate from **My work**, apply the files, then **Load my saved files**. Write your handoff from the observed patch and failures, save it, and choose **Resume in a fresh session**. The runner verifies that its parent belongs to a recorded first session.

Project 05 gives the maker 10 calls, checker 4, and maker revision 10. The final call in each allowance is reserved for its deliverable. A missing review stays missing. The optional single-role comparison gets the same 24 calls. Your Python evaluation executes against the recorded checks; its `run.log` call is captured and published to the stable W&B run. Protected acceptance checks remain separate from your evaluation.

App instrumentation runs in the Electron main/service process. The supplied runtime owns the Forge SDK's conversation, turn, isolation and shutdown lifecycle; your `observe` function creates and ends its tool spans inside that context. Pi uses its separate Weave tracing process. Model training and student-managed GPUs are outside these labs: sandboxes are CPU-only and inference uses Forge's hosted endpoint.

## Use Electron on your laptop

Install Git and Node **22.19 or newer**. Use native Windows PowerShell or Terminal on macOS/Linux. The commands below work in all three; an Electron display server is required on Linux.

```sh
git clone https://github.com/ash0ts/learn-harness-engineering.git
cd learn-harness-engineering
git checkout forge-workshop-v1.0.0
npm ci --prefix forge
npm ci --prefix forge/workshop/base
node --import ./forge/node_modules/tsx/dist/loader.mjs forge/src/cli.ts workshop init --project project-01 --workspace ../my-forge-01
cd ../my-forge-01
npm ci
npm run dev
```

Use `project-02`, `project-03`, `project-04` or `project-05` and a separate directory to initialize another lesson. The immutable workshop tag identifies the course version; `workshop.json` records the exact base and editable file list. Do not edit that manifest or the protected runner.

The window title labels the default **offline fixture answers** mode. Import `fixtures/short.txt` or `fixtures/long.txt` using the native file picker. Select the document, index it, ask a question, and inspect History. Each workspace has its own `.workshop-data` directory.

```sh
npm run check
npm run build
npm test
```

The unfinished lesson should fail its intended checks. Do not treat that failure as an installation problem. When ready for live app inference, supply `WANDB_ENTITY`, `WANDB_PROJECT`, and `WANDB_API_KEY` through your process environment, then run `npm run dev -- --live`. Keep the key out of source, shell scripts and notebooks. The main/service process handles it; the renderer has no SDK or credential access.

The same shared CLI supports `workshop check`, `scenario`, `agent` and `resume`. Paid CLI actions require `--execute`; live app inference additionally requires `--live`. Set `FORGE_BUDGET_USD=20` for student work and keep the evidence directory when returning. Python 3.11+ and `uv` are needed for private W&B publication; the scripts pin `wandb==0.31.0`.

## Move source between notebook and laptop

In a prepared notebook, save your draft and use **Download my editable workspace**. The JSON package contains source, fixtures, lockfile, provenance, notes and evidence references. It excludes dependencies and credentials. The original notebook's spending ledger stays with its copy.

From the course checkout, initialize the same project and revision, preview the upload, then apply it:

```sh
node --import ./forge/node_modules/tsx/dist/loader.mjs forge/src/cli.ts workshop import --workspace ../my-forge-01 --input ../workshop-workspace.json
node --import ./forge/node_modules/tsx/dist/loader.mjs forge/src/cli.ts workshop import --workspace ../my-forge-01 --input ../workshop-workspace.json --apply
```

An incompatible base is rejected. Keep the pinned checkout that created the notebook copy; do not silently migrate old snapshots to a newer tag.

To return laptop edits, export from the course checkout:

```sh
node --import ./forge/node_modules/tsx/dist/loader.mjs forge/src/cli.ts workshop export --workspace ../my-forge-01 --input ../my-edited-workspace.json
```

Upload that JSON through the notebook's native file upload. Click **Preview uploaded source diff**, inspect it, then **Apply the previewed files**. **Load my saved files** refreshes the editors and replaces unsaved text. Save and check before executing. The import validates paths, file hashes, editable files and base revision. It cannot overwrite runner or accounting files.

Every published execution also stores `submission.json` and `candidate.json` in its private W&B artifact. These provide an authenticated source-retrieval path when a browser download is unavailable; the publication report records which transfer paths were actually verified.

## Three-hour teaching schedule

| Time | Activity |
| --- | --- |
| 0:00–0:20 | Introduction, setup and first app inspection |
| 0:20–1:00 | Project 01 |
| 1:00–1:35 | Project 02; faster participants begin Project 03 |
| 1:35–1:45 | Break and save progress |
| 1:45–2:30 | Project 04; faster participants continue to Project 05 |
| 2:30–2:45 | Instructor demonstrations and discussion of Projects 03 and 05 |
| 2:45–3:00 | Explain one edit, its observed effect and its evidence |

Ask each student to show a source diff and its matching evidence. A green dashboard alone does not demonstrate understanding. A failed attempt can demonstrate useful diagnosis when the student can explain the request, tool activity, app behavior and next check.

The historical lesson narratives and research denominators are unchanged. New executions use `workshop-v1`. Platform-specific validation, notebook publication versions, browser download verification and the still-unverified independent student-account rehearsal are reported separately in the workshop release evidence.
