---
title: Context Anatomy
tags: [context, llm, agents, concept]
summary: What goes in the window and in what order — system-prompt altitude, the five layers organized by stability rather than topic, and stable-before-dynamic ordering for cache prefix matching.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--02-context-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--02-context-anatomy.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--context-management.md
---

# Context Anatomy

## The Components

A context window at inference time, roughly in order:

1. **System prompt** — role, task framing, behavioural constraints
2. **Tool definitions** — names, descriptions, parameter schemas
3. **Retrieved knowledge** — documents, search results, RAG chunks
4. **Memory** — summaries and facts carried across sessions
5. **Runtime state** — date, user, environment, permissions
6. **Message history** — the conversation, including tool calls and results
7. **The current turn** — what the user just asked

## System Prompt Altitude

System prompts must be calibrated to the **right altitude** — a Goldilocks zone between
two failure modes.

| Too low | Right altitude | Too high |
|---|---|---|
| Hardcoded if/else logic in prose | Specific enough to guide, flexible enough to generalize | Vague guidance assuming context the model lacks |
| Brittle — breaks on any unenumerated case | Heuristics with clear signals | Under-specified — model invents its own interpretation |
| "If the user says X, reply Y. If Z, reply W…" | "Prefer X when the signal is A; escalate when uncertain." | "Be helpful and use good judgment." |

**The low-altitude failure is the common one in engineered systems**, because each
production bug tempts you to add one more rule. The result reads like a decision tree, is
unmaintainable, and still misses the next edge case.

> When you catch yourself adding a fourth conditional to a prompt, the fix is usually a
> **tool or a code-level control**, not a fifth conditional.

## The Five Layers

Organize by **usage frequency, stability, and enforcement requirement** — not by topic.

### Layer 1 — Persistent instruction
Valid in every session: agent identity, project-wide conventions, architectural
invariants, safety constraints, prohibited actions. Short, explicit, stable, operational.

**Test:** *if it isn't true in nearly every task, it doesn't belong here.*

### Layer 2 — On-demand knowledge
Reusable procedures relevant only to certain tasks: skills, playbooks, deployment
procedures, eval methodologies, debugging checklists, long reference docs.

Governed by **progressive disclosure** — only a short name and description (*what* +
*when*) stay permanently visible; full content loads on activation. A `skills/` directory
is this made concrete: ~10 tokens resident, thousands loaded on demand.

**Write the description as a routing rule, not a feature summary** — "Use when … / Do not
use when …", with negative examples; explicit exclusions are what make routing precise.
Where the full content lands is a cache vs instruction-following trade-off: appending to
the system prompt follows best but breaks the prefix on every load; reading it as a plain
file keeps the cache but many models treat it as reference, not orders; resident metadata
plus a dedicated skill-loading tool writes the cache once and keeps routing and execution
as separate steps. See [[Cache-Stable Context Layout]].

### Layer 3 — Runtime injection
Values changing between sessions, turns, users, environments: date/time, user or tenant
ID, environment variables, permission state, task status.

Assemble **programmatically at request time** rather than storing in the system prompt —
information stays current, and irrelevant dynamic data doesn't consume context every turn.
Date/time is canonical: without injection the model guesses, and every relative date
("last quarter", "recent") resolves wrong.

### Layer 4 — Long-term memory
Accumulated across sessions: preferences, repeated corrections, project discoveries, prior
decisions, known failure patterns. **Never a full transcript pasted forward** — organize as
a compact index plus retrievable detail. Must be **editable and auditable**, so wrong or
outdated entries can be removed rather than accumulating. See [[Memory as Context]].

### Layer 5 — Deterministic system
Behaviour that must be reliable belongs in **code**, not context: hooks, permissions,
schemas, validators, tool constraints.

> A model may ignore, misunderstand, or inconsistently follow a textual instruction. **A
> code-level control cannot be talked out of enforcing itself.**

This layer is the answer to prompt-altitude drift. "The agent keeps doing X" is usually a
hook, not a stronger sentence.

## Ordering: Stable Before Dynamic

