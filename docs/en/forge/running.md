# Running the Forge track

Start with the [article series](./index.md) or its saved notebooks. Reading the saved analysis does not start inference or a coding trial. A hosted notebook's own runtime can incur compute charges.

The original [offline exercises](/en/projects/) remain the default. Their mock behavior and unfinished features are preserved. Live Forge runs are opt-in and use sample course data.

## Local setup

Install Node 22.19+, Python 3.11+, and `uv`. From the course checkout:

```sh
npm ci --prefix forge
npm run build --prefix forge
npm run forge --prefix forge -- doctor
npm run check --prefix forge
npm test --prefix forge
npm run forge --prefix forge -- validate-notebooks
```

Supply `WANDB_API_KEY` externally. Set `WANDB_ENTITY` to a writable team and keep the results project private. `WANDB_PROJECT` defaults to `learn-harness-engineering-forge`; this delivery uses the `wandb` team. Credentials and SDK clients stay in the main/service layer.

The frozen campaign used Forge's OpenAI-compatible inference endpoint and `Qwen/Qwen3.6-35B-A3B`. A live qualification checks availability and capabilities before comparisons. An unavailable model stops the affected campaign; the runner does not substitute another model or mock response.

## Plan before launching

This command describes a comparison without starting paid trials:

```sh
npm run forge --prefix forge -- compare --project project-01 --repeats 3
```

Review the model, source, treatments, and reservations. With credentials, a private project, and budget authorization configured, these are explicit paid actions:

```sh
export WANDB_ENTITY=wandb
export WANDB_PROJECT=learn-harness-engineering-forge
npm run forge --prefix forge -- doctor --qualify --execute
npm run forge --prefix forge -- compare --project project-01 --repeats 3 --execute
```

Run qualification again after a protocol change. Keep the source revision and generation settings fixed within a comparison. A new run from an edited checkout belongs to a new source cohort; it does not replace the saved course results.

## Read the evidence

The [primary comparison dashboard](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=dfs83wdpatt) selects the latest qualified complete blocks per project. The [operations dashboard](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=l9e45ofb461) covers execution, publication, loops, and graph states. Both require private-project access.

Use the [public results report](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/forge/results/README.md) for counts, frozen revisions, and exclusions. Historical grades affected by asynchronous UI waits, the citation selector, or an unspecified task contract remain archived. Derived dashboard rows are not additional coding attempts.

The checker starts a new sandbox from the baseline plus the exported patch. It executes application services and Electron under Xvfb. The services use deterministic course Q&A defaults; live inference has separate qualification. Read the assertion and its evidence before generalizing a pass to other behavior.

## Budget and recovery

The default application budget is $50, including estimated inference, sandbox, and notebook execution costs. The coordinator reserves estimated in-flight cost before launch and defaults to CPU workers, two concurrent trials, and bounded lifetimes. This is an application control, not a guaranteed provider billing cap.

This delivery records a later explicit unlimited-budget authorization. `FORGE_BUDGET_USD=unlimited` must match the authorization in the ledger. It does not remove accounting or worker limits. Recorded delivery estimates total $19.042267, including $6 charged conservatively for unknown usage; these are not invoices.

Keep `forge/local-results/budget.json` across launches. Do not delete it to bypass a halt. Missing pricing, unknown usage, or uncertain cleanup stops further paid work until the record is reconciled with evidence or an explicit audited decision.

Loop checkpoints preserve pending trial IDs, candidate paths, deadlines, and interventions. A pending operation must be reconciled before resume. The real timer exercise retains its original deadline after recovery. See [Project 07](./07-bounded-loops.md) for the executed example and [Project 08](./08-state-machine.md) for checksum-bound approval.

## Notebooks and publication

The [canonical Marimo sources](https://github.com/ash0ts/learn-harness-engineering/tree/codex/forge-notebooks/forge/notebooks) contain pinned Python dependencies and runner provenance. To open the overview locally:

```sh
uv run --with marimo==0.25.1 marimo edit forge/notebooks/00-overview.py
```

Saved analysis is self-contained. Paid reruns require the displayed coordinator revision, Node dependencies, external credentials, and the existing shared budget ledger. A new hosted analysis runtime has no mounted coordinator by default. Notebook cells call the shared TypeScript runner; they do not reproduce the app in Python.

Publication creates a BASIC notebook, renames it, opens an authenticated EDIT session, and loads canonical source through the Marimo editor. Normal saving commits the source. Verification checks the committed `currentVersion`, source checksum, and rendered output before marking publication successful.

Reuse the IDs in `forge/publication-manifest.json` and check for remote edits before replacing source. The [publication guide](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/forge/PUBLISHING.md) documents the workflow. The article series does not change the nine published notebook sources or their experimental snapshots.
