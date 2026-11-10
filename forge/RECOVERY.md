# Recover a course operation

Use the original evidence directory, account, project, notebook owner and pinned runner revision. Recovery never launches another coding agent or replaces historical grades.

```sh
npm --prefix forge run forge -- recovery-report --output /path/to/evidence
npm --prefix forge run forge -- recover --output /path/to/evidence --operation OPERATION_ID --publish
```

The report distinguishes task outcome, sandbox cleanup, token telemetry, and publication. A terminated sandbox alone cannot prove an interrupted request had zero cost. A completed grade can be published again: the publisher reads back the stable run and artifact first and verifies committed bytes before saving its receipt.

When request usage or cleanup is unknown, retain the reservation. An instructor can supply a JSON evidence file **inside the evidence directory**, then run:

```sh
npm --prefix forge run forge -- reconcile --output /path/to/evidence --operation OPERATION_ID --evidence reconciliation.json
```

The evidence contract is:

```json
{
  "schemaVersion": 1,
  "operationId": "OPERATION_ID",
  "instructor": "person who reviewed the evidence",
  "reason": "where the missing usage and termination evidence came from",
  "requests": [
    {"key": "phase-1-2", "inputTokens": 100, "outputTokens": 20,
     "receipt": {"path": "provider-receipt.json", "sha256": "SHA256_OF_RECEIPT"}}
  ],
  "sandboxes": [
    {"id": "SANDBOX_ID", "reservationId": "OPERATION_ID-sandbox-actor",
     "cleanup": "verified", "seconds": 60,
     "receipt": {"path": "termination-receipt.json", "sha256": "SHA256_OF_RECEIPT"}}
  ]
}
```

These numbers are an example, not reconciliation evidence. Provide actual provider usage and metered or conservatively bounded sandbox lifetimes. Include every unresolved request and every sandbox. The command verifies checksums and remote terminal state before changing accounting. Existing pricing comes from the operation's recorded protocol. A legacy qualification without embedded pricing also needs its original `protocol` in the evidence file.

Do not delete a ledger, clear pending actions, change notebook ownership, or charge an unknown request as zero to unblock a class. Keep original protected evidence. Publication/network failures and aborted inference are different failures and need different evidence.
