## Let the work continue without your next prompt

A loop keeps an agent working after you stop typing. That only helps if the loop knows when to act, which evidence to believe, and when to stop. In this project you take the harness you finished in Project 06 and run three experiments on it: a goal-driven loop against doing the work by hand, a monitor that wakes up on a schedule, and a maker and checker run by a controller.

**What you hand in:** two versions of `goal.md`, a comparison of manual and goal-driven work, a monitoring prompt and a log covering two real hours, three role prompts, at least five recorded maker and checker rounds, and a retrospective.

The course brief links Project 07 starter and solution folders that don't exist at the revision we use. Start from your own verified Project 06 commit instead. Write down which commit, and make a separate branch for each experiment. Pick a medium-sized task with a clear check, such as adding validation for a fixed list of inputs. In the brief you run the goal loop in the agent's `/goal` mode and schedule the monitor with `/loop` or Codex thread automation.

<!-- cell -->
## The lab, experiment 1: by hand versus a goal loop

Write `goal.md` in four parts: the behavior you want, how to verify it, when to stop, and what the agent must not touch. A goal you can test names a command and a threshold, and "make it robust" names neither.

Do the task by hand first, prompting the agent yourself. Record the turns, each time you stepped in, the quality of the result and how long you spent. Then reset to the same starting state and let the goal loop do the same task to the same standard. The loop's progress has to live in files, because each round starts a fresh session.

Revise the goal based on what failed, and keep both versions. If your revision changes the task or the limit on calls or cost, call it a new setup. Compare your own effort only where you measured it, because token counts don't show how long you spent reading a confusing patch.

Give the loop explicit reasons to stop: success, a deadline, a limit on calls or cost, cancellation, and no progress. If two rounds in a row produce the same patch, that's evidence another round may not help, even though the goal isn't met yet.

<!-- cell -->
## The lab, experiment 2: monitor for two hours

Pick a monitoring task where something can change, for example a test suite that your instructor alters in documented ways while the monitor runs. Write a monitoring prompt that states the check, the repair the agent is allowed to make, and when it has to ask a person. Schedule it every 10 to 30 minutes for at least two real hours.

Log every scheduled start and every real start, what was found, what was repaired, each false alarm, each regression, and each time you had to follow up. Save the evidence even when a cycle finds nothing. Otherwise a clean check and a wake-up that never happened look the same.

A sped-up timer is fine for testing that scheduling and cancellation work, but it doesn't replace the two hours. Two hours on the timer is not two hours of model time, so keep three numbers apart: wall-clock time, the time an agent session was running, and the time you spent following up.

<!-- cell -->
## The lab, experiment 3: maker, checker, controller

Write three prompts. The maker changes the app. The checker starts in a fresh conversation with the candidate patch, runs the checks you declared, and reports specific findings. The controller reads those and decides whether to continue, retry, stop or ask a person.

Add an entry to `loop-state.md` for every round: the candidate's revision or checksum, what the maker did, the checker's evidence, the outcome, the next step, and anything you did by hand. The lab asks for at least five recorded rounds. Choose a sequence of tasks with enough distinct work to fill them. Don't switch off a legitimate stop on success or on no progress just to reach five. If the loop stops early, report the experiment as incomplete and change the task design for the next run.

Check that the two roles are separate. Give the checker the acceptance criteria and something it can run. Don't let the maker's explanation of why the patch is right be the only thing it sees. Keep the rejected candidates too, so a later reader can see why the controller asked for another round.

<!-- cell -->
## What happened when we ran it

Our recorded loops do a different job from the lab. Instead of carrying a finished Project 06 app forward, in every round the agent starts in a fresh sandbox and tries to repair the defect planted in the course's Project 04 app, and the grader runs Project 04's checks on the patch.

The timer loop, `project-07-real-timer-qualified.json` under *Checkpoints and decisions*, ran for two real hours, recorded eight rounds that all failed, and stopped at its deadline. Its one recorded intervention falls between rounds 3 and 4: the loop had paused at a shared budget halt, and it was resumed against the same deadline once the ID of a pending round that had never launched was cleared. Rounds 6 and 8 (3ceefbaf and bc00b68c) failed only the Electron check, as did all three rounds of the first goal loop, `project-07-goal-live.json`, which stopped at its round limit (`status` reads `round_limit`). We made those runs at protocol revision 2 of our runner and grader. At that revision an empty patch got the same error on that check, and at revision 4 an empty patch passed it. The goal loop that passed, `project-07-goal-revision4.json`, did so in its first round at revision 4, so don't rank a goal loop against a timer loop from these runs. Two more entries hold a single round each: an earlier timer loop that ended `blocked` after a round recorded as telemetry missing, and a goal loop whose round failed the compile check.

We ran the maker and checker loop twice, once at revision 2 and once at revision 4, and both times it stopped after two rounds because the second round's patch matched the first, which the runner records as `no_progress`. All four patches are empty: in every round the agent used all of its model calls in the Maker, Checker (read-only) and Maker revision steps (10, 4 and 10) without making an edit or writing a review. To see one of those rounds, choose f444fd47 under *Inspect one attempt* and open its Maker step in Agent Lens: none of the commands there changes a file, and one of them prints `src/services/indexing-service.ts`, with the starter's `// BUG:` comment above the defect, before the ten model calls run out.

That leaves most of the lab undone on our side. We have no manual-versus-goal comparison, no monitoring experiment, and no maker and checker loop that got past two rounds.

The timeline below shows the real timer run. Read its rounds as a chain: each round after the first started from the previous round's patch, so they aren't eight independent tries and you can't turn them into a success rate. The patch is all a round inherited: our runner at that revision didn't give the next round the grader's feedback (we added that afterwards), and no timer round wrote the `session-handoff.md` we asked for in the task.

Lecture 13 also covers GPU autoresearch, which is a training workload we didn't run. Our runs used hosted inference and CPU sandboxes.

<!-- cell -->
## Hand in, and defend one stop

Hand in both versions of the goal and the manual comparison; the monitoring prompt and the two-hour log; the maker, checker and controller prompts; the five-round state record, or a clear statement that it's incomplete; and a retrospective covering all three experiments.

Pick one point where a loop stopped and defend that decision from the saved state. If your loop had crashed right after starting an agent session, would resuming have launched a duplicate? What would the controller have to check first? Which miss by the checker did you see happen, and which one are you only worried about?

In your retrospective, report separately where the loop saved you from stepping in and where it only repeated a problem it couldn't solve.
