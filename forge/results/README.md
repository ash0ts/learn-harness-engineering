# Forge track delivery and evidence

**Status: implementation is in dependent draft PRs; the live study and hosted notebook publication are incomplete.**

The frozen upstream revision is `a9342ff471f2c0e60be0c08b9f4a7c502df4e442`. The [public personal fork](https://github.com/ash0ts/learn-harness-engineering) preserves the original offline course. Results belong to the private `wandb/learn-harness-engineering-forge` project. No PR has been merged.

## What ran

| Evidence | Actual completion |
| --- | --- |
| Offline application checks | 15/15 app copies pass existing type, build, test and available architecture checks |
| Forge integration tests | 27 pass, including accelerated timer, graph approval/rollback and shared sandbox slots |
| Documentation | VitePress build and English anchor validation pass |
| Canonical notebooks | 9/9 validate and render locally without credentials |
| Qualification | 1/4 marked passed; successful record predates protocol revision 2 |
| Coding trials | 1 attempted; 0 passing, 0 complete comparison blocks |
| Real two-hour exercise | Started, then halted during its first trial; not completed |
| Live graph exercise | Not launched |
| Hosted notebooks | 9 BASIC records created; 0/9 canonical sources uploaded and verified |

The one coding attempt was a timer trial. Its original outcome remains `telemetry_missing`. An audit found that all eight submitted calls returned usage; a ninth attempt was refused locally by the input bound. Its billing estimate was reconciled, but the failed attempt was not relabeled as a successful trial. Later fixes corrected the virtual Pi working directory, excluded macOS tar metadata and counted only submitted inference requests. The latest qualification under the revised protocol timed out with one submitted inference and no returned token usage. That unresolved attempt halted paid launches.

## Budget

Known/audited estimated spend: **$0.029610**. Unresolved reservations: **$2.00**. Original application budget: **$50.00**. These are estimates, not an invoice or guaranteed billing cap.

The unresolved $2 qualification reservation is retained. The provider billing query has returned no course-project rows, including previously observed calls; this cannot be interpreted as zero spend. No paid launch, notebook EDIT session or inference was started after this halt. Creating/renaming BASIC notebook records did not launch notebook compute. Notebook execution pricing remains unset until a runtime resource/rate check can support a reservation.

The ledger and its audit trail are included in `delivery.json`. It must not be reset to resume. Resume only after usage reconciliation or an explicitly recorded user exception, then qualify the frozen protocol again before comparisons.

## Evidence links

- [W&B timer trial](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/ace2d466a1f64998) · [versioned trial artifact](https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/trial-ace2d466-a1f6-4998-bb1c-130618b52651:v0)
- [Agent Lens coding conversation](https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge/conversations/01a1afca-9cab-751c-8d3f-02d983484664)
- [Qualification audit run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/course-audit-20261106) · [qualification evidence and exact source archives](https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/forge-course-qualification-evidence:v0)

Agent Lens was inspected in the authenticated UI. The coding conversation contains nested model and tool activity. Separate application conversations show four turns (import, indexing, two Q&A calls) and twelve spans. Concurrency isolation is implemented with `runIsolated()`; a live concurrent trace qualification is still outstanding. The unsuccessful inference conversation is retained with its error.

## Hosted notebook records

**These links currently open BASIC placeholders, not the canonical course notebooks.** The manifest records their stable IDs, intended source revisions/checksums and original committed BASIC versions. No publication success is claimed.

| Notebook | Remote record | Status |
| --- | --- |
| 00-overview.py | [Forge track: evidence before conclusions](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTM%3D) | created_basic_not_uploaded |
| 01-minimal-harness.py | [01 · Minimal instructions and explicit harnesses](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTQ%3D) | created_basic_not_uploaded |
| 02-workspace-docs.py | [02 · An agent-readable workspace](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTU%3D) | created_basic_not_uploaded |
| 03-session-recovery.py | [03 · Interrupted-session recovery](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTY%3D) | created_basic_not_uploaded |
| 04-runtime-feedback.py | [04 · Runtime evidence and the seeded defect](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTc%3D) | created_basic_not_uploaded |
| 05-role-separation.py | [05 · One feature, three role arrangements](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTg%3D) | created_basic_not_uploaded |
| 06-capstone.py | [06 · Capstone reliability](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTk%3D) | created_basic_not_uploaded |
| 07-bounded-loops.py | [07 · Goal, timer and maker-checker loops](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMjA%3D) | created_basic_not_uploaded |
| 08-state-machine.py | [08 · Checkpointed graphs and human approval](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMjE%3D) | created_basic_not_uploaded |

## Reproduce and resume

From this checkout:

```sh
npm ci --prefix forge
npm run build --prefix forge
npm run check --prefix forge
npm test --prefix forge
python3 forge/scripts/check_apps.py
npm ci
npm run anchors:check
npm run docs:build
npm run forge --prefix forge -- validate-notebooks
python3 forge/scripts/report.py
```

The coordinator uses the existing `forge/local-results/budget.json`. Supply credentials externally. After reconciliation, run `doctor --qualify --execute`, then schedule complete comparison blocks with `compare --repeats 3 --execute`. The loop and graph commands are documented in Projects 07 and 08. An ambiguous pending checkpoint requires review rather than an automatic replay.

For publication, run `uv run --script forge/scripts/publication.py check-remote NOTEBOOK.py` before opening EDIT. Reserve notebook compute from the same ledger, then load canonical source through the authenticated Marimo editor and use its normal save workflow. Run `verify NOTEBOOK.py` afterward. It checks committed `currentVersion`, source SHA-256, fresh rendered output, absence of cell errors and an idle launch control. It will reject the current BASIC placeholders. Reuse manifest IDs; do not create replacements to bypass remote-edit detection.

## Limits of the evidence

- No treatment-effect conclusion is supported: there are no complete comparison blocks and no successful coding trial.
- Offline build/test success is distinct from the protected service and Electron checks. The seeded Project 04 empty-chunk defect is detected; the original sandboxed preload also fails the Electron bridge check. Those exercise gaps remain for the learner/agent to fix.
- Generation settings and model are frozen in `forge/protocol.json`; a changed protocol needs qualification. The model was listed and successfully called during earlier qualification, but the most recent request timed out.
- The actual two-hour timer, live graph retries/rollback/approval, and concurrent trace isolation remain unqualified. Unit tests do not replace those live exercises.
- Hosted notebooks need a mounted shared coordinator checkout for paid reruns. Analysis is self-contained; a hosted runtime without that checkout cannot execute reruns.
- Hosted notebook source commit and rendered output remain unverified. BASIC version checksums intentionally differ from canonical sources.
- Human-intervention time and time saved were not measured. No model training was performed.
