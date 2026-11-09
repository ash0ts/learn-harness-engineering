# Native Forge course notebooks

The nine Markdown files are the canonical lesson text. `course_packets.py`
adds editable submission scaffolds; `lesson_cells.py` supplies native Marimo
evidence tables, selectors, images, worksheets, and downloads. `learner_cells.py`
and `learner_workspace.py` add native self-service setup, execution, progress,
and explicit graph decisions.
`create_notebooks.py` embeds these into self-contained `.py` notebooks. There is
no website/HTML import layer and no remote image dependency.

The original-course comparison uses upstream revision
`a9342ff471f2c0e60be0c08b9f4a7c502df4e442`. The lessons restore its student work:

| Project | Restored assignment | Saved Forge evidence limitation |
|---|---|---|
| 01 | Source-removed weak condition, complete minimal harness, two builds | Saved study starts from unfinished app source and a shorter harness |
| 02 | Full workspace documentation, import/detail/persistence, fresh session | Generic guide; all six UI import checks timed out |
| 03 | Feature ledger, one feature per verified commit, startup and handoff | Patch recovery did not implement the complete original discipline |
| 04 | Structured runtime observations, diagnosis time and repair scope | Saved grade includes chunk repair and guards, not a full timing study |
| 05 | Same history upgrade, three roles, plans/reviews and common rubric | Role documents also vary; reference scores are not executed evidence |
| 06 | Fixed task set, complete harness, cleanup/rerun, single ablations | Saved experiment is narrower; reset UI refresh remains a checker gap |
| 07 | Manual/goal, two-hour monitoring, five maker/checker rounds | Saved repair loops do not complete these original assignments |
| 08 | Graph contract, serial/parallel comparison, targeted rollback, two reviews | Saved graph lacks the timing comparison/two approvals; Pi approval is pending |

Every notebook keeps the original assignment separate from the recorded adapted
case. No results or human approvals are invented. GPU autoresearch is identified
as a lecture case study, not an executed GPU training lab.

Generation preserves each existing notebook's `saved` data and `runner_commit`
by default. Use `--refresh-evidence` only when intentionally updating evidence
from `forge/results/snapshot.json`. Use `--runner-commit` only for an intentional
coordinator revision change. Rendering lessons must not silently change either.

```sh
python3 forge/scripts/create_notebooks.py
python3 forge/scripts/validate_notebooks.py
```

Validation executes all saved views without API credentials, reconciles data
with the snapshot, independently checks the displayed primary cohort, and
requires native embedded images and downloadable lab material. Image hashes and
source provenance are in `evidence.json`. Hosted publication still requires the
normal authenticated Marimo editor save and exact committed-source/render checks.

Each learner copies a lesson to a writable private project and opens Edit.
Prepare installs Git, checksum-verified Node 22.19.0, the exact runner commit,
and lockfile dependencies. Forge injects the session identity and credential;
keys never belong in notebook source. Sandbox access currently needs the learner's own key through a masked,
session-memory prompt. A separate explicit action qualifies live access before paid trials. Progress artifacts retain the ledger, observations,
patches, grades and checkpoints across runtimes. A pending action on restore
blocks automatic retries. These controls run the Forge adaptation; the original
assignment's additional work remains explicit. See [self-service setup](../../docs/en/forge/classroom.md).
