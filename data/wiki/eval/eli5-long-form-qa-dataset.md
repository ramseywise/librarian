---
title: ELI5 Long-Form QA Dataset
tags: [eval, concept]
summary: "ELI5 pairs 272K Reddit questions with paragraph-length answers and TF-IDF-built web support documents, showing that a multi-task Seq2Seq model still hallucinates and ROUGE cannot rank abstractive against extractive systems."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-fan-2019-eli5.md
---

# ELI5 Long-Form QA Dataset

ELI5 asks for explanations of open-ended questions in a paragraph or more. It is built from a Reddit subreddit: 100 Common Crawl pages per question are retrieved with Lucene and compressed by TF-IDF selection into one support document. The full dataset has about 272K questions, an average answer of 130.6 words and an average support document of 857.6 words. Baselines are extractive (TF-IDF, BidAF), a language model, and Seq2Seq (Transformer big), including a multi-task variant trained on language modelling, masked word prediction and answer generation. Evaluation uses ROUGE, two intermediary metrics (**FILL-1**, accuracy at generating varied nouns, verbs and adjectives given correct preceding tokens; **ROUGE-20%**, completing the last 20% of an answer given the first 80%, the question and the support document) and crowd studies.

## Results

All self-reported.

- In 1000 pairwise crowd comparisons (3 raters each, five systems), the gold answer beats every trained model at least 85.5% of the time. The plain language model is rated below every other setting in 91% or more of pairs.
- On full answers the multi-task Seq2Seq model scores ROUGE-1 28.9, topping the trained models. On ROUGE-20% it reaches ROUGE-1 37.2, against 32.7 for question + document to answer and 33.6 for question to answer. Its perplexity of 32.7 matches the language model, while question + document to answer has 55.1. BidAF is the best extractive baseline at ROUGE-1 23.5.
- An oracle that can use the whole web sources gets ROUGE-1 54.8, against 27.4 from the support document alone, so the support document restricts access to relevant content. With 500 passages extracted (1000 examples), under 9% of oracle sentences come from the 20 top-ranked by TF-IDF.
- Raters choose the multi-task model over the extractive one only 57% of the time. In 100 evaluations by the authors with the support document in view, 19% of multi-task answers were fully accurate against 40% of extractive ones, although relevance favoured multi-task (84% against 68%).
- Of 500 sampled training pairs, 65% of support documents contain the answer and 92% hold relevant information, and gold answers fully address the question in 94.5% of cases.
- Perplexity and FILL-1 indicate appropriateness poorly, so the authors suggest reporting complete ROUGE and ROUGE-20% instead.

## Limits

- The support document comes from a simple TF-IDF heuristic; the extraction notes that the oracle shows large loss.
- The authors say ROUGE cannot rank abstractive against extractive systems.
- Crowd accuracy ratings were made without the support document.
- Training hyperparameters not stated; appendices A, E and F are not in the PDF.
- The passage count is inconsistent across sections (15 in 3.1, versus a mention of 20 in 6.2).
- The extraction notes the models are from the pre-LLM era, so the baselines are dated.

## See Also
- [[Long-Form QA Evaluation Hurdles]] — related
- [[RAG Evaluation]] — prerequisite-for
- [[DrQA Machine Reading at Scale]] — related (factoid counterpart with Wikipedia as evidence)
