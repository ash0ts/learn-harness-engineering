## Find the text that vanished

A short document indexes fine, but a longer one produces chunks with nothing in them. The app still shows a reassuring status, and retrieval has no text to return.

In this project you find that planted defect twice: once with sparse feedback from the running app, and once after adding structured signals for startup, import, indexing and errors. The broken app and the task stay the same both times.

**What you hand in:** a reproduction, a diagnosis backed by logs, a narrow repair, architecture checks, and a comparison of how long diagnosis took and how much the repair touched. Before you start, predict which signal will expose the defect first.

<!-- cell -->
## The lab: observe before you repair

Start both versions from the course's Project 04 app and the same sample documents. Include one document over 1,000 characters, a short one as a control, and one with more than one paragraph. Choose those before you run anything, and don't change them afterwards.

Have the app record its startup state, what was imported and how big it was, each change of indexing status, chunk counts, and errors. Each log line should let you tie one operation to its input and its outcome. Keep document text and credentials out of the logs; an identifier and a length usually answer the question.

The planted line is:

```typescript
const chunkContent = content.length > 1000 ? '' : buffer.trim();
```

If you're an instructor teaching this as a blind diagnosis, hide this section until students have a reproduction; the course's Project 04 app also has a `// BUG:` comment above the planted line. Afterwards, ask them why a short sample document that indexes fine missed it, and which boundary case would have caught it sooner.

<!-- cell -->
## The lab: compare two ways of debugging

1. Start each version from the same broken source with the same task.
2. Note when the first diagnosis backed by evidence appears. Keep that time separate from the first guess and from the final repair.
3. Keep the logs and commands that connect the diagnosis to the defect.
4. Grade the repair in a clean workspace: import, index, check the chunks have text, retrieve a passage, and use the Electron window.
5. Run the architecture checks. Add a forbidden Node import to renderer code, confirm the guard rejects it, then take it out again.

Measure how much the repair touched from the exported diff: files changed, behavior changed, and edits that had nothing to do with the defect. A big patch can be correct, but every unexplained change makes it harder to say what fixed the bug. If you helped, write it down in `interventions.csv` with the time it happened.

<!-- cell -->
## What happened when we ran it

The main comparison is six attempts on the planted defect, three per treatment. `minimal` got the task. `runtime-feedback` also got an instructions file, an architecture note, and a small script that shows the real chunks and indexing status after a build.

All six attempts fixed the defect: the long document's chunks kept their text. The source we gave the agent has a `// BUG:` comment above the planted line, and in all six attempts the agent read that file before it built or edited anything. `runtime-feedback` passed 3 of 3 and `minimal` passed 2 of 3. The grade also includes the architecture guard from the last step of the lab, a script we had the agent write, and in the one attempt that failed, the guard didn't reject the forbidden Node import in the renderer.

Because every attempt fixed the bug, we can't say the extra feedback fixed it. In each of the three `runtime-feedback` attempts the agent ran the feedback script once, after it had rewritten the indexing code. The only difference in the grades was one attempt's architecture guard. Outside the grades, all three `runtime-feedback` attempts were stopped at the limit of 24 model calls, while the three `minimal` attempts finished on their own after 18 to 22 calls. We also didn't time diagnosis under controlled conditions or grade the structured logging and repair size the lab asks for, so we have no evidence about debugging speed.

Under **Inspect one attempt** below, pick `0865dc24` (`runtime-feedback`, attempt 1) and click **Open in Agent Lens** in its **Coding agent** row. Find the command that prints `src/services/indexing-service.ts` and the `// BUG:` comment in its output, then the command that rewrites that file, then `node runtime-feedback.cjs`. In `9feeffa8`, the `minimal` attempt that failed, find what the agent ran to test the guard it had written. Each attempt has only the coding agent's conversation, because inside the sandbox the app makes no model call when it answers a question.

<!-- cell -->
## Hand in the chain from symptom to fix

Hand in the sample documents, your first reproduction, your timestamped observations, your diagnosis and the logs behind it, each repair patch, the architecture-guard evidence, the clean-workspace grading results and a capture of the Electron window. Add a short comparison of time to a supported diagnosis and how much each repair touched. If you didn't observe a time, leave it blank.

Ask a partner to find the defect from your evidence before they read your explanation. If your logs only say "indexing failed", make them more specific. If they dump every internal value, cut until the path from cause to symptom is readable.

**Discuss:** which requirement explains 2 of 3 versus 3 of 3 here? What experiment would you need before claiming faster debugging? If you could keep one log event, which would it be?
