# Eight hands-on labs: release candidate

The overview and Projects 01–08 now use a guided workshop flow: predict a change, edit real files, check the saved source, execute an explicit activity, and explain its evidence. The immutable local runner candidate is `forge-workshop-v1.1.0-rc.1`, commit `72736fc171adf6f50fdd4a99f48a6f4ff576769a`.

**This candidate has not been republished to Forge.** The existing nine notebook IDs still serve the preceding release. Live rehearsal stopped when Sandbox creation failed and its read-back lookup returned `access denied`. The owner deferred that access issue. The failed attempt and its unresolved $0.142 reservation remain recorded; no replacement attempt or notebook runtime was launched.

## What changed

All eight labs have named activities, native file editors, a combined **Save and check my edits** action, visible draft/snapshot state, a next-step message, supplied-source inspection and a concrete Forge evidence question. Candidate selection uses saved executions rather than requiring learners to copy an execution ID. Historical material follows the practical exercise.

| Lab | Technical work | Evidence learners must explain |
| --- | --- | --- |
| 01 | Typed Import IPC, bounded Forge request, answer instructions | Button/file-picker behavior, excerpts, answers, usage and restart persistence |
| 02 | Workspace guidance, acceptance criteria, Sandbox SDK command | Staged file hashes, command output, Pi's actual reads and document-detail behavior |
| 03 | Metadata, verification entry, honest handoff | Separate sessions, the resumed session's reads, candidate ancestry and preserved work |
| 04 | Forge tool spans, chunk statistics, narrow indexing repair | Nonempty stored text, student-authored spans, errors and matching UI output |
| 05 | Maker/checker prompts, review rubric, evaluation and logging | Actual review, subsequent patch, separate conversations and W&B metrics |
| 06 | Feedback persistence, real service benchmark, React reset state | Feedback after restart, measured service results, disappearance of stale UI/history |
| 07 | Stop policy and next-session feedback | Fixed deadline, actual failed checks, candidate/feedback hashes and observed stop |
| 08 | Routes, repair plan, serial/parallel verification policy | Lane hashes/timing, retained failures, rollback and explicit checksum-bound decision |

Projects 06–08 now have independent unfinished checkpoints. Project 07 runs at most two explicit 12-call rounds within a durable 30-minute window; the historical two-hour exercise remains separate. Project 08 verifies before repair or approval, caps repairs/nodes, preserves failed candidates, and never approves itself. Both keep student policy separate from protected accounting and lifecycle controls.

## Qualification completed

- **81 TypeScript tests passed**, including all eight unfinished checkpoints failing their intended checks, eight completed examples passing, and eight targeted regressions failing.
- **53 Python tests passed**, covering coordinator, recovery, workbench and guidance behavior.
- All **nine canonical saved views** rendered without credentials, inference or sandbox launches. The documentation build passed.
- The preservation audit retained **544 historical files**, all nine historical evidence payloads and narrative order. Existing research denominators were not rewritten.
- Browser-driven native Marimo checks exercised prepare, baseline failure, actual file edits and passing checks in **all eight labs**. The overview's three route choices rendered distinct guidance. Unconfirmed paid actions in Projects 07–08 were refused before launch.
- These browser checks used a private local adapter for preparation/persistence, real shared CLI checks, and disabled paid dispatch. They are assisted qualification cases, **not live Forge or independent-student evidence**.
- Actual macOS Electron verification rejected the Project 06 baseline and passed the reference repair, including feedback, visible reset and restart. Project 08's identical reference patch passed serial and parallel service/Electron lanes; their receipts show real overlap in parallel mode. OS dialog selection was automated; this does not qualify native picker interaction on Windows.

The browser receipts and validation source checksums are in [status.json](./status.json). Full source snapshots, logs and screenshots remain in the private local qualification directory, `forge/local-results/workshop-v1.1/`.

## Live attempt and accounting

The new cohort has **one infrastructure failure, zero completed application rehearsals and zero recorded model calls**. Its [W&B run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/f0f01ef8130aecd6118e) and versioned artifact retain the unsuccessful attempt. Neither a sandbox identity nor terminal receipt was obtained, so resource cost is unknown and the **$0.142 reservation remains outstanding**. Do not interpret missing usage as zero.

The shared rollout ledger has **$5.926200092 in settled estimates from preceding work**, plus that new unresolved reservation. The separate historical $2 reservation remains unchanged. These are application estimates, not billing guarantees. The prior release dashboard and its denominators are unchanged; there is no successful v1.1 live dashboard to present.

## Teaching and rollout

Use the [student/instructor guide](../../../docs/en/forge/workshop.md) for the intended workflow. The three-hour core remains 01, 02 and 04; 03 and 05 are extensions. A follow-up can use 06, 07 and 08 for reliability, feedback and control flow. The local candidate uses the same source/checks as the notebooks and requires no separate deployed service.

Before calling this version classroom-ready, restore Sandbox access, reconcile the retained failed launch using supporting evidence, rehearse the new activities in fresh private Forge copies, and republish all nine existing IDs through the native editor. Verify committed source and rendered output after saving. Preserve the current published notebooks until those gates pass. See [HANDOFF.md](./HANDOFF.md).

Independent student-account rehearsal, actual browser-download verification, and new macOS/Windows/Linux parity qualification remain separate unmet gates. Existing five-lab platform evidence is historical. Sandboxes use CPUs and hosted Forge inference; these labs do not teach GPU provisioning or model training.
