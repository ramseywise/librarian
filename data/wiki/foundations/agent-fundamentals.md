---
title: Agent Fundamentals
tags: [foundations, llm, concept]
summary: "Agent = LLM + Context + Tools, read as policy, observation space and action space — the five-part context and what breaks when each part is removed, the four-step tool call, why RL-trained 'model-as-agent' still needs a harness, the three places an agent can learn, and when a workflow beats an autonomous agent."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--03-agentic-foundations--agent-fundamentals.md
  - data/raw/repos/learn-ai-engineering/generative-ai--03-agentic-foundations--README.md
  - data/raw/papers/2026-11-07-ai-agents-definitive-guide-ch04-models-behind-agents-capabilities-optimization.md
  - data/raw/papers/2026-11-07-building-applications-with-ai-agents-ch02-designing-agent-systems.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch04-building-web-scraping-agent-llm.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch11-future-ahead.md
---

# Agent Fundamentals

**Agent = LLM + Context + Tools.** Each term is broader than it first sounds, and each has
an RL analogue:

| Term | Role | Covers | RL analogue |
|---|---|---|---|
| LLM | Reasoning engine | Intent, planning, choosing the next action; knowledge from pretraining, decision policy from post-training | Policy |
| Context | Working set | Environment state, user memory, domain knowledge, own state, task progress | Observation space |
| Tools | Action interfaces | Tool calls, on-demand skills, generated code, sub-agents, messages to the user, external events | Action space |

The observation and action spaces are the **interface between model and world**, the way
an instruction set is the interface between software and hardware. What is not in context
does not exist for the model; an action not in the tool set is something it can only
recommend in words. So with the model held fixed, the primary lever is **expanding context
and tools** — many "we need a smarter model" problems are interface problems. General agents
were built by taking the union of web research, file/code and screen action spaces, not by
swapping models. Expansion must be on-demand, relevant and permissioned: irrelevant context
is noise, and every tool adds selection cost and attack surface (see
[[Tool Design as Harness Surface]]).

## Tools

By direction of interaction: **perception** (world → agent on request: search, reads,
queries), **execution** (agent → world: code, writes, API calls), **collaboration** (agent ↔
agent or human: delegation, confirmation), **event triggers** (world → agent unprompted:
email, cron, webhook — these wake the agent rather than being called), and **user
communication** (progress updates, check-ins).

A tool call has four steps: the context declares the tools (name, purpose, schema); the
model decides whether, which and with what arguments; the framework executes and appends the
result; the model decides what next. The developer defines and runs tools; **the model makes
every decision about using them**.

General vs. specialised: a sandboxed code interpreter (network off by default, confined
directory, CPU/memory/time/output limits) composes better than a pile of single-purpose
tools, while payments, deletes, outbound email and deploys stay as dedicated tools with
explicit parameters, narrow permissions and an audit trail. General capabilities for
exploration; specialised tools to constrain risk.

## Context: static prefix plus trajectory

| Part | Lifetime |
|---|---|
| System prompt (role, rules, cross-session memory, injected environment state) | Static prefix |
| Tool definitions | Static prefix |
| User messages (plus retrieved knowledge) | Trajectory |
| Assistant messages (reasoning, content, tool calls) | Trajectory |
| Tool results | Trajectory |

The prefix is constant across the conversation, which is what makes KV caching work; the
trajectory grows every turn. [[Context Anatomy]] covers ordering and caching in depth.

**Ablation: every part is load-bearing.** Removing one part at a time (keeping the system
prompt) gives a distinct failure for each:

| Removed | Failure |
|---|---|
| Tool definitions | Cannot act; does not know tools exist |
| Tool results | No feedback, so it repeats the same call and loops forever |
| Reasoning in assistant turns | Consecutive decisions contradict each other |
| Message history | Loses continuity, restarts the task, repeats finished steps |

An agent can only decide on what is in its context.

## The loop

