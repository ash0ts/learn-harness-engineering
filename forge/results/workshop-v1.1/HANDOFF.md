# Resume the eight-lab candidate

Repository: `ash0ts/learn-harness-engineering`. Work in the existing checkout and eight dependent draft PRs; keep them unmerged. Use `GH_REPO=ash0ts/learn-harness-engineering` and explicit `--remote origin` with `gh stack`.

## Retained state

- Runner candidate: `72736fc171adf6f50fdd4a99f48a6f4ff576769a`; immutable tag `forge-workshop-v1.1.0-rc.1`.
- Canonical notebooks: `forge/notebooks/`; generator: `forge/scripts/create_notebooks.py`; shared UI metadata: `workshop_teaching.py`; coordinator: `workshop_workspace.py`.
- Eight lab manifests/examples: `forge/workshop/`. Loop and graph implementations: `forge/src/workshop-loop.ts` and `workshop-graph.ts`.
- Private qualification evidence: `forge/local-results/workshop-v1.1/`. Local browser edits were assisted checks with paid execution disabled. Do not present them as Forge rehearsals.
- Shared $25 rollout ledger: `forge/local-results/rollout-v5/budget.json`. Outstanding operation: `workshop11-capstone-live-20261112`; reservation: `workshop11-capstone-live-20261112-sandbox-grader`, $0.142. Preserve its infrastructure-failure outcome.
- Read-only access receipt: `forge/local-results/workshop-v1.1/access-check.json`. Both the course project and `wandb/sandbox` returned Sandbox access denied. W&B artifact access worked.
- No new notebook runtime was opened. The attempted overview reservation failed before allocation. Nine existing published notebook versions are unchanged; IDs and previous source hashes remain in `forge/publication-manifest.json`.

## Next actions after access is restored

1. Read applicable skills/repository instructions and inspect the current stack/working tree. Never overwrite concurrent edits.
2. Use the existing approved secure credential source in process memory. Do not print, commit or upload credentials. Recheck read-only Sandbox access before any paid launch.
3. Inspect the failed operation, sandbox journal and provider records. Its lookup tag is `workshop11-capstone-live-20261112-grade`. Establish whether creation occurred and obtain terminal/lifetime or explicit no-dispatch evidence. Reconcile through the supported recovery flow with checksummed evidence; do not delete its reservation or assume zero cost.
4. Keep two-worker concurrency, per-request reservations, fixed limits and no implicit replacement work. `forge/local-results/workshop-v1.1/rehearse.ts` prepares assisted CLI qualifications for 06–08; choose new attempt IDs only after the existing failure is resolved. Genuine graph approval requires a new human decision on the actual verified checksum.
5. Rehearse named notebook activities in fresh private copies through the browser, including actual source propagation, Agent Lens read-back, grading, publication and cleanup. The local-only adapter under the temporary browser QA directory must never be published.
6. Use `publication.py` and the existing normal Marimo editor workflow. Check remote source against the reviewed manifest before each replacement, reserve the editor runtime, load canonical `.py` source through the file editor, save normally, verify committed bytes and rendered output, then terminate/settle the editor. No HTML imports or source-upload API workaround.
7. Reuse all nine IDs, overview through Project 08. Write a new release report/dashboard cohort; do not replace the five-lab owner-rehearsal record or historical 129/39-attempt comparisons. The old `workshop_dashboard.py` targets that historical release and must not be rerun as if it represented v1.1.
8. Record actual coverage and limits, then push owning stack layers. Do not move the old v1.0.0 or this candidate tag. A final release gets a new immutable tag.

## Validation commands

```sh
npm run check --prefix forge
npm test --prefix forge
python3 -m unittest discover -s forge/test -p 'test_*.py'
python3 forge/scripts/validate_workshop_preservation.py
python3 forge/scripts/validate_notebooks.py
npm run docs:build
```

The current results are 81 TypeScript and 53 Python passes, nine saved-view passes, eight browser edit/check flows, and a passing documentation build. Read `status.json` for exact source hashes. Paid Windows CLI cleanup, new three-platform qualification, independent student-account rehearsal, and browser-download acceptance remain unverified.

When rebasing from a lower stack layer, move ignored `forge/notebooks/__marimo__`, `forge/scripts/__pycache__`, and `forge/test/__pycache__` caches outside the checkout first. Some historical commits tracked those paths; the stack extension can otherwise retry a checkout obstruction indefinitely. Preserve source and evidence, and never switch branches while a rebase is running.
