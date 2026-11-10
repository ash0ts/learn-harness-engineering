## Make one feature the unit of progress

A handoff that says "indexing mostly works" leaves the next session guessing. In this project you shrink the claim until it can be checked: one named feature, one verification record, one commit.

You'll build four things into the app: document metadata, chunking, an indexing status, and answers with citations back to the source, which the starter calls grounded Q&A. Some of them depend on others: retrieval needs the chunks, and a citation only means something if retrieval found the right text. Treat a label that says "indexed" as a claim until you have looked at what was stored.

**What you hand in:** a feature list with evidence, one commit per feature, a session handoff, and proof that a fresh session can carry on from a clean state. Before you start, predict where a broad "done" could be hiding unfinished work.

<!-- cell -->
## The lab: write down the order

Start from the course's Project 03 starter. Before the agent edits anything, draw the dependency chain: metadata, then chunking, then indexing status and grounded Q&A. Use the feature IDs from the starter's list, and make sure each one has an acceptance test you can observe.

Each feature entry needs an ID, a description, its dependencies, a status, the command that verifies it, a path to the evidence, and when it was last tested. Reset any entries that arrive already marked complete. Check the evidence paths too: one that points into a temporary folder that has since been deleted proves nothing.

The agent's startup routine reads `AGENTS.md` and the architecture and product notes, installs and checks the environment, and reads the feature list. Write the startup script, `init.sh`, so those checks are repeatable. Write the handoff and progress log to say where work stopped, and the clean-state checklist to record whether the working tree, the tests and the list of remaining work agree with each other. The starter has none of these four files, and **Download the lab brief and templates** further down this page gives you a template for each.

<!-- cell -->
## The lab: one feature at a time

1. Pick one unfinished feature whose dependencies are done.
2. Build only that feature. If the agent finds something unrelated, it writes it down for later.
3. Run the feature's verification. Look at the stored metadata, the chunk contents, the status changes or the citations, whichever applies.
4. Attach the evidence and change the status only if the check supports it. Record failures as failures.
5. Commit with the feature ID. Write the next step into the handoff before picking another feature.

Stop the agent at a feature boundary and start a new conversation. Give it the files and nothing from the previous chat. Before it edits, ask it to tell you which feature is next and what evidence shows the earlier ones are done.

For grounded Q&A, follow a displayed citation back to the imported document and confirm the text is there; a plausible answer with something citation-shaped after it doesn't count. For indexing, use documents long enough to produce several chunks and check that none of them is empty.

<!-- cell -->
## What happened when we ran it

Our recorded version tests less than the lab does. We let the agent work for one session, kept its patch, and started a second session with no memory of the first. The main comparison is three attempts from each of two starting setups, which the notebook calls treatments. `minimal` got the task and the unfinished app, and `recovery` also got an architecture note and a short `AGENTS.md` with a rule to write `session-handoff.md` before a session ends and read it first on resume. We did not give the agent the feature list or the startup script. The closest it got to the one-feature-at-a-time routine was one sentence in that `AGENTS.md`: "Work one acceptance criterion at a time." Each session was allowed 12 model calls and the agent used all 12 every time, so the break fell wherever call 12 landed. The agent wrote no `session-handoff.md` in any `recovery` attempt, and in five of the six attempts its second session left the patch unchanged.

Neither treatment passed in the main comparison: 0 of 3 each. Four of those six attempts didn't compile, so the grader stopped at the build. For those four, the six checks after the build are marked "not executed" in the figure below and left out of the table under **Inspect one attempt**. The other two compiled and then failed the metadata check, with `wordCount` as the first assertion to fail. One of those two, the `recovery` attempt 0809587e, also failed the check on a single document's indexing status. Its patch is empty, so its grade is the grade of the app we started from, which passed five of the seven checks, the build among them.

The two attempts that compiled did show an answer in the Electron window, which makes a convincing screenshot even though both failed. Compare the screenshot below, from 9d859517, with that attempt's checks under **Inspect one attempt**, and name one requirement you can't check from the screen. Then pick 1500360a (`recovery`, attempt 1) and open Session 2 in Agent Lens. Find the command that looks for `session-handoff.md`, then follow what the agent does from there to its last command, `npm run check`, which fails with three type errors.

<!-- cell -->
## Hand in a restart someone else can repeat

For the lab, hand in the feature list before and after, the per-feature commits, the startup script, the progress log, the handoff, the clean-state checklist and the transcript of the fresh session. Include the patch at the break and your own final checks.

Ask a partner to pick a feature you marked complete and rerun its verification from a clean checkout. Then ask them which feature is next. If they can't do both, work out whether the app is wrong or your records are.

**Discuss:** when a check fails early, what can you say about the behavior the later checks would have tested? Which evidence belongs in the feature entry, and which in the record of the whole attempt? How would you stop a stale "passed" from surviving a later code change?
