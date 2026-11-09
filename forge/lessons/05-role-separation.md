## Give three teams the same feature

Adding a reviewer sounds sensible. But under a fixed allowance, that reviewer takes calls away from implementation. A planner takes another share. This project makes that tradeoff visible.

Implement the same ConversationHistory upgrade in three isolated conditions: one role, generator/evaluator, and planner/generator/evaluator. The feature must show full questions and answers, citations, confidence, and a confirmation before clearing history.

**Your deliverable:** three patches for the same feature, planning and review artifacts where applicable, and one independent rubric applied to all three. Predict what the extra roles will catch and what they might leave unfinished.

<!-- cell -->
## Freeze the feature and the rubric

Use the original Project 05 variants, but verify that the application baseline and required feature are equivalent before running. Preserve any role-specific instructions as the treatment. Keep model, fixture, generation settings, and total allowance fixed within the comparison.

Write acceptance criteria before the first attempt:

- History preserves order and the full question and answer, including long text.
- Citations can be expanded and remain tied to the correct answer.
- Confidence is displayed with the relevant item.
- Clearing requires confirmation, cancellation preserves history, and confirmation clears it.
- Import, indexing, Q&A, and persistence continue to work.

Use the same independent checker for all three. The evaluator in a treatment is part of the working process; its “pass” is not the final grade. Preserve its rubric, revision notes, and any disagreements with the protected checker.

<!-- cell -->
## Run the three arrangements

For the single-role condition, one context plans, edits, and verifies. Save its self-checks.

For generator/evaluator, start the evaluator in a separate context with the task, candidate patch, and allowed evidence. Have it produce concrete findings. Return those findings to the generator for revision. Record which findings were addressed and which were disputed.

For planner/generator/evaluator, first create a plan or sprint contract with scope, acceptance criteria, and handoff rules. The generator implements that contract. The evaluator checks the actual result. A plan earns no credit for describing behavior that was never implemented.

Record the total allowance and the share assigned to each role. More roles with more total calls would answer a different question. Also record what files and conversational context cross each boundary; role separation on paper can collapse into a single shared context in practice.

<!-- cell -->
## What the saved comparison found

The Forge campaign allocated 24 model calls per attempt: 24 to the single maker; 10 + 4 + 10 to generator/reviewer/revision; and 4 + 8 + 4 + 8 to planner/generator/reviewer/revision. Review edits were discarded so the reviewer did not secretly become a second implementation worker.

Single role passed 2/3. Generator/evaluator passed 2/3. Planner/generator/evaluator passed 0/3. Across the nine attempts, three failed compilation and two failed because history truncated the full answer. The task and total allowance were fixed, but role-specific documents also changed; this is not a pure test of role count alone.

The original course includes reference scores of 1.6, 3.3, and 4.9. Those are not scores from this Forge campaign and must not appear as executed evidence. The result here gives us no basis to claim that adding a planner improved completion under this budget.

<!-- cell -->
## Read the review that did not prevent the failure

Choose a failed attempt below. Compare the evaluator's findings with the independent grade. Did the evaluator inspect the full answer, run the build, or merely read a component? Did the maker have enough allowance left to act on the finding? A missed defect and an unimplemented correction are different failures.

Then choose a passing attempt. Check that its screenshot supports the relevant assertion and that persistence/clear behavior has separate test evidence. A good-looking history panel cannot prove that cancellation preserves stored data.

Submit the three patches, role prompts, plan where applicable, evaluator rubric and notes, call allocation, independent checks, and a comparison. Explain one failure at a role boundary using the trace. Finish with a proposed change to the allocation or handoff that you would test next, labeled as a new experiment.
