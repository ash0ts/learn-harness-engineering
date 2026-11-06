# Learn harness engineering with Forge

This optional track runs the eight projects as reproducible experiments. Pi edits the application inside a fresh CoreWeave Sandbox. A second sandbox grades its exported patch against real services and Electron under Xvfb. Agent Lens records the coding agent and knowledge-base app as separate conversations; W&B Models stores configurations, metrics and evidence artifacts.

The original exercises still work offline. Their mock defaults, starter gaps and lecture skeletons remain learning material. The Forge track does not use simulated benchmark scores as experimental evidence.

## Learning path

| Project | Controlled question | Canonical notebook | Forge notebook |
| --- | --- | --- | --- |
| Overview | What counts as evidence, and what remains unknown? | [00 · Overview](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-notebooks/forge/notebooks/00-overview.py) | [Open in Forge](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTM%3D) |
| 01 | Do explicit repository rules help this unfinished app? | [01 · Minimal harness](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-notebooks/forge/notebooks/01-minimal-harness.py) | [Open in Forge](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTQ%3D) |
| 02 | Can a fresh agent use workspace documentation? | [02 · Workspace docs](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-notebooks/forge/notebooks/02-workspace-docs.py) | [Open in Forge](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTU%3D) |
| 03 | Can another session recover from files and a patch? | [03 · Session recovery](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-notebooks/forge/notebooks/03-session-recovery.py) | [Open in Forge](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTY%3D) |
| 04 | Does runtime feedback expose the seeded indexing defect? | [04 · Runtime feedback](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-notebooks/forge/notebooks/04-runtime-feedback.py) | [Open in Forge](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTc%3D) |
| 05 | Does role separation improve the same history feature? | [05 · Role separation](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-notebooks/forge/notebooks/05-role-separation.py) | [Open in Forge](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTg%3D) |
| 06 | Does the complete harness improve verified behavior? | [06 · Capstone](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-notebooks/forge/notebooks/06-capstone.py) | [Open in Forge](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTk%3D) |
| 07 | When should a durable loop continue or stop? | [07 · Bounded loops](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-notebooks/forge/notebooks/07-bounded-loops.py) | [Open in Forge](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMjA%3D) |
| 08 | How do retries, rollback and human approval compose? | [08 · State machine](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-notebooks/forge/notebooks/08-state-machine.py) | [Open in Forge](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMjE%3D) |

Start with the overview, then follow project order. Each notebook explains the experiment, displays a saved evidence snapshot, exposes configuration, and can invoke a bounded rerun through the shared TypeScript coordinator. Opening a notebook never starts an inference or coding trial. Hosted notebook runtime itself may incur compute charges.

## Local setup

From the course checkout, install Node 22.19+, Python 3.11+ and `uv`, then run:

```sh
npm ci --prefix forge
npm run build --prefix forge
npm run forge --prefix forge -- doctor
npm run check --prefix forge
npm test --prefix forge
npm run forge --prefix forge -- validate-notebooks
```

For live work, supply `WANDB_API_KEY` externally and set `WANDB_ENTITY` to a writable team. `WANDB_PROJECT` defaults to `learn-harness-engineering-forge`; create it privately. This delivery uses the `wandb` team. Use sample course data only. The renderer receives neither credentials nor SDK clients.

```sh
export WANDB_ENTITY=wandb
export WANDB_PROJECT=learn-harness-engineering-forge
npm run forge --prefix forge -- doctor --qualify --execute
npm run forge --prefix forge -- compare --project project-01 --repeats 3
# Inspect the plan and reservations before this explicit paid action:
npm run forge --prefix forge -- compare --project project-01 --repeats 3 --execute
```

The pinned provider is Forge's OpenAI-compatible endpoint with `Qwen/Qwen3.6-35B-A3B`. Qualification checks model availability, sandbox execution/cancellation, Pi tool use and live app inference. Provider unavailability stops the campaign; it never substitutes mock answers or another provider. Protocol revisions require another successful qualification.

## Read the evidence

