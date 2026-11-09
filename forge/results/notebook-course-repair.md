# Course notebook revision

The notebooks now teach the original eight-project progression, with a separate
recorded Forge case in each lesson. The comparison against the frozen upstream
briefs is recorded in [the lesson source guide](../lessons/README.md).

The revision adds native Markdown lesson cells, 15 embedded figures/captures,
independent-grade inspection for a selected trial, observation worksheets, and
downloadable lab/submission packets. Historical cohorts and raw records remain
available in collapsed sections. No HTML website import is used.

The original assignments include work that the saved campaign did not complete:
the full minimal harness, feature-by-feature continuity, capstone cleanup and
ablations, the manual/goal comparison and five-round loop exercise, serial versus
parallel measurements, and two graph approval passes. These gaps are stated in
the relevant lessons. No GPU training job is claimed. No new coding/inference
trials were launched for this content revision, and historical outcomes,
checkpoints, human approvals, and pinned runner revisions were preserved.

All nine saved views execute locally without API credentials. Validation checks
snapshot consistency, the independently recomputed primary cohort, embedded
images, and downloadable packets. The packets were decoded from the actual
exports and checked as valid ZIP archives. A live local check verified that the
trial selector changes the displayed grade and that paid launch is disabled
without a configured coordinator. Desktop and 390-pixel-wide lesson views were
inspected. A browser download-event probe timed out; the verified downloadable
payloads, rather than that event, establish the packet contents.

Hosted publication uses the existing notebook IDs and normal Marimo source
editor. Two remote changes consisted only of added empty cells; their sources
were preserved and reviewed before replacement. Exact committed bytes are
required. Rendered cell source is compared after removing the generated Python
function indentation, matching Marimo's cell serialization; changed lesson text
is still rejected. Output hashes, errors, all historical aggregates, the primary
cohort, images, and downloads are checked independently.

The live editor and saved preview can diverge during a full-file replacement.
A successful live view alone does not mark publication complete. The publication
manifest records success only after committed source and saved output agree.
Editor resources and termination receipts use the existing budget ledger.

Publication status, notebook URLs, source revisions, checksums, and rendered
verification counts are authoritative in
[`publication-manifest.json`](../publication-manifest.json). Session accounting
and the final revision receipt will be recorded alongside this report when all
nine publications are verified.
