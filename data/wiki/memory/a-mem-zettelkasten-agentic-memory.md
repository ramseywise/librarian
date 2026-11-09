---
title: "A-Mem Zettelkasten Agentic Memory"
tags: [memory, pattern]
summary: "A-Mem stores each interaction as a linked note whose keywords, tags and context an LLM writes, then lets new notes trigger link creation and rewriting of neighbouring notes; ablations on LoCoMo credit link generation and evolution, but with GPT-4o it loses to full context on single-hop and adversarial questions (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-xu-2025-mem.md
---

# A-Mem Zettelkasten Agentic Memory

A-Mem (a 2025 preprint, venue shown as a NeurIPS-checklist version) borrows the Zettelkasten method of atomic, interconnected notes. Each interaction becomes a note holding its content, timestamp, LLM-written keywords, tags and context, an embedding and links. When a note is inserted, its nearest neighbours by embedding similarity are pulled in; an LLM then chooses which links to form and may also revise those neighbours' context, keywords and tags (the paper calls this memory evolution). At query time the nearest notes by embedding similarity are returned. There is no training; everything is prompting.

## Results

Setup: LoCoMo unless noted, F1, a single run per cell. All figures are self-reported.

- Ablation with GPT-4o-mini: removing both link generation and evolution takes multi-hop F1 down to 9.65 from 27.02; link generation alone (without evolution) keeps 21.35.
- Tokens: about 1,200 per memory operation against about 16,900 for the full-context LoCoMo baseline and MemGPT, a stated 85-93% reduction.
- With GPT-4o, temporal F1 is 39.41 against 9.09 for full context, but A-Mem loses on single-hop (48.43 against 61.56) and adversarial (36.35 against 52.61) questions.
- With GPT-4o-mini multi-hop F1 is 27.02 against 25.02 for full context and 26.65 for MemGPT, a small margin; with small open models (Qwen2.5-1.5b) it beats the baselines in most cells.
- On DialSim, F1 is 3.45, which the paper states as 35% above full context; absolute scores are very low.
- Retrieving more notes helps up to a point: multi-hop F1 is 19.91 with 10 notes, 27.02 with 40 and 26.81 with 50.
- Retrieval-time microbenchmark: 0.31 microseconds at 1,000 memories to 3.70 at 1,000,000; it times vector search only, not the LLM calls for linking and evolution.

## Limits

- Organisation quality depends on the underlying LLM; text only; only LoCoMo and DialSim, both conversational QA; the ablation uses GPT-4o-mini alone; no error bars.
- The extraction notes that the text asserts a doubling of multi-hop performance for GPT models though the table margins are small, and that the headline GPT results use a retrieval count tuned per category (up to 50) although the text states 10.

## See Also
- [[Memory Store Operations]] — prerequisite-for
- [[Memory Forms Taxonomy]] — prerequisite-for
- [[MemGPT / Letta Virtual Context Memory]] — alternative-to
- [[Mem0 Extract-and-Update Memory]] — alternative-to
