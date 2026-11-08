---
title: ACC Bounded Memory Control for Agents
aliases:
  - Agent Cognitive Compressor
tags: [memory, pattern]
summary: "ACC rewrites one bounded, schema-governed state (the Compressed Cognitive State) every turn instead of replaying the transcript or retrieving artifacts; the paper reports qualitatively flat memory size and lower hallucination and drift over 50-turn episodes but gives no numeric effect sizes in its text."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-bousetouane-2026-ai-agents-need-memory-control.md
---

# ACC Bounded Memory Control for Agents

ACC (a 2026 preprint with no venue; the source uses the acronym without expanding it) controls within-session state. Each turn it recalls candidate artifacts, qualifies them, commits a new Compressed Cognitive State (CCS) that replaces the old one, acts, and then stores the turn in an artifact store. The CCS is made of nine typed fields: an episodic trace, a semantic gist, focal entities, a relational map, the goal, constraints, a predictive cue, uncertainty and artifact references. Retrieved artifacts count as external evidence and cannot change the state unless the compressor commits them under the schema, which the paper presents as a defence against memory poisoning (a design claim, untested).

## Setup

Three agents: full-transcript replay, a retrieval agent with its own store (top 5 artifacts per turn in the text, top 3 in a figure caption), and ACC. 50-turn live episodes in IT operations, cybersecurity and healthcare; 600 evaluations for 30,000 turns. Hallucination is H = U / max(1, S+U) from auditing claims against a canonical memory that the judge maintains; drift is D = (V+O) / max(1, |K|). Judges score 0 to 10, blinded and order-randomised. The model, judge and compressor models are not named.

## Results (qualitative; the text has no numbers)

- Replay grows near-linearly in memory tokens; retrieval and ACC stay bounded (self-reported).
- For replay and retrieval, hallucination grows as turns accumulate and jumps after stress turns, while ACC remains close to zero (self-reported).
- ACC has the strongest relevance and coherence and is competitive on answer quality and instruction following (self-reported).

## Limits

- The extraction notes the text contains no numeric results; results exist only as figures it did not read. Evaluation is judge-based only, with no seeds, intervals or significance tests, and the authors state no limitations section.
- Tokens are not matched (replay is unbounded by design), there is no no-memory baseline, no sliding-window or plain-summary baseline, and no ablation of the qualification gate or schema. The extra compressor call's cost is not measured.
- The paper is about working state in one session, not learning across sessions.
- Internal inconsistencies: top-5 in the text against top-3 in the caption and conclusion; finance appears as a domain in places while three domains are listed elsewhere. Many references are unverifiable and some are duplicated.

## See Also
- [[Context Compaction]] — alternative-to (compression of history in a session)
- [[Memory as Context]] — prerequisite-for
- [[Memory Lifecycle]] — prerequisite-for
- [[Compression Strips the Epistemic Frame]] — related
