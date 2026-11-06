# Project 08: Executable orchestration graphs

The Forge track adds an explicit TypeScript state machine alongside the existing
lecture skeleton. Its nodes are plan, make, verify, rollback, approval, done,
rejected, and failed. Every transition is persisted. Maker sessions use Pi; exported
patches run through independent service and Electron verification lanes in parallel
fresh sandboxes. Failures route to rollback and bounded retry. Previous candidate
artifacts remain available even when the next workspace returns to its baseline.

From `forge/`, with qualification complete and the shared budget available:

```sh
npm run forge -- graph --checkpoint local-results/p8-graph.json --execute
```

A passing candidate stops at `approval`. Review its patch and verification evidence.
Execution does not resume merely because a file exists or a timer expires. Supply
an explicit decision bound to the candidate checksum:

```sh
npm run forge -- graph --checkpoint local-results/p8-graph.json --decision approve --actor YOUR_NAME --sha256 REVIEWED_SHA256
```

Use `reject` to decline the candidate. Approval records acceptance of the exported
exercise patch; it does not merge a GitHub PR or overwrite the course starter.
`--resume` reloads the checkpoint. An interrupted paid operation needs reconciliation
before retry, so a lost response cannot silently launch duplicate work.

Unit tests exercise rollback, retry, concurrent verification, pause, checksum
validation, and explicit resume using test fixtures. Live trial evidence is reported
separately. The original LangGraph lecture material remains explanatory material.