Open the private [qualified comparison dashboard](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=dfs83wdpatt),
[archived revision 4 comparison dashboard](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=wz8re0rb108),
[historical revision 3 dashboard](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=ssij233dnka),
[original revision 2 dashboard](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=tsgaokxuthw),
and [execution/publication audit](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=l9e45ofb461).
The [evidence report](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/reports/Forge-harness-course-%E2%80%94-verified-execution-and-comparison-evidence--VmlldzoxODI2MzgyOA==)
shows exact denominators and links every treatment to original trials and artifacts.
Dashboard aggregate runs are derived views, not additional coding attempts.

Revision 3 bundles each learner preload for Electron's sandboxed module loader,
bounds actor-visible tool output, and expands the frozen input payload limit.
The original offline starters retain their intended gaps. These revisions are
separate cohorts; differences between them cannot isolate any one harness change.

Revision 4 corrects asynchronous UI polling and requires the actual answer text to
appear before capturing evidence. Revision 2 and 3 native grades remain recorded,
but their UI waits do not establish visible-answer acceptance. The report separates
those historical grades from revision 4 and from supplemental patch qualifications.

The initial revision 4 Project 05 citation selector clicked answer prose, and Project 06
left its feedback IPC arguments unspecified. Those two source/project cohorts are
excluded from qualified comparisons while their native grades remain archived.
The follow-up freezes interactive citation controls, native/custom confirmation tests,
and an explicit feedback payload shared by both capstone treatments. The primary
dashboard selects the latest qualified complete blocks per project; the source revision
remains visible. See `forge/measurement-notes.json` for the exclusions.

Protected app checks execute actual services with deterministic course Q&A defaults.
Live Forge app inference is qualified separately. These checks do not measure production
answer quality.

Trials start from frozen, identical unfinished application code with only the selected harness files. Reference solutions and historical scores are excluded. Repeats rotate treatment order. Protected graders run after the coding sandbox terminates, in a fresh workspace with the original baseline plus the exported patch. Service success does not establish UI success: Electron runs under Xvfb and gets its own checks.

Report task failures, infrastructure failures, missing telemetry and budget exhaustion separately. The target is three repeats per automated variant; incomplete blocks do not establish treatment differences. Human interventions must be observed or entered by a learner. The track makes no inferred time-saved claim and trains no models.

Pi uses its documented Weave tracing extension; application hooks use the Forge SDK in a separate process, with isolated concurrent contexts and shutdown flushes. Follow [course conversations in Agent Lens](https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge/conversations) and [course runs in W&B](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge). Access requires project membership.

## Budget and recovery

The default application budget is $50 including inference, sandboxes and notebook execution. It reserves estimated in-flight costs before paid launches, defaults to CPU-only sandboxes and two trial workers, and collects patches/logs/checkpoints before teardown. Unknown pricing, missing usage or uncertain cleanup halts new paid work. This is a conservative application control, not a guaranteed provider billing cap.

This delivery records a later explicit unlimited-budget authorization in its ledger. `FORGE_BUDGET_USD=unlimited` must match that recorded authorization; accounting and worker bounds still apply.

Keep the shared `forge/local-results/budget.json` ledger across launches. Do not delete it to bypass a halt. Reconcile an uncertain attempt only from billing evidence or an explicit audited user decision. Timer exercises checkpoint between sessions and release idle sandboxes; the real exercise lasts two hours. Accelerated tests are separate evidence. Graphs pause at approval and need an explicit checksum-bound approve/reject decision before resuming.

## Notebooks and publication

Canonical Marimo sources live in `forge/notebooks/` with pinned Python dependencies and runner provenance. To view one locally:

```sh
uv run --with marimo==0.25.1 marimo edit forge/notebooks/00-overview.py
```

The analysis view is self-contained. Paid reruns require a mounted coordinator checkout at the displayed runner revision, Node dependencies, external credentials and the existing budget ledger. A hosted analysis notebook without that coordinator cannot launch reruns. The Python cells call the shared runner; they do not reimplement the app.

Publication creates a BASIC notebook in the private project, renames it, opens an authenticated EDIT session and loads the canonical source through the Marimo editor. The normal save workflow commits source. A notebook is only marked published after its committed `currentVersion`, source checksum and rendered output are verified. Reuse recorded notebook IDs and detect remote edits before replacing source. Consult the repository publication manifest and results report for actual completion status; the manifest records verification separately from the stable source and hosted links above.
