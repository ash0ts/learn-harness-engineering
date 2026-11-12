"""The student-facing task and evidence questions; historical prose stays intact."""
LABS = {
 'project-01': {
  'learn':'Follow one question from a button through typed IPC, retrieval and a real model request.',
  'before':'Clicking Import cannot yet choose a document. The live request also raises an explicit unfinished-code error.',
  'edit':'Complete importFromPicker in src/renderer/workshop-import.ts. In workshop/inference.ts, build the bounded request from the supplied question, citations and model. Write instructions for a question the excerpts cannot answer.',
  'inspect':'Open the app conversation in Agent Lens. Find the question turn, retrieval tool and model call. Compare the excerpts sent to the model with the visible answer and reported tokens. The unsupported question is an observation, not a guaranteed refusal.',
  'explain':'Which part of your code connected the button? Which instruction changed the answer? Point to the snapshot, screenshot and matching model call.',
  'actions':[('offline-app','Run the import and restart scenario','Exercise your actual Electron build with offline answers first. Inspect the file-picker receipt and screenshots.','restart'),('live-app','Test my request with Forge inference','Ask a supported and unsupported question. Inspect the two real requests and Agent Lens turns.','restart')],
 },
 'project-02': {
  'learn':'Make the workspace carry the task, boundaries and checks an agent needs; prove what it actually read.',
  'before':'Import works, but the detail IPC handler returns no content. The guidance and sandbox command are deliberately incomplete.',
  'edit':'Write AGENTS.md, docs/ARCHITECTURE.md and feature_list.json using real paths and observable criteria. Complete inspectWorkspace in workshop/sandbox-task.ts using the supplied Sandbox object. Leave the narrow detail repair for Pi, or implement it yourself and mark that choice in your notes.',
  'inspect':'Inspect the commands.run output and terminal sandbox status. In Pi’s Agent Lens conversation, find the actual file-read tool outputs for your documents; file presence alone proves nothing. Then inspect its patch and the detail-view screenshot.',
  'explain':'What did Pi learn from a file you wrote? Which read proves it? Did its patch satisfy your acceptance criterion after restart?',
  'actions':[('offline-app','Run my sandbox SDK command','Run the bounded check you wrote and inspect the current detail view. A failed unfinished app is useful baseline evidence.','restart'),('agent','Give Pi my workspace and task','Freeze your files and run the narrow document-detail task with a 24-call allowance. Inspect real reads and changes.','restart')],
 },
 'project-03': {
  'learn':'Separate durable progress from conversation memory and verify what a fresh session recovers.',
  'before':'Document word counts are wrong, and the handoff headings contain no usable progress.',
  'edit':'Implement documentMetadata, record its real check in feature_list.json, and write an honest session-handoff.md. After the first session, select its candidate below, inspect/apply the diff, then update the handoff before resuming.',
  'inspect':'Compare the two conversation IDs, candidate hashes and observedHandoffRead receipt. Find the handoff text in the fresh session’s tool output before its first edit. Check that the earlier metadata feature survives restart.',
  'explain':'What survived only because it was in the workspace? Distinguish a handoff existing, being read, and helping produce a correct app.',
  'actions':[('offline-app','Check metadata in the app','Inspect your current implementation and persistence before involving Pi.','restart'),('agent','Run the first bounded session','Give Pi 12 calls. Save its actual candidate and failures; the next session will not inherit this conversation.','restart'),('resume','Resume from my saved handoff','First apply a recorded candidate and save your handoff. Start a fresh 12-call conversation from those files.','restart')],
 },
 'project-04': {
  'learn':'Instrument a real service boundary and use its observations to diagnose a defect.',
  'before':'The long fixture appears indexed but contains empty chunk text. The observation wrapper currently emits no student spans.',
  'edit':'Complete observe in workshop/instrumentation.ts with Forge startTool/end calls for success and failure. Record useful chunk statistics, then make a narrow repair in indexing-service.ts. Keep the supplied isolated conversation and shutdown flush.',
  'inspect':'Compare short and long fixtures before/after your patch. In Agent Lens, open student.indexing.start and student.retrieval.chunks under the matching app turn. Inspect chunkCount, nonemptyCount and error handling. A functional repair without your spans fails the instrumentation check.',
  'explain':'Which observation distinguishes “indexed” from “usable”? Show a student-authored span and the exact source change it helped justify.',
  'actions':[('offline-app','Inspect chunks in my Electron build','Run the selected fixture without inference; inspect stored chunk text and the visible chunk panel.','restart'),('live-app','Run and inspect my Forge spans','Execute the instrumented app, then follow the matching conversation link and verify parent/child activity and usage.','restart')],
 },
 'project-05': {
  'learn':'Give making and checking different jobs, and compute an evaluation from observed checks.',
  'before':'History truncates answers. The role prompts lack a concrete deliverable, the rubric is empty and the evaluation logs no meaningful metrics.',
  'edit':'Write maker/checker prompts and rubric.json. Complete evaluate and log_evaluation in workshop/evaluation.py. The maker must implement the history feature; the checker must produce an actual REVIEW within its allowance.',
  'inspect':'Open the separate maker, checker and revision conversations. Compare changes-1 with changes-3 and read review.json. An empty review or unchanged revision remains evidence. In W&B, inspect your student metrics and source artifact, then the clear-history screenshots.',
  'explain':'Which checker finding changed the maker’s next action? Does your evaluation describe the actual checks, including failures?',
  'actions':[('offline-app','Inspect conversation history','Exercise the current history UI, persistence and clearing behavior.','clear-history'),('agent','Run maker, checker and revision','Use 10 + 4 + 10 calls. Compare the actual review, revision and independent UI checks.','clear-history')],
 },
 'project-06': {
  'learn':'Turn “the app works” into explicit persistence, benchmark and clean-state evidence.',
  'before':'Feedback is returned but never persisted. Reset leaves the last answer visible. The benchmark does not execute services.',
  'edit':'Repair feedback persistence in qa-service.ts and the reset React state in App.tsx. Complete workshop/benchmark.ts by calling the real import, indexing and Q&A services and returning measured counts.',
  'inspect':'Compare service benchmark output with the actual app. Follow feedback through a restart, then reset and inspect the screenshots for stale documents, answers, citations and history. In a live run, trace the same Q&A in Agent Lens; compare source and outcome in its W&B run.',
  'explain':'Which check would catch a backend-only reset? What can your deterministic benchmark establish, and what still needs an answer-quality evaluation?',
  'actions':[('offline-app','Benchmark and reset my app','Run the service benchmark, record feedback, reset the visible app and restart it.','reset'),('live-app','Trace the capstone with Forge','Repeat the app scenario with real inference; inspect the matching turns before the reset.','reset')],
 },
 'project-07': {
  'learn':'Build a bounded feedback loop whose next fresh session uses the actual previous failure.',
  'before':'The policy always runs and its prompt says only “Try again.” The metadata feature is unfinished.',
  'edit':'Complete nextAction and nextPrompt in workshop/loop.ts. First test the stop conditions without inference. You may repair metadata yourself or let Pi attempt it; record which you chose.',
  'inspect':'After each explicit round, inspect the saved deadline, candidate hash, failed checks and feedback hash. Open the fresh Pi conversation and find that feedback. Continue only while the recorded policy permits it. Each round has 12 calls; the short exercise allows at most two rounds over a fixed 30-minute window, with no idle sandbox.',
  'explain':'What evidence did the second session receive that the first did not? Which stop condition fired? A repeated failure is not progress merely because another round ran.',
  'actions':[('offline-app','Inspect the loop task in the app','Check the current metadata feature and restart behavior without coding inference.','restart'),('loop','Run the next bounded loop round','Run one explicit round, or read back an unfinished round. Inspect the checkpoint before continuing. A completed loop starts a new retained execution on the next explicit action.','restart')],
 },
 'project-08': {
  'learn':'Make verification, repair, rollback and human approval explicit, durable decisions.',
  'before':'The routing function asks for approval before verification. The plan and metadata repair are unfinished.',
  'edit':'Complete route and verificationMode in workshop/graph.ts, and write workshop/plan.md. Compare serial and parallel independent service/Electron lanes on the same code. Only your explicit decision may approve a verified candidate.',
  'inspect':'Read the route event after every node. A failed candidate remains saved; a failed repair restores the baseline. Compare lane snapshot hashes and timing. At approval, inspect the verified source diff, checks and screenshots before deciding that exact checksum.',
  'explain':'Which route handled an app failure, and which would handle unknown usage? What did rollback restore? Why does a passing checker still stop at human approval?',
  'actions':[('graph','Execute the next graph node','First verify the starting snapshot. Then explicitly execute its repair route. A verified candidate pauses below for your decision; this action never approves it.','restart')],
 },
}

def teaching_cell(project):
    lab=LABS[project]
    text=("### What you will learn\n\n"+lab['learn']+"\n\n**Inspect the starting checkpoint.** "+lab['before']+
          "\n\n**Your edit.** "+lab['edit']+"\n\n**Forge checkpoint.** "+lab['inspect']+
          "\n\n**Be ready to explain.** "+lab['explain'])
    return 'def _(mo):\n    mo.md('+repr(text)+')\n    return'
