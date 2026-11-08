---
title: MedBrowseComp
tags: [eval, reference]
summary: "A benchmark of 1,000+ multi-hop medical fact-seeking questions built from HemOnc.org and linked sources; accuracy falls as hop count rises, search helps most at low hop counts, and computer-use agents trail API-driven deep research (self-reported, one run per system)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2025-medbrowsecomp.md
---

# MedBrowseComp

MedBrowseComp (Chen et al., arXiv 2505.14963, 2025) follows BrowseComp's design for oncology and
haematology. Questions are chained from HemOnc.org through PubMed and ClinicalTrials.gov to the FDA Orange Book
and Yahoo Finance, with one to five hops. Two sets exist: MedBrowseComp-50 (10 questions per hop
depth, graded by GPT-4.1 mini plus a human check) and MedBrowseComp-605 (121 per hop, LLM-judged only).

## Results (self-reported, one run per system)

- **MedBrowseComp-50:** O3 deep research 51.0%, Gemini 2.5 Pro deep search 49.0%, Perplexity deep
  research 40.0%, Claude 3.7 Sonnet computer use 36.0%; O3 with plain search 38.0%, Gemini 2.5 Pro search 28.0%, Sonar Pro 20.0%.
  At five hops, O3 deep research scored 1 of 10 and Gemini deep search, Perplexity deep research and Sonar Pro 0.
- **MedBrowseComp-605:** Gemini 2.5 Pro search 30.1% against 13.2% without search; GPT-4.1 with search
  13.2% against 17.3% without, so search was worse.
- **Strict accuracy** drops questions with a "not applicable" correct answer (n=453 remain): Gemini 2.5 Pro search 24.5%, GPT-4.1 search
  5.5%, and nearly every four- and five-hop cell near zero. Raw four-hop scores look inflated by such answers (an observation in the extraction, not a claim by the authors).
- **Computer use** (Claude 3.7 Sonnet, four one- and two-hop task types, 121 questions each): 11.57% to 36.36%
  depending on the field asked for. Each GUI action produces about two screenshots, which the authors say inflates context to around 200,000
  tokens against about 2,000 for a text-only equivalent.
- The experiments cost $3,690 in total, roughly $2,500 of it for computer use. Annotators agreed with GPT-4.1 mini on 98% of answers on the 50-question set.

The authors list trajectory errors: for deep research, inefficient tool use, poor source choice and failing to parse long tables; for computer use,
greedy attribute extraction, overlooking information and aimless wandering.

## Limits

One run per system, so no variance; one question moves a MedBrowseComp-50 score by 2 points. Subscription products were queried manually
over 28 April to 6 May 2025 and differ in tools, not just model. Computer use covers only
four shallow task types. No clinicians reviewed answers, coverage is oncology and haematology, and some
conclusion statements do not obviously match the tables. The systems date from May 2025.

## See Also
- [[Gaia2]] — related (another agent benchmark with search tasks)
- [[Trajectory Over Outcome]] — related (the authors catalogue trajectory errors)
- [[Eval Contamination Defenses]] — related
- [[Web Agent Benchmarks (WebShop and Mind2Web)]] — related
- [[GAIA General-Assistant Benchmark]] — related
- [[MEDEC]] — related (medical error detection benchmark)
- [[FINDER and DEFT (Deep Research Agent Failures)]] — related (deep research agent failure taxonomy)
