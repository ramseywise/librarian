---
title: XLNet Permutation Language Modeling
tags: [llm, pretraining-and-data, pattern]
summary: "XLNet maximises expected autoregressive likelihood over sampled factorisation orders, with two-stream attention for target-aware prediction on a Transformer-XL backbone, to get bidirectional context without BERT's [MASK] tokens."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-yang-2019-xlnet.md
---

# XLNet Permutation Language Modeling

Yang et al. ask whether a pretraining objective can keep autoregressive likelihood, with no input corruption and no independence assumption between predicted tokens, while still learning bidirectional context.

## Mechanism

- **Permutation language modeling:** maximise expected autoregressive log likelihood, averaging over factorisation orders. A sampled order determines which tokens are context for each prediction; attention masks implement the order while positions stay in natural order.
- **Partial prediction:** only the last 1/K tokens of the sampled order are predicted.
- **Two-stream self-attention:** a content stream sees its own token, and a query stream sees position but not content, with shared parameters.
- **Backbone:** Transformer-XL's segment recurrence and relative position encodings, with relative segment encodings added.
- The authors contrast the objectives with an example: BERT scores both "New" and "York" given "is a city", while XLNet scores "York" given "New" and "is a city".

## Reported results (self-reported)

- Same data (BooksCorpus and Wikipedia) and BERT hyperparameters: the 24-layer XLNet-Large-wikibooks is ahead of the strongest of three BERT-Large variants (original, whole-word masking, no NSP) on RACE; MNLI and SQuAD 2.0 are also compared, and RTE jumps by about 7 points.
- Base-sized ablation (Wikipedia and BooksCorpus, median of 5 runs): replacing BERT-Base with Transformer-XL trained on BERT's objective already helps, and the permutation objective adds more. Taking out the memory hurts, and RACE (the task with the longest context) suffers most. Adding NSP does not help overall (RACE rises slightly, SQuAD 2.0 F1 falls). Dropping span-based prediction lowers SQuAD 2.0 F1.
- At scale (XLNet-Large on 32.89B tokens, 512 TPU v3 chips, 500K steps at batch 8192, with RoBERTa's hyperparameters) XLNet is ahead of RoBERTa on RACE test, is compared on SQuAD 2.0 dev F1 and MNLI dev, and is slightly below on RTE dev.
- The authors see the biggest improvements on tasks with longer context and credit Transformer-XL for them.

## Limits

- No parameter count is reported; XLNet-Large is described only as comparable in size to BERT-Large.
- Ablation rows are medians of 5 runs with no spread given, and several differences (SST-2, the NSP rows) are under a point.
- Table 1 compares with the strongest of three BERT variants. Only the Base-scale row (Transformer-XL trained with BERT's objective) separates the permutation objective from the Transformer-XL backbone.
- The large-scale result against RoBERTa uses different data from the like-for-like comparison, and data effects are not separated from the objective.
- The model was still underfit when the 500K steps ended, and the SQuAD 1.1 test result comes from an older model version.
- That the permutation objective mainly improves data efficiency is a conjecture supported only by qualitative attention analysis.

## See Also
- [[BERT Masked-LM Pretraining and Its Refinements]] — prerequisite-for (the masked-denoising objective it contrasts with)
- [[ELECTRA Replaced Token Detection]] — alternative-to
- [[Denoising Seq2Seq Pretraining: BART, MASS and GLM]] — extends (GLM draws on the permutation idea for span order)
- [[Transformer Architecture]] — prerequisite-for
