## Build one app, and check every claim

An agent tells you the job is done. The app opens, then you ask it a second question and the conversation history disappears. Which of those three things goes in the grade?

We keep coming back to that question as we follow one small app, an Electron knowledge base that imports documents and answers questions about them, through eight projects. In each one you change something around a coding agent: its instructions, the documents in its workspace, the feedback it gets, who reviews its work, or when it stops. Then you check what the agent delivered by opening the app and testing it, whatever the agent said about it.

**Start with Project 01.** Open it from the links at the top, read the task, and write down what would convince you the app works. Keep that, because at the end of Project 01 you compare it with what you found when you checked the app yourself.

To read the lessons and the recorded attempts you need a Forge account, view access to this course's project, and a private project you can write to, where your copy of each notebook runs. To run an attempt yourself you also need your own W&B API key.

<!-- cell -->
## The eight projects

| Project | What you change | What you hand in |
|---|---|---|
| 01 · Minimal harness | The instructions and workspace around the agent | Two separate attempts, the harness for the second, and a comparison |
| 02 · Readable workspace | The files a fresh session uses to find its way | One task across two fresh sessions per workspace, plus the files session two starts from |
| 03 · Session recovery | The unit of progress and its evidence | A feature list with evidence, one commit per feature, a session handoff, and a clean restart |
| 04 · Runtime feedback | The observations available during debugging | A reproduction, a diagnosis from logs, a narrow repair, architecture checks, and a comparison |
| 05 · Roles | Who plans, implements, and checks the same feature | Three patches, the plans and reviews, and one independent rubric applied to all three |
| 06 · Capstone | The complete operating harness | The harness, a comparison on a fixed task set, cleanup and rerun evidence, and runs with one component removed at a time |
| 07 · Loops | Who decides when to continue or stop | Two goal versions, a manual/goal comparison, a two-hour monitoring log, three role prompts, at least five maker and checker rounds, and a retrospective |
| 08 · Graphs | The paths, state, concurrency, and approvals | A graph contract, a serial/parallel comparison, a targeted rollback, and two human reviews |

Work through them in order. If you only have one class meeting, do Project 01 and read one Project 04 conversation in Agent Lens, the tool that records each agent conversation. Project 07 starts from the harness you finished in Project 06, and Project 08 from the workflow you ran in Project 07, so they don't work well as standalone demos.

<!-- cell -->
## What is in each notebook

Every project notebook has three parts, in this order.

**The lab** is the assignment. The notebook describes it and gives you the brief and templates to download, but you do the work in your own workspace, with an editor, Git, Node, Electron and whichever coding agent you use. The lab's hand-in list comes after the other two parts, near the end of each project notebook.

**The recorded attempts** are ours, reported in each lesson under *What happened when we ran it*. While building this course we had a coding agent called Pi attempt a cut-down version of Projects 01 to 06 in fresh sandboxes, three times per setup. For Projects 07 and 08 we ran Pi on the Project 04 repair inside a loop and a graph. A separate grader applied each patch to a clean copy of the app and tested the real thing. You can open any attempt, see which checks passed, and read the agent's whole conversation in Agent Lens. Plenty of them failed, and we kept those in.

**Your own attempt** is optional practice for the lab and doesn't replace it. Under *Run this lesson yourself* you can launch the same kind of attempt from your copy of the notebook and put your result next to ours. Each lesson shows what its recorded attempts took; in the main comparison that was an estimated 5 to 18 cents each, and yours is charged to your own project.

Everything here ran on CPU sandboxes, with model calls going to one Qwen model, `Qwen/Qwen3.6-35B-A3B`, on Forge's hosted inference. We didn't train a model or use a GPU, even though the experiment records are stored in W&B Models. The GPU autoresearch example in Lecture 13 is a separate case study.

<!-- cell -->
## Read a result from the outside in

