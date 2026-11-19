---
title: "Domain-Specific Pretraining from Scratch: Galactica and BloombergGPT"
tags: [llm, pretraining-and-data, comparison]
summary: "Galactica trains on a curated 106B-token scientific corpus with a working-memory token and task prompts, repeating data for about 4 epochs; BloombergGPT trains on half finance text and half public text and stops at about 80% of one epoch; both are self-reported and neither has an ablation."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-taylor-2022-galactica.md
  - data/raw/papers/2026-11-07-wu-2023-bloomberggpt.md
---

# Domain-Specific Pretraining from Scratch: Galactica and BloombergGPT

Both papers train a decoder-only model from scratch on domain text rather than adapting a general model. BloombergGPT's extraction names Galactica as the inspiration for mixing domain and public data.

| | Galactica (Taylor et al., 2022) | BloombergGPT (Wu et al., 2023) |
|---|---|---|
| Sizes | 125M to 120B | 50.6B, 70 layers, BLOOM-style |
| Corpus | 106B curated scientific tokens (papers 88B, 83.0%; remainder includes textbooks, knowledge bases, code, SMILES strings, protein sequences, DNA sequences, and filtered CommonCrawl), with 358M further tokens of task prompts | 708B tokens: FinPile (Bloomberg finance text, 363B) and public data (345B; Pile, C4, Wikipedia) |
| Training length | 450B tokens, about 4.25 epochs | 569B tokens, about 80% of one epoch |

## Galactica mechanisms

- A working-memory token, written `<work>`, encloses step-by-step reasoning; citations and each sequence modality also get special tokens. The extraction treats `<work>` as an alternative to chain-of-thought prompting.
- Prompt pre-training puts task prompts into the corpus instead of instruction-tuning afterwards.
- Repeated data: validation loss was still dropping at 450B tokens, and the 120B model began to overfit only as the fifth epoch started, where it was stopped. The authors report that about 4 epochs of repeated tokens did no harm; the extraction records that Hernandez et al. (2022) found repetition harmful.
- Reported results (zero-shot unless noted, self-reported): the 120B model gets 20.4% on MATH with 5-shot Minerva-style CoT against 8.8% for PaLM 540B; on 57 BIG-bench tasks it outscores OPT 175B and BLOOM 176B (5-shot, weighted accuracy); it sets state of the art on PubMedQA and MedMCQA, with those training sets inside pre-training; its CrowS-Pairs stereotype score is below those of OPT 175B and GPT-3; TruthfulQA MC1 accuracy stays low.

## BloombergGPT mechanisms

- Size came from a Chinchilla approach-1 fit given 0.75 of a 1.3M A100-40GB-hour budget, which gave a compute-optimal size near 50B but wanted many more tokens than existed. Training ran on 512 A100 40GB GPUs with ZeRO3, MiCS and activation checkpointing in BF16.
- Tokenizer: Unigram; vocabularies from 25,000 to 550,000 entries were tried, the one minimising encoded C4 size was chosen and rounded to a power of 2.
- The run ended at step 146,000; the checkpoint at step 139,200 was picked on validation loss and downstream evals, since held-out loss had stopped improving.
- Few-shot comparison (self-reported) against three open models (GPT-NeoX at 20B, OPT at 66B, BLOOM at 176B parameters): best average on the public finance tasks (5-shot, NER 20-shot; the baselines average 51.90, 53.01 and 54.35); second to GPT-NeoX on public NER; a very large margin on internal aspect sentiment (5 Bloomberg tasks, 5-shot; baselines 29.23, 35.76, 33.39); well ahead on joint NER and entity disambiguation (baselines 39.26, 58.79, 45.43); behind the larger BLOOM176B on internal NER.
- General ability: under BLOOM176B and PaLM540B on BIG-bench Hard (23 tasks at 3-shot: BLOOM176B scores 44.91 and PaLM540B 52.3), about level with BLOOM176B on 5-shot MMLU and under GPT-3 (43.9, as reported from Hendrycks 2021).
- Training Chronicles (Appendix C): month-ordered curriculum learning stalled and was dropped; in v1.0 the gradient norm began rising near step 12k and four fixes failed; a v2.0 restart that changed many things at once ran stably for an unknown reason; after step 115,500 validation loss flattened, and learning-rate cuts and dropout did not clearly help.

## Limits

- Neither paper isolates the effect of its corpus. Galactica has no run without prompts and no comparison of prompt pre-training against instruction tuning, and its repeated-token finding lacks a matched uncurated-corpus run, leaving quality versus modality open. BloombergGPT lacks a twin trained on public or on finance data alone, and lacks a tokenizer ablation, so its ranking of causes is untested.
- Galactica sets zero-shot scores against 5-shot baselines, includes in-domain benchmarks, uses one run per size with no significance tests, has a 2048-token context and overfit an out-of-domain protein set from epoch 4. The extraction adds that the model was pulled from the public demo soon after release, which the paper does not say.
- BloombergGPT's weights, FinPile and internal benchmarks are unreleased, so internal results cannot be verified; internal task text likely sits in FinPile, which the authors concede as possible contamination. Shot counts were set to maximise average performance and each model-task pair reports the best of three classification methods, without error bars. Toxicity and bias were not measured, the budget was nearly spent when training stopped, and its data ends July 2022.
- The extraction does not give BloombergGPT's own public-finance average.

## See Also
- [[Continued Pretraining for Domain Adaptation]] — alternative-to (adapt a general model with domain text instead)
- [[Scaling Laws: Kaplan, Chinchilla and Error Landscapes]] — prerequisite-for (the fits BloombergGPT used for size)
- [[Chain-of-Thought Prompting]] — related (the prompting counterpart of the working-memory token)
- [[BIG-Bench Hard]] — related
