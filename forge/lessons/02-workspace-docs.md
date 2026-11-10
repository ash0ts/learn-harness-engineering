## Leave a workspace someone else can pick up

An agent comes back for a second session with no memory of the first, but the files are still there. Can it finish the feature from the files alone, or do you have to retell the story?

In this project you give an agent the same task in two workspaces: make the app import a document, show its details, and still have it after a restart. One workspace is thin, and the other has architecture and product notes, a feature list, and a handoff written at the end of the first session.

**What you hand in:** the same task done across two fresh sessions in each workspace, plus the files that let the second session find the unfinished work. Before you start, predict which fact the second session will have the most trouble recovering.

<!-- cell -->
## The lab: write docs that answer a newcomer's questions

Start both workspaces from the same Project 02 app code, the starter linked from the original course brief under **Sources and further reading**, and keep them separate. Give each the same task and the same total allowance across both sessions, and decide now where session one will stop. The second session has to be a brand-new conversation, because if a summary of the first chat is still in the agent's context, you are no longer testing the files alone.

In the documented workspace, write the shortest answers you can to these:

- Where does import enter the app, and which service owns persistence?
- What does the renderer get through the preload bridge? What has to stay out of renderer code?
- What should the document detail view show?
- Which feature is unfinished, and which exact command checks it?
- What changed in session one? What failed? What should session two look at first?

Put facts that stay true in the architecture and product notes, what has and hasn't been accepted in the feature list, and what just happened in the handoff. Don't paste the whole transcript into all three, or the next session has to search the same story three times. Wherever you point to evidence, give a path another process can open.

<!-- cell -->
## The lab: break the conversation on purpose

1. Run session one on the import, detail and persistence task. Stop at the point you decided on beforehand, even if a feature is half done.
2. Save the workspace and export the patch. In the documented workspace, have the agent write an honest handoff that names the unfinished work and the checks that failed.
3. Throw the conversation away. Start a fresh agent in the saved workspace with the original task and only the files that workspace is allowed.
4. Watch what it reads before it edits. Does it find the entry point? Does it redo finished work? Does it check what session one claimed?
5. Grade the final patch in a clean environment. Import through the real file picker, open the detail view, restart, and check the content is still there.

Count one two-session run as one attempt. Session two depends on session one, so they aren't two independent tries. If you supply something the files were missing, write down that you did and what you said.

<!-- cell -->
## What happened when we ran it

Our main comparison is six attempts, three per treatment, where a treatment is the setup the agent starts with. Each attempt got two fresh sessions and 24 model calls, 12 per session. `minimal` had only the task. `workspace-docs` also had a short general-purpose `AGENTS.md`, a one-paragraph architecture note, and a rule to write `session-handoff.md` before each session ends, which is a lot thinner than the documentation the lab asks you to write. Every session was stopped when its model calls ran out, and no `workspace-docs` session wrote that file, so we never tested a second session that had a handoff to read.

All six attempts passed the checks that call the app's services directly and then failed the check that imports a document through the Electron window, each time with a timeout. Both treatments scored 0 of 3, and we have no screenshot of a working Project 02 app to show you.

From this we know that the app's import and persistence services, which no attempt changed, still worked when called directly, and that the same import driven through the window did not finish. We can't tell why from a timeout alone: it could be a dialog that never closed, a button the check clicked that doesn't start the import, an event that never fired, or a defect in the app. So we can say the import failed the end-to-end check, but not that the import code is broken.

Under **Inspect one attempt**, choose 6e00cd09, a `workspace-docs` attempt from the main comparison, and read its checks. The timeout is the only detail the grader recorded for the failed check. Then propose one diagnostic that would tell two of those causes apart, without changing the task and without going back to edit the score. Also open **Session 2** in Agent Lens, find where the agent looks for `session-handoff.md` and what comes back, and count the commands before its first edit. In five of the six attempts the second session's first edit was among its last two commands, and in 6aeae35a it made none.

<!-- cell -->
## Hand in the handoff as well as the code

For the lab, hand in from each workspace both session transcripts, the patch at the break and the final patch, together with your documentation, your handoff, and the UI and service evidence from your own check. Add a short list of the facts session two got from the files and the facts a person had to supply, and say whether your prediction held.

Then ask a partner to start from the break using only your handoff. If they have to ask you something, that's a gap you watched happen, so write down the missing fact as evidence before you fix the document.

**Discuss:** what belongs in the architecture note, what belongs in the feature list, and what goes stale after the next session? Describe one edit that makes the workspace easier to resume without making it longer.
