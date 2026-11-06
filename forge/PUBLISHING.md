# Publishing the Forge notebooks

Canonical sources are the nine Marimo files in `forge/notebooks/`. The private
project is `wandb/learn-harness-engineering-forge`. Its stable notebook IDs and
expected remote versions live in `forge/publication-manifest.json`.

Supply credentials through the environment. Keep the existing budget ledger and
its authorization history. The default application cap is $50; this delivery's
ledger records the user's later unlimited authorization. Worker lifetimes and
concurrency remain bounded in either mode.

## Prepare evidence and source

Finish the runs included in a notebook's evidence snapshot. Do not count a trial
until its `finishedAt` exists. Preserve failed qualifications and incomplete
attempts. Build the saved snapshot, generate the notebooks with an exact runner
revision, then validate their unpaid analysis view:

```sh
python3 forge/scripts/snapshot_results.py
python3 forge/scripts/create_notebooks.py --runner-commit EXACT_COMMIT
python3 forge/scripts/validate_notebooks.py
```

Commit canonical sources before publication. Marimo is pinned to the version
used by the authenticated editor, including its normal source formatting. A
source change requires a new source checksum and another verification.

## Use the existing editor workflow

`publication.py ensure` creates a `BASIC` record and renames it only when the
manifest has no existing ID. It never uploads arbitrary source. Repeated runs
reuse the recorded IDs. An uncertain create must be reconciled before retrying.

For each notebook:

1. Run `uv run --script forge/scripts/publication.py check-remote FILE.py`.
   It compares the remote version, edit timestamp and source checksum with the
   manifest. Preserve and review unexpected remote edits before replacement.
2. Reserve the editor's compute through `notebook_session.ts reserve SESSION_ID
   NOTEBOOK_ID`. Use a unique ID such as `notebook-15314-editor-1`. The script
   verifies private-project access before reserving costs.
3. Open that notebook's recorded URL in the authenticated Forge EDIT session.
   Attach its observed runtime ID with `notebook_session.ts attach SESSION_ID
   SANDBOX_ID`. This verifies the actual 2 CPU / 4 GiB resource shape against the
   recorded rates.
4. In Marimo's command palette, open **Helper panel > Files**. Upload the
   canonical `.py` file using its own filename. Open it in the text editor, copy
   its complete source, then open the existing `notebook.py` and replace its
   source. Save through the editor. Do not replace source through an undocumented
   notebook API or overwrite the artifact directly.
5. Re-run the saved-analysis cells through Marimo's normal command palette.
   Leave the explicit paid-rerun button idle. Let the normal save workflow commit
   source and rendered output.
6. Run `uv run --script forge/scripts/publication.py verify FILE.py`. The verifier
   requires exact committed source bytes, the committed local source revision,
   matching rendered cell code and output hashes, error-free cells, and aggregate
   values independently recomputed from the embedded trial evidence. It rechecks
   `currentVersion` at the end to detect concurrent edits.
7. Close the editing tab and run `notebook_session.ts stop SESSION_ID`. It waits
   for terminal runtime state and charges the measured wall-clock upper bound to
   the same ledger. Keep the receipt in `forge/local-results/notebook-sessions/`.

Run the TypeScript session commands from the course root using:

```sh
node --import ./forge/node_modules/tsx/dist/loader.mjs \
  forge/scripts/notebook_session.ts reserve SESSION_ID NOTEBOOK_ID
```

Use the same prefix for `attach` and `stop`. `FORGE_BUDGET_USD` must match the
existing ledger; it does not authorize changing a ledger's limit.

## Verify delivery

After all work and editing sessions finish, run `audit_traces.py` and
`audit_sandboxes.ts`, rebuild `report.py`, and publish `publish_evidence.py` with
the pinned W&B dependency through `uv run --script`. These read existing evidence
and upload artifacts; they launch no inference or coding trial. The audit stores
exact source archives for every recorded execution and notebook revision.

The delivery report distinguishes the frozen comparison study, subsequent
runtime qualifications, and manual graph fixtures. A graph fixture that passes
both verification lanes remains paused until an explicit checksum-bound human
decision. It is never counted as a successful Pi coding attempt.

Opening a hosted notebook displays saved analysis. A paid rerun additionally
requires a mounted coordinator checkout at the displayed revision, installed
dependencies, external credentials and the existing durable ledger. A fresh
hosted runtime has no such coordinator mounted by default.
