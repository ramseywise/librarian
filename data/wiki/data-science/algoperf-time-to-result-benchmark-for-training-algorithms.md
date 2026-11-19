---
title: "AlgoPerf: Time-to-Result Benchmark for Training Algorithms"
tags: [data-science, comparison]
summary: "AlgoPerf scores training algorithms by wall-clock time to reach a fixed validation and test target on 8 workloads, with tuning counted inside the protocol; Dahl et al. report that its baselines rank NadamW with tuned beta1 first among the strict-budget runs."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-dahl-2023-benchmarking-neural-network-training-algorithms.md
---

# AlgoPerf: Time-to-Result Benchmark for Training Algorithms

Dahl, Schneider, Nado and colleagues want a reliable way to compare training algorithms: update rules, tuning protocols, schedules and data selection. They propose fixed hardware, several fixed workloads, randomised held-out variants and explicit tuning accounting, to deal with three problems: deciding when training is finished, sensitivity to the workload, and fair tuning. Every number below is the benchmark authors' own measurement of their baselines in their own setup, so it is self-reported.

## How it works

- A **workload** pairs a dataset (with preprocessing), a model and a loss with a target on an evaluation metric. **Time-to-result** is the wall-clock time until a run first hits both the validation and test targets; it is infinite when the runtime cap is passed.
- A submission supplies four functions, named init_optimizer_state, update_params, data_selection and get_batch_size, and may also add a hyperparameter search space. Timing covers 8 fixed workloads, while 8 held-out variants of them act as a penalty.
- To set targets, the authors tuned four optimizers on each workload using 200 quasirandom trials, then reran the winning configuration 20 times.
- Under the **external tuning ruleset**, a submission gets 20 quasirandom trials drawn from a workload-agnostic search space (or from an **OptList**, a fixed list of 20 points), repeated across 5 studies; the median time per workload is scored. The **self-tuning ruleset** has no external tuning and gives 3 times the runtime budget.
- A **performance profile** records, per workload, the ratio of a submission's time to the fastest one's, and the fraction of workloads within each ratio tau. Integrating that curve for tau from 1 to 4 gives a score between 0 and 1. The score therefore depends on which baselines are in the profile and is relative.

## Baseline results

Setup for this section: 8 fixed workloads, external tuning (20 trials, 5 studies), timing on the official system, held-out criterion ignored.

- NadamW with tuned beta1 scored 0.849960 and AdamW 0.600141. NadamW hit the target on 7 of the 8 workloads (not ImageNet ResNet-50), and the authors call it the provisional state of the art. Fixing beta1 at 0.9 (Table 12 search spaces) dropped NadamW to 0.599691, level with AdamW at 0.596985 in that comparison (all self-reported).
- Distributed Shampoo had the top step-based score, 0.854210, but each step took 1.5 to 2 times longer, so no runtime score was given. It ran the same number of steps as the others, on TPU, since the official system could not run it on every workload.
- Heavy Ball and Nesterov, given the standard box search spaces, reached no target and scored 0.0; given OptLists of 20 points they scored 0.230504 and 0.233373 respectively.
- LAMB reached the target on just 2 workloads, yet was 7% faster than the rest on the WMT Transformer; its score was 0.248619.
- On GPUs the authors' Adafactor needed 10 to 20% more time per step than AdamW. SAM and Distributed Shampoo needed 1.5 to 2 times as much.

## Section 2 experiments on tuning and workloads

- On CIFAR-10 with a Wide ResNet 28-10 (cosine decay, learning rate swept per optimizer), changing the last stride to 1x1 from 2x2 pushed Nesterov's test error up, 0.0376 to 0.0726, while AdamW barely moved (0.0407, then 0.0420). Warmup repaired Nesterov (0.0380 against 0.0378). Initialisation's largest Hessian eigenvalue rose, 32 to 1052, under the stride change.
- For a WMT De->En Transformer, with 100 random-search trials for each optimizer and architecture pair, swapping Pre-LN for Post-LN lowered BLEU by 2.974 for Nesterov, by 0.5208 for AdamW and by 0.2569 for Shampoo.
- Eight workloads, 100 quasirandom settings per optimizer, one run per setting: no one shared setting stayed within 16.9% of per-workload tuning everywhere. The best worst-case gap, Phi, came to 0.169197 with NadamW and 0.195425 with AdamW.
- ImageNet ResNet-50 with AdamW, same 100 points: step budgets of 186,666 and 233,333 picked identical best hyperparameters and gave nearly equal validation error. The authors conclude that results tuned toward different goals are unfair to compare.
- Re-running the best target-setting configuration under 20 seeds gave wide LibriSpeech spread: the spread in validation WER reached 36.77% of the minimum for the Conformer and 51.25% for DeepSpeech.
- Held-out variants that moved NadamW's best hyperparameters were hard to find. Among 60 random OGBG GNN variants (Nesterov, 100 points each), around 30% trained to within 10% of the base target, and almost all of those kept the base optimum; the authors dropped the approach.

Over 8 fixed plus 8 held-out workloads at 5 studies of 20 trials, scoring one submission under external tuning takes about 1161 machine-hours, while tuning it fully would take roughly 23,223 hours (provisional, probably a slight overestimate).

## Limits

- The authors admit that setting targets involved hand trial and error over search spaces, used 200 trials (not a legal submission), and yielded targets that are mostly not state-of-the-art error rates.
- Only three hand-designed variants exist per workload; they may not differ much from each other and often repeat kinds of change, such as swapping an activation.
- The hardware is a single class (8x V100) with one batch-size regime. Baselines mostly ran on TPUs and were extrapolated from a fifth of the steps on GPUs.
- The failures of Heavy Ball and Nesterov reflect the box search spaces rather than the update rules. Shampoo got a step-budget advantage, and the authors' Adafactor ran slower than expected.
- Criteo, fastMRI and OGBG are bound by the data pipeline on the official system, which favours costlier optimizers.
- Baselines skip the held-out criterion, and scores are relative to the set of baselines.
- The API rules out model parallelism and K-FAC-style architectural access, allows only random search for external tuning, and supports JAX and PyTorch; no language-modelling, video or image-generation workload is included.
- The Section 2 experiments are small: Phi rests on a single run per setting, and the Wide ResNet and extra-batch-norm runs are one-sweep demonstrations with little detail. Before submissions open, the DeepSpeech validation target was expected to move from 0.1162 down to 0.111825.
- The scoring cost is a barrier, and the benchmark requires all workloads.
- The extraction gives AdamW two scores, 0.600141 in the main comparison and 0.596985 beside fixed-beta1 NadamW, without explaining the difference.
- The paper's narrow-versus-broad AdamW search-space comparison is left off this page: the extraction says its cell directions were mapped by hand from a flattened table and need rechecking.
- It is a preprint.

## See Also
- [[Adam, AdamW and Decoupled Weight Decay]] — prerequisite-for
- [[Hyperparameter Search Budgets and Selection Optimism]] — related
