---
title: Harness Orchestration
tags: [llm, agents, infra, concept]
summary: "Subagents are a context management technique before they are an architecture — isolate as a firewall, define the task graph before parallelizing, and treat the four multi-agent failure modes as harness bugs; label sources and synthesize before delegating."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--07-orchestration.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--07-orchestration.md
  - data/raw/papers/2026-11-06-dibia-2024-autogen-studio.md
  - data/raw/papers/2026-11-06-hao-2026-brain-inspired-graph-multi-agent.md
  - data/raw/papers/2026-11-06-lin-2026-skill-mas.md
  - data/raw/papers/2026-11-06-lin-2026-stellar-colosseum.md
  - data/raw/papers/2026-11-06-qi-2026-beyond-individual-intelligence.md
  - data/raw/papers/2026-11-06-benkovich-2026-agyn.md
  - data/raw/papers/2026-11-07-building-applications-with-ai-agents-ch05-orchestration.md
  - data/raw/papers/2026-11-07-context-engineering-multi-agent-systems-ch04-assembling-context-engine.md
  - data/raw/papers/2026-11-08-building-applications-with-ai-agents-ch03-user-experience-design-agentic-systems.md
---

# Harness Orchestration

> Subagents are a context management technique before they are an architecture. Treat the
> second as a consequence of the first.

## Subagents as Context Firewall

The primary justification is not division of labor — it is **context isolation**.

> Sub-agents function as a **context firewall**: discrete tasks run in isolated windows so
> intermediate noise never accumulates in the parent thread responsible for orchestration.

A search that reads 40 files and finds 3 relevant ones should return **the 3, not the 40**.
The subagent absorbs the exploration; the orchestrator receives a condensed summary
(**~1,000–2,000 tokens**). The parent stays coherent far longer than it otherwise could —
which makes this a direct instrument of [[Long-Horizon Execution]].

*"When working on hard problems that require many, many context windows to solve, sub-agents
are the key to maintaining coherency across many sessions."*

The settled default:

> **Orchestrator holds the plan; subagents hold the details.**

Isolation is also the **most expensive** context lever — tokens multiply and cross-agent
context is lost — so reach for it when a genuine context or trust boundary exists, not for
tidiness.

## Protocols Precede Collaboration

> **Establish a task graph and isolation boundaries *before* introducing parallelism.**

Parallelism added to an undefined task structure produces **collision, not speed**. Define
what each agent owns, what it receives, what it returns, and what it may touch — then
parallelize.

Isolate is also the **most expensive of the four context levers** (see
[[Context Engineering]]): real tokens multiply and cross-agent context is lost. Reach for it
when a genuine context or trust boundary exists, **not for tidiness**.

## Role-Based Separation

From cheapest to most involved:

### Explorer / Executor

| Role | Tools | Model | Context |
|---|---|---|---|
| **Explorer** | Read-only | Cheaper | Isolated, disposable |
| **Executor** | Full | Stronger | Holds the plan |

Read-only exploration is safe and parallelizable, so it can run cheap and wide.
**Constraining the tool set *per role* is the point** — the explorer physically cannot
mutate anything. That is a grant, not a label; see
[[Execution Boundaries and Guardrails]].

### Planner / Executor

Splits decomposition from implementation. The fix for *"the agent got lost in a 40-step
task."*

### Generator / Evaluator

Splits production from judgment — the structural answer to self-evaluation bias. See
[[Verification Loops]].

### Full Pipeline

One reported harness runs a role chain end to end: **Orchestrator → PO-Spec → Feature Design
→ Tech Lead → Build → QA**, with three supporting concepts:

- **Roles** — behavioral definitions holding each agent's logic, prerequisites, constraints,
  and process.
- **Artifacts** — concrete deliverables from each agent, **tagged with task IDs for
  traceability**.
- **Workflow standards** — governance covering technology practice, inter-agent
  communication, and state tracking.

Because artifacts are stored and indexed by task ID they become a **searchable historical
record**: past implementations serve as reference patterns for future work (*reuse the
pagination approach from task 214*).

> **Multi-agent state that persists is organizational memory, not just plumbing.**

## Graph-Based Orchestration

Google's ADK 2.0 replaces ad-hoc Python loops with **structured, declarative, graph-based
primitives**. The harness becomes a **topology** rather than control flow buried in code.

