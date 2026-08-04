---
title: Memory as Context
tags: [memory, llm, agents, concept]
summary: Memory is not a sibling pillar of context engineering but the mechanism by which context outlives a window — every memory decision is a decision about what occupies a future context window.
updated: 2026-08-04
sources:
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

## Short-Term Memory: State and History

Within a session, prior states and agent outputs are a memory tier too. **Multi-shot
refinement** — an agent revising its own earlier output — depends on those prior states
being available.

The tension: prior revisions are exactly the content that fills a window fastest, and
superseded drafts are prime pruning candidates.

**The resolution:** keep the *latest* state verbatim plus a compact record of what changed
and why, rather than the full revision chain. **The rejected drafts rarely matter; the
reason for rejection often does.**

## See Also
- [[Context Engineering]] — part-of
- [[Agent Memory Types]] — implements
- [[Context Compaction]] — complements
- [[Context Failure Modes]] — mitigates