When you look at an attempt, start with what the grader observed in the running app, then read the patch, then the agent's conversation, and its final message last. Going in that order makes it harder to accept a confident explanation for behavior that never worked.

Agent Lens is where you read the conversation. For each attempt it keeps the task the agent was given, every model call it made, every command it ran and what came back. Use it to find out why an attempt ended the way it did: what the agent read before it edited anything, whether it ever launched the app, and where it stopped. It can't tell you whether the app works, so use the grader's checks for that.

The main comparison has 39 attempts across Projects 01 to 06, three per treatment, where a treatment is the setup the agent starts with. Nineteen of the 39 passed. One of the nineteen, e53c3cad (Project 01, `explicit`), has an empty patch, so when it passed all five checks the grader was testing the app as we supplied it. Pick it in the selector below and open its "Coding agent" step in Agent Lens: the agent reads the source, runs the check, build and test scripts, and stops without editing a file. The selector lists 129 attempts in all and labels the 90 outside the main comparison Archive: earlier trial runs, diagnostics, and the loop and graph rounds from Projects 07 and 08. Those are two different denominators, and the labels keep them apart so you don't blend them into one success rate.

Three attempts on one task can't show that a harness helps in general, but they can show where a claim stops holding. In Project 02's main comparison every service check passed, on service code that no attempt changed, and all six attempts still failed when the check that imports a document through the real window timed out. In Project 06 a reset cleared the stored data while the screen could still show the old documents.

**Before you open the attempts, discuss:** if both treatments pass 3 of 3, what would you refuse to conclude? What task would give a written rule a real chance to matter?

<!-- cell -->
## For instructors

**Before class.** Share this notebook's link and give students view access to this course's project; a link alone does not grant access. Test that with a student account before you teach. Each student copies a lesson into a private project they can write to, and works in that copy. The recorded Agent Lens conversations and run records stay in the course project, which is what that view access is for.

Keep the course originals read-only for students, and present from a copy yourself. Opening an original in the editor with edit rights can save a new version of it even if you change nothing.

To present a lesson, run its cells and switch to Preview for a clean reading view. Switch back to the editor before anyone connects sandbox access, because the key prompt does not appear in Preview.

Running an attempt uses the student's own API key, held only in the notebook session's memory, and saves progress to the student's project. Never hand out an instructor key. Each copy keeps its own spending limit; that is not a class-wide billing cap, so use your project or account billing controls for one. For a controlled study, keep the model settings, task, starter code, test fixtures and budget fixed within each comparison, and keep reference solutions out of the agent's workspace.

**A 90-minute first class.** Spend 10 minutes predicting failures, 15 inspecting the starter and acceptance criteria, 35 running the two treatments, 20 reading the patches, checks and Agent Lens conversations, and 10 comparing observations. These are teaching timeboxes, not measured completion times. A notebook session lasts one hour, so have pairs save their notes and finish any running attempt before it ends, then prepare and connect again. Treat a slow run as a follow-up, and do not call an unfinished attempt a failure only because class ended.

**Before students leave.** Have each pair save its notes, download its progress, and hand in the patch, run record and evidence alongside them. They return to the same copy next time and restore the workspace. Ask another pair to reproduce one claim. A screenshot can illustrate a claim, but without the command, fixture, revision and check it is weak evidence.

**Completion checklist**

- Every learner can open the shared notebook and knows which account pays for any live work.
- Each comparison starts from separate copies of the same app code, with reference solutions kept out.
- A grader that is separate from the coding agent tests the exported patch.
- Evidence from the services and evidence from the Electron window are kept separate.
- Unfinished work, infrastructure errors, missing usage data and failed app checks each get their own label.
- The learner records when they stepped in and how long they spent. A blank means it wasn't measured.
- Students hand in their own work on the lab. The recorded attempts are not their assignment.

Use the project worksheets to collect the evidence. Keep unresolved limitations in the conclusion, and bring them to the class discussion.