Ordering is not cosmetic — it determines **cache economics and attention placement**.

Prompt caching works by **prefix matching**: the cache hits only on an exact-match prefix,
and the first differing token invalidates everything after it.

```
[ system prompt ] [ tools ] [ stable memory ]     <- static, cacheable prefix
[ retrieved docs ] [ history ] [ runtime state ]  <- dynamic, changes per call
[ current query ]                                 <- last
```

**Put a timestamp at the top of the system prompt and you have destroyed cache reuse for
the entire window on every single call.**

This aligns with a second effect: for long-document work, put longform data above the
query — up to 30% quality improvement when the query appears at the end. Cache economics
and attention placement point the same direction. See [[Long-Context Prompting]].

The full list of cache breakers (timestamps, unordered serialisation, mid-session tool
changes, model switches) and the boundary-ordering rules are in
[[Cache-Stable Context Layout]]. Two runtime-state consequences have their own pages:
chat templates make prior reasoning part of the conversation state
([[Reasoning State Pass-Back]]), and current task state belongs in a small overwritten
block at the end of the window ([[Agent Status Bar]]).

## Structure Within the Window

- **Delimit untrusted content** — wrap user input and retrieved documents in tags so the
  model can distinguish instructions from data. Also the first line of injection defence.
  See [[XML Prompt Structuring]].
- **Structured outputs are context engineering** — a schema constrains what comes back,
  which determines what the *next* turn's context contains. Schema discipline compounds
  across a loop. See [[Structured Output]].
- **Few-shot examples: diverse and canonical** — a handful of well-chosen examples
  outperforms an exhaustive rule list at fewer tokens. See [[Few-Shot Prompting]].

## The Formal View

The context-engineering survey literature writes context as a typed assembly rather than a
string: `C = A(c_instr, c_know, c_tools, c_mem, c_state, c_query)` — instructions,
retrieved knowledge, tool definitions, persistent memory, dynamic state, the query. **Context
engineering is designing `A`** (selection, ordering, formatting) under a token budget
([[Context Window Budgeting]]), not writing any single component.

### Examples: How Many, Which Ones
- **Two to five** examples capture most of the gain; measure before adding more.
- **Select by similarity to the query** when there is a pool — retrieved examples beat a
  fixed set on heterogeneous traffic.
- **Cover the output space** — at least one example per output class, including "none" or
  "refuse", or the model under-produces the missing classes.

## Worked Example: Tuning a Deep-Research Agent

A published case study (a planner agent writing search tasks plus a search worker) fixed
every failure by changing the context, not the model:

| Symptom | Context fix |
|---|---|
| Planned 3 searches, ran 2, gave no reason | State the completion rule — flexible ("skip only if overlapping, say why") while developing, strict in production |
| Status values drifted (`pending`/`to-do`, `done`/`finished`) | Enumerate allowed values — every free-text field code reads needs a closed set |
| "Latest" news was a year old | Inject the current date as dynamic context, after the stable prefix |
| One agent did tasks, memory, search and report; forgot steps as context grew | Split a search worker that gets only the query text, on a cheaper model ([[Multi-Agent Context]]) |
| Decisions were opaque | Write the task list to external state so every decision is inspectable |
| Undefined behaviour on search failure | Error-path instructions: retry once, record, continue |

Before shipping, check the context for **completeness, clarity, consistency** (system
prompt and tool descriptions agree) and **testability**; then track task-completion rate,
behavioural consistency and error rate as it changes. Over-constraint vs
under-specification is a calibration problem that evals settle ([[Evaluating Context]]).

## See Also
- [[Context Engineering]] — part-of
- [[Why Context Is Finite]] — depends-on
- [[Memory as Context]] — extends
- [[Measuring Fixed Context Overhead]] — extends (how to measure what the stable layers actually cost)
- [[Cache-Stable Context Layout]] — extends
- [[Reasoning State Pass-Back]] — extends
- [[Agent Status Bar]] — extends
- [[Context Window Budgeting]] — prerequisite-for
- [[Few-Shot Prompting]] — extends
