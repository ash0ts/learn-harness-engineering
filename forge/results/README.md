# Forge course delivery and evidence

Status: **verified delivery**. All eight PRs remain drafts; none has been merged.

The [public personal fork](https://github.com/ash0ts/learn-harness-engineering) preserves the offline course at upstream `a9342ff471f2c0e60be0c08b9f4a7c502df4e442`. Results and notebook sources belong to the private `wandb/learn-harness-engineering-forge` project.

## Actual execution

| Evidence | Recorded result |
| --- | --- |
| Existing offline app checks | 15/15 pass |
| Forge integration tests | 36 pass; 0 fail |
| Canonical notebooks | 9/9 render locally without inference credentials |
| Hosted notebook verification | 9/9 |
| Qualification attempts | 2/5 pass |
| Coding attempts | 59 completed; {'task_failed': 58, 'telemetry_missing': 1} |
| Complete comparison blocks | 18 |
| Real two-hour timer | Completed |

A completed comparison block contains every treatment for the same project, repeat and source revision. Completion does not imply a passing patch. The independent checker executes the exported patch in a fresh sandbox and distinguishes service behavior from Xvfb/Electron behavior. Source revisions and protocol hashes remain attached to each attempt.

## Comparison results

| Project | Treatment | Source | Attempts | Pass | Task failure | Infrastructure failure | Missing telemetry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| project-01 | explicit | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-01 | minimal | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-02 | minimal | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-02 | workspace-docs | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-03 | minimal | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-03 | recovery | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-04 | minimal | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-04 | runtime-feedback | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-05 | gen-eval | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-05 | plan-gen-eval | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-05 | single-role | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-06 | capstone | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-06 | minimal | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-07 | goal | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |
| project-07 | maker-checker | `8f4521bc34bb` | 2 | 0 | 2 | 0 | 0 |
| project-07 | timer | `8f4521bc34bb` | 8 | 0 | 8 | 0 | 0 |
| project-07 | timer | `bf760399391f` | 1 | 0 | 0 | 0 | 1 |
| project-08 | graph | `3ebea13e2609` | 3 | 0 | 3 | 0 | 0 |
| project-08 | graph | `8f4521bc34bb` | 3 | 0 | 3 | 0 | 0 |

The complete comparison blocks contain **39 coding attempts**, with **0 end-to-end passes**. If every treatment fails the full criterion, these results do not establish a treatment ranking.

| Main comparison check | Passed | Executed |
| --- | --- | --- |
| Electron window, preload, import, indexing and question UI under Xvfb | 0 | 31 |
| actual indexing keeps every nonempty paragraph | 31 | 31 |
| actual retrieval and Q&A persist two turns | 31 | 31 |
| architecture checker rejects a seeded boundary violation | 5 | 6 |
| extracted metadata | 0 | 4 |
| real import and persistence after reconstruction | 31 | 31 |
| single-document indexing is reflected in status | 3 | 4 |
| strict compile and renderer build | 31 | 39 |

**29/59 attempts** reached the local input-context guard. This is a bounded execution result, not evidence that the task is impossible. Original tool/error traces and unfinished patches remain available.

## Independent check results

| Check | Passed | Executed |
| --- | --- | --- |
| Electron window, preload, import, indexing and question UI under Xvfb | 0 | 42 |
| actual indexing keeps every nonempty paragraph | 39 | 42 |
| actual retrieval and Q&A persist two turns | 39 | 42 |
| architecture checker rejects a seeded boundary violation | 10 | 17 |
| extracted metadata | 0 | 4 |
| real import and persistence after reconstruction | 42 | 42 |
| single-document indexing is reflected in status | 3 | 4 |
| strict compile and renderer build | 42 | 59 |

A check omitted after compilation failed is not counted as an executed service or UI check. Shared failures can mask differences between treatments; the end-to-end outcome remains failed.

## Instrumentation and execution qualification

Agent Lens readback verified **96/96 conversations**, including actual token usage and isolated span parentage. The readback includes **29 error spans**; their errors remain visible rather than being counted as successful calls.

W&B Models readback verified **59/59 runs and committed trial artifacts** against the local configuration, outcomes and usage.

- Concurrent app tracing `concurrency-61ad1e33-0ede-46ff-b513-1a700e9798ce`: passed; 2 isolated conversations.
- Sandbox lifecycle `sandbox-qualification-15043cce-9df6-4cc6-9e66-44b1947ea5e2`: failed; 1 live checks. AssertionError [ERR_ASSERTION]: cancelled process must no longer exist

1 !== 0

- Sandbox lifecycle `sandbox-qualification-eab8e9f7-6d4d-4d1c-8582-5cbf4f41197c`: passed; 5 live checks. 
- Sandbox lifecycle `sandbox-qualification-f566ddc3-297f-4483-98a8-47c6d15a402c`: failed; 0 live checks. CWSandboxValidationError: tags contains invalid value: sandbox-qualification-f566ddc3-297f-4483-98a8-47c6d15a402c-interrupt. tags may contain letters, numbers, '.', '_' or '-', must be 59 characters or fewer, must end with a letter or number, and may start with '.', '_' or '-'

Manual graph qualification candidates validate runner control flow and checker behavior. They are explicitly excluded from Pi trial counts and treatment comparisons.

## Loops and graph states

- `project-07-goal-live.json`: **round_limit**, 3 recorded rounds; 0 entered/observed interventions.
- `project-07-maker-checker-live.json`: **no_progress**, 2 recorded rounds; 0 entered/observed interventions.
- `project-07-real-timer-qualified.json`: **deadline**, 8 recorded rounds; 1 entered/observed interventions.
- `project-07-real-timer.json`: **blocked**, 1 recorded rounds; 0 entered/observed interventions.
- `project-08-control-flow-qualification.json`: **approval**, 2 maker attempts, 6 durable transitions. An approval pause requires an explicit checksum-bound human decision.
- `project-08-graph-diagnostic-feedback.json`: **failed**, 3 maker attempts, 10 durable transitions. An approval pause requires an explicit checksum-bound human decision.
- `project-08-graph-live.json`: **failed**, 3 maker attempts, 10 durable transitions. An approval pause requires an explicit checksum-bound human decision.

## Spend estimates

Known/audited estimate: **$5.563528**. Conservative charges for unknown usage: **$2.000000**. Total charged estimate: **$7.563528**. Active reservations: **$0.000000**.

The original $50 application cap was removed after the user explicitly authorized an unlimited budget. Worker concurrency and lifetimes remain bounded. The timed-out qualification retains unknown token usage; its full $2 reservation was charged conservatively. Estimates are not provider invoices. Notebook EDIT compute is measured separately at the verified 2 CPU / 4 GiB rates ($0.3408/hour), including publication work. The durable ledger records authorizations and reconciliations. It must not be reset.

Budget snapshot as of capturedAt. Final publication/editor costs are recorded separately in the delivery report and W&B audit artifact.

## Draft PRs

- [Forge 1/8: Runtime and Agent Lens tracing](https://github.com/ash0ts/learn-harness-engineering/pull/1)
- [Forge 2/8: Reproducible sandbox execution](https://github.com/ash0ts/learn-harness-engineering/pull/2)
- [Forge 3/8: Opt-in knowledge-base app instrumentation](https://github.com/ash0ts/learn-harness-engineering/pull/3)
- [Forge 4/8: Controlled comparisons for Projects 01–06](https://github.com/ash0ts/learn-harness-engineering/pull/5)
- [Forge 5/8: Executable bounded Project 07 loops](https://github.com/ash0ts/learn-harness-engineering/pull/6)
- [Forge 6/8: Durable Project 08 graphs and approval](https://github.com/ash0ts/learn-harness-engineering/pull/7)
- [Forge 7/8: Nine Marimo notebooks and English learning path](https://github.com/ash0ts/learn-harness-engineering/pull/8)
- [Forge 8/8: Publish and verify the course track](https://github.com/ash0ts/learn-harness-engineering/pull/9)

## Notebooks

| Notebook | Publication status |
| --- | --- |
| [Forge track: evidence before conclusions](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTM%3D) | published_verified |
| [01 · Minimal instructions and explicit harnesses](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTQ%3D) | published_verified |
| [02 · An agent-readable workspace](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTU%3D) | published_verified |
| [03 · Interrupted-session recovery](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTY%3D) | published_verified |
| [04 · Runtime evidence and the seeded defect](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTc%3D) | published_verified |
| [05 · One feature, three role arrangements](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTg%3D) | published_verified |
| [06 · Capstone reliability](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTk%3D) | published_verified |
| [07 · Goal, timer and maker-checker loops](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMjA%3D) | published_verified |
| [08 · Checkpointed graphs and human approval](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMjE%3D) | published_verified |

The publication manifest binds each stable notebook ID to its canonical source commit, SHA-256, committed currentVersion, and rendered-output SHA-256. Verification compares rendered cell source and output code hashes, including when Forge omits its legacy lastStaticOutputAt timestamp. Opening the notebook renders saved evidence; paid reruns require an explicit action.

## Evidence and reproduction

[W&B course audit](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/course-audit-20261106) · [versioned evidence and exact source archives](https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/forge-course-qualification-evidence:v2)

Per-trial W&B runs, artifacts and Agent Lens conversation links are in `snapshot.json` and the notebooks. Original failed attempts are retained alongside later qualification and comparison runs.

```sh
npm ci --prefix forge
npm run check --prefix forge
npm test --prefix forge
python3 forge/scripts/check_apps.py
npm run anchors:check
npm run docs:build
python3 forge/scripts/validate_notebooks.py
python3 forge/scripts/report.py
```

Supply `WANDB_ENTITY`, `WANDB_PROJECT` and credentials externally. Use the existing shared ledger. `doctor --qualify --execute` qualifies the frozen protocol; `compare --repeats 3 --execute` schedules complete blocks. The Project 07 and 08 learning pages document loop, checkpoint and approval commands.

Notebook publication uses the normal authenticated Forge EDIT/Marimo file editor and save workflow. Reserve compute using `forge/scripts/notebook_session.ts`, check for remote edits with `publication.py check-remote`, load canonical source, run saved-analysis cells, then verify committed source and rendered output with `publication.py verify`. Terminate and account for every editing session.

## Limits

- These are repeated runs of one frozen task per project, not a broad benchmark. Three repeats do not establish general treatment effects.
- A task failure is evidence about this bounded attempt. Passing offline checks is not substituted for Electron or held-out service evidence.
- The frozen comparison study and two-hour exercise use their recorded runner revision. Later cancellation and retry-diagnostic fixes are qualified separately; historical attempts are not rewritten or rescored.
- Original early failures and audited accounting corrections are preserved. Missing usage is never reported as zero usage.
- Hosted saved analysis is self-contained. Paid reruns require the configured shared coordinator checkout with Node, pinned dependencies, external credentials, qualification and the existing durable ledger; a fresh hosted runtime has no mounted coordinator by default.
- The two-hour timer status above comes from its actual wall-clock checkpoint. Accelerated tests are reported separately.
- Graph retries and rollback may end in failure. Human approval is never inferred from a test or automatically supplied by the agent.
- No human time savings were inferred, no model training was performed, and only sample course data was used.