| Primitive | Role |
|---|---|
| **Agent** | Model definition, instructions, state target mappings |
| **`@node`** | Arbitrary Python — deterministic computation, tool calls, classification |
| **Edge** | Declarative routing based on state values or return codes |
| **JoinNode** | Synchronization barrier — blocks until parallel branches complete |

### Typed state

Pydantic schemas replace unstructured dictionaries:

```python
class GatewayContext(BaseModel):
    raw_payload: str = ""
    detected_language: str = "UNKNOWN"
```

ADK **validates inputs and outputs at node boundaries**, so key errors surface at the
boundary rather than three nodes downstream. Schema inheritance lets base configurations
extend across workflows.

This is *encode constraints, don't document them* applied to orchestration: **the contract
between agents is enforced, not documented.**

### Event-driven routing

Nodes return `Event` objects carrying routing instructions:

```python
return Event(actions=EventActions(route="loop_back"))
```

The engine evaluates and executes the matching edge. This **decouples node logic from graph
topology** — a node states its *outcome*; the graph decides what that means. Rewiring the
workflow doesn't touch node code.

### Subgraph composition

ADK 2.0 treats **compiled workflows as first-class nodes**, so self-contained sub-flows nest
inside higher-level coordinators — the same composition property that makes functions
useful, applied to agent graphs.

## Multi-Agent Failure Modes

| Failure | Shape | Mitigation |
|---|---|---|
| **Loop oscillation** | Two nodes bounce work between them indefinitely | Iteration counters on cyclic edges; forced escalation |
| **Context pollution** | Nested workflows leak state upward, defeating isolation | Explicit boundary schemas; return summaries only |
| **Concurrency collision** | Parallel branches write the same state or file | JoinNode barriers; per-branch ownership of state keys |
| **Consensus deadlock** | Reviewer agents never agree, blocking progress | Tie-break rule, majority threshold, or a final arbiter |

**All four are harness bugs. None is fixed by a better model**, and all four get worse as
agent count rises — which is the practical argument for **keeping agent counts as low as the
task allows**.

## Handoff Design

What crosses a boundary is the whole design:

- **Structured, not prose.** A typed schema — findings, files touched, confidence, open
  questions — beats a paragraph.
- **Summaries, never transcripts.** Sending a subagent's full history back **defeats the
  firewall**.
- **State on disk, references in the message.** Large artifacts go to files; the handoff
  carries paths. See [[Long-Horizon Execution]].
- **Declare what was *not* done.** Scoped claims prevent the orchestrator from assuming
  coverage that doesn't exist.
- **Label every source in the subagent's prompt.** A role statement, then inputs tagged by
  origin (`[FROM_MAIN_AGENT]`, `[FROM_USER]`, `[TOOL_RESULT]`), then explicit boundaries, then
  a JSON output schema. A subagent that can't tell instructions from data will follow
  injected text.
- **Synthesize, don't delegate understanding.** "Based on your findings, fix the auth bug"
  pushes the orchestrator's job onto the worker. The orchestrator reads the findings and
  hands down a precise spec — file, line, change, and what done looks like.

### Collaboration primitives

Multi-agent tooling reduces to a few primitives — `spawn`, `cancel`, `send_message`,
`list_agents` — each run in one of four modes: **sync** (wait for the result), **async**
(task ID now, event later), **streaming** (partial results), or **multi-turn** (a
conversation with the worker). Choose per task: a 30-minute research job should never be a
sync call. Async workers need the parent to be an event loop that consumes results at safe
points — see [[Asynchronous Agent Event Loop]].

## When *Not* to Go Multi-Agent

Multi-agent is the expensive option. **Single agent with verification is the correct
default**; escalate only when:

- **Context genuinely doesn't fit** — the firewall argument, the strongest reason.
- **Roles need different tools or trust levels** — read-only explorer, sandboxed executor.
- **Self-evaluation bias is the blocker** — you need an external evaluator.
- **Branches are genuinely independent** — real parallelism, not sequential work in costume.

Absent one of these, added agents multiply token cost and introduce the four failure modes
while solving nothing. In order of increasing cost: **single agent with verification →
two-agent supervisor → multi-agent with a shared harness layer.**

## A no-code builder as evidence for the build-debug loop

