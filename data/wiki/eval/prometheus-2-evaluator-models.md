---
title: Prometheus 2 Evaluator Models
tags: [eval, llm, concept]
summary: "Prometheus 2 is an open evaluator model made by training one judge for direct 1-5 rubric scoring and another for pairwise ranking, then merging their weights; on FLASK its 8x7B version reached 0.555 Pearson with humans against 0.449 for the first Prometheus and 0.679 for GPT-4 (self-reported), and merging beat joint training."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-kim-2024-prometheus-2.md
---

# Prometheus 2 Evaluator Models

Kim et al. (arXiv 2405.01535, 2024) release open evaluator models built on Mistral-7B and
Mixtral-8x7B. A judge model is trained on synthetic feedback in two formats, **direct
assessment** (score one response 1-5 against a rubric, with written feedback first) and
**pairwise ranking** (choose A or B). The authors then combine the two with a linear merge of
the weights, theta_final = alpha x theta_direct + (1 - alpha) x theta_pairwise, so one model does both.
Training data are synthetic: 1,000 criteria and 20,000 instructions, 100,000 direct instances
and 200,000 pairwise instances, with the pairwise feedback written by GPT-4. A human check of
200 samples by 5 annotators rated coherence 99.5% and suitability 98.5%.

## Results (self-reported)

- **Direct assessment.** The four benchmarks were Vicuna Bench with 320 judgments, MT Bench with 320, FLASK with 2,000
  and Feedback Bench with 1,000, scored 1-5 against a reference and averaged over 3 runs. The
  Prometheus 2 models' Pearson correlation with humans, GPT-4 and Claude-3-Opus stayed above 0.5.
- **Against human scores on FLASK** (200 prompts, 12 rubrics, 2,000 responses): Prometheus-2-8x7B
  0.555, Prometheus-2-7B 0.545, Prometheus-13B 0.449, GPT-4-1106 0.679.
- **Against proprietary judges.** Measured against GPT-4-1106 on Vicuna Bench, the 8x7B model scored 0.685 and the 7B 0.666,
  against 0.492 for Prometheus-13B and 0.351 for Auto-J.
- **Pairwise accuracy** (single run, reference-free): 8x7B scored 85.52 on HHH Alignment (221
  pairs) against GPT-4's 90.95, 71.96 against 79.90 on MT Bench Human Judgment without ties
  (3,360 pairs) and 79.98 against 83.12 on Auto-J Eval without ties (1,392 pairs).
- **Merging against joint training** (Mixtral-8x7B): average direct Pearson 0.670 merged, 0.595
  joint and 0.625 direct-only; average pairwise accuracy 79.15, 75.29 and 75.36.
- **Not an ensembling effect.** On Mistral-7B, merging two direct-assessment models with
  different seeds gave 0.517 against 0.539 for a single model, while merging a direct and a
  pairwise model gave 0.624.
- **Reference answers.** Removing the reference lowered FLASK correlation with humans for every
  judge: 0.555 to 0.411 (8x7B), 0.545 to 0.425 (7B), 0.679 to 0.616 (GPT-4-1106).
- **Consistency.** Krippendorff's alpha across 3 samples at temperature 1.0 on Vicuna, MT Bench
  and FLASK was 0.6383, 0.6862 and 0.7874 for 8x7B against 0.7366, 0.8271 and 0.8355 for GPT-4;
  the authors say training on feedback data only slightly improved consistency.

## Limits

The checks are indirect, measuring how closely the models track humans, GPT-4 or Claude. Most references for
direct assessment are other LLM judges, with human scores only on FLASK and BiGGen Bench, where
the best figure is 0.555. The formats are fixed (1-5 Likert or A/B, no ties natively, no checklists). The
authors give no explanation of why merging works and did not retune the merge for 8x7B. There are
no confidence intervals and pairwise results are one run. Position, verbosity and self-preference
bias, non-English data, code or RAG tasks, and cost were not analysed. The highest-pairwise-accuracy claim covers only 8x7B; on HHH the 7B reached 74.66, below
PairRM (84.62) and UltraRM (83.71). Feedback Bench is in-domain, and the paper's tables disagree in places (7B merged
FLASK 0.659 in one table, 0.617 in another). Its comparison models are dated, ending at Claude-3-Opus.

## See Also
- [[FLASK Skill-Set Evaluation]] — prerequisite-for (the rubric benchmark it is tested on)
- [[LLM-as-Judge Evaluation]] — related
- [[LLM Judge Biases]] — related (bias analysis the paper leaves out)
- [[J1 Reinforcement-Learned Judge]] — related
- [[PandaLM]] — alternative-to (an open judge distilled from GPT-3.5 labels)
- [[Self-Taught Evaluators]] — alternative-to (a judge trained on synthetic pairs)
