## Turn the hidden workflow into explicit edges

Your loop already has a graph, even if it lives only in your head: implement, test, inspect, retry, approve. This project writes down those transitions and makes them durable enough to pause, branch, and resume.

Start from the P07 workflow you actually ran. The original assignment does not require LangGraph or any particular framework. A TypeScript state machine is a valid implementation if its state, routing, parallel work, rollback, and human decisions are explicit.

**Your deliverable:** a graph contract, a serial/parallel experiment, targeted rollback evidence, and two complete human review passes. Predict one implicit transition that currently depends on a person remembering what happens next.

<!-- cell -->
## Experiment 1 · Draw the contract

Create `graph.md` with each node's purpose, inputs, outputs, state ownership, and failure behavior. List every edge and its condition. Identify at least one previously implicit edge, such as what happens when compilation prevents a UI test from running.

Define durable shared state: task revision, candidate patch checksum, completed checks, evidence locations, retry count, pending decisions, and stop reason. Assign an owner for each field. A node should not overwrite another node's result merely because its own view is stale.

Checkpoint before and after external work. On resume, reconcile pending operations before launching replacements. Draw cancellation, infrastructure error, and missing telemetry paths alongside success and task failure. A graph diagram that only contains the happy path is missing the expensive part.

<!-- cell -->
## Experiment 2 · Compare serial and parallel verification

Choose independent checks that can run in separate workspaces against the same exported candidate. Specify fan-out inputs and the fan-in rule: which results are required, how failures combine, and what happens if a lane times out.

Run the same candidate and checks serially, then in parallel, keeping resources and fixtures recorded. Use independent worktrees or sandboxes so lanes cannot modify each other's files. Record wall time, model/token usage where applicable, infrastructure cost, and quality outcomes.

Parallel execution is not automatically a speedup. Startup overhead, resource contention, and waiting for the slowest lane can dominate. Measure the comparison; a diagram with two arrows is not timing evidence. Repeat under the same conditions if you want to discuss variability.

<!-- cell -->
## Experiment 3 · Roll back to the responsible layer

Define a routing rule for each failure. A bad plan may need replanning; an implementation defect may return to the maker; an infrastructure timeout may need reconciliation rather than a code rewrite. Preserve the rejected candidate and its evidence before rollback.

Add a human approval node that pauses execution. The review request should identify the exact candidate checksum, task, grade, unresolved limitations, and approve/reject choices. Resume only after an explicit decision bound to that candidate. A previous approval does not authorize a different patch.

Complete two full review passes for the original exercise. Record the decisions, issues the human caught, agreement or disagreement with the checker, and observed waiting time. Do not auto-approve a candidate to keep a classroom demo moving; use a paused checkpoint as the teachable state.

<!-- cell -->
## Read the saved graph carefully

The Forge implementation routes a real Pi patch through planning, making, protected grading, separate service/Electron verification, rollback/retry, and approval. Its rollback currently returns to making; it does not demonstrate all of the targeted replanning routes in the original assignment. We also did not run a controlled serial-versus-parallel timing comparison or two human review passes.

The recorded sequence includes an architecture-guard failure, a compilation failure, and a later candidate that passed the checks. That passing Pi candidate remains paused for approval. A different manual qualification patch was explicitly approved; it validates the approval mechanism and is not approval of the Pi candidate.

The distinction matters because a graph can execute exactly as designed and still be waiting for a required decision. “Reached approval” and “accepted” are separate states. Inspect the candidate checksum and decision fields in the evidence browser before making either claim.

<!-- cell -->
## Submit the transitions, not just the diagram

Submit `graph.md`, node/edge contracts, shared-state ownership, serial and parallel measurements, lane-isolation evidence, rollback records, and two checksum-bound human decisions with their review notes. Include at least one interrupted/resumed execution and explain how duplicate work was prevented.

Use the worksheet to propose a routing decision for a real failed candidate. State the responsible layer, the evidence that supports your choice, and what must be invalidated before another attempt. Then compare your route with the implemented graph.

**Final discussion:** what is still a policy choice rather than a technical fact? Which decision must remain human? Which checkpoint would let another instructor resume this exercise without relying on your memory?
