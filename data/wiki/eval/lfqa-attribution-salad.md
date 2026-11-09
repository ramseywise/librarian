---
title: LFQA Attribution and SALAD
tags: [eval, reference]
summary: "SALAD is a sentence-level human attribution dataset for long-form QA answers; with evidence documents in context, many sentences are supported and the last sentence is the likeliest to be unsupported, and a T5 NLI judge is the best automatic detector (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-chen-2023-understanding-retrieval-augmentation-long-form.md
---

# LFQA Attribution and SALAD

Chen and colleagues (COLM 2024) ask how in-context evidence documents change long-form answers and how attributable those answers are to the documents. **Attribution** here means the share of an answer that the evidence documents entail, following an attribution framework from earlier work. The paper runs two controlled studies (fix the model and vary the documents; fix the documents and vary the model) and releases SALAD, 12k human judgements over 4k answer sentences.

## Setup

Three to four evidence snippets (human, WebGPT, Bing or random) are prepended to an ELI5 question. Answers come from three generators: GPT-3.5 (the text-davinci-003 model), Alpaca-7b and WebGPT-175B, with three samples per setting, on the 271-question ELI5 test set released with WebGPT; 100 questions are annotated. Each answer sentence is labelled by MTurk workers as Supported, Partially Supported or Not Supported (Krippendorff's alpha 0.71). NLI models and QAFactEval are then tested as automatic attribution judges.

## Results

Self-reported, on the setup above.

- Given the same WebGPT documents, 32 percent of Alpaca's sentences are unsupported, against 3 percent for WebGPT, which is fine-tuned with retrieval; GPT-3.5 has 85 percent supported and 11 percent unsupported. With no documents in context, just 22 percent of GPT-3.5 sentences and 23 percent of Alpaca sentences are backed by the WebGPT documents. Overall, 59 percent of annotated sentences are supported, 6 percent partial, 35 percent unsupported.
- An answer's final sentence is nearly twice as likely as the rest to be unsupported. Content order follows document order, and the second half of the documents (apart from the final 10 percent) gets cited less; shuffling weakens but does not remove this (Pearson 0.1445 unshuffled, 0.1359 shuffled, judged by T5).
- Error types among unsupported sentences (30 per setting, 17 for WebGPT, not mutually exclusive): retrieval failure 54 percent, hallucinated facts 72 percent, incorrect synthesis 14 percent; about 14 percent were annotation errors.
- In a hand check of 20 questions, the document sets were sufficient to answer in 85 percent of WebGPT cases, 50 percent of human and 45 percent of Bing.
- Relevant documents shift surface statistics more than random ones do. For GPT-3.5 they shorten answers (219 to about 172-185 words) and raise perplexity (6.13 to 11.63 with WebGPT documents; 6.76 with random). For Alpaca they lengthen answers (113 to 138-187). GPT-4 with random documents often abstains (1.6 sentences on average).
- Random documents leave attribution to the relevant documents nearly unchanged, which the paper reads as models ignoring irrelevant documents. With Bing documents, the T5 judge scores supportedness at 48.53 percent against 23.06 percent with random ones.
- T5-11B NLI is the best automatic detector: average F1 60.1, accuracy 82.6, against human 71.2 and 88.6 and random 21.3 and 68.0.

## Limits

- One domain (ELI5), 100 annotated questions, 3 samples per setting; models are old, and WebGPT outputs only. GPT-4 appears only in surface statistics.
- Attribution is not factuality: an unsupported sentence may still be true (the authors note this).
- NLI thresholds were set using the evaluation data, and no dev set exists. The shuffle control is judged by the T5 model, not humans.
- The authors say their finding departs from earlier work that saw no difference between random and relevant documents, and offer reasons (low-relevance retrieval in that fine-tuning, ELI5 train-test overlap).

## See Also
- [[Long-Form QA Evaluation Hurdles]] — contradicts (earlier finding that random and relevant documents made no difference for smaller fine-tuned models)
- [[Generative Search Engine Verifiability Audit]] — related (its data is reanalysed here)
- [[ALCE Citation Benchmark]] — related
- [[FActScore]] — related (same last-sentence trend, in biographies)
- [[Lost in the Middle]] — related (positional effects, in factoid QA)
- [[RAG Evaluation]] — prerequisite-for
