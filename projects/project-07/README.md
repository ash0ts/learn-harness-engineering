# Project 07: Executable long-running loops

The optional Forge track runs Pi in bounded sessions against the same unfinished
Project 04 app. A goal loop stops on verified success, no progress, round limit,
deadline, or infrastructure failure. A maker-checker loop adds independent review
contexts; checker filesystem changes are discarded before the maker revises.
Every round exports a patch, terminates its worker, and grades in a fresh sandbox.
The next session reconstructs the workspace from the frozen source and patch.

From `forge/`, after qualification and with credentials supplied externally:

```sh
npm run forge -- loop --mode goal --checkpoint local-results/p7-goal.json --execute
npm run forge -- loop --mode maker-checker --checkpoint local-results/p7-review.json --execute
npm run forge -- loop --mode timer --checkpoint local-results/p7-timer.json --duration-seconds 7200 --interval-seconds 900 --max-rounds 8 --execute
```

The real timer exercise spans two hours. It launches at most eight sessions and
holds no sandbox while waiting. An accelerated unit test uses a virtual clock;
it is not evidence of a completed two-hour exercise. Each launch reserves costs
against the shared $50 ledger. A blocked budget or unavailable capability stops
further paid work. Resume using the same checkpoint and `--resume`; an ambiguous
pending trial requires evidence reconciliation before another launch.

Record human interventions with `addIntervention()` in `forge/src/loops.ts`.
Notes are learner-entered and timestamped, never inferred from model activity.
Offline source exercises and lecture examples remain usable without Forge.
