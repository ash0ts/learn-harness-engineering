# Visual evidence for the Forge articles

The audience is an engineer reviewing the course's claims. The page's job is to connect a result to the exact attempt, protected checks, delivered patch, visible application state, and archived operations. The canonical companion is [`docs/en/forge/evidence.md`](../docs/en/forge/evidence.md); the original nine articles retain their prose with figures inserted beside the relevant claims.

## Evidence boundary

The fixed report inputs come from publication commit `258cf51fdc692f9be60952d8dd811de90588a0c4`. `docs/public/forge/evidence/catalog.json` records their SHA-256 values. The primary IDs are selected from `delivery.primaryComparisons.trialIds`, not inferred from a passing outcome or an image's appearance. The generator requires 39 primary attempts and 19 complete passes among 129 total recorded attempts.

Every attempt preserves its native outcome, source revision, repeat number, model settings, checker/application/patch hashes, actual usage, recorded estimate, check-level results, trace/run/artifact links, screenshot availability, and evidence-file hashes. Non-primary records remain labeled as historical, diagnostic, loop, or graph evidence. Missing checks and missing images are not converted into failures or passes. The generator makes no paid launches and does not change grades.

Public exports are limited to metadata, original sample-course captures, and derived figures. Raw model/tool conversations, patches, fixture output files, and detailed command logs remain in the private artifacts. The full archive is `wandb/learn-harness-engineering-forge/forge-course-qualification-evidence:v4` (8,512 files, 35 source archives). The later decision is in `forge-qualification-human-approval:v0`. The companion does not weaken either project's access controls.

## Visual inventory and interpretation

| Visual | Reader question | Source | Boundary |
| --- | --- | --- | --- |
| Primary outcome matrix | Which individual repeats passed? | The 39 explicit primary IDs and their original grades | One task per project; no population or causal ranking |
| Six check matrices | Where did an attempt stop satisfying acceptance? | Recorded protected checks | Gray means not executed; a UI failure can conceal multiple causes |
| Role allocation chart | Which role consumes the call allowance? | `forge/src/trial.ts` role schedules | Ceilings are not actual token usage or equal cost |
| Timer timeline | When did the eight trials run within two hours? | Original timer checkpoint and linked start/finish timestamps | Bars are total trial elapsed intervals, not billed worker occupancy |
| Trial evidence chain | What crosses from actor to checker? | Staging, trial, and sandbox implementation | Workflow explanation, not a screenshot of an execution |
| Session boundary | What survives a fresh conversation? | Two-phase trial execution | Does not claim recovery from an arbitrary machine crash |
| Recorded graph attempts | Which candidate reached approval? | Explicit-contract graph transitions and three trial grades | Pi remains paused; the later manual approval names a different checksum |
| Application captures | What was visibly present at a recorded checkpoint? | Unmodified Xvfb/Electron PNGs | A visible answer does not establish every assertion; missing captures stay missing |
| Five native dashboard captures | How did Forge display comparisons, audits, and source links? | Original authenticated publication captures | Derived aggregate runs are not coding attempts; captures predate manual approval |
| Coding/app trace captures | Are conversations separated and operations nested? | Original Agent Lens captures and span readback | Captures show examples; the audit establishes broader reconciliation |
| Nine notebook views | What source/configuration/analysis did the published notebook display? | Original authenticated Marimo captures | Different saved cohorts remain visible; source correctness also requires committed-version readback |
| Supplemental captures | What did a diagnostic or independent lane display? | Graph lanes, manual qualifications, checker diagnostics | Kept outside coding-attempt counts and primary screenshots |

There are no generated illustrations or recreated product screens. Source images are copied byte-for-byte; the manifest records `transformation: none`, original artifact path, source URL, and SHA-256. Full-size originals remain linked. Wide data figures scroll within their container on phones, with text alternatives and equivalent check records in the explorer.

The capstone final frame still displays previous document/answer content after the checker calls reset through IPC. The article now says exactly what was observed: empty service stores and no citations on the subsequent request, without an assertion that the rendered document list refreshed. This finding does not rewrite the original grade.

## Reproduce locally

Download the private course artifact into `forge/local-results/` with its relative paths intact. Use the immutable report inputs from the publication commit above. On a checkout of the full stack:

```sh
uv run --locked forge/scripts/article_evidence.py --reports forge/results
python3 forge/scripts/article_diagrams.py
python3 forge/scripts/package_article_evidence.py
npm run anchors:build
npm run anchors:check
npm run docs:build
npx tsx forge/scripts/validate_article_visuals.mts
```

When rebuilding from the article PR alone, pass a directory containing the four fixed report inputs plus `dashboards.json` to `--reports`; that branch does not yet contain the publication layer's reports. The generator also reads the original `trace-audit.json` from the downloaded evidence.

Matplotlib 3.10.8 produces the data figures with bundled DejaVu Sans; the script lock pins its dependencies. The workflow diagrams are editable self-contained SVG generated with Python's standard library. The existing Vue/VitePress renderer supplies the explorer and galleries. There is no external browser CDN or paid-service call when reading the companion.

The included generator scripts run from a checkout of this course with the private evidence inputs; the ZIP alone is not a replacement for that checkout. Browser validation uses the repository's pinned Playwright dependency and a locally installed Chrome.

The portable ZIP includes original exported captures, PNG/SVG figures, workflow SVGs, catalog, CSV, manifest, and these reproduction notes. It deliberately excludes raw private logs and conversations. The manifest binds each distributed file to its SHA-256 and records the input hashes and artifact readback result when available.

## Verification

Numeric checks reconcile every primary ID, repeat, result, and matrix cell to the original records. A read-only W&B audit compares local evidence bytes with the committed artifact manifest; this establishes byte agreement, not semantic correctness of a grade. Article snapshots and their assets are validated separately.

Browser checks cover desktop and phone layouts, all figure sources, internal links and fragments, filters, empty states, selected-trial reloads, browser back/forward, pagination, keyboard interaction, and downloaded CSV/JSON agreement. Visual inspection covers the rendered figures, original captures, and the actual article column. All eight PRs remain drafts; the series does not approve the pending Pi candidate or merge a patch.
