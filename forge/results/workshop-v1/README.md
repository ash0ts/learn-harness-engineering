# Five hands-on Forge labs: release evidence

Runner `d760596a441c76b797c9224641accc4a416a9af0` is tagged `forge-workshop-v1.0.0`. [Three-platform qualification](https://github.com/ash0ts/learn-harness-engineering/actions/runs/43227923247) passed on macOS, Windows and Linux.

[Open the workshop overview](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTM%3D) · [Student and instructor guide](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/docs/en/forge/workshop.md) · [Immutable runner tag](https://github.com/ash0ts/learn-harness-engineering/tree/forge-workshop-v1.0.0).

[Workshop rehearsal dashboard](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=leid7r3frfp).

| Notebook | Saved version | Current source and render verified |
|---|---|---|
| [00-overview](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTM%3D) | 47 | True |
| [01-minimal-harness](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTQ%3D) | 53 | True |
| [02-workspace-docs](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTU%3D) | 40 | True |
| [03-session-recovery](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTY%3D) | 40 | True |
| [04-runtime-feedback](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTc%3D) | 33 | True |
| [05-role-separation](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTg%3D) | 32 | True |

The manifest records full source and rendered-output checksums. Projects 06–08 retain their previous source and published lesson.

The eight dependent PRs remain draft and unmerged: [1](https://github.com/ash0ts/learn-harness-engineering/pull/1), [2](https://github.com/ash0ts/learn-harness-engineering/pull/2), [3](https://github.com/ash0ts/learn-harness-engineering/pull/3), [5](https://github.com/ash0ts/learn-harness-engineering/pull/5), [6](https://github.com/ash0ts/learn-harness-engineering/pull/6), [7](https://github.com/ash0ts/learn-harness-engineering/pull/7), [8](https://github.com/ash0ts/learn-harness-engineering/pull/8), [9](https://github.com/ash0ts/learn-harness-engineering/pull/9).

These are owner qualification rehearsals, separate from the preserved 129-attempt archive and 39-attempt main comparison. Every failed attempt remains listed. A successful protected example demonstrates the execution path; it does not predict a student pass rate.

27 completed attempts: 3 infrastructure_failed, 14 passed, 10 task_failed.

Execution methods: 16 cli, 11 native-notebook-controls. Browser rehearsals have a separate cohort label; they are assisted qualification, not a student pass-rate estimate.

| Attempt | Project | Action | Outcome | Method | Evidence |
|---|---|---|---|---|---|
| `workshop-access-20261112` | project-01 | offline-app | infrastructure_failed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/workshopaccess202611) |
| `workshop-access-20261112-b` | project-01 | offline-app | infrastructure_failed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/2e744569e4af2406083b) |
| `workshop-access-20261112-c` | project-01 | offline-app | passed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/1fe4826cda2f49baac77) |
| `workshop-agent02-20261112` | project-02 | agent | infrastructure_failed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/d0ef8befa6a9b173c445) |
| `workshop-agent02-20261112-b` | project-02 | agent | passed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/2581f55459e663701f63) |
| `workshop-agent03-first-20261112` | project-03 | agent | passed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/fbd371847d0a1bde9ee3) |
| `workshop-agent03-resume-20261112` | project-03 | resume | task_failed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/b6c7e4f4814f4ee13448) |
| `workshop-agent03-resume-20261112-b` | project-03 | resume | task_failed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/36d892ff10d608a7e02c) |
| `workshop-agent03-resume-20261112-c` | project-03 | resume | passed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/16c1da66c33ff960fe7d) |
| `workshop-agent05-20261112` | project-05 | maker-checker | task_failed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/7d3917072a903c271f1a) |
| `workshop-agent05-20261112-b` | project-05 | maker-checker | task_failed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/04edbe706cf563415f54) |
| `workshop-agent05-20261112-c` | project-05 | maker-checker | passed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/1d68641285bf5b816c3f) |
| `workshop-live01-20261112` | project-01 | live-app | task_failed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/575ab876e951a6b93187) |
| `workshop-live01-20261112-b` | project-01 | live-app | passed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/e0257a8a0ab2c4908b71) |
| `workshop-live04-20261112` | project-04 | live-app | task_failed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/849281fec1da569dff20) |
| `workshop-live04-20261112-b` | project-04 | live-app | passed | cli | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/cfa201b6906b06d2120b) |
| `001a81e3-067f-41d0-a6c3-e0bb13c05b55` | project-02 | offline-app | task_failed | native-notebook-controls | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/0b83ae394d5d880d2b69) |
| `dec2a1cb-4318-4b95-803e-f6c9ac04a648` | project-02 | agent | task_failed | native-notebook-controls | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/199c8b9ab2f857f401fc) |
| `8ef29b23-c2ef-48f5-945a-e71adc27ba49` | project-03 | agent | passed | native-notebook-controls | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/a6be5f79655ad5d1f670) |
| `c782dce0-97a4-4aa9-9f13-80b089912e1c` | project-03 | resume | passed | native-notebook-controls | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/f05910917b55d0fe9e35) |
| `ee03a668-dca7-496d-bb5d-d096cb391697` | project-03 | offline-app | passed | native-notebook-controls | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/21738650b3f013807e0d) |
| `0ab8d97f-ed37-4ac4-b3dc-15aa0110b6ef` | project-04 | offline-app | passed | native-notebook-controls | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/6cf38a9295b2c55125ce) |
| `b0678251-b5ca-46c6-8af3-9652e05bcec5` | project-04 | live-app | passed | native-notebook-controls | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/d3a141be05b705b79611) |
| `c4581195-e195-4b80-af29-4d7b7acf1558` | project-04 | offline-app | task_failed | native-notebook-controls | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/4ddd2c94dde58895c125) |
| `e5652d9f-5129-4283-909b-cbca5af826d5` | project-05 | maker-checker | task_failed | native-notebook-controls | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/2d00ae2b486b0fc32e2d) |
| `fb8b61e4-c7b9-482c-8c36-3a64cba125c5` | project-05 | maker-checker | passed | native-notebook-controls | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/5644ab1c53d29522cbb9) |
| `9558b327-e562-41e6-8236-b9a265bbf31d` | project-01 | live-app | passed | native-notebook-controls | [run](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge/runs/cbcc7a985dbd9a0fb7d9) |

