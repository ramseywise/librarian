---
title: Coding-Agent Search and Edit Schemes
tags: [llm, agents, comparison]
summary: "The coarse-to-fine search ladder (glob, grep, semantic index, LSP) and five file-editing schemes compared — old→new string as the predictable default, start/end anchors as the economical compromise, and why line ranges fail without a live line map."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--03-tool-design.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--02-harness-anatomy.md
---

# Coding-Agent Search and Edit Schemes

The two tool families every coding agent ships, compared (Li, *AI Agents in Depth*, ch. 5).
A minimal coding kit is seven tools — code interpreter, bash, read, write, edit, glob, grep —
and search and edit are where the design choices concentrate.

## Search, Coarse to Fine

| Method | Good for | Blind spot |
|---|---|---|
| **glob** | Mapping the project by path | Content |
| **grep / ripgrep** | Exact names, error strings, regex structure | Synonyms — "auth" won't find `check_credentials` |
| **Semantic search** (AST-aware chunks, hybrid BM25 + embeddings, reranker) | Exploring an unfamiliar codebase | An index to keep fresh; code sent to an embedding service |
| **LSP definitions / references** | Renames, call chains | Needs a language server |

Two shipped positions: one coding agent deliberately builds **no index** and relies on
agentic grep and glob; another pays for an index to get cross-file semantic recall. **The
choice weighs infrastructure cost and data egress against recall.** See
[[Code Retrieval: Structural Index and Agentic Search]] for the retrieval-side treatment.

## Editing Schemes

| Scheme | Trade-off |
|---|---|
| **Old string → new string** | Predictable — fails loudly if the match isn't unique. Cost: deleting a large block means reproducing all of it |
| **Start + end anchors → new string** | Same reliability; a large deletion only needs its boundaries. The economical compromise |
| **Line ranges** | Cheap, but models miscount and numbers shift after every edit. Viable only with an IDE keeping a live line map |
| **Diff or skeleton + apply model** | High throughput with a trained fast-apply model; a naive merge lands in the wrong place |
| **Vim-like commands** | Efficient for moving code; small models struggle with the syntax |

**Default to old→new string, and return line-numbered reads** so references are precise.
The failure-loudly property is the point: an ambiguous match is an error the agent can see,
rather than an edit in the wrong place it cannot.

That property is undermined by **silent input transformation** — a harness that "helpfully"
normalizes curly quotes before an exact-match edit makes edits to files that genuinely
contain them fail invisibly. See parameter fidelity in [[Tool Design as Harness Surface]].

## See Also
- [[Tool Design as Harness Surface]] — instance-of
- [[ACI (Agent-Computer Interface)]] — instance-of (edit-tool design as interface design)
- [[Harness Anatomy]] — part-of (bash and the minimal coding kit)
