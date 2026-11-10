## Make the whole harness earn its place

By now most of the app exists. The capstone is about whether your way of running an agent on it is reliable. Can a new session start, make the requested changes, verify them, leave things clean, and then do it again?

You run a fixed set of tasks twice, once with a weak setup and once with the strongest harness you've built. Then you remove one piece of the harness at a time and rerun, which is how you test a claim like "this file helps".

**What you hand in:** the complete harness, a controlled comparison on the task set, evidence from cleanup and a rerun, and the results of removing one component at a time. Before you start, predict which component matters most and what failure you expect to see without it.

<!-- cell -->
## The lab: fix the task set and assemble the harness

Start both setups from the same Project 06 app code and the same tasks. Write down what has to work: import, indexing, retrieval, Q&A, history, feedback and reset, as far as your task set covers them. The starter has gaps on purpose. Leave them alone until the attempt begins.

Build the harness from what you made in earlier projects: startup instructions and `init.sh`, the architecture and product notes, the feature list, the handoff and progress log, the clean-state checklist, quality criteria, checker instructions, and verification commands anyone can rerun. Keep each fact in one file. If five files state the acceptance criteria and two of them disagree, you've made yourself a second debugging job.

Decide what cleanup means before you run anything. Which generated files, caches, test data and temporary artifacts get removed? Which evidence has to survive? Check `git status`, write a cleanup report, and don't tidy away the only copy of a failed run's logs.

<!-- cell -->
## The lab: compare, clean up, then remove one piece at a time

1. Run the weak setup and the full harness from the same starting app. Export both patches and grade them independently.
2. Do the cleanup you defined, then rerun from a clean environment. See whether the same commands and fixtures give the same result.
3. Put the full harness back. Remove exactly one component, such as the handoff or the architecture guard, and run the same tasks under the same limits.
4. Restore it before you remove a different one. Label every run and keep the exact files it started with.
5. Compare each run against the failure that component was supposed to prevent. If something unrelated broke, don't blame the missing piece without evidence.

Parts of the course's `benchmark.sh` simulate the work. Copying files or estimating chunk counts can illustrate the exercise, but it doesn't show the real services or the window working. For your evidence, run the real services and open the real Electron app, and keep compiling, service behavior and what's visible on screen as three separate checks.

Before you read our results, write down what a user would expect a reset to do.

<!-- cell -->
## What happened when we ran it

Our recorded version is a narrower task. The agent had to add persistent feedback and a data reset on top of the existing import, indexing and Q&A path. We also asked it for `scripts/benchmark.sh`, a clean-state checklist and a handoff, and our grader checked none of those. We compared `minimal`, which got only the task, with `capstone`, which got an instructions file, an architecture note and a rule to keep a handoff file. We did not run the lab's full task set, the cleanup-and-rerun step, or any run with one component removed.

In the main comparison, `capstone` passed 3 of 3. `minimal` passed 1 of 3, and its two failures didn't compile. We gave `capstone` three things at once, so we can't say which of them, if any, made the difference. No passing patch contains a checklist or a handoff file, although `capstone`'s instructions told the agent to write `session-handoff.md`, and all four passing attempts were stopped at the limit of 24 model calls.

Under **Inspect one attempt**, open the **Coding agent** conversations of `4eb48651` (`capstone`, passed) and `1fb04273` (`minimal`, failed) in Agent Lens, and in each look for a type-check command such as `npm run check` after the agent's edits. In `4eb48651`, the second run of the agent's own `scripts/benchmark.sh` fails after creating a `test-data-` directory, and that directory is still in the patch we graded.

Then we looked closely at the passing attempts and found a gap in our own grader. In its last check, which drives the Electron window, the grader submitted one feedback entry and read it back without restarting the app, then called `app.resetData()` through the app's bridge and asserted four things: no documents, no Q&A history, no feedback, and no citations on the next question. But we didn't assert that the screen refreshed, and the Electron window could still be showing the old document list and the old answer, as in the capture below.

Compare what you wrote about reset with what our grader tested, which you can read in the `project-06` block of `forge/graders/check.cjs` on the `codex/forge-publication` branch of the course repository. Then write the missing check in your observation worksheet as a proposed change to the grader. Don't apply it to the old scores, because a changed check is a new protocol and those attempts were graded under the old one.

<!-- cell -->
## Hand in and discuss

Hand in the full harness, the task set, the weak and full patches with their grades and your comparison, the cleanup report, the evidence from the clean rerun, each run with one component removed and its result, and a final review against your quality criteria. Say which observations support each component, which are still inconclusive, and whether your prediction about which component matters most held up.

**Before you move on to loops:** someone else should be able to run your startup routine, find the unfinished work, run the checks and follow the handoff without talking to you. A loop will repeat whatever that routine does, including the parts that don't work.
