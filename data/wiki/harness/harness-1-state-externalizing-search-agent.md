---
title: Harness-1 State-Externalizing Search Agent
tags: [harness, pattern]
summary: A 20B search agent trained with RL inside a harness that holds the candidate pool, curated set, evidence graph and verification records outside the model; ablating harness parts at inference cuts recall without retraining.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-jiang-2026-harness-1.md
---

# Harness-1 State-Externalizing Search Agent

The harness splits policy from environment. Prompt-tier working memory shows the candidate pool, a curated set (cap 30, lowest-importance eviction, importance tags), an evidence graph from regex entity extraction, verification records, search history and a budget marker; full text sits in an outer tier reached by review and read actions. Observations are compressed by sentence-level BM25 (4 sentences kept) and deduplicated by MinHash. Context budget is 30,720 of 32,768 prompt tokens. The same state interface serves teacher, SFT, RL and evaluation. Reward combines set quality, trajectory recall, answer terms, a tool-diversity term and a turn penalty. Numbers are the paper's (self-reported). Base model gpt-oss-20b; 8 retrieval benchmarks; averages of 3 runs; at most 30 documents returned; shared Qwen3-Reranker-8B.

## Reported results

- **Average curated recall 0.730**, 11.4 points above Tongyi DeepResearch 30B; competitive with frontier models that were run inside the Context-1 harness, which caps episodes at 64 turns.
- **Held-out benchmarks gain more.** Against Context-1: +17.0 points on four never-trained sets against +7.9 on four source-family sets. RL used SEC queries only (3,453); SFT used 899 filtered trajectories.
- **Remove the harness, keep the policy** (100 BrowseComp+ queries, one mechanism off per row, no error bars): recall 0.584 to 0.513 with everything disabled; single removals cost 3.9% to 7.9% of final-answer recall, except content dedup, where removal helped by 1.6%. Without a mechanism the policy reverts to search-heavy behaviour with less reading and verifying.
- **No tool-diversity reward:** diversity falls from about 6 to 3.5 and recall plateaus near 0.53, against about 0.60 with it (one run each, read from a figure).
- **A fixed GPT-5.4 gains from the harness without RL:** curated recall 0.511 with naive search-add, 0.807 in the Context-1 harness, 0.849 in the Harness-1 harness.
- The authors describe what still separates it from Opus-4.6 as a selection problem, not a discovery one.

## Limits

- Scope is evidence-seeking retrieval in a 40-turn, 32K-context episode; report writing, abstention and an adversarial web are excluded; the evidence graph is built with regular expressions, and verification uses an LLM as proxy.
- Harness nudges are hard-coded prompting, so some of the gain is not policy capability. Frontier baselines run in Context-1's harness, not their own. One RL run per configuration; no confidence intervals.
- The extraction notes internal inconsistencies: BrowseComp-Plus final-answer recall is 0.658 in the text and 0.667 in Table 2; the 11.4-point headline gain is measured against Tongyi DeepResearch while the held-out gains are measured against Context-1, and the extraction notes flag the "closest open baseline" wording as unreconciled.

## See Also
- [[Deep Research Agent Systems]] — prerequisite-for
- [[Long-Horizon Execution]] — related
- [[Tool Design as Harness Surface]] — related
