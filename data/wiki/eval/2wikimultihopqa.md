---
title: 2WikiMultiHopQA
tags: [eval, reference]
summary: "A 192,606-question multi-hop QA set generated from Wikipedia text and Wikidata triples, with the triples as evidence paths; the paper reports a single-hop model scoring 8.7 F1 lower than on HotpotQA and baselines far below humans (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-ho-2020-constructing-multi-hop-qa-dataset.md
---

# 2WikiMultiHopQA

Ho and colleagues (2020) ask how to build a large multi-hop QA dataset that guarantees multi-hop reasoning and also gives a structured explanation of the path from question to answer. Their hypothesis: joining Wikipedia text to Wikidata triples and logical rules produces natural questions that genuinely demand multi-hop reasoning, and that are more difficult than HotpotQA's. Later retrieval papers, such as [[FLARE Forward-Looking Active Retrieval]] and [[Adaptive-RAG Query Complexity Routing]], use it as an evaluation set.

## Construction

Hand-written templates applied to the overlap between Wikipedia summaries and Wikidata triples produce questions of four types:

- **comparison** questions;
- **compositional** and **inference** questions, the two subtypes of a **bridge question** (one that goes through a bridge entity connecting two paragraphs);
- **bridge-comparison** questions, which combine a bridge hop with a comparison.

Checks force two-hop reasoning, distractor paragraphs come from bigram tf-idf retrieval, and a single-hop model is used to split the data. Each sample carries **evidence**: the (subject, property, object) Wikidata triples along the reasoning path. Logical rules (28 of them, mined with AMIE and manually verified) generate the inference questions. The set has 192,606 questions, against 112,779 for HotpotQA and 4,588 for R4C.

## Results

Self-reported by the paper.

- Single-hop BERT (answer F1, HotpotQA distractor setting against 2WikiMultiHopQA, following Min et al. 2019) scores 8.7 F1 lower here, which the authors take to mean many examples need multi-hop reasoning.
- A HotpotQA baseline model (distractor setting, joint answer and supporting-fact score without the evidence task) gets joint F1 26.76 here against 40.52 on HotpotQA, and answer F1 40.95 against 58.54.
- With an added evidence-generation head, the test split gives answer F1 43.93, supporting-fact F1 65.26, evidence F1 14.94 and joint F1 5.41. On 100 random test samples evidence F1 is 16.7 for the model against 78.8 for humans; the human upper bound on answers is 91.8 F1 (three annotators, max per sample), against 98.8 on HotpotQA (borrowed figure).
- By question type, inference has the lowest joint F1 (1.40); bridge-comparison has the highest supporting-fact F1 (89.16) and the lowest answer F1 (20.45).
- The single-hop model used for the split has five-fold F1 86.7; the questions it solves form the train-medium split (154,878).
- Answer types: yes/no 31.2 percent, date 16.9 percent, film 13.5 percent, human 11.7 percent; 708 unique types. A manual check found 8 of 100 training samples with a Wikipedia and Wikidata mismatch.

## Limits

- Hand-written templates and 28 rules limit language variety. Only 7,478 inference questions survive because only single-valued Wikidata relations were kept.
- The 8-in-100 mismatch rate partly explains the 91.8 F1 human ceiling. Evidence F1 depends on one gold name per entity while humans may use aliases, which the authors conjecture lowers the score.
- Sentence-level supporting-fact prediction is binary and cannot test reasoning (the authors' point), so that F1 stays high regardless.
- No baseline hyperparameters, seeds or compute are reported; one baseline family and a 100-sample human study. The baselines are a 2018 HotpotQA model and BERT, with no later retrievers or LLMs.

## See Also
- [[Compositionality Gap]] — related (another multi-hop test of composing facts)
- [[Self-Ask Prompting]] — related (question decomposition for multi-hop questions)
- [[RAG Evaluation]] — prerequisite-for
- [[FRAMES Benchmark]] — related (a later multi-hop retrieval benchmark)
- [[HotpotQA]] — prerequisite-for (the earlier multi-hop set it is compared with)
