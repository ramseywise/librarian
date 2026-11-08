---
title: FINDER and DEFT (Deep Research Agent Failures)
tags: [eval, reference]
summary: "A 100-task checklist benchmark (FINDER) and a 14-category failure taxonomy (DEFT) built by coding about 1,000 reports from 12 deep research agents; generation failures, led by fabricated content, were the largest class, ahead of retrieval and reasoning (self-reported, LLM-assisted labelling)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhang-2025-how-far-we-genuinely-useful.md
---

# FINDER and DEFT (Deep Research Agent Failures)

The OPPO AI Agent Team (arXiv 2512.01948, 2025) argues that deep research agents (DRAs) are weaker at collecting, combining and checking evidence, and at revising plans, than at grasping what was asked. The paper contributes two artefacts: FINDER, a benchmark, and DEFT, a failure taxonomy.

## FINDER

FINDER reuses 100 PhD-style tasks from DeepResearch Bench, 50 in Chinese and 50 in English, rewritten by seven experts and given 419 checklist items that Gemini 2.5 Flash then refined. Reports are scored on a checklist pass rate and with two inherited measures: RACE (report quality, judged relative to a reference report) and FACT (citation accuracy).

## DEFT

DEFT comes from coding agent reports in the grounded-theory style: an LLM coder proposes codes, a codebook is refined, experts review, and the codes roll up into three levels. The result is 14 categories under reasoning, retrieval and generation, ordered by pipeline stage. A held-out pair of agents (WebThinker and OpenManus) was used as a saturation check, and the other nine agents built the taxonomy. A bounded cosine remap turns category error counts into positive scores.

## Results (self-reported)

Setup for the failure shares: about 1,000 reports from 12 DRAs on FINDER; labelled by LLM coders with a human check, and the extraction notes that who labelled the full set is not stated.

- Generation failures were 38.76% of coded failures, retrieval 33.10% and reasoning 28.14%. The largest single category was Strategic Content Fabrication at 18.95%.
- Within retrieval, Insufficient External Information Acquisition was 16.30% and Verification Mechanism Failure 8.72%.
- Within reasoning, Failure to Understand Requirements was 10.55%, Lack of Analytical Depth 11.09% and Rigid Planning Strategy 5.60%.
- Category counts correlate (14 categories, no sample size or significance given): Lack of Analytical Depth with Insufficient External Information Acquisition 0.73, and the latter with Strategic Content Fabrication 0.53. The authors read this as poor retrieval feeding confident fabrication.
- Agreement: Krippendorff alpha by core category ran 0.7410 to 0.9152, and checklist pass-rate alpha was 0.8025 (OpenManus) and 0.8708 (WebThinker), four experts against Gemini 2.5 Flash on the two held-out agents.
- Top-line scores depend on the lens. RACE overall (Gemini 2.5 Pro as judge, Gemini 2.5 Pro Deep Research as reference): Gemini 2.5 Pro Deep Research 50.95, Kimi K2 48.28, O3 Deep Research 46.25. FACT citation accuracy: O3 at 65.98, Gemini at 57.09 and Perplexity at 5.25. Checklist pass rate: MiroFlow (English) 72.19, Tongyi 67.54.

An appendix case shows a verification failure: an agent listed references with inaccessible or non-existent URLs and then claimed all references had been cross-verified; no rate is given.

## Limits

- LLMs helped assign the failure labels, and the agreement check spans only two agents and 14 items.
- The extraction flags that the RACE judge and the reference report are both Gemini 2.5 Pro, a self-preference risk, with Gemini on top of the table. RACE is relative to a reference, so the authors say absolute scores across benchmarks carry little meaning.
- Missing FACT cells arise from anti-scraping protections and fabricated URLs, so they reflect eval gaps, not only agent faults.
- The extraction notes the systems are unlike in scale and tooling: some are bare API models, others frameworks over different base models.
- The authors' reasoning-resilience insight is asserted without a test. Models date from autumn 2025.
- Internal inconsistencies, as the extraction lists them: the introduction says generation is over 39% and retrieval over 32%, against 38.76% and 33.10% in the body; the Gemini row of the main table has stage scores near 90 but an average of 72.89; the same MiroFlow RACE score is 42.20 in the main table and 45.54 in the stability table; the category numbering in the text differs from the category table; one appendix ends mid-sentence with its table missing.

## See Also
- [[Eval Failure Taxonomy]] — related (a stage-ordered failure taxonomy)
- [[Error Analysis (Open and Axial Coding)]] — related (coding agent outputs into failure categories)
- [[MedBrowseComp]] — related
- [[LLM-as-Judge Evaluation]] — related (a same-vendor judge and reference)
- [[GAIA General-Assistant Benchmark]] — related
