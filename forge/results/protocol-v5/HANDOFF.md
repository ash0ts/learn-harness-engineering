# Resume the protocol 5 repair rollout

The code is in the existing eight draft branches of `ash0ts/learn-harness-engineering`; `codex/forge-publication` contains the complete stack. No PR is merged. The nine candidate notebooks pin runner `dcf7e447f565961e790ed1f4a25815b278db124e`, retained by tag `forge-course-runner-v5-recovery-dcf7e447`. They have **not** replaced the hosted notebooks. Use [the status report](README.md), [machine-readable counts](status.json), and [dashboard receipt](dashboard.json) for current evidence.

## Blocking evidence

- Evidence root: `forge/local-results/protocol-v5` (ignored, private). Keep this directory independently of checkout changes.
- Operation: `qualification-b9c2070d-c685-41e6-8734-baac3fee02bb`, source `bed84c0dd83e64e9c2be0ee982572174ba30eda2`.
- First request: 396 input / 61 output tokens. Second request: timed out, usage unknown. A trace showing zero does not establish zero billed usage.
- Sandbox `597700c7-e972-4fba-a436-dbf24d57ce35` was verified terminated; lifetime bound 209.785 seconds. No worker is intentionally left running.
- Preserve the full $2 reservation. Billing read-back returned HTTP 403; Agent Lens read-back did not resolve the second request. Uncapped authorization does not remove this accounting gate.

Use the existing credentials through the approved local mechanism, never notebook source or chat. Obtain an authoritative usage receipt, then follow [the recovery and reconciliation contract](../../RECOVERY.md). Recovery must not launch another agent. Do not delete the ledger, alter the failed outcome, clear reservations manually, or substitute a cost estimate for missing usage.

## Remaining execution

1. Review the operation and settle only from verified request/cleanup receipts. Reproduce the original full Pi lingering-worker failure; the two SDK-only clean exits are not that reproduction.
2. Freeze the final checkout using `python3 forge/scripts/protocol5.py freeze --schedule forge/local-results/protocol-v5/schedule.json`. Preserve the generated IDs. `commands` prints the schedule without executing it. Qualification and all 24 baseline/reference/regression controls must pass before scored runs.
3. Run the separate cohort through `run --execute`, using the same output/ledger. Targets: 39 P01–06 attempts; nine loop controllers including three actual 7,200-second timers; three graphs; three serial/parallel pairs on one qualified patch. The scheduler stops on interrupted work or unknown accounting. Resume a timer explicitly with its original checkpoint and deadline; never replay an interrupted scheduled step blindly.
4. Request two new human decisions only after presenting actual verified candidates and checksums. Earlier approvals cannot be reused. Preserve every failed candidate and observed missing handoff/review.
5. Perform the owner-account rehearsal, then actual native-download checks in authenticated Forge Edit and Preview. Inspect archive bytes and restore into a fresh runtime, verifying notes, costs, trials and disconnected sandbox credentials. The user said only the owner can test; an independent student-account rehearsal remains unverified.
6. Compare remote source/version against `forge/publication-manifest.json` before replacing anything. Publish the nine candidate files to the same IDs through the native Marimo editor, with normal save. Do not use HTML import or claim publication from local render alone. Verify committed source checksum, currentVersion and rendered output before changing the publication manifest.

Keep the original 129-attempt archive and 39-attempt comparison unchanged. `repair_report.py` builds the separate status projection; `protocol5_dashboard.py --execute` uploads its private audit artifact and verifies every evidence file after read-back. Neither launches compute. Historical dashboards and the new protocol-5 dashboard have separate denominators.

## Local validation already completed

61 TypeScript tests, 47 Python learner/publication/scheduler/artifact tests, six additional publication guards, all 15 offline app suites, documentation build, anchor checks and all nine credential-free saved views pass. The presentation comparison preserves cell/heading order, labels, images and historical results; [the explicit factual edits](presentation.json) are the only lesson-language changes. These checks do not establish live classroom readiness.
