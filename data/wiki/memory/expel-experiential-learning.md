---
title: ExpeL Experiential Learning
tags: [memory, concept]
summary: Training-free agent that gathers trajectories, has gpt-4-0613 distil a list of natural-language insights from them, and at test time prompts with all insights plus the most similar successful trajectories; reported gains over ReAct on ALFWorld and HotpotQA (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-zhao-2024-expel.md
---

# ExpeL Experiential Learning

ExpeL (2024) turns an agent's past attempts into reusable text knowledge without updating weights. In stage 1, trajectories are gathered on training tasks using ReAct with Reflexion retries. In stage 2, gpt-4-0613 distils a list of insights, drawing on pairs of failures and successes and on chunks of L successes, editing the list with ADD, EDIT, UPVOTE and DOWNVOTE operations. At test time the task prompt receives every insight plus the top-k most similar successful trajectories as few-shot examples (*experience recall*, by task similarity), and the agent makes a single attempt.

## Results (self-reported)

Setup: the actor is gpt-3.5-turbo-0613 and the insight extractor gpt-4-0613, with four-fold validation.

- ExpeL beats ReAct on ALFWorld and HotpotQA success rate in the ablation table; insights moved from HotpotQA to FEVER (adapted by gpt-4-0613 with target demonstrations) lift success over ReAct.
- Combined with Reflexion retries on ALFWorld, ExpeL reaches 64.2% at round 3. Single-pass ExpeL matches or exceeds Reflexion without retries on HotpotQA (40% against 39% at round 3), while on ALFWorld the printed text reads 54% against 59%.
- Insights-only against retrieval-only shows opposite strengths: HotpotQA 36% and 31%, ALFWorld 50% and 55%, WebShop 37% and 38% (read from prose about Fig 5).
- Ranking trajectories by task similarity beats reasoning similarity (48.5 +/- 2.1) and random sampling on ALFWorld.
- LLM-generated insights beat hand-crafted ones (32.0 +/- 1.1 hand-crafted); adding reflections to the insight stage hurts (29.0 +/- 0.4); a gpt-3.5-turbo extractor (32.0 +/- 0.4) is worse than gpt-4.

## Limits

- Text observations only; only closed API models tested; all insights fit in the context, and lifelong use would need retrieval over insights.
- Z, H, L, k, the training-set sizes and the task counts are not stated in the text, there is no appendix in this PDF, and Fig 5 values appear only in the figure.
- The behavioural analysis is manual inspection of trajectories, so anecdotal; transfer is tested on one pair only.
- The authors note the prompting approach lacks the theoretical underpinnings of RL.

## See Also
- [[Reflexion]] — prerequisite-for
- [[ReAct Pattern]] — prerequisite-for
- [[Agent Memory Types]] — prerequisite-for
- [[Self-Controlled Memory Framework]] — related
