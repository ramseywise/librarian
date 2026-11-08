---
title: DeepDive Knowledge-Graph Search Agent Training
tags: [harness, pattern]
summary: Synthesise hard multi-hop search questions from knowledge-graph random walks with blurred attributes, then train a search agent with multi-turn RL whose reward subtracts a keyword-overlap penalty for redundant queries.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lu-2025-deepdive.md
---

# DeepDive Knowledge-Graph Search Agent Training

**Data.** A random walk over a knowledge graph (KILT and AMiner) picks a path of 5 to 9 nodes; an LLM chooses each next node. Attributes along the path are blurred (dates become ranges), Gemini-2.5-Pro hides the entity names and then writes the question, and the answer is an attribute of the final node. A difficulty filter keeps questions a baseline model cannot answer directly. **Reward.** Binary: a trajectory earns 1 when all of its steps are well formed and an LLM judge accepts the final answer. A redundancy penalty subtracts 0.1 times the mean pairwise Jaccard similarity of keyword sets across the trajectory's search queries. Training is GRPO on QwQ-32B (SFT first), with actions search, click and open. Numbers are the paper's (self-reported). Judge: Llama-3.1-70B; every dataset evaluated twice and averaged.

## Reported results

- DeepDive-32B reaches 15.3% on full BrowseComp (1,266 instances, turn limit 128), where the paper says most open-source models score under 10%; OpenAI DeepResearch is listed at 51.5%. A closed-model row (Claude-4-Sonnet-Thinking with browsing) is 14.7.
- **Data ablation (BrowseComp-266 subset, QwQ-32B).** Base 1.9; SFT with HotpotQA 4.9; SFT with KG data 7.5; adding RL 9.2 (HotpotQA) against 12.0 (KG data).
- **Redundancy penalty** (same subset): about 14% fewer tool calls and about 20% higher accuracy late in training, which the extraction notes is relative on an 8% to 13% scale.
- **Test-time scaling** (8 samples, BrowseComp-266): 12.0 single, 18.8 majority vote, 24.8 choosing the sample with fewest tool calls, 37.6 pass@8.
- A semi-automated variant with human annotators plus o3 (2,997 English and 275 Chinese pairs) reached 22.2% (Table 3). Contamination check: over 97% of BrowseComp samples clean.

## Limits

- The authors say synthetic data is much easier than BrowseComp and that the RL model over-searches; the 9B variant gains little from RL.
- Ablations use a 266-question subset with no seeds or error bars; baselines mix self-run and copied results.
- The extraction notes internal inconsistencies: 3,090 against 3,250 QA pairs; 22.2% (Table 3) against 20.8% (text); Xbench 51.8 (Table 1) against 50.0 (Tables 2 and 3).

## See Also
- [[Deep Research Agent Systems]] — prerequisite-for
- [[Knowledge Graph Retrieval]] — related
- [[RL for Retrieval Policies]] — related
