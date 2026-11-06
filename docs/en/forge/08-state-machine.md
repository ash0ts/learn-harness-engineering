# Binding human approval to the patch we tested

The Pi-generated patch passed on its third attempt. The protected grade passed, and separate service and Electron verification lanes passed. The graph then stopped at `approval`. It did not merge the patch or treat the passing tests as a human decision.

Later, the user approved a manual qualification candidate with a different checksum. We recorded that decision against the original qualification checkpoint and moved that checkpoint to `done`. The Pi candidate stayed paused.

Project 08 preserves the patch identity alongside the checks and human decision. A delayed response can then be matched to the candidate the person reviewed, even after another candidate has been produced.

## Name the transitions before automating them

The course uses an explicit TypeScript state machine. The planning step records the frozen task. The maker runs Pi and exports a candidate. Verification runs the checks. A failing candidate is discarded through rollback; a passing candidate reaches the human gate.

| State | Work recorded | Next state |
| --- | --- | --- |
| `plan` | Frozen task acceptance criteria | `make` |
| `make` | Candidate patch, checksum, trial, protected grade | `verify`, or `failed` at the attempt limit |
| `verify` | Independent service and Electron results | `approval` when required results pass; otherwise `rollback` |
| `rollback` | Discarded candidate and restored starting point | `make`, or `failed` when attempts are exhausted |
| `approval` | Candidate awaiting an explicit checksum-bound decision | `done` or `rejected` |

The production runner requires a passing protected grade as well as the independent verification lanes before it reaches approval. The service lane and Electron lane run in parallel in their own fresh sandboxes. We reserve their estimated costs together before starting them.

The graph writes its state at transitions and marks a pending operation before performing work. An interrupted pending operation must be reconciled before resume. Writing a checkpoint does not make a remote action transactional; it gives the operator a durable record of which action may be incomplete.

LangGraph's [persistence documentation](https://docs.langchain.com/oss/javascript/langgraph/persistence) and [interrupt documentation](https://docs.langchain.com/oss/javascript/langgraph/interrupts) describe persisted graph state and pauses awaiting external input. Our small TypeScript implementation tackles those responsibilities directly; it does not use LangGraph or inherit its execution guarantees.

## The first two candidates failed for different reasons

The first candidate in the explicit-contract Pi run compiled and passed the recorded import, indexing, Q&A, and Electron checks. It failed the architecture probe: its guard accepted a prohibited Node import in the renderer. The graph recorded the grade, ran its verification stage, and rolled back.

The second candidate failed TypeScript compilation. The graph again recorded failure and rolled back.

On the third attempt, the candidate passed the protected checks and both independent lanes. That candidate has checksum beginning `c74cf9cf3716`; the full value is retained with the patch. The graph reached `approval` after nine recorded transitions and three maker attempts.

Rollback here means the next maker starts from the last verified patch, or the frozen baseline if there is no verified predecessor. The failed patch remains an immutable evidence artifact. Its edits do not stay in the next working tree merely because they were the latest edits made.

The next attempt also receives recorded verification feedback. This lets a maker reconsider the specific failure while working from the restored source. It does not guarantee that the next patch will preserve every correct change from the discarded candidate. The compilation failure on attempt two is a reminder to inspect each result independently.

## A test cannot require a path the task never named

An earlier graph run had a task-contract problem. The task required an architecture guard without naming the script path the protected checker expected. A candidate implemented a Vite-based guard and failed the script-path requirement. The diagnostic feedback also omitted the expected path.

We retained that run as contract-discovery evidence and made `scripts/check-architecture.sh` explicit in the task for the new run. Its three attempts are a separate frozen execution. The final passing patch should not be described as the third attempt of an uninterrupted sequence that quietly changed the task midway through.

The same issue appeared with the feedback API in Project 06. In both cases, the grader knew something the agent's task did not say. That is a measurement defect to repair, not an occasion to praise the grader for being strict.

## Approval binds the decision to bytes

The approval command loads the waiting checkpoint, reads the candidate patch, and computes its SHA-256 checksum. It requires that checksum to match both the recorded candidate and the checksum supplied with the decision. If the file changed after review, the command refuses the transition.

The recorded decision includes approve or reject, the actor, the candidate checksum, and the time. Those fields let a reviewer ask what was approved after the conversation has moved on. They also prevent a delayed approval for an earlier candidate from being applied to a different patch by accident.

The course CLI is not a complete multiuser authorization service. It records the supplied actor and decision after the user explicitly authorizes it in this workflow. A deployed approval service would also need authenticated identity, access control, and a policy for who can decide. A checksum identifies content; it does not identify a person.

## Two candidates, two records

We also ran a deterministic manual control-flow qualification. It first exercised the broken baseline, then used a known repair to check that rollback and verification could lead to an approval pause. This validates the runner's control flow. It is excluded from Pi coding-trial counts.

The user's later approval named that manual candidate, whose checksum begins `91c4a2df7b9a`. We verified that the original checkpoint still referenced those bytes and recorded the decision. Its service and Xvfb/Electron lanes had passed. That original qualification predates the additional full protected-grade qualification, so the approval does not add a missing historical check.

| Candidate | Recorded state after the user's decision | Meaning |
| --- | --- | --- |
| Original manual qualification, `91c4a2df7b9a…` | `done` | The named qualification candidate was approved |
| Pi attempt three, `c74cf9cf3716…` | `approval` | The tested Pi patch still awaits its own decision |
| Later manual qualifications | `approval` | Their checkpoint decisions were not changed |

The [public approval receipt](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/forge/results/qualification-approval.json) records the exact checksum and checkpoint. The [saved Project 08 notebook](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMjE%3D) is a pre-decision analysis snapshot; the [operations dashboard](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=l9e45ofb461) includes the later manual approval. Both Forge views require private-project access.

## Review one transition at a time

For this exercise, follow the passing Pi candidate from its exported patch to the protected grade, through both verification lanes, and into the waiting checkpoint. Check that every record refers to the same candidate. Then compare it with the manual approval receipt and confirm that the checksums differ.

The graph has completed the automated work required to ask for a decision. The next step for that Pi candidate is still a person's approve or reject response. No PR has been merged, and nothing about the passing tests changes who owns that decision.

Return to the [series overview](./index.md) or use the [runner guide](./running.md) to inspect the saved state locally before attempting a resume.