The [[ReAct Pattern]] — reason, act, observe, repeat — re-sends prefix plus full trajectory
on every call. Accumulation is what lets the model know which stage it is at and what has
been tried, and the structured trajectory is both a debugging record and raw training
material ([[Post-Training for Agents]]). The cost: **total tokens grow quadratically** with
trajectory length, which is why compaction exists. Exit conditions for an autonomous loop: a
final-output tool is called, the model replies with no tool calls, an unrecoverable error,
or the round cap (see [[Loop Termination Design]]).

## Model as agent

Frontier models now internalise the **tool-calling decision policy** through RL — when to
call, which tool, whether to continue, chains of hundreds of calls. Two points are often
confused:

- **RL teaches the decision; it does not contain the tool.** Search and sandboxes still run
  outside the weights, now often server-side as API built-ins. The loop moved from client
  to server and the decision moved into the model.
- **A stronger model makes the harness matter more, not less.** The more decisions the
  model owns, the more a wrong one costs, so constraint and verification get finer-grained
  ([[Harness Engineering]]).

Freeform tool calling (raw code or SQL instead of JSON-escaped arguments) changes the API
format, not the loop.

## Three places an agent can learn

| Path | Lives in | Persists | Best for |
|---|---|---|---|
| Contextual adaptation | The current context | This task | Fast, cheap adjustment |
| External artifacts | Docs, prompts/skills, code, harness | Across tasks; auditable | Facts, statable strategy, deterministic rules |
| Parameters | Weights, via post-training | Permanently | High-dimensional skills rules cannot express |

They run at different timescales and combine; [[Self-Learning Agents]] covers the
non-weight paths and [[Post-Training for Agents]] the weight path.

## Choosing a model

Evaluate on your own tasks, not leaderboards — tool-calling ability varies more than
general benchmarks suggest. Use a reasoning model for anything multi-step. **Output speed is
latency**: 2 s slower per round over 20 sequential rounds is 40 s. Multimodality is a hard
requirement when inputs include images, audio or video. Closed models lead on capability;
open weights win on cost, private deployment and fine-tuning.

## Workflow vs. autonomous agent

Climb only as far as needed: **single call → workflow → autonomous agent**.

| | Workflow | Autonomous agent |
|---|---|---|
| Path | Fixed in code; the LLM works inside nodes | Chosen at runtime from feedback |
| Strength | Steps cannot be skipped or reordered; injection confined to one node | Handles the unforeseen |
| Weakness | Only preset exception branches | Costlier; errors compound; needs explicit stops |
| Fits | Compliance-critical, decomposable processes | Open-ended tasks with unpredictable step counts |

Real systems mix them: a workflow spine for the compliance-critical path, agent nodes for
the flexible parts. The three principles (keep it simple, keep it transparent, design the
agent–computer interface so misuse is impossible — *poka-yoke*) are in
[[Agentic Workflow Patterns]] and [[ACI (Agent-Computer Interface)]].

## Guardrails

Defence in depth, layered by position: **input** (relevance and safety classifiers,
moderation, rules), **execution** (rate each tool by reversibility, permission level and
financial impact; high risk goes to review or human confirmation), **output** (PII filters,
content validation). [[Constitutional Classifiers]] are the reference design for the
classifier layer. Escalate to a human when retries pass their cap and before high-risk
operations, at least until reliability is proven ([[Execution Boundaries and Guardrails]]).

## Model sizing and role staffing (two book chapters)

Albada (Building Applications with AI Agents, ch. 2) gives a selection table built from HELM MMLU scores, reported by the book with no date or run settings: the 8B Llama 3.1 Instruct Turbo is listed at an MMLU of 56.1 and fits on one RTX 3090; the 70B Llama 3 is listed at 79.3 and needs about 160 GB of VRAM spread over four A100s; the 405B Llama 3.1 reaches 84.5 at the cheapest relative price; DeepSeek-v3 reaches 87.2 for 2.75x that price; Claude 4 Opus with extended thinking reaches 86.5 for 75x (table values the book reports, not its own runs, so self-reported). Rules of thumb it states: a single 24 GB consumer GPU can serve models of roughly 14B parameters or fewer, flagship models need at least 12 GPUs. Its advice is to use big models for open-ended tasks, small ones for repetitive well-defined tasks, route dynamically, and compare candidates on your own task because benchmarks only guide.

