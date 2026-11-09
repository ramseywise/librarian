---
title: DetectGPT
tags: [foundations, concept]
summary: "DetectGPT flags text sampled from a model by comparing its log probability with that of T5-perturbed rewrites; the normalised gap is larger for model samples, giving zero-shot detection with no training data or watermark (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-mitchell-2023-detectgpt-2301-11305.md
---

# DetectGPT

Mitchell, Lee, Khazatsky et al. (ICML 2023, PMLR 202; arXiv 2301.11305) ask if text drawn from an LLM can be spotted zero-shot, with nothing but the source model's log probabilities, by looking at how curved that log-probability surface is nearby. They hypothesise that a small rewrite of machine text scores lower under the model than the original, whereas a rewrite of human text can score higher or lower, because model samples lie in regions of negative curvature.

## Mechanism

Given a passage, generate k rewrites with a stock T5 mask-filling model, score the passage and every rewrite under the source model, and compare the passage's log probability with the average over the rewrites, dividing by the rewrites' standard deviation; a gap above a threshold epsilon means machine-written (Algorithm 1). The raw gap is called the **perturbation discrepancy**: the passage's log probability minus the expected log probability of rewrites drawn from q(.|x). The paper's **white box** setting lets the detector evaluate a sample's log probability without knowing the architecture or parameters. There is no training, no labelled data and no watermark.

## Results (self-reported)

- On fake news from GPT-NeoX 20B (XSum, 500 samples, temperature 1, T5-11B rewrites) it outperforms the strongest zero-shot baseline, which scores 0.81.
- Across five generators, namely the 20B NeoX, GPT-J, Neo-2.7, OPT-2.7 and GPT-2, and 500 samples per generator, it is top in 14 of 15 dataset-model pairs and averages 0.06 AUROC higher.
- With GPT-NeoX 20B on SQuAD it falls to 0.79 AUROC but stays over the baselines. On WritingPrompts with GPT-NeoX every method does well, the gap is small, and LogRank beats it.
- For GPT-3 and Jurassic-2 (175B) over PubMedQA, XSum and WritingPrompts (150 samples each), its average AUROC is comparable to the best supervised detector, against 0.82 for RoBERTa-large, 0.77 for RoBERTa-base and 0.69 for log p(x). On GPT-3 text, RoBERTa-large wins XSum (0.92 to 0.84) and DetectGPT wins PubMedQA (0.84 to 0.71).
- Using T5-3B to replace random 5-word spans in GPT-J samples from XSum, AUROC remains above 0.8 until almost a quarter of the text (up to 24%) is replaced.
- Nucleus sampling at p=0.96 eases detection on XSum, averaged over 5 models; log p(x) and LogRank reach 0.92 and 0.93 there.
- A scoring model that differs from the source weakens detection. GPT-2 scoring its own samples gives 0.99 (mean over XSum, SQuAD and WritingPrompts at 200 samples each), and other pairings go as low as 0.60.
- Accuracy levels off near 100 perturbations, measured with T5-large rewrites on XSum, SQuAD and WritingPrompts, using GPT-2 and GPT-J and 100 examples per dataset.

## Limits

- It requires the source model's log probabilities, and getting them from an API model costs money.
- A decent perturbation function is a prerequisite; where mask-filling models handle rephrasing badly, accuracy suffers (a possible reason for PubMedQA's lower score).
- Compute is heavier than for the baselines, with around 100 rewrites sampled and scored for each passage.
- A mismatched scoring model hurts, so the method fits white-box use best.
- Very long passages may do worse, as T5 loses track once 20 or more masks are present.
- In-distribution, on English news, supervised detectors match or beat it.
- Only sampled base models (GPT-2 up to GPT-3, and Jurassic-2) were tested; ChatGPT is named as impossible to score, RLHF models were not tried, and paraphrasing is only simulated through T5 replacement.
- The authors point to two 2023 papers on paraphrase evasion and defer it to future work.

## See Also
- [[GLTR]] — alternative-to (rank and entropy features under a detection model)
- [[Green-List LLM Watermark]] — alternative-to (needs control of the generator)
- [[Min-K% Prob Pretraining-Data Detection]] — related (another detector built on token probabilities)