AutoGen Studio (Dibia et al., Microsoft Research; EMNLP system demonstration 2024) is a React and FastAPI tool where multi-agent workflows are declarative JSON specs, with a playground, a profiler that tracks, for each agent, message counts, token use, dollar cost and whether tool calls worked, and export as JSON, a Python manager, a CLI endpoint or a Docker container. The authors describe multi-agent workflows as brittle and say the tool is a prototype to export, not a production system. The only quantitative evidence is adoption: more than 200K installs over five months plus more than 135 GitHub issues (both self-reported), which are installs and not active users; the authors' own walkthrough of a fictional persona splitting one agent into four is anecdotal. There is no user study or comparison with other tools, and its claim that the design patterns apply to every multi-agent framework is asserted. The largest issue cluster, 27 issues (self-reported), covered API keys, model configuration and server connections. The extraction notes two internal inconsistencies: the abstract counts four design principles where Section 3 lists three core objectives, and Section 7 announces two future research areas but lists three.

## Measured results on team structure (2025-2026 preprints, self-reported)

Each bullet is one preprint's own result under its own setup; none is a replication.

- **BIGMAS** (Hao et al., arXiv 2603.15371): a designer model builds a task-specific graph of nodes that read and write a shared workspace with four partitions (read-only context, working area, system state, answer sink), and an LLM orchestrator routes when a node has several successors. Writes are validated and a failed write never changes the workspace. On Game24, Six Fives and Tower of London, 100 instances each, single runs, DeepSeek-V3.2 went 25/12/6 to 36/30/20 against ReAct 26/18/10 and a tree-search baseline 30/25/18; all six models improved on all three tasks (for example GPT-5 96 to 100 on Game24). Node counts averaged 3.07, 3.87 and 4.82 per graph. The extraction flags that the routing-call comparison between failing and passing runs is internally inconsistent, that no ablation separates the designer, workspace and orchestrator, and that there are no seeds or compute matching.
- **Skill-MAS** (Lin et al., arXiv 2606.18837): a frozen meta-agent writes the multi-agent system from a text skill document that is evolved over 10 rounds with 5 rollouts per task. Average scores were 29.49, 27.55, 38.41 and 41.05 across four small models against best baselines of 21.29, 24.83, 32.23 and 35.70 on four benchmarks (test sets of 84 to 168 items; no variance). The unevolved starting skill already matched or beat several baselines, evolution cost up to 59 USD per model is excluded from the headline cost, and without ground-truth labels performance drops. The evolved skills moved from a linear pipeline to parallel fan-out, a merge node and link verification.
- **Stellar Colosseum** (Lin, Woodruff et al., Google Research, arXiv 2609.15983): a fixed pipeline of strategy exploration, a readiness gate, DAG decomposition, parallel section solving and global verification, where each stage proposes candidates, an adversarial falsifier attacks them, and overlapping random-sample trees aggregate the survivors. On 300 theorem-proving tasks (LLM grader) it scored 54.0% and 55.0% with two Gemini models against 30.3% for direct Gemini 3.1 Pro; a cross-model selection rule using eight critiques reached 71.0%. On 222 Codeforces problems the only ablation (a code-execution probe) moved 213 to 218 solved. The authors concede there is no compute-matched evaluation and no ablation of the core stages, and that falsification does not establish correctness.
- **Survey taxonomy** (Qi et al., arXiv 2605.14892): organises multi-agent work along role, communication, orchestration and interaction axes, and failure analysis into three families (system structure, execution stage, causal lifecycle). It reports no experiments of its own; figures it quotes for other systems (2.8x gain with 90% fewer tokens, 4.55% and 15% of cost) are second-hand and unverified, and its attribution-benchmark sizes range from 148 to over 2,000 cases.
- **Agyn** (Benkovich and Valkov, arXiv 2602.01465, under review): an issue-resolution team with four roles (manager, researcher, engineer, reviewer), each running in a separate sandbox, with all traffic routed through the manager's manage tool. Manager and researcher ran GPT-5 (medium reasoning) and engineer and reviewer GPT-5-Codex (medium); a task counts only if the reviewer approves the pull request. It reports 72.2% on SWE-bench Verified text-only (500 tasks, fixed configuration, apparently one run) against 71.8% for OpenHands with GPT-5, 71.8% for mini-SWE-agent with GPT-5.2 (high) and 65.0% for mini-SWE-agent with GPT-5 (medium); the paper's "7.4% higher" is 72.2 against the 65.0 row, and mini-SWE-agent with Gemini 3 Pro scored 74.2. There is no ablation against a single agent, no cost or token figures, and the authors say small leaderboard gaps need caution. The GitHub MCP integration bloated context, so they moved to the gh command line. Failures reported include manager stalls waiting on agents that had finished.

