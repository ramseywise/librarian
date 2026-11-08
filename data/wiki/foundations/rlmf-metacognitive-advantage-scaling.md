---
title: RLMF Metacognitive Advantage Scaling
tags: [foundations, pattern]
summary: "Reinforcement learning with metacognitive feedback scales each GRPO completion's advantage by how accurately the model judged its own confidence faithfulness, instead of adding a reward term; on faithful calibration of small models it beat plain GRPO in the paper's runs."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-liu-2026-reinforcement-learning-metacognitive-feedback-elicits.md
---

# RLMF Metacognitive Advantage Scaling

RLMF (Liu et al., Yale and Google Research, COLM 2026, arXiv 2606.32032) trains a model to state numeric confidence for each sentence it writes so that stated confidence matches its intrinsic confidence, estimated from sampling consistency over 20 extra samples. The task metric is faithful calibration (cMFG*, a metric the authors propose).

## Mechanism

GRPO runs with 32 samples per prompt and no standard-deviation normalisation. For each completion the gold faithfulness is the fraction of sentences whose stated confidence is within tau = 0.10 of the intrinsic one. The policy is also prompted online to predict that fraction, and the metacognitive score is Z = 1 minus the squared gap between predicted and gold. The advantage is split into other rewards and a faithfulness part. For completions whose faithfulness is above the group mean, the faithfulness advantage is multiplied by (k + Z), with k = 1; below the mean it is left alone. So among completions that already do well, those that judged themselves more accurately are reinforced more. Training is SFT first (for the output format), then GRPO with a weighted composite reward (faithfulness weight 12, strict and soft format 3 each, factual calibration 1, accuracy 1) on 2000 PopQA examples, selected as the model's highest and lowest self-rated halves.

## Results (self-reported; single seed, 1.7B to 8B models, LoRA rank 64)

- Qwen3-8B cMFG* 0.83 for RLMF against 0.51 for standard RL (the headline "up to 63%"); Llama3.1-8B 0.84 against 0.77. Accuracy for Qwen3-8B was 0.57 for RLMF.
- Table 1: gains of 29% and 25% in average cMFG* over MetaFaith prompting and FUT SFT respectively.
- Qwen3-8B+RLMF scored cMFG* 0.83 with accuracy 0.57; MetaFaith-prompted Gemini-3.1-Pro scored 0.70 with accuracy 0.78.
- Metacognitive data selection against random and active-learning selection (Qwen3-8B): 0.83, 0.76, 0.72.
- Using Z as an extra reward instead of scaling advantages reached about 0.79 to 0.83 cMFG* but accuracy fell to 0.22 to 0.31; the authors say hacking appears when no faithfulness threshold is applied.
- Training on one dataset (PopQA, SelfAware, HaluEval or UMWP) gave average cMFG* of 0.80 to 0.84 on Llama.
- Three expert annotators on 120 examples preferred RLMF over FUT on the four dimensions at win rates of 95% to 98%.

## Limits

- The paper has no limitations section. Its ethics note says better faithfulness does not replace verification, and a footnote says the self-assessment gains do not amount to broad metacognition.
- Seed 42 only, no error bars; checkpoints were chosen on the in-domain PopQA test set (up to 1000 examples).
- Models are 1.7B to 8B with thinking mode off; the task is faithful calibration only, not general tasks such as math.
- Plain RL on Qwen3-8B degenerated into gibberish, so part of the 63% reflects a weak comparison point. Rewriting needs a second LLM, accuracy trails frontier models, and cMFG* is the authors' own metric, also used to score the baselines.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Preference Optimization Algorithms]] — prerequisite-for (GRPO advantage computation)
- [[Reward Hacking and Overoptimization]] — related (extra-reward variant hacked)
- [[Logprobs as Confidence Signal]] — related
- [[MetaCrit Adaptive Critique]] — related
