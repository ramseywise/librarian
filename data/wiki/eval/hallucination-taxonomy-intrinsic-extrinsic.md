---
title: Intrinsic vs Extrinsic Hallucination
tags: [eval, concept]
summary: "The NLG hallucination survey by Ji and colleagues defines intrinsic hallucination as output that contradicts the source and extrinsic as output the source can neither support nor contradict, then reviews metrics and mitigations; nearly every number is quoted from earlier work."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-ji-2022-survey-hallucination-natural-language-generation.md
---

# Intrinsic vs Extrinsic Hallucination

Ji and colleagues (ACM Computing Surveys; arXiv v7, July 2024) survey hallucination in natural language generation: definitions, causes, metrics, mitigations and open problems across tasks (summarization, dialogue, generative QA, data-to-text, machine translation, vision-language), with a later section on LLMs updated in January 2024.

## The taxonomy

- **Intrinsic hallucination**: output that conflicts with the source content.
- **Extrinsic hallucination**: output that the source cannot confirm, so the source neither supports nor contradicts it.
- **Faithfulness** means remaining consistent and truthful to the given source, and is the antonym of hallucination. **Factuality** follows an earlier summarization paper in taking world knowledge as the fact.

The survey applies the split per task, and says the definition of hallucination is not standard for generative QA.

## Numbers quoted from earlier work

The survey gives no setup details for these, so treat them as reported secondhand.

- InstructGPT is said to lower the closed-domain hallucination rate from 41 percent to 21 percent.
- Three abstractive summarizers analysed in earlier work had hallucinated content in 25 percent of summaries, which overlap metrics (ROUGE, BLEU, METEOR) miss. In WikiBio, 62 percent of first sentences contain information missing from the infobox. 74 percent of QMSum samples are described as inconsistent facts.
- TruthfulQA (817 questions, 38 categories): scaling up is reported as less promising than fine-tuning for truthfulness. Retrieval augmentation is reported to reduce hallucination in knowledge-grounded dialogue; top-k style diversity decoding correlates with more hallucination.
- RAG faces retrieval noise, conflicts at the augmentation stage and the need to refuse on thin evidence, and poor evidence can lower response quality.

## Practices the survey recommends

Treat n-gram overlap metrics as inadequate for hallucination and pick a metric family by failure mode: information-extraction-based, QA-based, NLI-based, faithfulness classifiers or LM-based. Prefer task-specific faithfulness data over generic NLI data, keep human evaluation, apply NLI at sentence level, not over a whole document, for long sources, and for black-box models sample several completions and measure agreement. Context-aware decoding and DoLa are decoding-only mitigations.

## Limits

- A survey: nearly every number comes from earlier work. Most metrics reviewed predate LLMs; the short LLM section is the only LLM-era coverage.
- The authors concede generative QA has no standard hallucination definition, metric or annotated dataset, and that hallucination in LLMs lacks a theoretical account.
- The text names RAG as a mitigation but gives no measured RAG hallucination rate and no RAG-specific metric.

## See Also
- [[LLM Hallucination Surveys]] — extends (later LLM-era taxonomies)
- [[Summarization and Translation Hallucination Studies]] — related
- [[TruthfulQA]] — related
- [[SelfCheckGPT]] — related (the sampling-agreement approach for black-box models)
- [[Summary Factual Consistency Metrics]] — related
- [[RAG Evaluation]] — prerequisite-for
