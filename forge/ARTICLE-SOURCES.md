# Sources for the Forge article series

The canonical articles live in [`docs/en/forge/`](../docs/en/forge/). Research and editorial sources were read on November 6, 2026. Citations beside the relevant claims explain how each source relates to this course. External benchmark scores are not combined with the course's results.

## Course evidence

The articles use the [recorded delivery report](https://github.com/ash0ts/learn-harness-engineering/blob/61b606d97ec1a642b9997dfb618041b727534e66/forge/results/README.md), its [machine-readable summary](https://github.com/ash0ts/learn-harness-engineering/blob/61b606d97ec1a642b9997dfb618041b727534e66/forge/results/delivery.json), and the underlying trial records, patches, command output, protected grades, and checkpoints. The report identifies frozen source revisions and excluded cohorts. Full evidence is in the private [course-evidence artifact, version 4](https://wandb.ai/wandb/learn-harness-engineering-forge/artifacts/course-evidence/forge-course-qualification-evidence:v4).

| Article | Claims checked against course evidence | Boundary retained in the prose |
| --- | --- | --- |
| Overview | 19/39 primary passes; 129 completed attempts across all protocols; six project rows | Historical, diagnostic, loop, and graph attempts are not extra primary repeats |
| 01 | Minimal 3/3; explicit 3/3; identical staged app; protected service and Electron checks | No observed separation on one task does not establish equivalence |
| 02 | Both treatments 0/3; all six compile and service checks pass; Electron acceptance times out | The timeout does not identify its root cause |
| 03 | Both treatments 0/3; four compile failures; two metadata failures; one recorded status failure | Later assertions not reached are unobserved, not independently failed |
| 04 | Minimal 2/3; runtime feedback 3/3; all six chunk-preservation checks pass | The separating failure is the renderer-import guard, not chunk repair |
| 05 | Single 2/3; maker/checker 2/3; planner/maker/checker 0/3; three compile failures and two truncated-answer failures | Role schedules share a call ceiling, not equal token cost or identical guidance |
| 06 | Minimal 1/3; capstone 3/3; two compile failures; explicit feedback object contract in the corrected cohort | Passing reset and feedback assertions does not establish crash safety or arbitrary live-answer quality |
| 07 | Real two-hour timer: eight historical failed rounds and one observed intervention; later goal: one pass; later maker/checker: two empty patches and no progress | The three executions use different source revisions and are not a controlled ranking |
| 08 | Explicit-contract Pi run: guard failure, compile failure, then a pass awaiting approval; original manual qualification separately approved | Manual qualification is excluded from Pi counts; approval of one checksum does not approve another |

The approval claim is backed by the [immutable receipt](https://github.com/ash0ts/learn-harness-engineering/blob/61b606d97ec1a642b9997dfb618041b727534e66/forge/results/qualification-approval.json). The saved Project 08 notebook predates that decision; the operations dashboard includes it. No experiment records or published notebook sources were changed while writing these articles.

## Primary research and documentation

| Source | Version or publication date used | Article and purpose |
| --- | --- | --- |
| [SWE-agent](https://arxiv.org/abs/2405.15793v3) | v3 | 01: agent-computer interfaces as an experimental variable |
| [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988v3) | v3, September 29, 2026 | 02: context-file effectiveness and cost; uses the revised findings, not the stronger wording of an earlier abstract |
| [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) | November 26, 2025 | 03: fresh contexts and persistent progress artifacts |
| [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) | January 9, 2026 | Overview and 06: task/trial/grader distinctions and unspecified acceptance contracts |
| [ReAct](https://arxiv.org/abs/2210.03629v3) | v3 | 04: actions and observations informing subsequent decisions |
| [Pi integration for Agent Lens](https://docs.coreweave.com/products/agent-lens/integrations/pi) | Documentation inspected November 6, 2026 | 04: the documented Pi Weave extension |
| [Forge tracing instrumentation](https://docs.coreweave.com/products/agent-lens/tracing/instrument) | Documentation inspected November 6, 2026 | 04: application tracing, isolated concurrent contexts, shutdown flush |
| [How we built our multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system) | June 13, 2025 | 05: independent research contexts, parallel work, and added usage |
| [Agentless](https://arxiv.org/abs/2407.01489v2) | v2 | 05: a prescribed localization/repair/validation pipeline as a simpler comparison |
| [Reflexion](https://arxiv.org/abs/2303.11366v4) | v4 | 07: feedback retained between attempts without updating model weights |
| [LangGraph persistence](https://docs.langchain.com/oss/javascript/langgraph/persistence) and [interrupts](https://docs.langchain.com/oss/javascript/langgraph/interrupts) | Documentation inspected November 6, 2026 | 08: persisted execution state and explicit external resume decisions |
| [METR's developer-productivity update](https://metr.org/blog/2026-02-24-uplift-update/) | February 24, 2026 | Overview: selection and concurrent-work limitations in productivity measurement |

These sources motivate questions and explain mechanisms. None establishes why a particular course attempt failed without its local evidence. The course is not a replication of their protocols.

## GitHub writing skills used

The user requested research into GitHub skills for removing formulaic AI prose. We read and applied two checklists at fixed revisions:

- [AnswerDotAI's `write-prose`](https://github.com/AnswerDotAI/skill-plugins/blob/92a2109bf10badf94dd869c69644b7130bd065e9/plugins/codex-aai/skills/write-prose/SKILL.md): remove throat-clearing and repeated conclusions; name the actor and action; give each section a reason to exist. File blob: `9f60320206f88ef85eecd647b8f13f9b2d2a1053`.
- [FeedHive's `ai-slop-detector`](https://github.com/FeedHive/ai-slop-detector/blob/95d550706040191b0e75f1d89296a648bacb126e/skills/ai-slop-detector/SKILL.md): review vague claims, mechanical transitions, and stock phrasing. File blob: `49578a34e7a2ac7278110c10f40fff129136bf17`.

We used these as editorial prompts, not evidence of authorship or a numerical measure of writing quality. No third-party skill scripts were executed. Examples come from recorded course behavior or are explicitly marked as illustrative; proposed follow-up experiments are distinguished from completed runs.
