---
title: Pythia Training Suite and Memorization
tags: [llm, pretraining-and-data, concept]
summary: "Biderman et al. (2023) release Pythia, 16 models from 70M to 12B trained on the Pile or a deduplicated Pile in the same data order with 154 public checkpoints each, and use it for three case studies on memorization, term frequency and gender bias (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-biderman-2023-pythia.md
  - data/raw/papers/2026-11-07-black-2022-gpt-neox-20b.md
---

# Pythia Training Suite and Memorization

Pythia is a controlled suite for studying how language models change over training and with scale. It has eight decoder-only sizes from 70M to 12B parameters, each trained twice with GPT-NeoX: once on the Pile and once on a near-deduplicated Pile. All 16 models see the same data in the same order, about 300B tokens at batch 1024 x 2048 tokens, and the authors release tools to reconstruct the exact dataloaders. Checkpoints are saved at initialisation, at several early steps spaced logarithmically, and then once per 1,000 steps. That gives 154 per model (self-reported); the paper's comparison with other suites uses the model that has the fewest checkpoints in each.

## Design choices (self-reported)

- **Deduplication.** The deduplicated Pile holds about 207B tokens where the original holds 300B, so the deduplicated models pass over it about 1.5 times. Near-deduplication used MinHashLSH with a 0.87 threshold. Language-modelling quality showed no clear gain from deduplicating, and the repeated pass did no visible harm (8 benchmarks via the LM Evaluation Harness, final checkpoints and the 93k-step checkpoints, one run per size). The GPT-NeoX-20B paper, a source for this page, reports a similar finding at 20B: no validation-loss drop at the epoch boundary and no gain seen from avoiding deduplication, which the NeoX authors say contradicts Lee et al. but is hard to dismiss.
- **Parallel attention and MLP.** This design matched an OPT of equal parameters and tokens at every scale on 8 benchmarks, which goes against the earlier claim that it hurts below 6B.
- **Large batches.** Batches 4x to 8x the usual size caused no convergence trouble for models under 1B, and against GPT-3's batch sizes gave up to 10x faster wall-clock training on small models.
- **Cost.** Training the 12B model cost 72,300 A100-hours on 256 A100 40GB, and the paper's whole compute was 544,280 A100-hours. The authors put the price of running the suite with 25 random seeds at about 10 million USD, their reason for training one copy per size.

## Case studies

**Memorization as a Poisson process.** A string counts as (k, l)-memorized when a k-token training prefix leads the model to reproduce the following l training tokens. The authors use (32, 32) on the first 64 tokens of every training sequence, on the 12B model (Pile and deduplicated, batch of 512 sequences). The hypothesis that later data is memorized more was refuted: memorized sequences arise at a constant Poisson rate over the course of training (judged with a Q-Q plot), so data order does not affect memorization.

**Term frequency.** For models of 2.8B parameters or more, task accuracy correlates with the frequency of task terms in the data, starting after 65,000 steps (deduplicated models; arithmetic and TriviaQA with 0, 4 and 16 shots).

**Counterfactual gender bias.** Replacing masculine pronouns with feminine ones during the final 7% or 21% of training lowers measured bias on CrowS-Pairs and WinoBias, with only a marginal LAMBADA change. Setup: deduplicated 70M, 410M, 1.4B and 6.9B models; the 7% edit covers the last 21B tokens, and the 21% edit (63B tokens) was run on the 1.4B model only.

## Limits

- One training run per size, so there is no seed variance.
- The (32, 32) setting was picked largely arbitrarily, and testing any other pair would cost as much as retraining all 16 models.
- The gender-bias benchmarks were not designed for autoregressive models, and the authors leave CrowS-Pairs reliability as an open question.
- English only; a multilingual corpus was rejected.
- The suite was retrained (v0 to v1) and the models renamed; results are for v1 only.
- Under this tokenizer the Pile is 334B tokens, so standard training runs leave some of it unseen.
- GPT-NeoX-20B ran no deduplication and tested no downstream effect of it, used hyperparameters interpolated from GPT-3 that the authors say are almost certainly no longer optimal, and was a single run.

## See Also

- [[Open Pretrained Model Reports Comparison]] — related (GPT-NeoX-20B, OPT, BLOOM and OLMo setups)
- [[GPT-3 and Few-Shot In-Context Learning]] — related (the token budget Pythia matches)
- [[Transformer Architecture]] — prerequisite-for
- [[Extracting Training Data from Language Models]] — related (verbatim extraction attacks on GPT-2)
- [[Deduplicating Training Data (ExactSubstr and NearDup)]] — related (dedup lowers memorised output)
