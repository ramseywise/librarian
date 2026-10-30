---
title: Context-Aware Compression
tags: [context, context-management, agents, pattern]
summary: "Compressing tool results with the query and the agent's known state in the compressor prompt — in a course experiment it finished in 7 iterations and 40k tokens where per-result and combined summaries took 10–12 iterations and 93k–277k, while keeping identifiers verbatim; compression is understanding, so the compressor needs near-main-model capability."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--05-compression-compaction.md
---

# Context-Aware Compression

A compression strategy for bulky tool results (search pages, file reads) in which the
compressor is told **what the agent is trying to find and what it already knows**, so it
keeps what is new and relevant and drops the rest. One of the techniques under the
Compress lever, alongside [[Context Compaction]].

## Compress for Quality, Not Only Length

The usual failure is not a window that is too small but **information density that is
too low**. Ten searches scattered across 50k tokens make the model hunt for fragments at
every decision; one structured summary ("Known: A, B; still missing: C") turns a
conclusion that had to be reasoned into one that can be looked up. That is the same
mechanism as the [[Agent Status Bar]] — the status bar *adds* distilled conclusions,
compression *replaces* raw records with them.

## Six Strategies Compared

A course experiment tracked a set of public figures' current roles with a 128K-window
model; seven searches returned ~367k characters.

| Strategy | Result |
|---|---|
| No compression | Overflowed at iteration 5; task failed |
| Summarise each result separately (~11%) | 12 iterations, 277k tokens; facts repeated across pages |
| One combined summary (~4%) | 10 iterations, 93k tokens; very long inputs truncated at the tail |
| **Context-aware** — prompt includes the query and the known state (~3%) | **7 iterations, 40k tokens**; one 148k-char page compressed to 2k chars with every relevant fact kept |
| Context-aware + citations (~4%) | 223k tokens; lossy content, lossless index back to sources |
| Adaptive window — batch at 80%, `[COMPRESSED]` marker so nothing is compressed twice | 175k tokens; full fidelity during the early broad-gathering phase |

Context-aware compression cut tokens by more than 75% against the naive baselines.

## Design Principles

- **Information value is uneven:** decision points > evidence > noise.
- **Keep semantics intact.** "X left the organisation in May 2024", not "X left".
- **Same text, different task, different compression.** There is no task-independent
  summary.
- **Compression is understanding** — the compressor needs near-main-model capability; a
  cheap summariser loses what matters.
- **Identifiers survive verbatim.** UUIDs, hashes, IPs, ports, URLs, filenames, PR
  numbers — change one digit and the next tool call fails. Summarisers also tend to drop
  what *looks* re-acquirable: early decisions, the reasons behind constraints, failed
  paths.

## Beyond Summarisation

| Technique | How | Notes |
|---|---|---|
| Extractive | Keep key sentences verbatim | Faithful, cites cleanly; less compression |
| Abstractive | Rewrite shorter | Higher ratio; can introduce errors |
| Hierarchical | Summarise chunks, then the summaries | Scales; detail lost per level |
| Token pruning (LLMLingua-style) | Small model drops low-information tokens | 2–5× with modest loss on many tasks; unreadable to humans |
| Query-conditioned | Compress relative to the current question | Highest relevance per token; redo per query |

Don't confuse this with **contextual retrieval** ([[Contextual Retrieval]]): that runs at
index time and *adds* context to chunks; compression runs at query time and *removes* it.

## See Also
- [[Context Compaction]] — extends (per-item compression vs whole-history compaction)
- [[Agent Status Bar]] — alternative-to
- [[Compression Strips the Epistemic Frame]] — prerequisite-for (what any summariser tends to lose)
- [[Contextual Retrieval]] — alternative-to (index-time addition vs query-time removal)
- [[Context Window Budgeting]] — extends
