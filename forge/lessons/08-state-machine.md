## Write down the workflow that's in your head

Your loop already follows a graph: implement, test, inspect, retry, approve. You know which step comes after which and what happens when one fails, but so far only in your head. In this project you write it down as explicit steps and transitions, and save enough state that the work can pause, split into parallel checks, and resume.

Start from the workflow you ran in Project 07. You don't need LangGraph or any other framework. A state machine in TypeScript is fine, as long as the state, the routing, the parallel work, the rollback and the human decisions are all written down.

**What you hand in:** a graph contract, a serial-versus-parallel experiment, evidence of a targeted rollback, and two complete human reviews. Before you start, predict one transition that currently depends on a person remembering what comes next.

<!-- cell -->
## The lab, experiment 1: draw the contract

Write `graph.md`. For each node (a step) give its purpose, inputs, outputs, the state it owns and what it does on failure. List every edge (a transition between two nodes) and the condition for taking it. Find at least one edge you'd never written down, such as what happens to the UI test when the code doesn't compile.

Define the shared state that has to survive a restart: the task revision, the candidate patch's checksum, which checks have finished, where the evidence is, the retry count, any decision that's waiting, and the reason for stopping. Give each field one owner. A node working from an old copy of the state shouldn't be able to overwrite another node's result.

Save a checkpoint before and after any work that happens outside the graph, like starting a sandbox. When the graph resumes, it should first settle anything that was in flight, and only then start replacements. Draw the paths for cancellation, infrastructure errors and missing telemetry next to the paths for success and task failure, because a diagram with only the success path leaves out the ones that cost money when they go wrong.

<!-- cell -->
## The lab, experiment 2: serial versus parallel checks

Choose checks that can each run in their own workspace against the same exported patch. Say what each lane (one check in its own workspace) receives, and write the rule for joining the results: which lanes are required, how failures combine, and what happens when a lane times out.

Run the same patch through the same checks one after another, then side by side. Record the resources and fixtures both times. Give each lane its own worktree or sandbox so they can't change each other's files. Record wall-clock time, model and token usage where there is any, infrastructure cost, and the results.

Running in parallel isn't always faster. Startup time, competition for resources and waiting on the slowest lane can each eat the gain. Measure it, and if you want to talk about how much it varies, repeat the run under the same conditions.

<!-- cell -->
## The lab, experiment 3: roll back to the right place, and ask a person

Write a routing rule for each kind of failure. A bad plan goes back to planning and a defect in the code goes back to the maker. An infrastructure timeout needs its unfinished work settled; rewriting the code won't help. Before any rollback, keep the rejected candidate and its evidence.

Add a node that pauses for a human decision. The review request has to name the exact candidate by checksum, the task, the grade, the known limitations, and the two choices (approve or reject). The graph resumes only on an explicit decision tied to that checksum, so an approval given to one patch does not carry over to another.

Do two full reviews. For each, record the decision, what the reviewer caught, where they agreed or disagreed with your graph's checks, and how long the graph waited. Don't auto-approve to keep a demo moving. Show the class the paused graph instead.

<!-- cell -->
## What happened when we ran it

Our graph takes the task text as its plan and has Pi, our coding agent, write a patch. It sends the patch to the separate grader and to two verification lanes (one for the services, one for the Electron window), retries when a check fails, and pauses for approval when every check passes.

It covers less than the lab asks for. When a candidate fails its checks the only route is back to the maker, and after a third failed candidate the graph stops as `failed`, so it doesn't show the different rollback routes from experiment 3. We didn't time serial against parallel under controlled conditions, and we didn't do two human reviews.

Under **Checkpoints and decisions** below, the graph where Pi's patch reached approval is `project-08-graph-contract.json`, and its candidates are attempts 3e5cd770, 43ad509b and 03ca01ca, in that order. The architecture guard Pi wrote in the first (in the task we asked for a script that rejects Node imports in the renderer) let the grader's planted import through, and the second didn't compile. The third passed every check, and the graph paused there for approval, where it still is because nobody has approved that patch.

Pick 43ad509b and then 03ca01ca under **Inspect one attempt**, and in each follow **Open in Agent Lens** on the "Coding agent" step and go to the last command. In 43ad509b Pi writes a test file and is stopped at its 24-call limit, and that file is what fails to compile. In 03ca01ca Pi runs `npm run test` and one of the eight tests it wrote fails, while the grader and both lanes, none of which runs those tests, passed the patch.

We did approve one patch, later and separately, but it was a different one: a hand-written patch we used to test that the approval step works, which it does. That approval doesn't carry over to Pi's candidate (checksum starting `c74cf9cf`), and no entry below records it: the three `control-flow-qualification` entries hold the hand-written patch (checksum starting `91c4a2df`), and the one we approved, `project-08-control-flow-qualification.json`, was saved before the decision and still shows `node` as `approval`. The three entries that stopped as `failed` are graphs we ran before we named `scripts/check-architecture.sh` in the task, and six of their nine candidates failed the grader's architecture check because they had no file at that path.

"Reached approval" and "accepted" are two separate states, and Pi's candidate is in the first. When you read a saved state, look at the candidate checksum, the node it stopped on and whether it has an `approval` record before you describe the outcome: an accepted graph has `node` set to `done` and an `approval` record naming the checksum.

<!-- cell -->
## Hand in the transitions as well as the diagram

Hand in `graph.md`, the contract for each node and edge, who owns each piece of shared state, your serial and parallel measurements, evidence that the lanes were isolated, the rollback records, and two human decisions tied to checksums, with the review notes. Include at least one run that was interrupted and resumed, and explain what stopped it from doing work twice.

Use `rollback.md` from the lab packet (**Download the lab brief and templates**, above) to route one real failed candidate. Say which layer is responsible (the plan, the code or the infrastructure), what evidence supports that, and what has to be marked invalid before the next attempt. Then compare your route with what our graph did.

**Final discussion:** which of your routing rules are policy choices and which are technical facts? Which decision has to stay with a person? Which checkpoint would let another instructor resume your exercise without asking you anything?
