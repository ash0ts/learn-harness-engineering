## Give three teams the same feature

Adding a reviewer sounds like an obvious improvement. But if the total budget is fixed, every model call the reviewer makes is one the implementer doesn't get. Add a planner and the implementer's share shrinks again. In this project you test that trade.

You build the same upgrade to the app's conversation history three times, in three separate workspaces: with one agent doing everything, with a maker (the implementer) and a checker (the reviewer), and with a planner, a maker and a checker. The finished feature has to show each full question and answer, the citations, a confidence value, and a confirmation before history is cleared.

**What you hand in:** three patches for the same feature, the plans and reviews the extra roles produced, and one independent rubric applied to all three. Before you start, predict what the extra roles will catch and what they might leave unfinished.

<!-- cell -->
## The lab: fix the feature and the rubric first

Use the three variants in the course's Project 05, and check before you start that all three begin from the same app and ask for the same feature. The role instructions are the thing you're varying. Keep the model, the fixture, the generation settings and the total allowance the same.

Write the acceptance criteria before the first attempt:

- History keeps its order and shows the full question and answer, including long ones.
- Citations can be expanded and stay attached to the right answer.
- Confidence is shown with the item it belongs to.
- Clearing asks for confirmation. Cancelling keeps the history; confirming clears it.
- Import, indexing, Q&A and persistence still work.

Grade all three with the same independent check. A checker inside an arrangement is part of how that arrangement works, so its "pass" is one more thing you grade. Keep its rubric, its notes, and any place it disagreed with the independent check.

<!-- cell -->
## The lab: run the three arrangements

**One role.** A single agent plans, edits and verifies in one conversation. Keep its self-checks.

**Maker and checker.** Start the checker in a separate conversation with the task, the maker's patch and the evidence it's allowed to see. It returns specific findings. Give those to the maker for a revision, and record which findings were fixed and which were disputed.

**Planner, maker and checker.** The planner writes a plan first: scope, acceptance criteria, and how work is handed over. The maker implements that plan and the checker tests what was built. Planned behavior the maker didn't implement gets no credit.

Write down the total allowance and each role's share of it. If the three-role version gets more calls in total, you're answering a different question. Also write down which files and which conversation history cross from one role to the next. If the checker can read the maker's whole conversation, the two roles aren't separate.

<!-- cell -->
## What happened when we ran it

We gave every attempt 24 model calls and split them three ways. `single-role` gave all 24 to one agent, which stopped on its own after 14, 19 and 11 calls in its three attempts. `gen-eval` gave the maker 10, the checker 4, and the maker 10 more to revise. `plan-gen-eval` gave the planner 4, the maker 8, the checker 4, and the maker 8 to revise. The planner and checker could read and run things, but any file changes they made were thrown away, so neither could become a second maker.

That's nine attempts, three per arrangement (shown as Treatment in the notebook's tables). `single-role` passed 2 of 3, `gen-eval` passed 2 of 3, and `plan-gen-eval` passed 0 of 3. Of the five failures, three didn't compile and two cut off the full answer in the history view.

We can't pin that on the number of roles alone. The task and the total allowance were the same, but `single-role` got no instructions file, while `gen-eval` and `plan-gen-eval` got the same `AGENTS.md` and architecture note. In all six attempts with extra roles, every planner and checker spent its four calls reading files and was cut off before writing a plan or a review, so no maker received either. In three of the six (`ca16eac7`, `ef04c221` and `79398b0b`) the maker's revision left the patch unchanged. From the nine attempts, we can say only that on a 24-call budget the arrangement with a planner passed none of its three.

The course materials include a finished example of each arrangement with a rubric score out of 5: 1.6 for `single-role`, 3.3 for `gen-eval` and 4.9 for `plan-gen-eval`. We didn't measure those, and they aren't in our data.

Under *Inspect one attempt* below, choose `ef04c221`, a failed `plan-gen-eval` attempt, and open its **Checker (read-only)** step in Agent Lens. List the commands the checker ran. Did any of them build the app, or did the checker only read files? Then open **Maker revision** and find `npm run check` near the end. Compare what it printed with the failed check in the attempt's table of checks, and see what the maker did next. Did the maker have enough calls left to fix that error? A defect the checker missed and a fix the maker ran out of calls for are two different failures.

Then pick a passing attempt and read its table of checks. Order, the full answer, citations, confidence, cancel and confirm are all asserted inside one row, `Electron window, preload, import, indexing and question UI under Xvfb`, so a pass there is the test evidence that cancel kept the history. The screenshot below, from `73c46965`, was taken after the grader confirmed the clear, so its history panel is empty. Our grader accepts a confidence label or value and a citation excerpt anywhere on the page and never restarts the app, so we didn't check that each sits with its own answer or that history survives a restart.

<!-- cell -->
## Hand in and discuss

Hand in the three patches, the role prompts, the plan, the checker's rubric and notes, how you split the calls, the one independent rubric applied to all three, and a comparison.

Explain one failure that happened where one role passed work to the next, and point to the place in your agents' conversations that shows it. Finish by proposing one change you'd test next, to the split or to what passes between roles, and label it as a new experiment.
