## Let the process continue without your next prompt

A loop is useful only if it knows when to act, what evidence to trust, and when to stop. This project turns your completed Project 06 harness into three progressive experiments: manual versus goal-driven work, periodic monitoring, and a maker/checker process.

**Your deliverable:** two iterations of `goal.md`, a manual/goal comparison, a real two-hour monitoring log, three role/control prompts, at least five recorded maker/checker rounds, and a retrospective. These are learner exercises; the saved Forge runs below do not satisfy all of them.

The frozen original brief links Project 07 starter/solution folders that are absent at that revision. Start from your verified P06 final commit instead. Record that commit and make separate goal, timer, and maker/checker branches. Choose a medium task with a clear check, such as adding validation across a bounded set of inputs.

<!-- cell -->
## Experiment 1 · Manual work versus a goal loop

Write `goal.md` with four parts: the desired behavior, a reproducible verification method, stop conditions, and boundaries the agent must respect. A testable goal names the command and threshold; “make it robust” does not.

Run a manual baseline first. Record turns, interventions, result quality, and your actual time spent. Then reset to the same starting state and run the goal-driven condition using the same task and quality standard. Preserve the loop's progress in files between fresh sessions.

Revise the goal based on what failed and retain both versions. If the revision changes the task or allowance, label it as a new condition. Compare observed human effort only where you actually measured it. Token usage cannot tell you how long you spent reading a confusing patch.

Use success, deadline, call/cost bound, cancellation, and no-progress detection as explicit stop reasons. A repeated identical patch is evidence that continuing may be pointless, even when the headline goal remains unfinished.

<!-- cell -->
## Experiment 2 · Monitor for at least two hours

Choose a monitoring task that can produce new information, such as checking a controlled test suite while the instructor introduces documented fixture changes. Write the check, permitted repair, and human escalation rule. Schedule it every 10–30 minutes for at least two real hours.

Record each scheduled and actual start, finding, repair, false positive, regression, and follow-up intervention. Save the evidence even when a cycle finds nothing. A missed wake-up and a clean check are different outcomes.

An accelerated timer test is useful for validating scheduling and cancellation, but it does not replace the two-hour observation. Keep wall-clock duration, active worker time, and human follow-up time separate. A two-hour timer does not mean two hours of model computation.

<!-- cell -->
## Experiment 3 · Maker, checker, controller

Write three prompts. The maker changes the app. The checker gets a fresh context and a candidate patch, runs the declared checks, and returns concrete findings. The controller decides whether to continue, retry, stop, or ask a person.

Persist a `loop-state.md` entry for every round: candidate revision/checksum, maker action, checker evidence, outcome, next action, and intervention. Run at least five recorded rounds for the original exercise. Choose a bounded task sequence with enough distinct work to make those rounds meaningful; do not disable a valid success/no-progress stop merely to manufacture five repeated attempts. If the loop stops early, report the exercise as incomplete and revise the next run's task design explicitly.

Review the separation of contexts. The checker should not inherit the maker's persuasive explanation as its only evidence. Give it the acceptance contract and executable result. Preserve rejected candidates so a later reader can understand why the controller took another turn.

<!-- cell -->
## What was actually executed in Forge

The saved loop runner repairs the Project 04 defect in CPU sandboxes. That is a different task from carrying a completed P06 app into the original three experiments.

The real timer ran for two hours, recorded eight failed rounds and one observed human intervention, then stopped at its deadline. A later goal run passed. The maker/checker run stopped after two rounds with `no_progress`. We did not complete the original manual-versus-goal study, monitoring comparison, or five-round maker/checker assignment.

The timeline below shows the actual timer sequence. Treat its rounds as dependent attempts: each one can inherit the previous patch and feedback. They are not independent repeats for estimating a treatment's success rate.

Lecture 13 also discusses GPU autoresearch. That case uses a different training workload. This course campaign used hosted inference and CPU application sandboxes; it provides no GPU training or utilization evidence.

<!-- cell -->
## Submit and audit the stopping decision

Submit both goal versions and the manual comparison; the monitoring prompt and two-hour log; maker, checker, and control prompts; the five-round state record or an explicit incomplete status; and a retrospective covering all three experiments.

Choose one stop and defend it using the saved state. Could a crash after launching a worker cause a duplicate run on resume? What would the controller need to reconcile first? Which checker miss did you observe, and which hypothetical miss is only a concern for future testing?

Your conclusion should explain when the loop reduced observed intervention and when it simply repeated an unresolved problem. Keep those two experiences separate.
