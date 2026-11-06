# Project 07. Build Your First Automated Loop

> Related Lecture: [L13. Why You Need to Stop Prompting Your Agent](./../../lectures/lecture-13-loop-engineering/index.md)

## What You'll Do

This is the transition project from "Harness" to "Loop." You already know how to set up an agent with a proper environment, instructions, and feedback — now you'll turn that setup into a loop that runs on its own.

You'll do three progressive experiments: first turn a task from manual to `/goal`, then turn a monitoring task into a `/loop` timer, and finally build a full maker-checker loop to experience what it feels like when **you step outside the loop.**

## Project Files

Repo path: [`projects/project-07/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-07)

| Directory | What's Inside | What You Do |
|-----------|--------------|-------------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-07/starter) | A small knowledge base project with a complete harness (P06 final state), including AGENTS.md, feature_list.json, init.sh, session-handoff.md, clean-state-checklist.md. | Turn this harness into one that can loop automatically. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-07/solution) | Full implementations of three loops: goal loop, timer loop, maker-checker loop, plus loop state files and verification scripts. | Reference for loop design patterns and state management. |

## Tools You'll Use

- Claude Code or Codex
- Git
- Your complete harness from P06
- A terminal multiplexer (tmux or screen, for observing long-running loops)
- Optional: GitHub Actions or cron (for advanced event-driven / scheduled experiments)

## Steps

### Prep

1. Start from the same commit where you finished P06.
2. Create three branches: `p07-goal-loop`, `p07-timer-loop`, `p07-maker-checker`.
3. Confirm your harness works: run init.sh, verify state file, feature list, and handoff docs are all in place.
4. Pick a **target task** you want the loop to work on repeatedly. Choose something medium-sized with clear completion criteria — e.g., "add unit tests to all modules, reaching 80% coverage" or "add input validation to all API endpoints."

### Experiment 1: Goal Loop — From Manual Run to Auto Run

Switch to the `p07-goal-loop` branch.

1. **Write the goal description**: Turn your chosen task into a `goal.md` file containing:
   - Clear goal ("what counts as done")
   - Verification method ("how to confirm it's done" — run tests? run lint? check coverage?)
   - Stop condition ("when should it stop" — max turns? time limit? budget limit?)
   - Constraints ("what not to touch" — production config, database schema, etc.)

2. **First manual run**: Give the task to the agent manually, yourself. Record how many turns it took, how many times you intervened, and the result quality. This is your baseline.

3. **Run with `/goal`**: Use the same `goal.md` as input and run it in `/goal` mode. The agent loops on its own until the goal is reached or the stop condition triggers.

4. **Compare results**:
   - Difference in turn count
   - Difference in your intervention count
   - Difference in result quality (using the same verification standard)
   - Difference in time you spent

5. **Iterate on goal.md**: If the results are poor, revise the goal description and run again. Keep going until you're satisfied with the results, or until you've confirmed the limit of what a goal loop can do on this task.

### Experiment 2: Timer Loop — Turn Monitoring Into a Heartbeat

Switch to the `p07-timer-loop` branch.

1. **Pick a monitoring task**: Find a repetitive check you normally do manually. For example:
   - Run the test suite every hour, fix failures
   - Check for dependency security updates every morning
   - Check for coding style violations after each commit
   - Periodically scan TODO comments to see which ones are stale

2. **Write the monitoring prompt/script**: Lay out the monitoring steps clearly — what to check, what to do when problems are found, and when to call a human.

3. **Run with `/loop` (or Codex Thread automation)**:
   - Set a reasonable interval (10-30 minutes recommended — too short and you'll be annoyed, too long and you won't see the effect)
   - Let it run for at least 2 hours (or go do something else and come back later)

4. **Record the results**:
   - How many problems did it find?
   - How many did it fix on its own?
   - How many were false positives?
   - How many did it make worse?
   - How much time did you spend following up on its results?

5. **Reflect**: Is this monitoring task worth automating? Compare the time you saved vs. the time you spent following up. If it's not worth it, did you pick the wrong task, or is the loop poorly designed?

### Experiment 3: Maker-Checker Loop — Take Yourself Out of the Loop

Switch to the `p07-maker-checker` branch.

This is the most important of the three experiments. You'll build a **complete loop that doesn't need you to be there:**

1. **Design the loop structure**:
   - **Maker agent**: implements, writes code, modifies files
   - **Checker agent**: verifies, runs tests, does code review, passes / fails
   - **State file** (`loop-state.md`): records current round, what was done, verification results, what's next
   - **Stop condition**: N consecutive passes, or maximum rounds reached

2. **Write three prompts**:
   - Maker instructions (what to do, how to do it, what not to touch)
   - Checker instructions (what to verify, how to verify, what counts as pass, how to give feedback)
   - Loop control logic (who goes first, how handoff works, how to start the next round)

3. **Run at least 5 rounds**:
   - Round 1: Maker implements → Checker verifies → Fail → Feedback to Maker
   - Round 2: Maker revises based on feedback → Checker verifies → ...
   - ...
   - Until consecutive pass, or you call it

4. **Record each round's state**:
   - Round number
   - What the Maker did
   - What problems the Checker found
   - Pass / fail
   - Did you intervene? (if yes, why?)

5. **Final retro**:
   - How many times did you intervene? Why?
   - What would have happened if you hadn't intervened?
   - Did the Checker miss any problems?
   - Did the Maker keep making the same mistake?
   - Where is the quality ceiling of this loop? Maker capability, or Checker capability?

## How to Measure Results

| Metric | Exp 1 (Goal) | Exp 2 (Timer) | Exp 3 (Maker-Checker) |
|--------|-------------|--------------|----------------------|
| Task completion rate | Was the goal reached? | How many monitoring cycles ran? | How many rounds until pass? |
| Human interventions | How many times did you step in? | How much time did you spend following up? | How many times did you intervene? |
| Result quality | How does it compare to manual? | False positive rate? Missed issues? | How many issues did Checker find that you wouldn't have? |
| Time saved | How much time did you save? | Is it worth automating? | Time spent designing the loop vs. time saved |
| Reliability | Was the stop condition trustworthy? | Did it run away? | Can the loop get stuck in the same place? |

## What to Submit

- `goal.md` (Experiment 1's goal description, at least two iterations)
- Experiment 1 comparison notes: manual vs goal loop
- Experiment 2 monitoring prompt + 2-hour run log
- Experiment 3's three prompts (Maker / Checker / Loop control)
- Experiment 3's `loop-state.md` (at least 5 rounds recorded)
- Final retro: takeaways from all three experiments, how your understanding of loop engineering changed, what things are good candidates for loop-ification and what aren't

## Related Lectures

- [Lecture 13 — Why You Need to Stop Prompting Your Agent](../../lectures/lecture-13-loop-engineering/index.md)
- [Lecture 12 — Why Every Session Must Leave a Clean State](../../lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md) (every round of a loop needs clean state)
- [Lecture 11 — Why Observability Belongs Inside the Harness](../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md) (you need to see what's happening inside the loop)
- [Lecture 05 — Why State Files Are the Backbone of Continuity](../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) (loop state files are an extension of state files)


## Optional Forge experiment

Read [Two hours of agent work, with a stop condition](/en/forge/07-bounded-loops) for the executed Forge experiment and its saved notebook. The [Forge overview](/en/forge/) explains the shared setup. The offline exercise remains the default.
