# Deterministic graph qualification

`graph-repair.diff` is a hand-authored qualification patch against the Project 04 starter. It preserves long-document chunks, makes the sandboxed preload self-contained, and adds a renderer boundary check. It does not change the course starter.

This patch is excluded from coding-agent staging. It is not a Pi result or benchmark evidence. The publication qualification first verifies the unmodified starter (expected failure), rolls back, then verifies this patch with actual services and Electron in fresh sandboxes. A passing patch pauses for an explicit human decision. The separate Pi graph exercises retain their actual outcomes.
