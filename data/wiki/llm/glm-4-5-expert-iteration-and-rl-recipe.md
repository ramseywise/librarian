---
title: GLM-4.5 Expert Iteration and RL Recipe
tags: [llm, pretraining-and-data, concept]
summary: "GLM-4.5 is an open-weight 355B MoE (32B active) pretrained on 23T tokens, then post-trained by training reasoning, agent and chat experts and distilling them into one hybrid thinking model; its RL ablations, run on a smaller unnamed model, favour a two-stage difficulty curriculum and single-stage 64K length (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-team-2025-glm-4-5.md
---

# GLM-4.5 Expert Iteration and RL Recipe

The GLM-4.5 Team (Zhipu AI and Tsinghua University, preprint 2025) asks whether one open-weight MoE can combine agentic, reasoning and coding abilities (ARC) at frontier level using fewer parameters. Their hypothesis: a deeper, narrower MoE, multi-stage pre- and mid-training and expert-iteration post-training together give a parameter-efficient generalist.

## Recipe

- Models: GLM-4.5 has 355B parameters in total with 32B active, and GLM-4.5-Air has 106B with 12B active. Both offer hybrid thinking and non-thinking modes.
- Pretraining: 15T general tokens plus 7T tokens weighted toward code and reasoning, 23T in total. Mid-training, defined as post-pretraining stages on medium-size domain data, covers repo-level code, synthetic reasoning, and long-context and agent data, and extends context to 128K.
- Post-training: separate reasoning, agent and chat experts are trained (SFT first, then RL) and distilled into one hybrid model, followed by general RL and a pathology RL stage. RL runs on the Slime infrastructure with GRPO without a KL term.
- The authors say best-fit packing was not used in pre-training because random truncation works as data augmentation, and that early experiments with a WSD schedule underfit on SimpleQA and MMLU.

## RL and SFT ablations (a smaller experimental model, not GLM-4.5)

- For SFT prompt selection, discarding the bottom half of prompts by response length improved maths and science by 2% to 4% while using half the data; four responses per hard prompt added another 1% to 2%.
- A two-stage difficulty curriculum got 83.4% on AIME24 Avg@32 against 81.8% for a baseline that continues with moderate data; stage 2 uses verified-answer problems with pass@8=0 and pass@512>0.
- RL at a single 64K length got 83.4% against 80.6% for a multi-stage schedule of rising lengths (16K, 32K, 48K, 64K). The extraction lists this as contradicting DeepScaleR's multi-stage finding.
- For code RL, a token-weighted mean loss converged faster, ending at 46.5% against 46.3% on LiveCodeBench (read from a figure). Science RL restricted to expert-verified multiple choice got 65.8% on GPQA-Diamond against 62.9% for mixed-quality data.

## Reported results (self-reported, GLM-4.5 unless noted)

- SWE-bench Verified 64.2% (OpenHands v0.34.0, capped at 100 iterations, sampling temperature 0.6 and top_p 1.0, the 500-instance subset); TAU-Bench 70.1% (retail and airline, optimised user simulator); AIME 24 91.0% (thinking mode, mean of 32 samples, LLM validation); GPQA 79.1 (Avg@8); BrowseComp 26.4 against 18.8 for Claude Opus 4; Terminal-Bench 37.5 (Terminus framework).
- Across 12 ARC benchmarks it ranks third on average among the models evaluated and second on the agentic ones (models as of 28 July 2025).
- GLM-4.5-Base: MMLU 86.1 against 87.2 for DeepSeek-V3-Base, and GSM8K 79.4, the lowest among the bases compared (internal framework).
- CC-Bench (52 tasks, human expert judges, Claude Code harness): against Claude Sonnet 4 it wins 40.4%, ties 9.6% and loses 50.0%, with 90.6% tool-calling success.

## Limits

- Pre-training and mid-training stages have no ablation; the RL ablations use an unnamed smaller model.
- Hardware, compute, warmup steps, tokenizer and vocabulary are unstated. Base scores come from an internal framework, with GSM8K and MATH behind peers.
- Human evaluations rely on one evaluator, with no inter-rater agreement or significance tests. The frontier comparison dates from 28 July 2025.

## See Also
- [[GRPO Group Relative Policy Optimization]] — prerequisite-for (the RL algorithm)
- [[Post-Training for Agents]] — related
- [[Qwen and Qwen2.5 Technical Reports]] — related (another open-weight family report; Qwen3 is a GLM-4.5 baseline)
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Mixture-of-Experts Routing and Scaling]] — prerequisite-for
