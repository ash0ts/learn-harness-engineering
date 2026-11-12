## Build the shell twice

In this project you test whether a small harness changes what an agent delivers. By harness we mean what you put around the agent before it starts: an instructions file, a note on how the app is laid out, a list of what counts as done.

The task is the simplest in the course. You ask an agent to build the shell of an Electron knowledge-base app: a window with a document list, a question panel, and a local data directory. You ask twice, once with nothing but the task and once with a harness.

**What you hand in:** two separate attempts at the same task, the harness you used for the second, and a short comparison based on the patches, the commands you ran and what the app did on screen.

Before you run either one, write down what you will accept as a working shell and how you expect each attempt to go wrong. Will the agent forget to save data, break the bridge between the window and the main process, skip launching the app, or say it's finished too early? Put both in `comparison.md` from **Download the lab brief and templates**, and don't adjust your acceptance criteria once you've seen the result. For an attempt you run from this notebook, the prediction box is step 4 under "Run this lesson yourself".

<!-- cell -->
## The lab: set up two workspaces

Start from the course's Project 01 starter, linked from the original course brief under "Sources and further reading" at the bottom of this page. Make two separate workspaces outside this notebook.

The bare workspace has the reference app source removed and gets only the task prompt. The harness workspace gets these files as well:

| File | What it tells the agent |
|---|---|
| `AGENTS.md`, `CLAUDE.md` | How to start, which boundaries matter, how to verify |
| `init.sh` | How to install and check the environment |
| `feature_list.json` | What is unfinished and what counts as accepted |
| `claude-progress.md` | What has happened so far |
| `docs/ARCHITECTURE.md` | What the main process, preload script, renderer and services are each responsible for |
| `docs/PRODUCT.md` | What a user should be able to do in the shell |

Keep the two workspaces apart. If a solution folder sits next to the workspace, or a solution branch is reachable, the agent can find it, whatever your prompt says about ignoring it.

Reset the harness files before you begin: clear the feature statuses, the evidence and the `testedAt` fields in `feature_list.json`, and empty `claude-progress.md`. Harness files that still say "pass" from someone else's solution have already told the agent the answer.

Use the same task prompt and model settings for both attempts. Write down the source revision, the environment, the start time and the limit you're giving the agent. Decide now what happens if you step in to help: either the attempt ends there, or it continues as a separately labelled assisted run.

<!-- cell -->
## The lab: run both, then check the app yourself

1. Give the bare workspace the task. Save the exact prompt and the transcript, and let the agent work until it finishes or hits your limit.
2. Do the same in the harness workspace. Don't rescue either build by hand to improve its score.
3. Export each patch. Write down what the agent claimed separately from what you find.
4. Start the app from a clean environment. Check that the window opens, the document list and question panel appear, and the data directory exists where the app expects it.
5. If you claim something persists, restart the app and check. Keep the command output and what you saw.

It helps to draw Electron's three parts. The main process does the privileged work, like reading files. The preload script exposes a small, typed bridge, and the renderer, which draws the window, can only call that bridge. You open the app in step 4 above because a TypeScript build can pass while the bridge is missing in the running window, and you can't tell from a screenshot of an empty window whether asking a question works.

Grade each attempt as complete, partial or failed against the criteria you fixed at the start. Record the time to the first successful launch, every time you stepped in, the features that were missing, and any claim of success that came before the app worked. If you didn't measure something, leave it blank, and don't use token counts to estimate how long you spent.

<!-- cell -->
## What happened when we ran it

We ran a smaller version of this in sandboxes. The main comparison is six attempts, three per treatment, where a treatment is the setup the agent starts with; twelve earlier trial runs are listed below as Archive and aren't counted. Both treatments started from the same unfinished app source, so neither had to build from an empty folder. In the workspace, `minimal` got only the task file. `explicit` also got a short `AGENTS.md` and a one-paragraph architecture note, which is much less than the full harness in the table above. Both got the same prompt, which also told the agent to read `AGENTS.md` if there was one and to verify its work. Ours is a narrower comparison than the lab and doesn't stand in for it.

A separate grader applied each patch to a clean copy of the app and tested the real thing. In five checks it compiled and built the app, rebuilt the document store and checked the data was still there, indexed a document, asked two questions, and opened the Electron window to check the typed bridge. Before the agent started, we changed the course starter in both treatments: we added tracing hooks to the app's services, corrected the renderer's import paths, and changed how the preload script is built for the sandbox.

Both treatments passed 3 of 3, so we saw no difference in task success. In `explicit` attempt 2 (e53c3cad) the agent changed no files, and the app passed all five checks in the state it started in, with an Import button that only logs a message. The six attempts all started from that app, so the most you can conclude from a pass here is that the agent didn't break anything the grader checks.

That tie doesn't show that instructions are pointless, or that the two would tie on a harder task. We also can't compare what an agent claimed with what the grader found, because five of the six attempts were stopped mid-task at the 24-model-call limit and in the sixth, e53c3cad, the agent stopped on its own after 13 calls without writing a closing message.

Under "Inspect one attempt" below, choose e53c3cad and open its **Coding agent** conversation in Agent Lens. The agent prints `AGENTS.md` with its third command, later runs the two commands that file names, `npm run check` and `npm run build`, and stops without editing a file or launching Electron, which the file also tells it to test. Then open a7dcf5cb, a `minimal` attempt with no `AGENTS.md`, where the agent runs the same two commands anyway; in the other two `minimal` attempts the agent called `npx tsc` and `npx vite build` directly. Pick another rule from that printout and check whether the agent in e53c3cad only read it or acted on it.

<!-- cell -->
## Hand in and discuss

For the lab, hand in both prompts, both transcripts, the exported patches, your launch commands, screenshots, and the harness files from the second workspace. Add a one- to two-page comparison that includes what you measured and your original prediction. An attempt you ran from this notebook is practice and doesn't complete the lab.

Answer three questions. Which requirement was easiest to miss? Which observation changed how confident you were? What one harder task would you fix in place for a follow-up?

Choose a follow-up task where one specific rule could matter, for example a change that touches both persistence and the renderer, and change nothing else.

**Before you move on:** someone else should be able to launch both of your submissions and understand each grade without asking you what you meant by "works".
