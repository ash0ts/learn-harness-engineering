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
python3 forge/scripts/create_notebooks.py --refresh-evidence --runner-commit EXACT_COMMIT
python3 forge/scripts/validate_notebooks.py
```

Commit canonical sources before publication. Marimo is pinned to the version
used by the authenticated editor, including its normal source formatting. A
source change requires a new source checksum and another verification.

For lesson-only changes, omit `--refresh-evidence` and `--runner-commit`:
generation preserves each notebook's saved trial data and coordinator revision.
Edit `forge/lessons/*.md` and the native shared cells. Do not import an HTML
website into the notebook. The lesson, images, worksheets, and evidence browser
must remain native Marimo output. Hosted verification also checks the primary
cohort, embedded visuals, and downloadable lab material.

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
4. In Marimo's command palette, open **Helper panel > Files**. Open the existing
   `notebook.py` with **More options > Open file** and replace its text with the
   complete committed canonical Python source. You can paste those exact bytes
   from the local canonical file, or upload the canonical `.py` under its own
   filename and copy its source through the file editor. Do not paste an HTML
   export. Verification requires identical Python source bytes. Save through
   the editor. Do not replace source through an undocumented
   notebook API or overwrite the artifact directly.
5. Save the complete source, then stop that editor runtime while its browser
   session is still connected. The normal shutdown flush commits the source.
   Run `uv run --script forge/scripts/publication.py check-source FILE.py` to
   require an exact match with the committed local canonical file. Close the tab
   after this check. A source-only match does not mark publication complete.
6. Reserve a fresh render session and reopen the same notebook ID. Attach and
   verify its CPU resources. It loads the committed source without the old
   editor's cell registrations. Choose **Run all stale cells** in Marimo's
   command palette. Wait for the images, results, and both download links to
   appear, then choose **Save file**. Leave the paid-rerun button idle.
7. Keep the fresh browser/runtime session open until its saved preview updates.
   The worker polls every 30 seconds and can throttle preview-only uploads for
   five minutes. A shutdown flush is attempted, but is not sufficient evidence
   that complete output was committed. Do not stop the render runtime early.
8. Run `uv run --script forge/scripts/publication.py verify FILE.py` while the
   runtime is active. It requires
   exact committed Python bytes, the local source commit, matching rendered cell
   source and output hashes, error-free cells, independently recomputed historical
   and primary aggregates, embedded images, and downloadable packets. It rechecks
   `currentVersion` to detect concurrent edits. Every aggregate group must be
   present in the saved output, so the aggregate tables disable pagination.
9. After verification, run `notebook_session.ts stop SESSION_ID` while the browser
   remains connected. It verifies terminal state and accounts for the wall-clock
   upper bound. Verify the final publication again, then close the tab. If source
   and output differ, leave publication pending and investigate. Do not weaken
   checks or upload an HTML artifact directly to force success. A live editor
   view alone is insufficient. Notebook publication concurrency is accounted
   separately from the two-concurrent-trial experiment protocol; no coding trial
   is launched by this workflow.

Run the TypeScript session commands from the course root using:

```sh
node --import ./forge/node_modules/tsx/dist/loader.mjs \
  forge/scripts/notebook_session.ts reserve SESSION_ID NOTEBOOK_ID
```

Use the same prefix for `attach` and `stop`. `FORGE_BUDGET_USD` must match the
existing ledger; it does not authorize changing a ledger's limit.

## Verify delivery

After all work and editing sessions finish, rebuild `snapshot_results.py`, then
run `audit_comparisons.py`, `audit_models.py`, `audit_traces.py`, and
`audit_sandboxes.ts`. Validate all nine notebooks and verify their committed
publications again. Rebuild `report.py` and inspect its completion gates before
publishing `publish_evidence.py` with its pinned dependencies through
`uv run --script`. The publisher rejects files or source archives containing the
active credential before staging them. It stores exact source archives for every
recorded execution and notebook revision and reads their checksums back.

Run `uv run --script forge/scripts/dashboards.py` after publishing the final audit
metrics. It reuses the native Forge workspace and report IDs in
`forge/results/dashboards.json`. The primary view includes only qualified,
complete comparison blocks; archived views retain their original grades and
measurement limitations. Open the primary and operations dashboards to verify
their charts, source-evidence links, accounting totals, and zero active workers.
Rebuild `report.py` after these receipts are recorded. These audit and publication
commands launch no inference or coding trial.

The delivery report distinguishes the frozen comparison study, subsequent
runtime qualifications, and manual graph fixtures. A graph fixture that passes
both verification lanes remains paused until an explicit checksum-bound human
decision. It is never counted as a successful Pi coding attempt.

Users with edit permission can land in the Marimo editor. Choose **Run all stale
cells**, then **preview** to teach from the native lesson. This loads recorded
data and enables the evidence selector, worksheet, and downloads. Notebook
runtime compute can incur cost; these cells do not start inference or coding
trials. A paid rerun additionally requires a mounted coordinator checkout at the
displayed revision, installed dependencies, external credentials and the existing
durable ledger. A fresh hosted runtime has no such coordinator mounted by default.
