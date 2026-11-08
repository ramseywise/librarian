---
title: Generative Search Engine Verifiability Audit
tags: [eval, reference]
summary: A 2023 human audit of four commercial answer engines scoring each sentence's citations for recall and precision; the engines were fluent but often unsupported, and citation precision moved opposite to perceived utility.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-liu-2023-evaluating-verifiability-generative-search-engines.md
---

# Generative Search Engine Verifiability Audit

The audit asks whether the sources a generative search engine cites actually back what it says. Annotators (34 Amazon Mechanical Turk workers) judged Bing Chat, NeevaAI, perplexity.ai and YouChat on 1450 queries each, first response only, February to March 2023. Numbers are the paper's (self-reported).

## Metrics

- **Citation recall:** fraction of sentences worth verifying that their citations fully back. The authors treat every statement about the external world as verification-worthy.
- **Citation precision:** share of citations that support their sentence. A citation counted as partial support only if the sentence's citations jointly support it and no single one does.
- Whether a citation backs its sentence follows AIS (Rashkin et al. 2022). Fluency and perceived utility are 5-point Likert ratings, one annotator per pair; agreement on 250 pairs with three annotators was over 82.0% pairwise.

## Reported results

| System | Recall | Precision | Utility |
|---|---|---|---|
| Bing Chat | 58.7 | 89.5 | 4.34 |
| perplexity.ai | 68.7 | 72.7 | not listed in the extraction |
| NeevaAI | 67.6 | 72.0 | not listed in the extraction |
| YouChat | 11.1 | 63.6 | 4.62 |

Averaged over the four, recall is 51.5% and precision 74.5%; fluency is 4.48 and utility 4.50. Across the four systems, precision and utility correlate at r = -0.96 (four points, weak evidence). The authors hypothesise that systems copy or closely paraphrase cited pages, which is supported but may not answer the query (BLEU against cited evidence 31.3 on average, r = 0.80 with precision); they did not test it by intervention. Recall is higher for queries whose retrieved pages answer directly (NaturalQuestions queries that have a long answer score 58.5, the others 47.8); precision is lowest on open-ended queries (AllSouls 67.8, davinci-debate 70.3).

## Limits

- Verifiability is not factuality: a supported sentence may be false. Scoring is per sentence, each pair annotated once, four closed systems whose retrieval and prompts are not visible, and the systems have since changed.
- Abstention differs: NeevaAI declined 22.7% of queries, the others under 0.5%, which complicates comparison. ChatGPT and Bard were excluded for lacking inline citations.
- The two explanations (copying, retrieval relevance) are hypotheses.

## See Also
- [[FActScore]] — related
- [[Long-Form QA Evaluation Hurdles]] — related
- [[Deep Research Agent Systems]] — related
