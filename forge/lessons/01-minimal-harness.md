## Build the shell twice

The first exercise asks a simple question: does giving an agent a small, usable harness change what it delivers? You will ask it to build an Electron knowledge-base shell with a document list, a question panel, and a local data directory. The interesting moment is the first real launch, when source code becomes a window someone can use.

**Your deliverable:** two isolated attempts at the same task, the harness used in the stronger condition, and a short comparison grounded in patches, commands, and visible behavior.

Before running either condition, predict its most likely failure. Will the agent forget persistence, break the preload bridge, skip launch verification, or announce completion too early? Write your prediction in the worksheet. Do not change the acceptance criteria after seeing the result.

<!-- cell -->
## Prepare the original exercise

Use the original Project 01 starter and brief linked below. The weak condition removes the reference application source and receives only the task prompt. The stronger condition receives the minimal harness. Make two separate workspaces; a sibling solution directory or accessible solution branch can contaminate the comparison even when the prompt says to ignore it.

The stronger workspace needs these files:

| File | What it tells the next agent |
|---|---|
| `AGENTS.md`, `CLAUDE.md` | How to start, which boundaries matter, how to verify |
| `init.sh` | How to install and check the environment |
| `feature_list.json` | What is unfinished and what counts as accepted |
| `claude-progress.md` | What has actually happened so far |
| `docs/ARCHITECTURE.md` | Main, preload, renderer, and service responsibilities |
| `docs/PRODUCT.md` | The user-visible behavior the shell must support |

Reset feature statuses, evidence, and `testedAt` fields before the run. Clear inherited progress. A starter containing “passed” entries from someone else's solution is already telling the agent an answer.

Use the same task prompt and model settings for both attempts. Record the source revision, environment, start time, and limit. Decide in advance whether intervention ends the autonomous attempt or becomes a separately labeled assisted continuation.

<!-- cell -->
## Run, then verify

1. Give the weak workspace the task. Save the exact prompt and transcript. Let the agent work within the agreed limit.
2. Repeat in the strong workspace with the harness present. Do not manually rescue either build to improve its score.
3. Export each patch and record the agent's completion claim separately from the outcome.
4. Start the app from a clean environment. Confirm the window opens, the document list and question panel render, and the local data directory exists where the application expects it.
5. Restart the app to check anything you claim is persistent. Capture the relevant state and command output.

Electron has three boundaries worth drawing on the board: the main process handles privileged work, preload exposes a narrow bridge, and the renderer calls that bridge. A successful TypeScript build does not establish that the bridge is available in the running window. Nor does a screenshot of an empty window establish that the question flow works.

Measure completion as complete, partial, or failed against the frozen criteria. Record time to first successful launch, actual human interventions, missing features, and premature success claims. Leave unknown measurements blank rather than estimating them from token counts.

<!-- cell -->
## The recorded Forge case changed the starting point

Our saved experiment gave both treatments the same unfinished application source. The stronger treatment added a short `AGENTS.md` and architecture note. That differs from the original source-removed weak condition and its full minimal-harness package. Treat these six runs as an **adapted comparison**, not a replication of the original assignment.

Both treatments passed 3/3 qualified attempts. The protected checker reconstructed document persistence, indexed a document, asked two questions, and inspected the actual Electron window and typed preload bridge. The common baseline included the preload build adaptation needed by the sandbox environment.

The tie is worth teaching. There is no observed separation in task success here. It does not prove that instructions never help, or that the treatments are equivalent on harder tasks. This task may not stress the rules enough to reveal a difference.

Use the matrix and capture below to choose one passing run from each condition. Read the patch before the trace. Identify a boundary rule that could have changed an implementation decision, then find whether the trace supports that observation. Reading a rule is not the same as benefiting from it.

<!-- cell -->
## Submit and discuss

Submit both prompts, transcripts, exported patches, launch commands, screenshots, and the stronger workspace's harness files. Add a one- to two-page comparison with the measured outcomes and your original prediction.

Answer three questions: which requirement was easiest to miss, which observation changed your confidence, and what single harder task would you freeze for a follow-up experiment? A good follow-up gives a specific rule an observable opportunity to matter—for example, a change spanning persistence and the renderer—without changing several variables at once.

**Before moving on:** another learner should be able to launch both submissions and understand each grade without asking you what you meant by “works.”
