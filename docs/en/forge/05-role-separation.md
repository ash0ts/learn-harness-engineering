# A reviewer costs turns

We asked Pi to upgrade the same conversation-history feature in three ways: one coding role, a maker followed by a checker and revision, and a planner followed by that maker/checker sequence. The application had to display complete questions and answers in order, expose citations and confidence, preserve history, and confirm before clearing it.

The single-role treatment passed 2/3 attempts. Maker/checker also passed 2/3. Planner/maker/checker passed 0/3. Adding roles did not improve task success in this small comparison.

We gave each treatment a ceiling of 24 model calls. Every call spent planning or reviewing came out of that allowance.

## The schedules distribute the same allowance differently

| Treatment | Model-call allocation | Passing attempts |
| --- | --- | --- |
| Single role | 24 for the maker | 2/3 |
| Maker/checker | 10 maker, 4 checker, 10 maker revision | 2/3 |
| Planner/maker/checker | 4 planner, 8 maker, 4 checker, 8 maker revision | 0/3 |

The ceiling does not guarantee equal cost. Calls can consume different amounts of input and output, and an agent may stop before using every call. We record actual usage instead of treating “24 calls” as a token budget.

The role treatments also receive the associated repository guidance. The single-role condition starts with the minimal staged guidance. This comparison therefore evaluates those treatment packages; it does not isolate role count from every difference in instructions.

Both role separation and a call allowance can be reasonable design choices. What we cannot do is give a team of agents more total work, call its success a coordination benefit, and leave the extra compute out of the explanation. Our fixed ceiling exposes a different question: does spending part of the available work on another perspective pay for itself on this feature?

## The checker starts a new conversation

The maker edits the workspace. The checker then gets the task and the current workspace in a fresh Pi conversation. It does not inherit the maker's full conversation history. This creates an opportunity to inspect the code without relying on the maker's account of what it intended to do.

Planner and checker roles are instructed to inspect and return feedback. The coordinator preserves the candidate before those roles run and discards their filesystem changes afterward. Their intended contribution is the plan or review passed to the maker, not an unrecorded second implementation. This is a workflow boundary; it should not be mistaken for a general sandbox security guarantee.

The maker-revision phase receives the review text and can change the patch. After the actor phases end, a protected checker in a fresh sandbox grades the exported result. The model acting as reviewer never assigns the final course score.

That separation gives us something specific to inspect. A review may correctly identify a truncated answer, yet the maker may fail to repair it. A review may miss the problem entirely. Both cases can produce the same final failure, but they suggest different changes to the workflow.

## More agents help some kinds of work

Anthropic's [multi-agent research account](https://www.anthropic.com/research/multi-agent-research-system) describes independent context windows and parallel investigation for broad research tasks, along with higher token consumption. Those tasks offer work that can be divided across separate searches. Our history component is a tightly coupled code change with shared types, rendering, persistence, and confirmation behavior. We should not assume the same decomposition will help both.

The [Agentless paper](https://arxiv.org/abs/2407.01489v2) is a useful counterexample to equating architectural complexity with capability. Its software-repair method uses a prescribed sequence of localization, repair, and validation. We are not reproducing that method here. It gives us a reason to keep a simpler baseline in the comparison.

For this feature, the planner has four calls to produce something the maker would not otherwise discover quickly. The checker has four calls to find a defect that the revision phase can still repair. We can inspect whether that happened by reading the feedback beside the subsequent edit.

## What failed in the submitted patches

Of the five unsuccessful submissions, three failed compilation. The remaining two reached the history UI check and failed because the displayed answer was truncated. One was a single-role submission; the other used the planner/maker/checker treatment.

A truncated answer can look acceptable in a screenshot of a compact history list. The task asked for full answers. The protected check compares the stored response with the text in the history view, so an attractive preview does not satisfy that requirement.

The checker also exercises citation expansion, turn order, confidence display, and clearing history. For clearing, it first cancels confirmation and verifies the history remains. It then confirms and verifies removal. Clicking a Clear button once would miss the distinction between requesting deletion and authorizing it.

We had to correct our own citation selector before using these results. It originally matched answer prose containing the word “citation” instead of the interactive control. The corrected cohort uses an interactive element and supports both native and custom confirmation dialogs. Earlier outcomes remain archived and excluded from this comparison.

## Read the review beside the revision

In the [Project 05 notebook](https://forge.coreweave.com/notebooks/Tm90ZWJvb2s6MTUzMTg%3D), choose one maker/checker attempt and compare three artifacts: the patch before review, the review text, and the final patch. Private-project membership is required for the linked run evidence.

Look for a named defect and a corresponding edit. If the reviewer says “improve error handling” without identifying a failing operation, the maker has received another task to interpret. If it names a specific incomplete response in the history component, you can inspect whether the revision addresses it and whether the protected grade agrees.

The [public results report](https://github.com/ash0ts/learn-harness-engineering/blob/codex/forge-publication/forge/results/README.md) records the 2/3, 2/3, and 0/3 outcomes. Three attempts on one feature do not establish that planners are harmful or reviewers are redundant. They do leave us without evidence that either extra role improved success here. I would inspect the review-to-edit chain before increasing the role count again.

In [Project 06](./06-capstone.md), we keep the focus on the delivered behavior and ask whether the app can verify its services, preserve feedback, and return to a clean state.
