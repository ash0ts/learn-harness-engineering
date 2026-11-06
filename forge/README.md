# Forge track

Optional experiments for Learn Harness Engineering. Original exercises remain usable offline.

Requires Node 22.19+ and Python 3.11+. Run `npm ci --prefix forge`, then
`npm run forge --prefix forge -- doctor`. Supply `WANDB_ENTITY`, `WANDB_PROJECT`,
and `WANDB_API_KEY` in the process environment for live runs; do not commit keys.

Pi uses the Weave OpenTelemetry extension. Application traces use the Forge SDK
in a separate process. The default inference provider is Forge, with no fallback
to another provider or simulated answers in live mode.

The baseline source revision is recorded in `provenance.json`. Experimental
results are evidence about these tasks and settings, not a general model ranking.

Checks: `npm run check --prefix forge` and `npm test --prefix forge`.

## Optional app instrumentation

Run `npm ci --prefix forge && npm run build --prefix forge`. Build the selected
standalone app with its existing `npm run build`. For an opt-in live desktop run,
set `FORGE_APP_MODE=live` and `FORGE_APP_ADAPTER` to the absolute file URL of
`forge/dist/src/app.js`, then use the app's normal `npm run dev` command.
`WANDB_ENTITY`, `WANDB_PROJECT`, and `WANDB_API_KEY` belong to the main process.
The renderer only uses the original typed IPC bridge. Never enable live mode on
private documents for this course; use the sample fixtures only.

The dependency-free `src/services/forge-hooks.ts` in each app is generated from
`forge/app-hooks.ts.template`. All 15 copies are tested against the template.
Offline mode neither loads the SDK nor changes generation, retrieval, or starter
gaps. Live failures reject the operation before history is written. The old
confidence heuristic is retained as an exercise artifact, not a calibrated model
confidence score. The existing file picker still needs the learner's Electron 33
path-bridge fix where that gap is present.

For service evidence, use `npm run forge --prefix forge -- services APP_DIR
OUTPUT_JSON FIXTURE...` from the repository root (put the command on one line).
Add `--live` only for an authorized, budget-reserved run. This calls the selected
app's compiled import, indexing, retrieval, and Q&A services. It does not establish
that the Electron UI works. `python3 forge/scripts/check_apps.py` runs the existing
offline type, build, test, and available architecture checks across every copy.
