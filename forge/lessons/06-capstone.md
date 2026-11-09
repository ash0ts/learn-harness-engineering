## Make the whole operating harness earn its place

By now the app is mostly present. The capstone asks whether your way of operating it is reliable: can a new session start, make the requested changes, verify them, leave a clean state, and do it again?

Use the original fixed multi-feature task set. Compare a weak setup with your strongest harness, then remove one harness component at a time. The ablation is the part that makes “this file helps” testable.

**Your deliverable:** a complete operating harness, a controlled task comparison, cleanup and rerun evidence, and one-component ablations. Predict which component will matter most and name the observable failure you expect when it is removed.

<!-- cell -->
## Freeze the capstone before comparing

Start from identical original Project 06 application code and the same task set. Write down what must work across import, indexing, retrieval, Q&A, history, feedback, and reset as required by your selected contract. Preserve the starter's intentional gaps until the attempt begins.

Assemble the harness from earlier work: startup instructions and `init.sh`, architecture/product docs, the feature ledger, session handoff and progress, clean-state checklist, quality criteria, evaluator instructions, and reproducible verification commands. Keep facts in the files that own them. A harness that repeats contradictory acceptance criteria in five places creates another debugging task.

Define cleanup before running. Which generated files, caches, test data, and temporary artifacts should be removed? Which evidence must survive? Check `git status` and a cleanup report; do not delete the only copy of the failed run's logs in pursuit of a tidy directory.

<!-- cell -->
## Run the comparison and the ablations

1. Run the weak and full-harness conditions from the same starting application. Export both patches and grade them independently.
2. Perform the declared cleanup, then rerun from a clean environment. Check whether the same commands and fixtures reproduce the result.
3. Restore the full harness. Remove exactly one component—such as the handoff or architecture guard—and repeat the same task under the same limits.
4. Restore it before testing another ablation. Label every condition and preserve its exact staged files.
5. Compare the failures the removed component was meant to prevent. Avoid attributing unrelated failures to it without evidence.

The original `benchmark.sh` includes simulated operations. It can explain an exercise, but copying files or estimating chunks is not evidence that the real services and UI work. For Forge evidence, execute the actual application services and Electron under Xvfb. Keep compilation, service behavior, and visible interaction as separate checks.

<!-- cell -->
## The saved capstone is a narrower hardening task

The recorded Forge adaptation focused on feedback and reset alongside the real import/index/Q&A path. It compared minimal guidance with capstone guidance; it did not execute the original full task-set cleanup comparison and one-component ablations.

Capstone guidance passed 3/3. Minimal guidance passed 1/3; two attempts failed compilation. That is the observed result for this particular adaptation, not a measurement of every component in the original operating harness.

There is a revealing acceptance gap in the passing evidence. Reset emptied the service stores and a later question produced zero citations, but the final Electron screen could still show the old document list and answer. The checker did not assert that every displayed item refreshed after reset. The capture below makes that limitation visible.

<!-- cell -->
## Improve the acceptance contract

Before looking at the saved grade, write the reset behavior a user would expect. Then compare it with what was tested. Add a UI assertion for the stale state as a proposed checker revision. Do not silently apply the new requirement to old scores; a changed checker creates a new protocol.

Submit the full harness, task manifest, weak/full patches, cleanup report, clean rerun evidence, ablation definitions and results, and a final quality review. Explain which observations support each component's value and which remain inconclusive.

**Before moving to loops:** another person must be able to use your startup routine, identify the unfinished work, run the checks, and understand the handoff without a conversation with you. Automation amplifies both the useful parts and the gaps in that routine.
