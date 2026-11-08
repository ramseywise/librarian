---
title: FActScore
tags: [eval, reference]
summary: "A long-form factual-precision metric: split a generation into atomic facts and report the share a knowledge source supports; on 183 people biographies it showed ChatGPT falling from 80% to 16% as entities got rarer, and an automatic estimator came within 2% error of the human score (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-min-2023-factscore.md
---

# FActScore

Min et al. (EMNLP 2023) ask how to measure the factual precision of a long generation at a finer grain than a single true or false verdict. Their answer is the **atomic fact**, a short sentence carrying one piece of information. A generation is split into atomic facts (InstructGPT prompted few-shot, with human revision), and each is checked against English Wikipedia and labelled Supported, Not-supported or Irrelevant. The score is the fraction of facts supported, averaged over the prompts where the model actually responds.

## The automatic estimator

Human labelling used freelancers paid 15 to 25 USD per hour; the automatic estimator is the alternative to it. It retrieves passages with the GTR retriever (k=5) and asks a language model whether each fact is true or false given them. An optional second signal is a nonparametric masked-language-model probability (threshold 0.3), and the two are ensembled.

- The authors report an error rate under 2% against the human score for the best variant per subject (self-reported). Which variant is best depends on the subject.
- With Inst-LLAMA 7B as the evaluator and InstructGPT as the subject, retrieval plus the language model overestimated the score with an error rate of 14.1, against 1.4 once the nonparametric signal was added (self-reported).
- A ChatGPT evaluator with no retrieval had a large error rate on InstructGPT, a result the extraction reads as showing that retrieval matters.
- On the retrieval-plus-language-model evaluator, True/False prompting beat QA prompting, and the choice of retriever hardly mattered (BM25 scored 78.9 F1 micro against GTR Large, Inst-LLAMA 7B, InstructGPT subject; self-reported).
- Across 13 subjects with 500 biographies each, the two best estimators' scores are correlated. Automatic evaluation of those 6,500 generations avoided a human cost the authors put at $4 per generation.

## What it found about models

- Human evaluation covered 183 people entities with the prompt "Tell me a bio of <entity>" for InstructGPT, ChatGPT and PerplexityAI (the extraction gives no scores for the three).
- ChatGPT's score fell from 80% to 16% as entity frequency went from very frequent to very rare (human labels, self-reported). PerplexityAI, which retrieves, still dropped for rarer entities.
- PerplexityAI's citations barely correlated with whether a sentence was supported.
- Estimated on 500 biographies per subject, GPT-4 averaged 61 atomic facts per response to ChatGPT's 37, abstained less (12% against 16%) and scored comparably. Among 7B public models the estimated scores were about 40% for Alpaca and Vicuna, 30% for MPT-Chat and 17% for StableLM (self-reported).
- A proof of concept on NLP-paper summaries (10 prompts) gave a human score of 66.20 against 73.61 from the estimator.

## Limits

Precision only: the score has no recall term, so abstaining or writing fewer facts raises it, and the authors recommend reporting the abstention rate and facts per response beside it. Only people biographies and English Wikipedia are covered, and the paper's second domain is 10 prompts. It assumes facts that are undebatable, equally weighted and non-conflicting; 70% of annotator disagreements came from inherent debatability. Wikipedia gaps penalise true facts (3 of 30 checked). The estimator is imperfect on individual judgements. Human results cover 183 entities per model, and the systems are from before 2023 plus commercial ones.

## See Also
- [[SAFE Long-Form Factuality Scoring]] — alternative-to (also scores atomic facts, against web search instead of Wikipedia)
- [[SelfCheckGPT]] — alternative-to (a self-sampling check that FActScore's paper lists as a baseline)
- [[Chain-of-Verification]] — related (its biography results are reported in this metric)
- [[Tool-Augmented Factuality Checking]] — alternative-to (verifies claims with search or code tools)
- [[FACTS Leaderboard]] — alternative-to (a four-part factuality suite averaged into one score)
- [[Summary Factual Consistency Metrics]] — alternative-to (checks a summary against its own source document, not a knowledge base)
