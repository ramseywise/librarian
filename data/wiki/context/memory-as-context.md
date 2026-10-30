---
title: Memory as Context
tags: [context, memory, llm, agents, concept]
summary: Memory is not a sibling pillar of context engineering but the mechanism by which context outlives a window — every memory decision is a decision about what occupies a future context window.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--06-memory.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--05-memory-as-context.md
---

# Memory as Context

> Memory is not a sibling pillar of [[Context Engineering]]. It is the mechanism by which
> context outlives a window.

## The Framing

Memory has **no effect on a model except by entering a context window**. A memory store the
agent never reads is inert. So every memory design decision is really a context decision —
what gets written, what gets selected back in, at what size.

This reframes the design question from *"what should the agent remember?"* to:

> **"What should occupy the window three sessions from now, and how does it get there?"**

The second question is answerable. The first invites hoarding.

For the storage-side taxonomy and implementation mechanics (`BaseStore`, namespaces,
reflection), see [[Agent Memory Types]]. This page covers the context-side framing.

## Episodic vs Semantic — The Distinction That Matters

Of the memory tiers, one distinction governs whether a memory system converges or grows
without bound:

- **Episodic** memory accumulates **linearly with time** and rots. Most of what happened is
  not worth carrying.
- **Semantic** memory is *distilled from* episodes and stays **roughly constant in size**.

A system that only stores episodes grows forever. One that distills episodes into semantic
facts converges.

**The distillation step is the whole design:**

