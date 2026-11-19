---
title: HaluEval
tags: [eval, factuality-and-hallucination, reference]
summary: "HaluEval is 35,000 hallucinated-or-normal samples (5,000 human-annotated ChatGPT replies plus 30,000 ChatGPT-generated QA, dialogue and summarization samples) that tests whether an LLM can recognise hallucination; ChatGPT scores 62.59% on QA recognition (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-li-2023-halueval.md
---

# HaluEval

Li, Cheng, Zhao et al. (EMNLP 2023) ask what kinds of content LLMs hallucinate, how much, and whether LLMs can recognise hallucination in text. Following SelfCheckGPT they hypothesise that hallucination shows up in diverging responses, and that LLMs recognise poorly any hallucinated text lying near the truth. They define hallucination as content contradicting the source, or content that factual knowledge cannot confirm.

## Construction

- **General user queries (5,000):** Alpaca queries are given three ChatGPT replies each, and the 5,000 queries whose replies have the lowest BERTScore similarity are labelled for hallucination by three humans with max voting. 977 replies were labelled hallucinated, about 19.5%. Fleiss's kappa between labelers is 0.811.
- **Task-specific (30,000):** QA from HotpotQA, knowledge-grounded dialogue from OpenDialKG, summarization from CNN/Daily Mail. A two-stage **sampling-then-filtering** framework has ChatGPT write hallucinated answers in two styles (one-pass and conversational instructions), then pick the more plausible and harder of the two candidates.
- **Evaluation:** an LLM is shown a sample and asked yes or no whether it contains hallucination.

## Results (self-reported)

Setup: HaluEval recognition, temperature 0, a few-shot judge prompt for ChatGPT.

- ChatGPT recognises hallucination with 62.59% accuracy on QA and 58.53% on summarization (barely above chance). Claude 2 scores highest on QA among the models evaluated; GPT-3 davinci is around chance and Alpaca 7B far below it (6.68 on QA).
- On the general split ChatGPT scores 79.44% by Table 5 and 86.22% by Table 8.
- Three improvement strategies were tried on ChatGPT:
  - Retrieved Wikipedia knowledge raises QA recognition accuracy, 62.59 before and 76.83 after, while dialogue gains little, moving only from 72.40 to 73.80.
  - Chain-of-thought lowers QA to 59.58 but raises summarization from 58.53 to 61.21.
  - Sample contrast, showing the right and hallucinated samples together, is the worst at 49.19 on QA.
- ChatGPT fails to recognise 3,109 QA, 891 dialogue and 3,868 summarization samples; over half of the failures are in pattern I (1,559 for QA).

## Limits

- The hallucinated samples and the filter are both ChatGPT, so quality is capped by how well it follows the sampling instruction; the 30,000 generated samples have no reported human validation.
- It measures recognition, not generation rates or causes (the authors concede this). Each sample shows a randomly chosen hallucinated or right output.
- The authors warn that samples close to the truth may be misused and should be monitored.
- No repeated runs, seeds or significance tests; the 7B open models' very low scores are not diagnosed; retrieval details (retriever, passages) are not given.
- Tables 5 and 8 print different general-split accuracies for ChatGPT (79.44 against 86.22).
- 2023 API models and 7B open models are dated.

## See Also
- [[SelfCheckGPT]] — prerequisite-for (the divergent-responses idea used to pick which queries to annotate)
- [[LLM Hallucination Surveys]] — related (describes HaluEval and its 2.0 successor)
- [[Intrinsic vs Extrinsic Hallucination]] — related
- [[HotpotQA]] — prerequisite-for (the QA seed data)
- [[TruthfulQA]] — related (another benchmark of falsehood, scored by multiple choice)
- [[JEV-as-a-Judge Cascade]] — related (reports HaluEval label noise)
