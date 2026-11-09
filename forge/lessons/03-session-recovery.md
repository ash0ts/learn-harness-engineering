## Make one feature the unit of progress

A handoff that says “indexing mostly works” leaves the next session with a guess. This project makes the claim smaller: one named feature, one verification record, one commit.

Build document chunking, metadata, indexing status, and source-grounded citations. These features depend on one another. Useful metadata supports chunking; chunks support retrieval; retrieval makes a citation meaningful. A status label that says “indexed” is only a claim until the underlying state is checked.

**Your deliverable:** a feature ledger, feature-ID commits, a session handoff, and evidence that a fresh session can continue from a clean state. Predict where a broad “done” status could hide incomplete work.

<!-- cell -->
## Define the dependency order

Use the original Project 03 starter. Draw the dependency chain before asking the agent to edit: metadata → chunking → indexing status and grounded Q&A. Adjust the exact feature IDs to the starter's ledger, but keep each acceptance test observable.

Each feature entry should contain an ID, description, dependencies, status, verification command, evidence path, and last-tested timestamp. Reset inherited completion entries. An evidence path pointing at a deleted temporary directory is not durable evidence.

The startup routine reads `AGENTS.md`, architecture and product docs, installs/checks the environment, and reads the feature list. `init.sh` should make those checks reproducible. The handoff and progress log explain the current boundary; the clean-state checklist records whether the tree, tests, and remaining work agree.

<!-- cell -->
## Enforce the one-feature cycle

1. Select one unfinished feature whose dependencies are satisfied.
2. Implement only that feature. Record unrelated discoveries for later rather than silently expanding the task.
3. Run its verification. Inspect actual metadata, chunk contents, status transitions, or citations as appropriate.
4. Attach evidence and update status only if the check supports it. Record failures honestly.
5. Commit with the feature ID. Write the next action in the handoff before selecting another feature.

Interrupt the process at a declared feature boundary and start a fresh conversation. Give it the files, not the previous chat. Ask it to explain the next eligible feature and the evidence for the completed dependencies before editing.

For grounded Q&A, check that a displayed citation resolves to the imported source and the relevant content. A plausible answer with a citation-shaped string is not enough. For indexing, test documents long enough to produce multiple chunks and check that nonempty text survives.

<!-- cell -->
## The saved recovery experiment is narrower

Our Forge adaptation preserved a patch between two Pi sessions and added recovery instructions. It did not stage the original feature list, startup script, and complete one-feature workflow. Its results therefore test a written recovery treatment on unfinished application code, not the full original discipline.

Both treatments passed 0/3 qualified attempts. Four attempts failed compilation; the two that compiled failed metadata acceptance, with `wordCount` the first failing assertion. One also failed the single-document indexing-status check. Some downstream checks never ran after an earlier failure; they should remain “not executed.”

Two compiled submissions displayed answers in Electron. That makes an instructive screenshot, but not a passing submission. Compare the visible answer with the full grade below. Identify one missing requirement that the screen alone cannot establish.

<!-- cell -->
## Submit a restart another person can reproduce

Submit the feature ledger before and after, feature-ID commits, startup script, progress log, handoff, clean-state checklist, and fresh-session transcript. Include the boundary patch and final independent checks.

Have a partner choose a feature marked complete and rerun its verification from a clean checkout. Then ask them to identify the next eligible feature. If they cannot do both, distinguish an application failure from a state-recording failure.

**Discussion:** when a checker fails early, what can you conclude about downstream behavior? Which evidence belongs in the feature entry, and which belongs in the broader trial record? Describe how you would prevent a stale “passed” entry from surviving a later code change.
