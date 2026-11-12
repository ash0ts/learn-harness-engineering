# Illustrated Forge track: publication record

The [visual evidence workspace](https://forge.coreweave.com/wandb/wandb/learn-harness-engineering-forge?nw=su19wan3xra) is saved in the private `wandb/learn-harness-engineering-forge` project. It contains six summary panels, nine recorded-result figures, the 129-attempt table, and an image table containing 123 original captures. The publication run is explicitly excluded from coding-trial and primary-comparison counts.

The [article series](../../docs/en/forge/index.md) and [interactive evidence companion](../../docs/en/forge/evidence.md) connect the findings to original screenshots, protected checks, source revisions, patch identities, Agent Lens conversations, and private W&B artifacts. The primary comparison remains **19/39**. The complete history retains all **129** coding attempts. No outcomes or notebook snapshots were rewritten.

## Exact artifacts

- [Visual source and portable bundle](https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/forge-article-visual-evidence:v2): 165 files verified against the committed artifact manifest, with the downloaded ZIP also checked byte-for-byte.
- [Authenticated browser verification](https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/forge-article-visual-browser-proof:v0): twelve original captures plus the observation record; all 13 files verified against the committed artifact manifest.
- [Complete original course evidence](https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/forge-course-qualification-evidence:v4): 8,512 files, including 35 source archives. The visual audit matched 7,850 indexed local files to this artifact.
- [Machine-readable publication receipt](./article-visual-publication.json): source revision, workspace identity, run identity, artifact version, file checksums, and browser observations.

Article source: `2763962fda6dda9177e0e8405a4bf7de6e0b2b93`. Frozen experimental reports: `258cf51fdc692f9be60952d8dd811de90588a0c4`. Portable ZIP SHA-256: `84acc1e948631a830281252498fc3aef8e18bca6fe16deb6c567421fedb3ad1d`.

## Reproduce and inspect

The source contract and generation commands are in [ARTICLE-VISUALS.md](../ARTICLE-VISUALS.md). The public bundle contains 123 unchanged captures, nine SVG/PNG data figures, three editable workflow diagrams, a 129-row CSV, the JSON evidence index, reproduction scripts, and validation receipts. Raw conversations and patches stay in the private course artifacts.

Documentation and anchor validation pass. Browser checks pass across 22 desktop/phone page renders, 149 local resources, filtering, pagination, shared trial URLs, history navigation, keyboard expansion, and downloads. The native Forge workspace was separately inspected at 1280 × 720. At that height, some native media panels clip footer text; complete PNG/SVG originals remain downloadable. Native image panels, all nine figure views, and both table denominators were inspected after loading.

To update the private publication after rebuilding and validating the articles, use the externally supplied project credentials:

```sh
uv run --locked forge/scripts/publish_article_visuals.py
```

This reuses the existing run and workspace IDs and creates a versioned artifact. It neither starts a coding trial nor rescores evidence. After authenticating in Forge and saving actual captures and an `observations.json` into `forge/local-results/article-visual-publication/`, archive that inspected state with:

```sh
uv run --locked forge/scripts/record_visual_verification.py
```

The browser proof is a separate artifact so it can identify the exact already-published visual artifact without a checksum cycle. Keep previous artifact versions for audit. All eight PRs remain drafts; no candidate or PR was merged by this publication.
