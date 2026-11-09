## Find the text that vanished

A short document indexes successfully. A longer one produces chunks with empty content. The app can still show a reassuring status while retrieval has nothing useful to return.

This project asks you to add useful runtime observations and diagnose a seeded defect. Compare a condition with sparse feedback against one with structured startup, import, indexing, and error signals. Keep the defective application and task fixed.

**Your deliverable:** a reproduction, a diagnosis supported by logs, a narrow repair, architecture checks, and an observed comparison of diagnostic time and repair scope. Predict which signal will first expose the defect.

<!-- cell -->
## Observe before repairing

Start with the original Project 04 application and the same sample documents in each condition. Include a document over 1,000 characters, a short control document, and a document containing more than one paragraph. Freeze the fixtures before running.

Record startup state, import identity and size, indexing transitions, chunk counts, and errors. A useful log lets you connect one operation to its inputs and outcome. Avoid putting document text or credentials in logs when an identifier and length answer the diagnostic question.

The seeded expression is:

```typescript
const chunkContent = content.length > 1000 ? '' : buffer.trim();
```

For a classroom blind diagnosis, the instructor can withhold this section until learners have captured a reproduction. Once revealed, ask why a small happy-path fixture missed it and what boundary case would have exposed it sooner.

<!-- cell -->
## Compare debugging processes

1. Start each condition from the same defective source and give it the same task.
2. Record when the first supported diagnosis appears. Separate that timestamp from the first guess and the final repair.
3. Preserve the logs and commands that connect the diagnosis to the defect.
4. Grade the repair in a fresh workspace: import, index, inspect nonempty chunks, retrieve source text, and exercise the Electron UI.
5. Run architecture checks. Seed a forbidden Node import in renderer code and confirm the guard rejects it, then remove the test mutation.

Measure repair scope using the exported diff: changed files, changed behavior, and unrelated edits. A large patch is not automatically wrong, but unexplained changes make causal diagnosis harder. Human help belongs in the intervention record with its actual timestamp.

<!-- cell -->
## A working repair can still miss a guardrail

In the saved Forge adaptation, minimal instructions passed 2/3 and runtime feedback passed 3/3. All six attempts preserved the long document's chunk text. The failing minimal attempt did not correctly reject a seeded Node import in the renderer.

That result is more precise than “logs fixed the bug.” The full acceptance grade included an architecture guard, and the observed separation occurred there. The saved study did not establish a controlled difference in diagnosis time or fully grade the original structured-logging assignment.

Inspect both the coding-agent and application conversations in Agent Lens. They are distinct: one records the work that changes the app; the other records the app's service and inference activity. A trace explains a path through execution. It does not, by itself, prove that every required behavior passed.

<!-- cell -->
## Submit the diagnosis chain

Submit the fixtures, initial reproduction, timestamped observations, repair patch, architecture-guard evidence, service results, and actual UI capture. Add a short comparison of time to supported diagnosis and repair scope. Leave unobserved time fields blank.

Ask a partner to identify the defect using your evidence before reading your explanation. If the logs only say “indexing failed,” improve their specificity. If they dump every internal value, remove noise until the causal path is readable.

**Discussion:** which requirement explains the difference between 2/3 and 3/3 here? What new controlled experiment would be needed to claim faster debugging? Which single log event would you keep if you could keep only one?