## Book guidance on tool selection, plan-execute engines and interaction design

These are book chapters with no experiments; each point is the author's claim.

- **Tool selection and topology (Albada ch. 5):** start with the simplest planning approach that fits. Semantic tool selection (embed the tool catalogue once, embed the query with the same model) is called the most common and recommended for most cases; hierarchical selection is slower, often more accurate, and only worth it with many similar tools. Cap chain length because errors compound; use a chain for linear tasks and a graph only to branch and consolidate, with capped depth and branching and a unit test for each router. The chapter's code listings are partly broken and its LangChain agent types have dated.
- **Plan-execute engine (Rothman, Context Engineering for Multi-Agent Systems, ch. 4):** a Planner emits a JSON plan, an Executor runs it, and a Tracer records plan, resolved inputs and outputs. An Agent Registry's capability descriptions are the Planner's context, and `$$STEP_N_OUTPUT$$` placeholders chain outputs. The chapter shows one worked run with no evaluation or baseline; the plan is not re-planned on failure, no reflection step is built despite the name, and its "MCP" is a homegrown message envelope.
- **Interaction design (Albada ch. 3):** expose autonomy as adjustable levels (manual, ask, agent) with stated risks, decide up front which experiences are synchronous and which asynchronous, and on failure explain, preserve progress and escalate to a human. The chapter reports no user study, and its only figures are uncited speech and reading rates.

## See Also
- [[Agent Orchestration Patterns]] <!-- auto-linked -->
- [[Loop Detection and the Two-Retry Rule]] <!-- auto-linked -->
- [[Multi-Agent Context]] <!-- auto-linked -->
- [[Multi-Agent Role Specialization]] <!-- auto-linked -->
- [[Harness Engineering]] — related (part of)
- [[Harness Anatomy]] — related (part of)
- [[Long-Horizon Execution]] — related
- [[Verification Loops]] — related
- [[Context Engineering]] — prerequisite-for
- [[Execution Boundaries and Guardrails]] — prerequisite-for
- [[Asynchronous Agent Event Loop]] — extends (async workers and interrupts)
- [[Deep Agent Pillars]] — instance-of (subagent delegation as one pillar)
- [[Harness Subsystem Attribution]] — extends
- [[File-Disjoint Agent Waves in One Working Tree]] — instance-of
- [[AIOS]] — related (resource scheduling beneath agent frameworks)
- [[Aegean Stability-Horizon Consensus]] — instance-of (quorum plus stability horizon for stopping)
- [[AsyncThink Fork-Join Organizer]] — instance-of (learned fork and join inside one model)
- [[Conductor Learned Orchestration]] — instance-of (learned natural-language workflow)
- [[SALE Strategy Auction]] — instance-of (plan-bid assignment across model sizes)
- [[SAT Self-Organizing Agent Teams]] — instance-of (learned strategy bank)
- [[Agent Primitives Latent Composition]] — instance-of (reusable primitives over KV-cache)
- [[Delegation Ceiling and Posterior Distortion]] — related
- [[Coordination Network Measurement in Multi-Agent Coding]] — related
- [[CAID Centralized Asynchronous Isolated Delegation]] — instance-of (git-worktree delegation)
- [[HERMES Dev-Primitives]] — instance-of (dev-process primitives as orchestration)
- [[Harness Effect on Token Economics]] — related
- [[Harness-of-Harness Cross-Loop Development]] — related
- [[OpenHands Generalist Agent Platform]] — related
- [[Team of Rivals Critic-Veto Orchestration]] — related
- [[Agensh Orchestrator-Free Agent Scaling]] — related
- [[Team of Thoughts Heterogeneous Model Orchestration]] — related
- [[WebAgent and HTML-T5 Modular Web Automation]] — related
- [[CoAct-1 Coding Actions for Computer Use]] — related
- [[Muses-Bench Multi-User Agent Benchmark]] — related
- [[OS-Copilot FRIDAY Tool Repository]] — related
