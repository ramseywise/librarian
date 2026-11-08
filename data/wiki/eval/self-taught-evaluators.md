---
title: Self-Taught Evaluators
tags: [eval, llm, pattern]
summary: "Self-Taught Evaluators trains a pairwise judge with no human preference labels: it builds a worse response by answering a modified instruction, keeps judgments that pick the right side, and repeats; Llama3-70B-Instruct went from 75.4 to 88.3 on RewardBench (self-reported), with a 5.6-point swing from answer order alone."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wang-2024-self-taught-evaluators.md
---

# Self-Taught Evaluators

Wang et al. (arXiv 2408.02666, 2024) ask whether a pairwise judge can get better over rounds of training on synthetic preference data alone. Their hypothesis is that learning from judgments that agree with a built-in synthetic preference gives a stronger evaluator, with a curriculum arising on its own as the model improves.

## Method

1. Take reasoning instructions from WildChat (20,582 prompts).
2. Generate a good response, and a "bad" response by answering a modified version of the instruction (both with Mixtral 22Bx8 Instruct).
3. Draw N=15 judgments from the current judge for each example and retain one reasoning chain whose verdict is correct (rejection sampling against the synthetic label).
4. Fine-tune Llama3-70B-Instruct on the retained chains, then repeat, always restarting from the seed model.

## Results (self-reported)

- RewardBench overall accuracy of the Llama3-70B-Instruct seed rose from 75.4 to 88.3 at iteration 5 with no human preference labels; a 32-sample majority vote gave 88.7. On the Chat Hard subset the score went from 58.9 to 84.2, and on Chat it slipped from 97.6 to 96.6.
- The same recipe on labelled HelpSteer2 gave 85.6 as a generative judge, and 87.0 by iteration 3 to 4 in the iterative version. A classifier reward model on HelpSteer2 scored 88.8, and GPT4-0125 scored 84.3 (both taken from the RewardBench leaderboard).
- On MT-Bench agreement with humans (non-tie examples, scores averaged over both orders, vote over 32 samples) it reached 79.5, against 79.1 for GPT4-0125; the gain over the seed's 77.8 is small.
- Position-consistent accuracy on the HelpSteer2 validation set rose from 56.5 to 60.6 (iteration 5, two orders, three seeds).
- Putting the winning response always last or always first gave RewardBench accuracies of 85.5 and 91.1 for the iteration-5 model, depending on which.
- Prompting directly for a bad response gave 80.7 against 83.8 for the modified-instruction method. At iteration 1, using Mixtral for the responses and the judgments scored 83.9, ahead of Llama3.0 judging itself at 81.4.

## Limits

The authors note that generative judges produce longer outputs and cost more to run than score-only reward models. Only the 70B size was tested, and it needs a capable, already-aligned seed. Pairwise only. Only accuracy is reported, not compute cost, from a single training run per configuration with no confidence intervals. The targets are preference benchmarks rather than domain human labels, with no kappa or per-class error rates. Whether code, weights and data are released is not stated. Single-order numbers are not comparable across papers, since order alone shifts RewardBench by 5.6 points. The extraction's limits line gives the MT-Bench seed gain as 77.8 to 79.0 while its results give 79.5 with majority vote.

## See Also
- [[LLM-as-Judge Evaluation]] — extends (a judge trained without human labels)
- [[J1 Reinforcement-Learned Judge]] — alternative-to (reinforcement learning on synthetic pairs instead of rejection-sampled fine-tuning)
- [[PandaLM]] — alternative-to (judge trained on distilled GPT-3.5 labels)
- [[Prometheus 2 Evaluator Models]] — alternative-to (another trained evaluator model)
- [[LLM Judge Biases]] — related (position effect on judge accuracy)
