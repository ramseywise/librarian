---
title: Agents Interview Study Guide
tags: [interview, reference]
summary: Exam-prep reference for agent architecture questions — workflow vs agent distinction, composable patterns, ACI tool design, harness engineering, long-horizon reliability, and memory taxonomy.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--4-agents--interview-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--agents.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--4-agents--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--agents-design.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--agent-harness.md
  - data/raw/repos/sisyphus/interviewing--guides--4-agents--interview-guide.md
  - data/raw/repos/sisyphus/interviewing--guides--4-agents--00-overview.md
---

# Agents Interview Study Guide

Centerpiece topic for AIE/FDE loops. Interviewers test: (a) pick the simplest pattern that works, (b) design the system around the model (harness), (c) reason about reliability over long horizons and multiple agents.

## Workflow vs Agent — Always Open Here

- **Workflow**: LLMs + tools orchestrated through predefined code paths.
- **Agent**: the LLM dynamically directs its own process and tool use.

Anthropic's production guidance: start with the simplest thing — a single call with retrieval and examples is often enough. Add agency only when it measurably improves outcomes. Saying this first signals judgment, not weakness.

## Five Composable Workflow Patterns

| Pattern | Mechanism | Use when |
|---|---|---|
| Prompt chaining | sequential calls, gates between steps | fixed decomposition, accuracy > latency |
| Routing | classifier → specialized pipeline/model | distinct input classes |
| Parallelization | sectioning (independent) or voting (×N) | independence, or confidence via consensus |
| Orchestrator–workers | central LLM decomposes, delegates, synthesizes | subtasks unpredictable |
| Evaluator–optimizer | generator + critic loop | clear criteria + feedback demonstrably helps |

See [[Agentic Workflow Patterns]].

## Tool Design (ACI) — Highest-Leverage Detail

