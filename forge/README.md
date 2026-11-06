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
