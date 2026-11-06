# Forge comparison contract, version 1

Question: on these fixed course tasks, which harness treatments change verified
completion, token usage, retries, and failure modes? The unit is a task × harness
× repeat. Repeats of one task are not independent tasks.

Each treatment starts from the same starter source commit. Only allowlisted app
code, build configuration, synthetic documents, and the selected harness overlay
are staged. No reference solution, historic scores, personal agent configuration,
credentials, or protected checker is visible to the coding agent. P05 always uses
the same history upgrade. P02 and P03 restart the agent with a fresh context and
the exported workspace; only the continuity treatment asks for a durable handoff.

Freeze the protocol, task manifests, source commit, and checker checksums before
qualification. Use the pinned image and model; a model failure never selects a
replacement. Total model turns are bounded across roles. Balanced cyclic order
rotates the first treatment each repeat. Target three repeats of every variant.
Reserve a complete comparison block before scheduling it, at most two concurrent
trials. Do not replace failures with retries in reported denominators.

The actor sandbox is terminated before a fresh grading sandbox receives its
exported patch. Grade actual services and Electron under Xvfb. The actor cannot
edit protected checkers during its session. These controls do not prove resistance
to deliberately adversarial patches; the course studies normal coding agents.

Report task failure, infrastructure failure, missing telemetry, budget exhaustion,
and approval pauses separately. Keep all attempts and evidence. Never infer human
time saved: intervention timestamps and descriptions are observed or entered by a
learner. Historical course rubric scores and simulated benchmark numbers are not
measurements in this track. UI checks establish only the asserted interactions.

Publish denominators, paired outcomes, missing data, actual completed counts, and
estimated spend. Three repeats support a local consistency observation, not a
universal ranking. Pin source revisions in W&B artifacts and notebook manifests.

## Revision 3 follow-up (2026-11-06)

The original revision 2 campaign remains a separate cohort: 39 completed attempts,
zero task passes, and a shared preload failure in all 31 compiled Electron checks.
Revision 3 evaluates the same tasks and treatments after a common Forge runtime
adaptation bundles the learner's preload with the image-pinned esbuild dependency.
It does not repair task features or alter the original offline starter files.
Electron's restricted preload module loader is documented at
https://www.electronjs.org/docs/latest/tutorial/sandbox/.

Revision 3 also caps actor-visible command output at 12,000 characters per stream
(full captured logs remain in evidence) and raises the bounded provider payload
limit to 524,288 bytes. The model, 24-call budget, role allocations, generation
settings, fixtures, task assertions, and sandbox image remain fixed. New trials
must pass protocol qualification first. Grade the exported patch in a fresh
sandbox, including the same preload build adaptation. Show both revisions in
published views; do not pool them or interpret a revision difference as an isolated
harness-treatment effect. A passing task requires every protected assertion.

## Revision 4: awaited UI observations

A supplemental acceptance check on a revision 3 passing patch found that the
asynchronous `page.waitForFunction` predicates could complete while the expected
history entry was still absent. Revision 3 launches were halted; already-running
attempts were allowed to finish and were retained. Revision 2 and 3 native grades
are historical checker results, not verified visible-answer acceptance.

Revision 4 waits for the resolved IPC predicate in a bounded Node poll, then waits
for the actual answer text in the rendered UI before collecting a screenshot.
Import completion and history clearing use the same awaited poll. Protected helper
bytes are included in the checker checksum. A deliberately false asynchronous
predicate must time out in the regression test. Generation settings and task code
are unchanged from revision 3; compare treatments only within the new frozen
cohort. Supplemental checks remain separate records and never rewrite old grades.

## History and capstone checker qualification

The first revision 4 source (`b948c1fbac36bca7dae458795d9bfca3f5d2b7d3`)
used a citation text selector that could match answer prose. The saved Project 05
patch passes when the checker clicks an interactive citation control and supports
both native and custom confirmation dialogs. Project 06 also lacked an explicit
feedback argument contract; a valid object-based implementation failed the assumed
positional call. Preserve those native grades but exclude both affected cohorts
from qualified comparisons, as recorded in `measurement-notes.json`.

Rerun all three Project 05 treatments and both Project 06 treatments three times.
Use the same application bytes, model, generation settings, image and role budgets.
The capstone task now specifies the feedback object payload and reset semantics.
The corrected checker verifies submitted fields, confirmation cancellation/acceptance,
and empty retrieval after reset. Qualify the frozen checker against saved patches
before launching the follow-up. Provider qualification is reused only while the
protocol hash is unchanged. Compare treatments within each frozen project cohort;
do not silently replace, relabel, or pool the original unsuccessful attempts.
