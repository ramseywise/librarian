---
title: PandaLM
tags: [eval, llm, pattern]
summary: "PandaLM fine-tunes a LLaMA-based judge on 300K order-consistent pairwise labels distilled from GPT-3.5 and uses it to pick instruction-tuning hyperparameters; the 70B size agreed with humans slightly more than GPT-4 on a 999-pair test set while the 7B size scored 0.5926 and stayed below GPT-3.5 and GPT-4 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wang-2023-pandalm.md
---

# PandaLM

Wang et al. (arXiv 2306.05087, ICLR 2024) ask whether an open, locally run judge can replace human or API judges when choosing hyperparameters for instruction tuning. PandaLM is a LLaMA-based judge trained on pairwise comparisons that carry a verdict, a reason and a reference answer.

## Method

1. Distill about 300K pairwise comparisons from GPT-3.5, using Alpaca's 52K instructions and responses from five tuned models. Labels that change when the two positions swap are removed.
2. Fine-tune the judge to output the verdict, the reason and a reference answer.
3. Validate against a test set of 999 pairs labelled by humans (105 ties, 422 won by response 1, 472 by response 2), filtered by annotator agreement from 2.5K to 1K samples. Test responses come from five Alpaca-style tuned 7B models. At judging time the order is swapped and conflicting verdicts are set to Tie.
4. Use the judge to choose among 80 configurations (5 epochs, 4 learning rates, 2 optimisers, 2 schedulers) for five 7B-class base models; the search costs 800 comparisons, each repeated twice.

## Results (self-reported)

- On the 999-pair test set, PandaLM-70B agrees with humans slightly more than GPT-4; PandaLM-7B, at accuracy 0.5926, trails both GPT-3.5 and GPT-4. The extraction notes this sits awkwardly with the paper's wording that it is comparable to them.
- Training PandaLM-7B on the win/tie/lose label alone, without reason and reference, drops accuracy sharply.
- Models tuned with PandaLM-selected hyperparameters beat the Alpaca-hyperparameter models under GPT-4 judging, and by a larger margin under human judges (validation set of 170 instructions; mean over five base models).
- On the lm-eval average (ARC, HellaSwag, MMLU, TruthfulQA), LLaMA-7B improves with the PandaLM hyperparameters while Cerebras-GPT-6.7B drops, although the judges prefer it.
- In the PandaLM-7B search on Pythia, full fine-tuning was preferred over LoRA in 71 of 170 instances, and LoRA in 21.

## Limits

Search ranges follow common practice, so the true optimum may lie outside them. GPT-3.5 produced the training labels, and these may diverge from human preference. Evaluation looks at outcomes only and training is supervised only. Domain tests treat GPT-4 as gold, with a human check of 30 samples on BioASQ alone; the search used the 7B judge rather than the 70B for compute reasons. Code and math are untested. The paper reports no seeds, variance or significance tests, and the text links no code, weights or data.

## See Also
- [[Prometheus 2 Evaluator Models]] — alternative-to (another open evaluator trained for judging)
- [[LLM-as-Judge Evaluation]] — extends (a trained open judge)
- [[LLM Judge Biases]] — related (its swap-and-tie rule for position bias)
- [[Self-Taught Evaluators]] — alternative-to (a judge trained on synthetic labels instead of GPT-3.5 distillation)