```
episodic ×3: "the user corrected me about commit format"  (three separate events)
        ↓ distill
semantic ×1: "commit format is `type(scope): desc (#num)`"
```

Three records collapse to one fact, and the fact is the only part that changes future
behaviour.

## Log, Archive, Business State

**The trajectory is a log; long-term memory is an archive.** The trajectory is append-only
and never rewritten; long-term memory is rewritten, merged and pruned; working memory is
the filtered, activated subset of both that is in the window now. A third store,
**business state** ("awaiting payment"), records the task's stage for event-driven agents.
Post-session extraction should be **selective** (skip "the search returned 3 options"),
**abstract** ("prefers window seats", not tied to one flight) and **typed** (preference,
restriction, account number).

### Three Independent Axes

| Axis | Question | Options |
|---|---|---|
| Hierarchy | *Where* is it stored? | Trajectory · long-term memory · business state |
| Format | *How* is it stored? | Simple notes · enhanced notes · JSON cards · advanced cards |
| Cognitive type | *What* is stored? | Episodic · semantic · procedural (skills/playbooks retrieved by task type) |

The axes combine freely — a procedural memory can live as a JSON card in long-term memory.
Fuller taxonomies: [[Agent Memory Types]], [[Memory Forms Taxonomy]].

### Storage Formats

| Format | Wins | Loses |
|---|---|---|
| Simple notes (one atomic fact) | Cheapest; passes basic recall | Links between facts ("senior engineer, leads recsys" becomes unrelated facts) |
| Enhanced notes (narrative per topic) | Nuance | Redundant; one change rewrites several paragraphs; long text weakens embeddings |
| JSON cards (`category.subcategory.key`) | Partial updates; predictable | Rigid — one fact fits three categories |
| Advanced cards (facts + backstory, person, relationship, timestamp) | Disambiguation (the user's dentist vs their father's cardiologist, same surname) | Expensive to generate and maintain |

**Mix them:** advanced cards for critical, low-volume facts; simple notes for high-volume,
low-stakes ones.

**Beyond text — User as Code.** Keep an append-only fact log and periodically regenerate
**typed program state** from it (write-ahead log plus checkpoint). Aggregations
("international trips in 2025") become one expression — reported ~99% accuracy vs 6–43%
for retrieval-based memory — and conflict checks (drug class × allergy) or constraints
(passport validity vs departure date) run as code on every update, with a free-text
`notes` field for what won't type. Writing facts into model parameters is a research
direction, not a practice.

## Structured Note-Taking

Anthropic's term for the pattern: the agent **writes notes to persistent storage outside the
context window** and retrieves them later.

This is agentic memory in its simplest usable form — no vector store, no embeddings, just
files the agent maintains. A `NOTES.md` or `progress.md` updated as work proceeds survives
compaction, crashes, and session boundaries, **because it never depended on the window**.

Why it outperforms its complexity:

- **Write is cheap, read is selective.** Writing costs one tool call; the note re-enters
  context only when needed.
- **It is state extraction done eagerly.** An agent already keeping structured notes is
  trivially compactable — the state is already on disk. See [[Context Compaction]].
- **It is auditable.** A human can read the notes, correct them, delete wrong entries.
- **It doubles as crash recovery.**

**The discipline:** write the note **when the decision is made**, not when the window fills.

> Notes written under compaction pressure are *reconstructions*. Notes written in the moment
> are *records*.

## Index-Plus-Detail

The core architecture for long-term memory: **never load the full store.** Load an index;
fetch detail on demand.

```text
MEMORY.md (index)                       memory/*.md (detail)
- [Topic A](a.md) — one-line hook  -->   full content, loaded only when relevant
- [Topic B](b.md) — one-line hook
- [Topic C](c.md) — one-line hook
```

Claude Code's auto-memory is exactly this: `MEMORY.md` (first 200 lines / 25 KB) loads at
session start; topic files are read only when a hook line signals relevance.

This is **progressive disclosure applied to memory** — the same pattern as on-demand skills
in [[Context Anatomy]], and the same pattern as lightweight identifiers in
[[Context Retrieval Strategies]]. One idea, three applications: *keep a cheap pointer
resident, load the payload on demand.*

### The one-line hook is the highest-leverage text in the system

It is the **only** thing deciding whether the detail ever loads. A vague hook makes a
correct memory unreachable — the memory is present and useless, which is **worse than
absent**, because it creates false confidence that the fact is available.

## Memory Hygiene

Memory must be **editable and auditable**. Append-only memory is a slow-motion failure:
contradictions accumulate, and the model receives two conflicting facts with no basis to
choose — **context poisoning**, see [[Context Failure Modes]].

| Practice | Why |
|---|---|
| **Update over append** | Check whether an existing entry covers it; revise that one |
| **Delete what proved wrong** | A memory falsified by later evidence is worse than none |
| **One fact per file** | Granular files can be individually revised or deleted; a monolith cannot |
| **Absolute dates, not relative** | "Last week" written six months ago is now false |
| **Don't store what's derivable** | Code structure, git history, and file layout are already in the repo |
| **Verify before relying** | A memory naming a file or flag reflects what was true when written |

**The last two separate memory that compounds from memory that decays.** Memory should hold
what cannot be re-derived; anything re-derivable should be re-derived, because the source of
truth stays current and the memory does not.

Memory holds what the artifacts *don't* record — decisions, preferences, corrections, and
the reasons behind them.

### Automated Hygiene: Write Paths and Store Compaction

- **Reconcile on write.** Extract candidate facts per segment, vector-match each against
  existing memories, and have the LLM choose **ADD / UPDATE / DELETE / NOOP** ("moved to a
  new city" UPDATEs the old address instead of coexisting with it) — update-over-append,
  automated. See [[Memory Store Operations]].
- **Or buffer the writes.** Profile slots plus an event timeline, extracted in batches
  triggered by size or time, amortise LLM cost and keep reads fast.
- **Compact the store in tiers:** score importance (access frequency, age decay,
  uniqueness) and archive below threshold; cluster similar entries into one summary;
  generalise episodes into semantic or procedural rules. Keep version history for
  conflicts — some fields keep only the latest value (address), others the full history
  (job history).
- **Lifecycle metadata per item** (OS-style management): source and timestamp (resolve
  conflicts, expire), confidence (down-weight inferences), access count (promote/archive),
  scope (stop one user's facts leaking into another's context). See [[Memory Lifecycle]].
- **Sanitise logs locally.** Memory and logs collect PII; a small local model (~0.6B)
  returning typed spans catches natural-language PII ("my password is …") that regex
  misses, at reported >95% recall. Run regex first for throughput; never ship logs to a
  cloud API to be cleaned.

## Short-Term Memory: State and History

Within a session, prior states and agent outputs are a memory tier too. **Multi-shot
refinement** — an agent revising its own earlier output — depends on those prior states
being available.

The tension: prior revisions are exactly the content that fills a window fastest, and
superseded drafts are prime pruning candidates.

**The resolution:** keep the *latest* state verbatim plus a compact record of what changed
and why, rather than the full revision chain. **The rejected drafts rarely matter; the
reason for rejection often does.**

## Conversational Memory

In multi-turn RAG the corpus includes the conversation, so the hard problem shifts from
relevance to **continuity and intent resolution**. Three controls matter more than the
retriever: query construction (concatenate, rewrite standalone, or decompose), when to
retrieve (every turn is wasteful and can displace still-valid evidence), and recency vs
relevance weighting ([[Memory Decay Weighting]]). Recency weighting does not replace
update-over-append — both conflicting facts still occupy the window. Detail:
[[Memory-Augmented Conversational RAG]].

## Memory Architectures

- **MEM1 (constant-size memory):** agents trained to keep one internal state overwritten
  each turn match or beat larger models on long multi-hop QA at near-constant memory. The
  untrained takeaway: a fixed-size rewritten state block beats an ever-growing log
  ([[Structured Context and Schemas]], [[Agent Status Bar]]).
- **Reconstructive memory:** store fragments with source pointers and assemble task-specific
  memory at retrieval time; the risk is confabulated connections.
- **Two-tier memory:** a **resident tier** of a few critical advanced cards always in context,
  plus a **retrieved tier** of raw conversation chunks carrying [[Contextual Retrieval]]
  prefixes (who, when, intent). Either alone fails — resident context can't hold details;
  retrieval alone misses cross-session connections. Together they enable proactive service
  (an upcoming trip next to an expiring passport triggers an unprompted warning).
- **Designed memory vs searching the raw record:** recent evidence suggests that with
  strong models, a verbatim searchable record beats an extracted store, and a weak writer
  caps every reader — see [[Designed Memory vs Raw-Record Search]].

## Evaluating Memory

Grade in three levels: **basic recall** (exact values come back), **multi-session retrieval**
(find *all* relevant records — two cars means asking "which one?"), and **proactive
service** (connect unrelated-looking memories unprompted). Protocol: the agent writes
memory from session 1, revises it after each later session seeing only memory, then
answers a new question scored by a judge against a reference (LoCoMo is the public
benchmark; CAsT, QReCC, TopiOCQA, CORAL and mtRAG cover multi-turn retrieval). In
production also track **memory hit rate** and log which entries fed each answer, so a bad
answer traces to the memory that caused it. See [[Evaluating Context]].

## See Also
- [[Context Engineering]] — related (part of)
- [[Agent Memory Types]] — related
- [[Context Compaction]] — related
- [[Context Failure Modes]] — related (mitigates)
- [[Designed Memory vs Raw-Record Search]] — extends
- [[Memory Store Operations]] — extends
- [[Memory Lifecycle]] — extends
- [[Contextual Retrieval]] — extends (the retrieved tier of two-tier memory)
- [[Memory-Augmented Conversational RAG]] — extends
