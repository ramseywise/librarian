---
title: Context Anatomy
tags: [llm, agents, concept]
summary: What goes in the window and in what order — system-prompt altitude, the five layers organized by stability rather than topic, and stable-before-dynamic ordering for cache prefix matching.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--02-context-anatomy.md
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

## Structure Within the Window

- **Delimit untrusted content** — wrap user input and retrieved documents in tags so the
  model can distinguish instructions from data. Also the first line of injection defence.
  See [[XML Prompt Structuring]].
- **Structured outputs are context engineering** — a schema constrains what comes back,
  which determines what the *next* turn's context contains. Schema discipline compounds
  across a loop. See [[Structured Output]].
- **Few-shot examples: diverse and canonical** — a handful of well-chosen examples
  outperforms an exhaustive rule list at fewer tokens. See [[Few-Shot Prompting]].

## See Also
- [[Context Engineering]] — part-of
- [[Why Context Is Finite]] — depends-on
- [[Memory as Context]] — extends
