## Leave a workspace someone else can understand

An agent returns for session two with no memory of session one. The files are still there. Is that enough to finish the feature without you retelling the story?

Extend the knowledge-base app so a user can import a document, inspect its details, and find it again after a restart. The exercise compares a thin workspace with one containing useful architecture and product documentation, a feature list, and a session handoff.

**Your deliverable:** the same import/detail/persistence task across two fresh sessions in each condition, plus the files that let session two find the unfinished work. Predict which fact the fresh session will struggle to recover.

<!-- cell -->
## Make documentation answer operational questions

Start from identical Project 02 application code in isolated workspaces. Keep the task and total allowance fixed across the two conditions. The second session must be a new conversation; retaining a chat summary in hidden context would answer the question you are trying to test.

In the documented condition, write the smallest useful answers to these questions:

- Where does import enter the app, and which service owns persistence?
- What does the renderer receive through preload? What must stay out of renderer code?
- What should a document detail view display?
- Which feature is unfinished, and which exact command checks it?
- What changed in session one? What failed? What should session two inspect first?

Put stable facts in architecture/product docs, acceptance state in the feature list, and recent observations in the handoff. Copying the entire transcript into every file makes the next session search the same story three times. Record paths and evidence that another process can actually open.

<!-- cell -->
## Break the conversation deliberately

1. Run session one against the frozen import/detail/persistence task. Stop at the predeclared boundary, even if it leaves a partially completed feature.
2. Save the workspace and exported patch. In the documented condition, require an honest handoff identifying incomplete work and failed checks.
3. Discard conversational context. Start a fresh agent in the same saved workspace, with the original task and only the condition's allowed files.
4. Observe what it reads before editing. Does it find the entry point? Does it repeat completed work? Does it verify the prior session's claims?
5. Grade the final exported patch in a fresh environment. Import through the actual file-picker flow, inspect the detail view, restart, and verify persisted content.

One two-session attempt is one trial. Session one and session two are dependent observations, not two independent repeats. If a human supplies missing context, record the intervention and its content.

<!-- cell -->
## Services can pass while the user is stuck

In the recorded Forge adaptation, both treatments received two fresh sessions and the same total model-call allowance. The documented treatment used a generic workspace guide, rather than the original exercise's complete documentation package.

All six qualified attempts passed the recorded service checks. All six failed the Electron import-flow check by timeout. The observed outcome was 0/3 versus 0/3. There is no successful primary Project 02 app capture to show; a notebook screenshot would not fill that gap.

The result narrows what we know. Import and persistence worked through the exercised service path, while the tested UI interaction did not complete. A timeout alone does not distinguish every possible cause: a modal, locator, event, or application defect may need further diagnosis. It is a failed end-to-end acceptance check, not proof that all import code is broken.

Inspect one grade and its corresponding trace. Find the last observation before the timeout. Propose a diagnostic that distinguishes two plausible causes without changing the task or retroactively rewriting the score.

<!-- cell -->
## Submit the handoff, not just the finished code

Submit both session transcripts, the boundary patch, the final patch, the documentation package, and the independent UI/service evidence. Include a short list of facts session two recovered from files and facts a person had to provide.

Ask a partner to start from the boundary state using only your handoff. If they need an explanation from you, write down the missing fact before fixing the document. That is a directly observed weakness in the workspace.

**Discussion:** which information belongs in a stable architecture document, which belongs in the feature ledger, and which expires after the next session? Explain one edit that makes the workspace easier to resume without making it longer.