Treat the agent-computer interface like HCI. Tool descriptions written like docstrings for a junior dev: usage examples, edge cases, boundaries from neighboring tools. Careful parameter naming. Poka-yoke arguments so misuse is impossible (canonical: require absolute paths — one of the highest-impact fixes in Anthropic's SWE-bench agent).

Debugging heuristic: when the agent misuses a tool, fix the tool description before blaming the model. Tool quality beats tool quantity. See [[ACI (Agent-Computer Interface)]].

## Harness Engineering — "Agent = Model + Harness"

The harness is everything around the model that makes intelligence useful: system prompts/context policies, tools + skills + MCP servers, bundled infrastructure (filesystem, sandbox, browser), orchestration logic (subagents, routing, HITL), hooks/middleware for deterministic control, and a recovery path.

Four load-bearing parts to name: **acceptance baseline, execution boundary, feedback signals, rollback mechanism**.

Key moves:
- **Filesystem as durable state** — offload what doesn't fit in context; persist work across sessions; plan files as first-class artifacts.
- **Bash/code as the universal tool** — agents solve unforeseen problems by writing code, not by pre-designing every tool.
- **Sandbox + self-verification loops** — run tests, read logs, iterate; verification is the feedback signal that makes long runs converge.
- **Progressive disclosure (skills)** — load capability descriptions on demand; treat AGENTS.md/CLAUDE.md as a table of contents (~100 lines), details in on-demand docs.
- **Encode constraints, don't document them** — linters/types/CI enforce architecture.

Quotable thesis: **"a decent model with a great harness beats a great model with a bad harness."**

## Long-Horizon Reliability (Loop Engineering)

Long tasks outlive context windows. Pattern: externalize state to disk (task file, progress log), make the working loop reentrant so a fresh context can resume from the breakpoint, verify after every step. Rule of thumb: any task longer than ~30 minutes must have crash recovery — it's a requirement, not an option.

**Subagents as context firewall**: discrete noisy work (search, debugging) runs in isolated contexts that return only summaries, keeping the orchestrator thread coherent.

## Memory Taxonomy (Interviewers Expect This)

- **Working** — in-context
- **Episodic** — past interactions, conversation history
- **Semantic** — facts about the world/user
- **Procedural** — how-to, skills

Design points: curated MEMORY.md-style files + on-demand retrieval beats stuffing history. Memory writes should be reviewable/rollbackable. Caution: added memory can make chatbots sound smarter but reduce trust when it surfaces stale or misapplied facts — retrieval precision matters more than recall here.

See [[Agent Memory Types]].

## Follow-up bank (answer sketches)

*Provisional:* condensed from the reference answers to the chapter questions in *AI Agents in Depth* (Li), which the book itself flags as AI-drafted with light human review. Treat these as answer shapes to check, not settled claims.

**Where to spend the next unit of effort**
- *Stronger model, richer context, or more tools?* Find the weak link in failure trajectories:
  perception → context, decision → model, action → tools. Context is usually the answer.
- *ReAct cost grows quadratically with trajectory length.* Compress early turns to conclusions and
  state, write intermediate results to files and retrieve on demand, push subtasks into sub-agents.
- *Thousands of tools.* Group hierarchically (app, then tool), keep a resident catalogue with details
  loaded on demand like Skills, keep a few common tools always present ([[Dynamic Tool Discovery]]).

**Loops, termination, verification**
- *Detect and stop a loop.* Causes: repeated identical errors, hallucinated tools, compaction dropping
  state, stripped reasoning, unsolvable tasks. Cap iterations, fingerprint repeated tool + argument
  calls, escalate past a failure threshold.
- *Why does every premature termination need a verifier?* "Done" is a claim, not a proof: check it
  against real observations and an explicit definition of done, verify failure claims too, and cap
  verification rounds ([[Three-Layer Termination Check]]).
- *30-step vs 300-step budget.* Inject total and remaining budget every step. Small budgets go straight
  to the core function plus a basic check; large ones plan, implement, test and review, with milestones
  against shallow saturation.
- *Execute → validate → feedback beyond code.* Configs in a sandbox, documents rendered and
  screenshot-checked. Not for irreversible actions, where validation would itself act — use
  proposer–reviewer approval before the action ([[Proposer-Reviewer and Sidecar Gating]]).

**Workflow vs agent, humans in the loop**
- *Flight-booking support: workflow or agent?* A workflow backbone (verify → search → pay → book)
  guarantees ordering and confines injection to one node; agent behaviour only for open-ended parts
  (rebooking, alternatives); human confirmation for large payments and refunds.
- *User offline when approval is needed.* Fail safe — never default to executing. Do the reversible
  parts, document the rest, notify asynchronously with a timeout.
- *The agent "promised" an action it never took.* Prompt fix if the model knows and misphrases; a
  harness check comparing text with tool state when that is possible (always for high stakes); training
  only for broad language–action misalignment. Pick the smallest change that is easy to validate and
  roll back.

**Rules and self-improvement**
- *Accumulated rules bloat the system prompt.* Move anything enforceable into linters, CI or tool
  validation; track rule hit rates and conflicts; keep provenance in version control. One successful
  patch is not evolution until it improves later tasks and passes regression.
- *Code rules vs natural-language rules.* Code is deterministic and reads ground truth — the last line
  before irreversible actions — but cannot explain itself or find workarounds. Use both.
- *An experience note has three successes and one failure on a newer API.* Stratify evidence by version
  and conditions instead of counting votes: narrow its scope if it fails only on the new version, lower
  confidence or revoke it if it also fails under the old conditions.
- *A log format changed — adapt or report?* Diagnose first, then adapt *and* report. Adaptation must
  never swallow the anomaly signal.
- *Satisfaction and violations both rose.* Satisfaction is a quality metric, never a safety signal;
  guardrail metrics get hard thresholds an average cannot offset.

**Multi-agent**
- *Keeping a manager's decomposition good.* The strongest model plans, a reviewer checks the plan
  before execution, every subtask carries acceptance criteria and dependencies.
- *One searcher found the answer.* Worker signals `target_found`, manager broadcasts `terminate`,
  workers check at safe points and clean up (sessions, locks, writes) before exiting.
- *Why multi-agent if debate among equal models does not beat one?* External feedback (execution,
  screenshots) adds information, distinct objectives cover blind spots, isolated contexts get past the
  window limit.
- *Org pathologies in agent societies.* Unclear interfaces, misread goals, false "done", telephone-game
  cascades, cyclic handoffs, non-converging chats. Counter with contracts and a common envelope, task
  state machines with acceptance checks, independent cross-validation ([[Multi-Agent Failure Modes at Scale]]).
- *MCP's biggest gap.* Cross-session, event-driven triggers: it is request–response, so nothing
  standard wakes an offline agent ([[MCP Protocol]]).

## See Also
- [[Agentic Workflow Patterns]] — prerequisite-for
- [[ACI (Agent-Computer Interface)]] — instance-of
- [[ReAct Pattern]] — instance-of
- [[RAG Interview Study Guide]] — extends
- [[System Design Interview Study Guide]] — extends
- [[Situation-Indexed Decision Tree]] — extends (the agent spine links down into this guide)
- [[Durable vs Performative Knowledge Split]] — prerequisite-for (this guide is the durable side)
- [[AI Engineering Field Question Bank]] — related (cold-recall questions for this pillar)
- [[Bounding Agents Rather Than Trusting Them]] — extends (the termination and escalation answers)
- [[AI System Design Interviewer Rubric]] — extends
