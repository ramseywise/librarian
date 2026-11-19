---
title: SDPO Self-Distillation Policy Optimization
tags: [llm, reinforcement-learning, concept]
summary: "SDPO re-scores each rollout under the same model reprompted with environment feedback and distils that self-teacher's next-token predictions into the policy, giving token-level credit where GRPO gives one scalar; tested on Qwen3-8B and Olmo3-7B-Instruct."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-hubotter-2026-reinforcement-learning-self-distillation.md
---

# SDPO Self-Distillation Policy Optimization

Hübotter et al. (2026, preprint) investigate whether a model can read rich environment feedback in context (a runtime error, judge text, or a sibling rollout that succeeded) and turn it into dense per-token credit with no outside teacher. Their setting, Reinforcement Learning with Rich Feedback (RLRF), has environments return tokenised feedback as well as a scalar reward. The working hypothesis is that the same policy given the feedback, the self-teacher `pi_theta(. | x, f)`, is more accurate than the plain student, and that the benefit rises with the base model's ability to learn in context.

## Mechanism

For each question SDPO draws G rollouts and gathers feedback (a successful sibling can serve as the feedback). It then scores the original rollout again with the model prompted to include that feedback and minimises a stop-gradient divergence between student and teacher over the top-K logits. It is a policy-gradient method with the GRPO advantage `r_i - mean{r_i}` replaced by `log [pi_theta(y | x, f_i, y_<t) / pi_theta(y | x, y_<t)]`. It extends the idea in [[On-Policy Distillation]] by removing the external teacher. The baseline is an improved [[GRPO Group Relative Policy Optimization]].

## Results (self-reported)

- On science QA and tool use (Qwen3-8B and Olmo3-7B-Instruct; SciKnowEval and ToolAlpaca; fully on-policy) SDPO ends with a better aggregate accuracy than GRPO.
- On LiveCodeBench v6 with Qwen3-8B, SDPO is more accurate at step 80 and needs a quarter of the generations to match GRPO's final accuracy. The GRPO variants run in that setup score 40.1 (GSPO), 41.2 (CISPO) and 37.8 (high-entropy-token GRPO).
- For Olmo3-7B-Instruct on Chemistry, SDPO reaches in 50 minutes what GRPO reaches in 5 hours, with responses 11x shorter and accuracy higher; across tasks, Qwen3-8B responses shrink by about 3.2x.
- Gains concentrate on medium and hard questions (Qwen3-8B, LiveCodeBench v6): 46.6 against 37.8 on medium, 91.7 against 90.1 on easy.
- Credit at the logit level outperforms both token-level and sequence-level SDPO, and sequence-level SDPO still outperforms GRPO. Regularising the teacher matters (Qwen3-8B, LiveCodeBench v6): 36.1 with none, 48.8 with a frozen initial teacher, 49.3 with an EMA teacher, and the trust-region variant (alpha 0.01) is best.
- Forgetting check on Qwen3-8B after LCBv6 training, on the held-out IFEval, ArenaHard-v2 and MMLU-Pro sets: the base model scores 43.5, GRPO 41.8 and SFT on self-teacher generations 41.4; fine-tuning only on successful self-teacher generations gets 42.7 on LCBv6.
- Test-time SDPO on very hard LCBv6 questions (pass@64 under 0.03, Qwen3-8B): 41.5% for best-of-k and 35.6% for multi-turn discovery at 2750 generations, with SDPO needing about 3x fewer generations for 22% discovery. On hard questions it reaches 78% discovery@2750.
- In the teacher-prompt ablation (Qwen3-8B, LCBv6, to step 60), environment output plus the student's own solution scored 48.3 and a variant that also adds the original attempt scored 44.5; adding the student's own attempt reduces teacher and student entropy and student accuracy.

## Limits

- The method leans on in-context learning: on Qwen2.5-1.5B it does worse than GRPO, and feedback that misleads may not help.
- Models are capped at 8B, updates are on-policy only, runs fit on one node, and agentic or long-horizon tasks are absent. Computing teacher log-probs adds a little overhead.
- Section 3 hyperparameters were chosen by validation accuracy at 5 hours, on the data behind the test table (the split is not detailed), and train and test sizes are unstated. The SDPO advantages are biased relative to expected reward.

## See Also
- [[On-Policy Distillation]] — prerequisite-for (the external-teacher version this removes the teacher from)
- [[GRPO Group Relative Policy Optimization]] — alternative-to (scalar-reward advantage)
- [[GSPO Group Sequence Policy Optimization]] — alternative-to (a GRPO variant used as a baseline)
- [[Outcome vs Process Reward Models]] — related (dense credit without a learned step scorer)
