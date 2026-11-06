# Debugging an index full of empty chunks

The index could create chunk records, assign IDs, and report that it had indexed the document while storing an empty string in every chunk. Retrieval then had nothing to quote. A status indicator could look reassuring even though the content needed for the next operation was missing.

That is the seeded defect in Project 04. When the complete document exceeds 1,000 characters, the starter substitutes an empty string for the text it writes into each chunk. The code is intentionally wrong. Our experiment asks whether access to runtime feedback helps Pi repair the application and finish the accompanying verification work.

The runtime-feedback treatment passed 3/3 attempts; minimal instructions passed 2/3. All six submissions passed the check that indexed text was preserved. The remaining failure concerned an architecture guard. That detail changes how we should read the apparent advantage.

## Observe the value the next operation consumes

The faulty choice is small enough to show directly:

```ts
// Seeded course defect, not the repair.
const chunkContent = content.length > 1000 ? '' : buffer.trim();
```

The chunk can still have a document ID, an index, and metadata. Counting records alone will miss the loss of text. To diagnose this failure, inspect the `content` value and check that distinctive text from the input survives in the output.

The runtime-feedback treatment supplies a script that instantiates the actual persistence, document, and indexing services. It imports the sample document, runs indexing, and prints chunks and status. The accompanying instructions tell Pi to build the application and run that script. The experiment therefore offers an observation path the minimal treatment would have to construct or discover itself.

The sample has multiple paragraphs and is long enough to reach the defect. The protected checker uses a separate fixture and verifies that each paragraph's identifying text appears in a nonempty chunk. Checking a new fixture prevents a repair that merely recognizes the sample's exact text from satisfying the whole acceptance condition.

The [ReAct paper](https://arxiv.org/abs/2210.03629v3) studies interleaving model reasoning with actions and environment observations. It helps explain why a tool result can change the next decision. Our course does not reproduce ReAct's task protocol. Here the observation is specifically the output of the application's indexing services.

## Trace the app without mixing it into the coding session

We recorded Pi's model calls and tool activity in Agent Lens. We also added opt-in tracing around the app's import, indexing, retrieval, and Q&A services. These are different conversations: one concerns changing software, and the other concerns running that software against documents.

Pi uses the documented [Weave extension](https://docs.coreweave.com/products/agent-lens/integrations/pi). New application instrumentation uses the [Forge tracing SDK](https://docs.coreweave.com/products/agent-lens/tracing/instrument). Their tracing initialization runs in separate processes. In the TypeScript app, isolated tracing contexts prevent concurrent requests from borrowing each other's conversation state, and shutdown flushes buffered spans.

The record needs enough identifiers to join the observation back to the attempt: project, task, treatment, trial, role, source revision, sandbox, and W&B run. A span called `indexing.start` becomes much easier to interpret when we know which candidate produced it and which fixture the caller supplied.

Tracing does not decide whether the chunk is correct. It helps us find the operation and its returned value. The protected assertion about preserved text remains a separate piece of evidence. We also keep credentials and SDK clients in the main/service layer, outside the renderer.

## A guard script can pass by failing to check anything

The task also requires an architecture script that rejects Node imports in renderer code. Running that script on a clean repository is insufficient. A script containing `exit 0` would pass that demonstration with admirable consistency.

The protected checker runs the submitted guard on the clean candidate, writes a temporary renderer file that imports Node's filesystem module, and runs the guard again. It expects a failure, then removes the temporary violation. This tests whether the guard reacts to the behavior it is supposed to prohibit.

The one unsuccessful minimal-instructions attempt failed that probe:

```text
architecture checker accepted a Node import in the renderer
```

Its chunk-preservation check passed. The observed 3/3 versus 2/3 difference therefore does not show that only the runtime-feedback treatment discovered the indexing defect. Both treatments produced repairs that passed that check. The final separation came from another required behavior.

We would need a more focused experiment to isolate how the supplied runtime observation affects bug discovery. We could measure whether and when each attempt observes an empty chunk, then hold the other task requirements fixed. The current traces can support descriptions of individual attempts, but the pass-rate difference alone cannot supply that mechanism.

## Follow one document all the way through

For this exercise, start with the document content, then inspect the stored chunks, retrieved excerpts, generated course answer, and rendered answer. At each step, ask which property the next operation depends on.

| Operation | Property to inspect |
| --- | --- |
| Import | The saved content matches the input |
| Index | Nonempty paragraph text survives chunking |
| Retrieve | Returned excerpts come from the stored content |
| Answer | The response carries citations to retrieved excerpts |
| Render | The user can see the completed answer |

The course's deterministic Q&A defaults make this path repeatable. They do not establish the quality of a live model's answers to arbitrary documents. Live inference was qualified separately, and its errors are recorded explicitly rather than replaced with a mock response.

Open the [saved Project 04 notebook](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTc%3D) with private-project access and compare the failed guard with a passing one. The [public report](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/forge/results/README.md) preserves the check-level outcomes. Before giving an agent more feedback, identify the observation it needs to make its next decision. In this case, “index ready” was too far removed from the text retrieval needed.

Continue to [Project 05](./05-role-separation.md) for a different source of feedback: another model conversation reviewing the same candidate.
