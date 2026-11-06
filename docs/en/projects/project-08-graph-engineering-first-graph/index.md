# Project 08. Draw Your Workflow as a Graph

> Related Lecture: [L14. From Single Loops to Graph Engineering](./../../lectures/lecture-14-graph-engineering/index.md)

## What You'll Do

This is the transition project from "Loop" to "Graph." In the last project you built a maker-checker loop — implement, verify, feed back, implement again — where every decision happened inside one agent's context window. In this project you'll **make the structure that was hidden inside the loop explicit**: nodes, edges, shared state, and routing rules, written out word by word.

You'll do three progressive experiments: first draw your P07 maker-checker loop as an explicit graph, then add a parallel fan-out/fan-in node, then add a conditional rollback edge and a human-approval node. When you're done, you'll have felt this firsthand: **a graph isn't a new invention — it's what your loop becomes once it's complex enough.**

## Tools You'll Use

- Claude Code or Codex
- Git
- The maker-checker loop you built in P07 (or any agent workflow you can run repeatedly)
- A text editor or diagramming tool (drawing is not for looks — it's for getting the structure down on paper; `mermaid` or a hand-written `graph.md` both work)

## Steps

### Prep

1. Start from the repo where you finished P07, or from any agent workflow you're currently running.
2. Create three branches: `p08-explicit-graph`, `p08-parallel`, `p08-human-in-the-loop`.
3. Prepare a `state.md` as your shared state file: requirements, progress, and verification results all live here. This is the graph's "common workspace."

### Experiment 1: Draw the Loop as an Explicit Graph

Switch to the `p08-explicit-graph` branch.

1. **List every node**: write each step of the P07 maker-checker loop as a node. For each node, write down: its responsibility, its inputs, its outputs, and whether it's an agent or deterministic code.
2. **Draw every edge**: list each edge between nodes. Flag two special kinds:
   - Conditional edges: verify passed/failed — which path does each take?
   - Rollback edges: where does a failure return to?
3. **Write the shared state**: explicitly list the fields in the state (requirements, code, test results, review conclusions) and who reads/writes each.
4. **Write the routing rules**: state "where does execution go next" in the plainest if-then language, e.g.:
   ```
   if verify passed → merge node
   if verify failed → implement node
   if implement node lacks information → research node
   ```
5. **Write it all up as `graph.md`**: turn the above into one document — a mermaid diagram plus a node table and the routing rules.
6. **Answer this question**: after drawing, find at least one **edge that was implicit** — a decision path that used to live inside the agent's context, one you didn't even know existed.

### Experiment 2: Add a Parallel Fan-out / Fan-in Node

Switch to the `p08-parallel` branch.

1. **Pick a point that can parallelize**: find a spot where the task can be split into two independent parts. For example:
   - Split implementation into two independent modules, written in parallel by two agents
   - Split verification into two independent reviews: one runs tests and lint, the other does code review (different instructions, different focus)
   - Split research into two directions, one agent per direction
2. **Write the fan-out rule**: record in shared state that "this task is split into N parallel subtasks," each with its own context and its own node.
3. **Write the fan-in rule**: once all subtasks finish, who merges the results? What's the merge standard (e.g., both reviews must pass, or one is enough)?
4. **Isolate with worktrees**: run each parallel subtask in its own git worktree to physically avoid file collisions (review the Worktree primitive from Lecture 13).
5. **Run once and record**: record wall-clock time, token cost, and result quality before and after parallelization. Is parallelization actually faster? Or did coordination overhead eat the savings?

### Experiment 3: Add a Rollback Edge and a Human-Approval Node

Switch to the `p08-human-in-the-loop` branch.

This is the most important of the three experiments. You'll add two kinds of nodes to the graph:

1. **Conditional rollback edge**: give the verify node a "partially passed" path — instead of bouncing the whole thing back to the implement node, return with specific feedback to **the node that produced the problem**. For example: tests all pass but code review finds the requirements were misunderstood — roll back to the research node, not the implement node. This requires your shared state to record "which layer the problem came from."
2. **Human-approval node (human-in-the-loop)**: insert a human node before the merge node. Execution **stops** here and waits for you to write "approved" or "rejected" in `state.md`. The approval node can have a timeout rule: after N hours with no response, auto-reject or auto-escalate.
3. **Write the interrupt format**: how should an approval request be written — what happened, what changed, why a human is needed, what are the consequences of approving/rejecting?
4. **Run at least 2 full passes**: each pass stops at the human-approval node and you approve or reject once. Record: did your approval decisions agree with the verify node? Did the approval node catch anything the verify node missed?

## How to Measure Results

| Metric | Exp 1 (Explicit graph) | Exp 2 (Parallel) | Exp 3 (Human-in-the-loop) |
|--------|----------------------|-----------------|---------------------------|
| Structural visibility | How many implicit edges did you find? | Can shared state support parallel subtasks? | Can the rollback edge pinpoint the problem layer? |
| Failure localization | Can you point at which edge is wrong? | When a subtask fails, can you locate which one? | When approval rejects, can you name the layer? |
| Coordination cost | How long did writing the graph take? | Time saved by parallelism vs. coordination overhead | Approval wait time vs. value of problems caught |
| Observability | Can you now see what happens at each step? | Is every subtask's state visible? | Are approval requests written clearly? |
| Reliability | Does the graph description match actual runs? | Is the fan-in merge standard sound? | Do the timeout/escalation rules actually fire? |

## What to Submit

- `graph.md` (Experiment 1's complete graph description: mermaid diagram + node table + edge table + shared state fields + routing rules)
- The list of implicit edges you found in Experiment 1 (at least one)
- Experiment 2's fan-out/fan-in rules and one parallel run record (time/cost/quality comparison)
- Experiment 3's rollback-edge rules, approval-node format, and 2 rounds of human-in-the-loop records
- Final retro: as you moved from loop to graph, how did your way of working change? Which tasks deserve a graph, and which don't?

## Related Lectures

- [Lecture 14 — From Single Loops to Graph Engineering](../../lectures/lecture-14-graph-engineering/index.md)
- [Lecture 13 — From Manual Prompting to Autonomous Loops](../../lectures/lecture-13-loop-engineering/index.md) (your loop is a node in a graph; this project unfolds that node's internal structure)
- [Lecture 09 — Why Agents Declare Victory Too Early](../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) (why the verify node must be independent of the implement node — a structural problem, not a prompt problem)
- [Lecture 11 — Why Observability Belongs Inside the Harness](../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md) (the more complex the graph, the more you need to see what each node is doing)


## Optional Forge experiment

Read [Binding human approval to the patch we tested](/en/forge/08-state-machine) for the executed Forge experiment and its saved notebook. The [Forge overview](/en/forge/) explains the shared setup. The offline exercise remains the default.
