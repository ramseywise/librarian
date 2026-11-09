---
title: Harness-R1 Learned Harness Editing
tags: [harness, pattern]
summary: A small trained model writes Python hook patches around a frozen agent from that agent's failure trajectories, with reward equal to the measured success change when the patch is installed.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-shao-2026-harness-r1.md
---

# Harness-R1 Learned Harness Editing

Harness-R1 (Shao et al., a 2026 preprint) treats the runtime around an agent as an editable surface and trains a separate "harness engineer" model to edit it. The engineer reads a packet of failure trajectories from a frozen target model and emits patches that add Python hooks. The target's weights never change; only the engineer is trained, first with supervised fine-tuning on teacher examples and then with online GRPO.

## The editable surface

Four lifecycle hooks sit around the frozen policy and touch only its inputs and outputs:

- **Episode initialisation** sets starting context and state, and can return skills or a tool hint.
- **Pre-decision** adds retrieved guidance or interface constraints to the context before the agent decides.
- **Pre-action** is a guardrail that can canonicalise, rewrite, block or force an action the agent proposes, ahead of its execution in the environment.
- **Post-feedback** inspects the returned observation and injects a hint when the trajectory stalls.

The engineer's output is a structured `add_code_hook` object naming one hook and giving Python source. The host runtime interprets the effects (inject a hint, block and re-prompt, rewrite an action, force an action).

## Reward

The reward for a patch is the mean change in reward across the whole task batch when the same frozen target is rerun with the patch applied, counting tasks that already succeeded. A patch that is invalid, a no-op or incomplete scores 0 and regressions score negative. Each failure packet gets 8 candidate patches, with group-normalised GRPO and no KL term. The SFT set is 877 teacher examples (GPT-5.5) kept only when the reward change was non-negative.

## Results

All numbers are self-reported by the authors unless stated.

- Target Qwen3.5-9B, WebShop (500 tasks), ALFWorld (500) and DBBench (300), temperature 0, single run: average success goes up 9.3 points, from 44.3% to 53.6% (self-reported). The same tasks supply both the failures mined and the reward.
- Frontier models prompted once as editors, same setup: GLM-5.2 gets 48.8%, GPT-5.5 gets 47.9% and Qwen3.5-397B gets 45.8%, while an engineer trained by supervision alone gets 46.4% (self-reported). Self-Refine scores 41.8% and ReAct 47.5% on the same target.
- A target fine-tuned on 2,515 successful trajectories moves from 59.2% to 64.2% with an engineer retrained for it (one adaptation step, self-reported).
- One trained engine applied to 20 unseen target models (Llama, Gemma and Qwen, 1B to 72B), with a patch written from each target's own failures: mean gain +7.06 points, 56 of 63 target-benchmark cells improve, 3 regress by at most 2.0 points (self-reported). The 1B models gain little (+2.2 and +1.2).
- Removal ablation on fixed patches, vanilla Qwen3.5-9B, three reruns: full 53.1%, no pre-action 49.2%, no post-feedback 49.8%, no episode init 52.2%, no pre-decision 52.5% (self-reported). The authors say the ranking depends on the environment and the effects are not additive.
- Patches from only 10 failures, 3 seeds, 1,270 pooled held-out tasks: Harness-R1 +8.9 ± 1.5 points against -4.3 ± 2.5 for Qwen3.5-397B and -0.4 ± 3.6 for DeepSeek-V4-Pro as editors (self-reported).

A case study shows the risk: a Gemini-3.5-Flash editor's broad force-action rules took ALFWorld from 208/500 to 177/500, and 21 of its 39 valid patches reduced success. A narrow WebShop pre-action guard that blocks purchase when the price is over budget raised full successes from 2 to 5 on one hand-picked 10-task batch (illustrative).

## Limits

- The authors acknowledge that just one step from the vanilla to the fine-tuned model is tested, the reward is same-batch and has no held-out or efficiency term, and patches are not guaranteed regression-free.
- Only three short-horizon text environments; no coding or terminal benchmark.
- No confidence intervals on the main table; ablation has 3 reruns and held-out test 3 seeds.
- Hooks are hand-designed per benchmark and expose benchmark-specific state to the engineer, so some of the gain could be due to guards specific to each environment.
- Frontier editors saw one prompt and no reruns, which tests one-shot editing only.
- Internal inconsistencies in the extraction: Self-Refine's change is -3.3 in Figure 1 but 2.6 and 2.5 in the text; the body gives the SFT set as "roughly 1,000" examples while the appendix says 877.

## See Also

- [[Harness Anatomy]] — prerequisite-for
- [[Harness Continual Learning]] — related (other systems that update a harness over time)
- [[AutoHarness Synthesized Code Harness]] — alternative-to (an LLM writes the harness as code, without a trained editor)
- [[Meta-Harness End-to-End Optimization]] — alternative-to
