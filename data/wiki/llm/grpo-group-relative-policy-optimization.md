---
title: GRPO Group Relative Policy Optimization
tags: [llm, reinforcement-learning, concept]
summary: "A PPO variant with no value model: sample a group of outputs per question and use group-normalised rewards as advantages, with KL added to the loss; the DeepSeekMath paper's RL algorithm, with its reported MATH and GSM8K gains and its Maj@K versus Pass@K finding."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-shao-2024-deepseekmath.md
  - data/raw/papers/2026-11-08-murphy-rl-ch06-llms-rl.md
---

# GRPO Group Relative Policy Optimization

Shao et al. (2024, DeepSeekMath, preprint) ask whether a 7B open model can reach near-GPT-4 competition-math accuracy by combining web-mined math pretraining with a memory-light RL algorithm. GRPO is that algorithm. For each question it samples G outputs, scores them, and uses each reward normalised within the group, `(r_i - mean(r)) / std(r)`, as the advantage instead of a value-model estimate. A KL term to the reference policy is added to the loss, with the unbiased per-token estimator `pi_ref/pi_theta - log(pi_ref/pi_theta) - 1`. The summary view of GRPO inside the algorithm family is on [[Preference Optimization Algorithms]].

## Setup in the paper

DeepSeek-Coder-Base-v1.5 7B was continued-pretrained on 500B tokens (56% DeepSeekMath Corpus), instruction-tuned on 776K math examples, then trained with GRPO on about 144K GSM8K/MATH-related chain-of-thought questions. The RL stage used a policy learning rate of 1e-6, a KL coefficient of 0.04, groups of 64 outputs, a 1024-token cap and batch size 1024.

## Results (self-reported)

The first three bullets are DeepSeekMath-Instruct 7B before RL versus after RL, chain-of-thought, Top1, no tools; the last two give their own setups:

- MATH 46.8% to 51.7%; GSM8K 82.9% to 88.2%.
- CMATH (Chinese, out of domain, RL used English GSM8K/MATH-style data only) 84.6% to 88.8%.
- Tool-integrated reasoning, Top1: DeepSeekMath-RL 7B reaches 58.8% on MATH against 57.4% for Instruct.
- DeepSeekMath-RL 7B with majority vote over 64 samples gives 60.9% on MATH.

Training curves for a 1.3B DeepSeekMath-Instruct model (GSM8K and MATH, to roughly 8000 steps) are read qualitatively: late in training online rejection-sampling fine-tuning is ahead of the offline version, GRPO is ahead of online RFT, and GRPO fed process supervision is ahead of GRPO fed outcome supervision (see [[Rejection Sampling Fine-Tuning]] and [[Outcome vs Process Reward Models]]). Two rounds of iterative RL on the 7B model improved performance, mostly in the first round.

## Majority-vote gains without Pass@K gains

Sampling at temperature 0.7 with K from 1 to 64 (GSM8K and MATH, Instruct against RL 7B, values read off a figure), RL moves Maj@K but leaves Pass@K where it was. The authors take this to mean RL sharpens the output distribution instead of adding capability. [[RLVR Pass@k Reasoning Boundary]] tests the same question across many models and algorithms.

## Unified view

The paper writes SFT, RFT, DPO, PPO and GRPO as one gradient: an expectation over a data source of a per-token gradient coefficient (a function of question, output, position and reward) times the gradient of the log-probability. The three components that differ are the data source, the reward function and the algorithm.

## Data findings in the same paper

The DeepSeekMath Corpus holds 120B tokens drawn from 35.5M web pages over four rounds of fastText-based selection. Training DeepSeek-LLM 1.3B on 150B tokens gives GSM8K 23.8% and MATH 13.6%, against 11.5%/8.9% for OpenWebMath and 14.3%/11.2% for Proof-Pile-2. In the same 1.3B setup (DeepSeek-LLM 1.3B given 400B tokens of code or general text first, followed by 150B of math), code training before math helps: GSM8K+Python 17.4% against 14.3% after general training. arXiv-only training gave no notable gain on the 7B model (GSM8K 29.0% without, 28.1% with 40B arXiv tokens).

## Murphy's survey notes

Murphy's RL textbook chapter on LLMs says GRPO samples roughly 8 answers for each prompt and standardises the rewards by the group's mean and standard deviation; it cites DeepSeek-R1-Zero as the model trained this way, starting from DeepSeek-V3-Base on math and coding tasks with known answers (reported from the source papers, not re-run). The chapter derives, in a worked algebraic example (Eqs 6.27 and 6.28), that the advantage in Dr GRPO is the RLOO advantage multiplied by J/(J-1). It lists dropping the std division (Dr GRPO) or using a leave-one-out baseline as a way to avoid difficulty bias.

The chapter also notes that the claim that RL produced R1's emergent abilities is disputed: it cites Liu et al. 2025b, Yue et al. 2025 and Gan et al. 2025a for the view that the base model already held chain-of-thought-style patterns (see [[RLVR Pass@k Reasoning Boundary]]).

## Limits

- The authors say the model trails closed models on geometry and theorem proving, and that few-shot prompting does no better than zero-shot (unlike GPT-4). Their arXiv finding was not checked on other tasks, with other data mixes or at larger scale.
- RL drew only on questions already in the SFT set and used plain nucleus sampling. The sharpening reading of the Maj@K result is the authors' interpretation of curves.
- Hardware, compute, seeds, numeric precision and the clip epsilon are not given, the number of RL steps is missing, and the reward model is described only by reference to another paper.
- DPO and RFT are analysed in the unified view; the RL comparison figure has RFT, Online RFT and GRPO, with no DPO run.
- The one-stage code-and-math mixture lowered no-tool math at 1.3B; the authors conjecture limited capacity.

## See Also
- [[Trust Region and Clipped Surrogate Policy Optimization]] — prerequisite-for (the PPO clipped objective GRPO modifies)
- [[Generalized Advantage Estimation]] — related (the critic-based advantage that GRPO's group normalisation replaces)
- [[Preference Optimization Algorithms]] — prerequisite-for (the PPO to GRPO lineage this algorithm sits in)
- [[DAPO]] — alternative-to (four changes to GRPO for long-chain-of-thought math RL)
- [[GSPO Group Sequence Policy Optimization]] — alternative-to (sequence-level ratio instead of per-token)
- [[GDPO Decoupled Reward Normalization]] — alternative-to (per-reward normalisation for multi-reward RL)
- [[SDPO Self-Distillation Policy Optimization]] — alternative-to (token-level credit from a feedback-conditioned self-teacher)
- [[RLVR Pass@k Reasoning Boundary]] — related (pass@k study of GRPO-trained models)
- [[Outcome vs Process Reward Models]] — related
