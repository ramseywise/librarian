---
title: ELECTRA Replaced Token Detection
tags: [llm, pretraining-and-data, pattern]
summary: "ELECTRA trains an encoder to label every input token as original or replaced, where replacements are sampled from a small jointly trained masked-LM generator, so the loss covers all tokens rather than the roughly 15% BERT masks."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-clark-2020-electra.md
---

# ELECTRA Replaced Token Detection

Clark, Luong and Le ask whether a pretraining task defined over all input tokens can train a text encoder with less compute than masked language modelling.

## Mechanism

Masked positions are filled with samples drawn from a small masked-LM generator. The ELECTRA discriminator (a Transformer encoder) then tags every token in the result as original or replaced. Training minimises L_MLM + lambda * L_Disc over both networks together. The generator is thrown away afterwards, and the discriminator alone is fine-tuned for GLUE and SQuAD. The task is called replaced token detection.

## Reported results (self-reported)

- At the same compute (6.4e19 FLOPs, 110M parameters, Wikipedia and BooksCorpus, median of 10 runs), ELECTRA-Base scores above BERT-Base on GLUE dev, and above BERT-Large too.
- ELECTRA-Small (14M parameters, 4 days on one V100, 1.4e18 FLOPs) outscores GPT on GLUE dev and beats BERT-Small at equal FLOPs. Against BERT-Large it uses 1/20th of the parameters and 1/135th of the pretraining compute. Trained for 6 hours on one V100 (6.25% of training, 8.9e16 FLOPs) it still reaches 74.1 GLUE.
- At large scale (335M parameters, XLNet data), ELECTRA-400K matches RoBERTa and XLNet on GLUE dev with under a quarter of the compute (7.1e20 FLOPs); ELECTRA-1.75M (3.1e21 FLOPs) outscores RoBERTa-500K and XLNet. The authors' own BERT-Large baseline, given ELECTRA-400K's FLOPs, scores lower.
- Efficiency ablation (Base-sized, BERT data): computing the discriminator loss on only the 15% masked tokens brings ELECTRA down to BERT's level, while an MLM variant over all tokens recovers most of the difference between BERT and ELECTRA. A "Replace MLM" variant slightly outperforms BERT, so the [MASK] mismatch matters a little.
- Weight tying (Base-sized, 500k steps, equal generator and discriminator size): 83.6 untied, 84.3 with tied embeddings, 84.4 with all weights tied.
- An adversarially trained generator is worse at masked LM than a maximum-likelihood one (58% against 65% accuracy, 256-hidden generator) and does not help downstream.
- As a masked language model BERT is ahead of ELECTRA (77.9% against 75.5% accuracy, Base models, top-100 generator candidates).

## Limits

- The authors' BERT-Large baseline scores clearly below RoBERTa-100K, which suggests it needs either further tuning or RoBERTa's data; comparing XLNet's data with RoBERTa's is not entirely like for like.
- GLUE test comparisons involve ensembling and task-specific tricks; reported training times come from different hardware and sometimes unoptimised code.
- The account of why ELECTRA is parameter-efficient is speculative; the authors call for more analysis.
- The study is English only, FLOP counts leave out hardware effects such as ALBERT's communication savings, and per-task hyperparameters were not searched.

## See Also
- [[BERT Masked-LM Pretraining and Its Refinements]] — prerequisite-for (the masked-LM baseline it replaces)
- [[DeBERTa Disentangled Attention]] — related (DeBERTa also reports a variant pretrained with this objective)
- [[XLNet Permutation Language Modeling]] — alternative-to