Koenigstein (AI Agents: The Definitive Guide, ch. 4) staffs a multi-agent team by role: quick decoder-only models do the worker jobs, a reasoning model takes the analyst seat, an encoder (ModernBERT) scores relevance, and a slower, more deliberate LLM supervises. In its LangGraph example the analyst runs Qwen3-235B-A22B-Thinking with a 1536-token thinking budget, the workers run Qwen3-32B with thinking off and the supervisor is GPT-4.1, all at temperature 0. Its practitioner rule (no experiment shown) is that a thinking budget of 1000 tokens or more suits non-trivial reasoning; enable thinking for planning, tool selection and verification, disable it for short low-risk turns. Closed-model prices in the chapter run to $150 input and $600 output per million tokens (o1-pro) against about $0.3 and $3 for large open models on cheap clouds, undated. Its sequencing advice is to begin with managed APIs and shift toward self-hosting open models once the team has grown into it.

Limits of this section:

- Both chapters are practitioner guidance with no experiments. Albada's tables carry no date, MMLU protocol or run settings, and prices are relative and undated. Koenigstein's chapter is an Early Release draft; prices and model choices will age.
- Albada's example agent handles one tool though three are stated, its printed code is incomplete, and the text says three design patterns but lists two.
- Koenigstein's thinking budget is 1024 in one snippet and 1536 in the team setup, and a ModernBERT rope_scaling example claims 32k to 128k although its native length is 8192 per the chapter's own table.

## Brain, perception, action, and open problems (Raieli and Iuculano, ch. 4 and 11)

One book frames an LLM agent as a brain (reasoning, memory, decisions), perception (extra input modalities) and action (tools that change the environment). It sorts planning into decomposition-first, interleaved decomposition, multi-plan selection and memory-augmented planning, and suggests a formulate-then-reflect two-stage plan check. Its worked agent wraps search tools with a zero-shot ReAct prompt, keeps the sources used so answers can be traced, and gives each tool a name and description.

Chapter 11 surveys open problems: human-agent communication (show progress, confirm the goal before acting, say which actions need approval), multi-agent value, reasoning and creativity limits. It reports an expert-annotated taxonomy of multi-agent failures with 14 causes in three groups (specification and design, inter-agent misalignment, verification and termination), drawn from another paper's annotation of 150 traces (reported). It also states that multi-agent systems give marginal gains at higher cost, attributing this to unnamed studies.

**Limits of this source:** no experiments of its own. Chapter 4 describes a "web scraping" agent that only wraps search tools, uses a legacy agent API, and has no memory. Several figures in chapter 11 (share of jobs at risk, inference share of energy) lack a named study. Table 11.1 is captioned as failure causes yet compares single-agent and multi-agent trade-offs.

## See Also
- [[ReAct Pattern]] — prerequisite-for (the loop that ties the three terms together)
- [[Harness Engineering]] — extends (the production view: Model + Harness)
- [[Context Anatomy]] — extends (the five context parts in depth)
- [[Tool Design as Harness Surface]] — extends (the action-space side)
- [[Constitutional Classifiers]] — extends (the classifier guardrail layer)
- [[Post-Training for Agents]] — extends (the parameter learning path)
- [[Real-Time Multimodal Agents]] — extends (the same loop under real-time constraints)
- [[Agentic Workflow Patterns]] — alternative-to (fixed-path workflows)
- [[Single Agent With Tools]] — related
- [[SayCan Affordance-Grounded Skill Selection]] — related (an LLM's choice among skills weighted by what the robot can do now)
- [[SayCan Affordance-Grounded Skill Selection]] — related (an LLM's choice among skills weighted by what the robot can do now)
- [[World Knowledge Model for Agent Planning]] — related
- [[Foundation Models as Decision Makers (MDP View)]] — extends
- [[Code, Workflow, RAG or Agent Decision Guide]] — extends
- [[Agentic vs Agentive: Agent Model Position]] — related
- [[Adapting While Learning Tool Usage Adaptation]] — related
