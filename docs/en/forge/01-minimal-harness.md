# Six passing runs, no separation

The first comparison was supposed to make the role of repository instructions visible. We gave Pi an unfinished knowledge-base app and asked it to produce a usable shell: load the Electron window, show imported documents, accept a question, and preserve data. One treatment received minimal instructions. The other also received explicit repository rules and a short architecture guide.

Both passed all three attempts in the qualified comparison. We had six working submissions and no observed difference in task success. That is a perfectly serviceable result for a course, even if it makes a poor advertisement for adding more instructions.

## The minimal condition already has a lot around it

Calling a coding agent “prompt-only” can hide the machinery doing the work. Our minimal treatment still had Pi's tools, a task statement, a running environment, the starter application, a model-call limit, and a way to execute commands. It also had the shared build adaptation needed to load the preload code in Electron's sandboxed renderer environment.

That adaptation was part of the frozen baseline for both treatments. We did not give one treatment a functioning build path and ask the other to discover it. The application hash includes the adaptation so a later reader can check that equality.

The explicit treatment added an `AGENTS.md` file and an architecture note. Its instructions asked the agent to inspect before editing, keep the main/preload/renderer boundaries, work through acceptance criteria, run checks, and report incomplete work. The architecture note named the responsibilities of the services and the renderer's typed interface.

The [SWE-agent paper](https://arxiv.org/abs/2405.15793v3) studies how an agent's computer interface affects repository navigation, editing, and execution. It provides a reason to treat the environment around a model as an experimental variable. Our comparison changes repository instructions within Pi; it does not reproduce SWE-agent's interface experiments or compare Pi with SWE-agent.

## What had to work

Electron divides responsibility across processes. The main process can read and write documents. The preload exposes selected operations to the window. The renderer calls those operations and displays the results. A repair that bypasses this division may appear to work while giving renderer code filesystem access the course explicitly forbids.

We therefore asked the protected checker to do more than compile the submission. It reconstructed a document service against saved data, verified the imported content, indexed a document, and asked two questions. In the Electron window, it checked that the typed bridge existed and that `window.require` remained unavailable. It then waited for the answers to appear on screen.

The two answers are a small but deliberate choice. A one-answer demo can miss failures in accumulated history or in the UI update after a subsequent request. Two turns do not test every history behavior, but they exercise a handoff that a single successful call cannot cover.

Pi's own checks were part of its working process. The final grade came from a separate sandbox after the coding sandbox had stopped. That keeps a test modified by the agent from becoming the sole authority on the patch it just wrote.

## Six attempts on one task

Minimal instructions passed 3/3 attempts. Explicit rules passed 3/3. The attempts used the same application bytes, model settings, fixture, and protected checker within the comparison, with treatment order rotated across repeats.

We tested one app shell under one bounded setup. With three attempts each and no observed failures, we have little information about rare failures or harder tasks. A tie here leaves both a benefit and a cost from the extra instructions unresolved.

The task may be too easy to separate these treatments under this configuration. That is a hypothesis for the next experiment. It is not something the six passes prove.

We also cannot use this row to explain the much weaker results in Project 02 or 03. Those projects ask for different behavior. A change in task difficulty is enough to change the outcome, even if the instructions have no effect at all.

## Inspect the successful patch, too

When a patch passes, it is tempting to read only the green row. For this exercise, choose one passing attempt from each treatment and compare the exported diffs. Identify which files changed, which checks the agent ran, and which of the required behaviors the protected checker observed.

Then inspect the Agent Lens conversation. Did the explicit treatment read its instructions? Did it act on a boundary rule at a point where the minimal treatment made a different choice? A trace can support that behavioral observation. It cannot turn two passing results into evidence that one treatment improves task success.

There is another distinction worth preserving. An agent may finish its allocated calls without writing a final declaration of success, yet leave a patch that passes. It may also announce completion before the checker discovers a broken window. The course records the exported result separately from the actor's completion status.

## A next experiment that could teach us more

I would keep this comparison as the working baseline and add a task that stresses a specific rule. For example, require a feature that touches both document persistence and the renderer, then test whether either treatment introduces a direct Node import in the renderer. The rule now has an observable opportunity to matter.

That would be a new experiment. The task, expected behavior, and check would need to be frozen before the runs. Adding a harder task after seeing a tie is reasonable follow-up work; it belongs in a separately identified comparison.

For the next comparison, I would carry both treatments forward and keep the explicit rules short enough to inspect.

Open the [saved Project 01 notebook](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTQ%3D) with private-project access. The [public results report](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/forge/results/README.md) records the qualified cohort separately from earlier UI-check cohorts. [Project 02](./02-workspace-docs.md) follows what happened when the task required a file-picker import flow across two fresh conversations.
