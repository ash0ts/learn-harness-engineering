# Owner rehearsal and notebook rollout — 10 November 2026

The repaired student runner completed one live Project 01 attempt, saved its failed grade, and recovered publication without rerunning Pi. **All nine final notebook revisions are published and verified.** Native-editor saves were read back against canonical source, rendered cell code, saved aggregates, and idle run controls. The temporary browser-access failure cleared after sign-in; no permissions were widened.

[Share the overview](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTM%3D). It links to all eight lessons. Students need view access to the private course project, then copy a lesson into their own writable private project and use its existing controls. See [the classroom guide](../../../docs/en/forge/classroom.md). Native browser downloads and an independent student-account rehearsal remain unverified.

This is a rollout qualification, separate from the original 129-attempt archive, the historical 39-attempt comparison, and the planned protocol-five comparison campaign. See [the machine-readable receipt](status.json) and [private dashboard receipt](dashboard.json) for exact revisions, hashes, counts, checks, costs, and links.

## What ran

| Check | Observed result |
| --- | --- |
| Latest live inference qualification | Passed; actual token usage recorded |
| Project 01 baseline, reference repair, targeted regression | All three controls qualified: unfinished baseline and regression failed acceptance; protected repair passed |
| Student Pi attempt | One attempt, 24 dispatched model requests, 313,467 input and 3,384 output tokens |
| Independent grading | Four service/build checks passed; real Electron/Xvfb UI check timed out; task failed |
| Worker exit | Clean exit, no remaining active resources; actor and grader sandboxes terminal |
| Publication recovery | Same run and artifact read back; no replacement coding run |
| Agent Lens | Usage matched exactly across model spans; one additional local budget-rejection error span |
| Checkpoint | 353 file checksums verified; notes, three retained trials and spending restored into a fresh local workspace; credentials disconnected |
| Native browser download | Still unverified in Edit and Preview; SDK checkpoint retrieval does not count |
| Final notebook publication | 9/9 match final candidate source and rendered output |
| Independent student-account rehearsal | Unavailable; owner-account testing only |

[Open the live attempt](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/7d85a6fa3bb84a4a) or its [Agent Lens conversation](https://forge.coreweave.com/agent-lens/wandb/learn-harness-engineering-forge/conversations/01a1c6b0-1706-7113-80c9-9be9290bb83d). Both require access to the private course project. The failed UI check remains a failure; successful execution and upload do not imply that the agent repaired the application correctly.

The trace contains 25 `chat` spans: 24 dispatched requests and one `Model-call budget exhausted` error. The provider-boundary guard rejects the latter before dispatch. Its zero usage is supported by the guard and the 24 durable request settlements, rather than inferred from a zero-valued trace alone. Parent-turn usage is excluded from totals.

## Repairs exercised

The rollout reproduced two lifecycle problems: zombie descendants were counted as live processes, and a sandbox SDK connection probe kept an outer worker alive. The runner now distinguishes exited processes, records child cleanup, selects the gateway data plane, disposes sessions and tracing, and bounds finalization. The earlier forced shutdown remains recorded as a recovery event. The later full Pi attempt exited cleanly.

An overlong sandbox tag was rejected locally by the pinned SDK before transport. A zero-dispatch reproduction supported explicit reconciliation; the failed operation remains in history. The final gateway run then completed all three protected controls.

Publication initially failed because an absent artifact collection returned an error from the named lookup. The repaired exact-name collection query supports absence without suppressing other errors. Recovery uploaded the already graded evidence, then a second read-back recovered the completed write after the run summary became visible. The stable run and artifact IDs were reused.

The existing native download control now depends on the completed save state and cached checkpoint bytes. Its archive passed checksum, credential and local-home-path scans. An actual browser download remains an acceptance gate.

## Revisions and cost

- Actual student execution: `24dc1b64f28b394100aa3ba64b068bc2062aa2f1`.
- Publication recovery and final runner pin: `605b1d90c47eb309629589bf9d0f371aa27b8b12`, retained as tag `forge-course-runner-v5-models-605b1d90`.
- Canonical nine notebooks: `534efaab20e2354734a906e1572e7963569d9c43`.
- Local validation: 67 TypeScript tests, 51 Python tests, and all nine saved-view validations passed. Existing offline app results remain separate from this live rehearsal.
- Rollout estimate: **$2.034477163 of the authorized $25**; no outstanding rollout reservations. This conservatively includes overlapping notebook allowances and measured editor costs, not an invoice. The student attempt itself is estimated at $0.0947057527.
- The original unresolved $2 reservation remains unchanged in its original ledger. No new inference request in this rollout has missing usage.

All owned rollout runtimes were verified terminal. The final scratch runtime required the supported SDK stop after the GraphQL termination was not acknowledged. No GPU sandbox or model training ran; this track used CPU sandboxes and hosted inference.

## Research contract and remaining checks

The question is whether an owner can prepare, qualify, execute, preserve evidence, recover publication, and obtain a portable checkpoint through the existing lesson controls. The unit is one Project 01 minimal-treatment attempt, preceded by qualification and three protected controls. It is not a treatment comparison. Task, fixture, checker, model settings and image hashes are recorded in the trial artifact. No failed grade is excluded or relabeled.

Raw evidence stays private under `forge/local-results/rollout-v5` and the W&B evidence artifacts. Public files contain approved course metadata and sample evidence only. The private checkpoint retains historical attempts without adding them to the new cohort denominator. Inspect [the publication manifest](../../publication-manifest.json) before touching hosted source.

1. Complete actual native checkpoint downloads in authenticated Edit and Preview. Both checkpoint and small notes downloads timed out in embedded-browser automation. The links were visible and enabled; the iframe allowed downloads. Computer control could not inspect Codex’s native save dialogs. This does not establish the cause, and SDK retrieval is not a substitute for a browser download.
2. Inspect the actual downloaded bytes and restore into a fresh runtime. The completed SDK check verified 353 checksums, retained all three attempts and notes, preserved the new $3.1292283193 cumulative estimate, and left sandbox credentials disconnected.
3. Rehearse with a student account when one becomes available. Owner-only testing does not prove student permissions or entitlement.
4. For later updates, compare committed versions and source hashes against the publication manifest, preserve remote edits, reuse the same nine IDs, use the native Marimo editor, and verify source and rendered output again. Reserve costs before opening an editor; stop paid work if usage or cleanup is unknown.

The approved $25 exception covers this rollout only. It does not authorize bypassing the accounting gate for the full protocol-five research campaign. Keep all eight PRs as drafts and unmerged.

## Published lesson views

- [00 — Overview](screenshots/overview-final-preview.png)
- [01 — Project 01](screenshots/project01-final-preview.png)
- [02 — Project 02](screenshots/project02-final-preview.png)
- [03 — Project 03](screenshots/project03-final-preview.png)
- [04 — Project 04](screenshots/project04-final-preview.png)
- [05 — Project 05](screenshots/project05-final-preview.png)
- [06 — Project 06](screenshots/project06-final-preview.png)
- [07 — Project 07](screenshots/project07-final-preview.png)
- [08 — Project 08](screenshots/project08-final-preview.png)