Interventions: repaired the SDK stdin lifetime and staging mutation; disabled provider thinking explicitly within existing output limits; fixed a whitespace-sensitive history assertion; rewrote the student handoff to include its required evidence sections; and batched checker file reads to produce a review within its unchanged four-call allowance. Earlier failures were retained.

Successful Project 01 inference included abstention to the original ambiguous question. That answer is recorded, not relabelled as factual success. Project 04 records student-authored indexing/retrieval spans. Project 03 records the fresh session reading the handoff. Project 05 records the actual checker review and subsequent patch.

A fresh private Project 01 copy also completed the native Prepare → edit → Save → Check → Connect → Execute workflow. Its unfinished checkpoint failed first. The assisted implementation and an edited answer instruction then passed eight Electron checks, including restart persistence. The supported answer identified paragraph chunks; the unsupported answer abstained. Agent Lens readback matched two calls with 493 input and 45 output tokens. Source reload preserved progress and spending.

Browser testing exposed two editor update races. Disabling debounce addressed rapid tab switching, but edits grouped under one dictionary still lost earlier values while the kernel was busy. Each file now has its own native editor identity. A browser regression using the actual shared cells verifies both edits survive an eight-second save, and the live Project 03 copy retained all three edited files. Save and Execute remain explicit controls.

A notebook rename exposed a second recovery defect: the old progress key used its mutable display name. The coordinator now uses Forge’s stable notebook anchor, while retaining exact legacy identity receipts for recovery. The private rehearsal restored its original failure and saved files, reconciled both recorded session allowances, and retained spending before another explicit launch. A second native rename and fresh kernel restored the accepted patch, both attempts, and the prior spending plus only the new notebook allowance. Sandbox credentials were disconnected. No historical outcome or reservation was discarded.

The browser coverage record in `status.json` lists each exercised activity, its exact execution IDs, recovery observations and remaining limits. Screenshots, saved snapshots and read-back receipts are in the private rehearsal artifact.

Completed attempt estimate: $0.3847. Shared rollout ledger, including prior rollout work and notebook sessions: $5.9262. These are estimates, not provider billing caps. The separate unresolved historical $2 reservation remains unchanged.

Validation: the 77 TypeScript tests, Python suites, nine unpaid saved views and documentation build pass. The latest browser-repair check includes 50 Python recovery/workbench tests. A preservation audit checks 544 original files, all historical notebook payloads and the unchanged Project 06–08 sources.

Remaining limits:

- Owner-account rehearsal only; no independent student account.
- Native browser downloads remain unverified; repeat clicks produced no observable download event or inspected file.
- Native notebook upload chooser automation timed out; CLI source import/export passed separately.
- CI exercises the actual Import button with a stubbed OS picker; native picker acceptance is separate.
- Windows local dev/build/check/source exchange qualified; paid CLI worker cleanup is not qualified.
- Rehearsals include protected examples and explicit prompt interventions, not a randomized comparison.
- The app’s confidence display is a course heuristic, not a calibrated model probability.
- CPU sandboxes and hosted Forge inference; no student GPU provisioning or model training.
