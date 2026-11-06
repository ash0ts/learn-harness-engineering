# Writing a repository guide an agent can use

A new coding session opens a repository and has to decide where to start. A short guide can name the test command, explain an unusual boundary, or point to unfinished work. It can also give the agent another document to read while the import button stays broken.

In Project 02, we compared minimal instructions with a workspace-docs treatment. The task required document import, full-content detail, persistence across service reconstruction, and a file-picker flow in Electron. Both treatments worked across two fresh Pi conversations. Neither passed any of its three qualified attempts.

The failures were narrower than that score suggests. All six submissions passed the recorded compile, import/persistence, indexing, and Q&A service checks. All six timed out during the Electron acceptance stage. A repository guide had not been enough to complete the UI flow.

## What information the guide adds

Our workspace treatment staged an `AGENTS.md` file and a short architecture document. The main process owns filesystem access. The preload exposes typed inter-process communication, or IPC. The renderer calls `window.knowledgeBase` rather than reaching into Node directly. The guide also asked the agent to write a handoff file before ending a session and to read that file when it resumed.

These instructions reduce the need to rediscover local conventions. They do not supply the implementation of the file picker, nor do they guarantee that the agent understands the existing import path.

We deliberately kept both treatments on the same unfinished source. Giving the documented condition a reference solution would answer whether extra working code helps, which is a much less interesting question. The stage contains the task, selected guide files, application code, and sample data. It excludes historical scores.

Each conversation gets 12 model calls, for a 24-call allowance across the trial. The second conversation sees the workspace left by the first, but it does not receive the first conversation's full message history. This tests a specific kind of continuity: recovering from files in a surviving workspace.

## The research does not say “write a bigger AGENTS.md”

Gloaguen and colleagues' [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988v3), revised in September 2026, examines generated and developer-committed repository context files across coding agents. They report that context files do not generally improve task success in their settings, while increasing inference cost by more than 20% on average. Their analysis distinguishes following instructions from completing the task: agents can obey a guide and still spend effort that does not help the repair.

Their repositories, tasks, agents, and context files differ from this course. The paper gives us a reason to test the guide, but cannot establish why our import flow failed.

For this app, I would use the guide for information the agent cannot safely infer from a directory name. The location of persisted state, the allowed renderer interface, and the command that exercises an Electron window qualify. A paragraph describing every service in the repository may merely repeat what a file search can reveal.

The choice is about the decision each instruction changes. If a sentence cannot identify one, it is a candidate for removal from the treatment, followed by a new frozen comparison. Deleting prose because it feels verbose is an editorial judgment; claiming that deletion improves an agent requires another run.

## A service import is easier to test than a user's import

The service checker calls the import method with a real path, reconstructs the service against its saved directory, and reads back the document. That establishes a persistence behavior under the fixture. It bypasses the interaction through which a user chooses a file.

The UI checker starts Electron under Xvfb, supplies the sample path through the file-selection mechanism, and waits for the application to report an imported document. It also checks full-content access through the typed bridge, then continues through indexing and question answering.

Those operations cross several boundaries:

| Boundary | Evidence to inspect |
| --- | --- |
| File selection to import request | Does the click or file input produce the expected call? |
| Renderer to preload | Is the method present with the expected arguments? |
| Main process to persistence | Does the selected file become a stored document? |
| Persisted result to rendered view | Does the UI refresh and show the content? |

The recorded timeout tells us the UI acceptance stage did not reach an expected state. It does not locate the first broken boundary. Inspect the corresponding command output and patch before calling it a file-picker bug, a refresh bug, or an IPC bug.

This is where the all-zero score becomes less satisfying and more instructive. There is working service behavior to preserve. There is an end-to-end path that still fails. Rewriting the architecture guide before locating that failure risks spending another six trials on the wrong intervention.

## Make a handoff that names the unresolved operation

For a learner reviewing these runs, start with one failed UI attempt and write a small handoff from its evidence. Name the last operation confirmed to work, the next state the checker waited for, the relevant files, and the exact command needed to reproduce the failure. Mark an unverified explanation as a hypothesis.

For example, “import works” is too broad if only the service method was tested. “The service stores and reloads the fixture; the Electron stage times out before its expected state is observed” preserves the distinction the next session needs. It does not pretend to know the cause.

Then compare that handoff with what the agent left on disk. A next session should be able to spend its first few calls reproducing the unresolved operation. If it instead repeats every completed service check, the handoff may be carrying history without carrying the next decision.

Use the [Project 02 notebook](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTU%3D) to select the saved attempts; it requires private-project access. The [public report](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/forge/results/README.md) preserves their grades. [Project 03](./03-session-recovery.md) examines the state that survives when the next conversation starts.
