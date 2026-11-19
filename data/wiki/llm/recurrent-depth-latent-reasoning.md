---
title: Recurrent-Depth Latent Reasoning (Huginn)
tags: [llm, reasoning-and-planning, concept]
summary: "Geiping et al. train a 3.5B transformer with a weight-shared recurrent block iterated a random number of times, so extra test-time iterations in latent space raise reasoning scores with no chain-of-thought data or longer context."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-geiping-2025-scaling-up-test-time-compute.md
---

# Recurrent-Depth Latent Reasoning (Huginn)

Geiping et al. test whether a model built around a recurrent block with shared weights, trained on randomly drawn iteration counts, gets better at reasoning when it is run for more latent iterations at inference. Results are the authors' own (self-reported), from a single run.

## Architecture and training

- A decoder-only transformer in three parts: a 2-layer prelude P embeds the input, a 4-layer recurrent core R is iterated r times, and a 2-layer coda C produces the output. Starting from a random state s0 drawn from a Gaussian, the core repeatedly maps the pair (embedded input e = P(x), previous state) to a new state, so the embedding is re-injected at every step, and the coda reads the final state s_r.
- Trained once: 3.5B parameters, about 795-800B tokens, 4096 AMD MI250X GPUs on Frontier (52-64 TFLOP/s per GPU, 41%-51% achievable-FLOP utilisation).
- r is sampled per micro-batch (locked-step sampling, one depth synchronised across workers) as r ~ Poisson(e^tau) + 1 with tau log-normal around a mean of 32 plus 1. Gradients pass through only the last 8 iterations.
- Stability took three tries. Run one (parameter-free norms, no embedding scale, a simple adapter, learning rate 4e-4) collapsed. Run two used pre-norm, and the model learned to ignore its state: perplexity was identical whether r was 1 or 32. Run three, with sandwich norm and learning rate 4e-5, worked.

## Results

Evaluated at r from 1 to 64.

- Scores keep climbing as test-time iterations increase, up to a compute load matching a fixed-depth transformer of 50B parameters.
- GSM8K with chain-of-thought prompting (8-shot, chat template, system prompt) scored 0.00/0.00 at r=1 and 34.80/42.08 at r=32, for the 0.8T-token model. At 180B tokens the recurrent model was about 5 times better than a fixed-depth twin trained identically on GSM8K.
- ARC-C: 38.23 at r=32 against 23.72 for an early checkpoint at r=1 and 24.06 for the final model at r=1. At r=1 the model barely improves between the 180B and 800B token checkpoints, so the later gains show up only with more recurrence.
- With no system prompt, r=32 scores GSM8K 28.05/28.20 and Minerva MATH 12.58; among the compared models only OLMo-2-1124-7B does better in maths (GSM8K 66.72/66.79, MATH 19.08). Code at r=32: MBPP 24.80, HumanEval pass@1 23.17, above general-purpose open models but below StarCoder2. On zero-shot lm-eval tasks it sits near OLMo-7B, ahead of Pythia and behind the later OLMo models.
- The useful number of iterations depends on the prompt: ARC-C plateaus near 8-12 with no examples, near 20 with one example and near 32 with 25-50 examples.
- An exponential moving average of the last 75 checkpoints improved GSM8K at r=64.
- Giving OpenBookQA a relevant fact lifted Huginn from 38.2 to 49.2 (OLMo-2 open-book 53.4).
- Adding several single-digit operands improves with recurrence; multi-digit operands need over 16 iterations, and sums of 4-5 operands were rarely solved.

## Features shown zero-shot

- Per-token adaptive compute by KL-based early exit (threshold 5e-4) did not significantly hurt MT-Bench; the exit step differs by topic (moral scenarios take about 3.5 more steps than high school mathematics) and continuous chain of thought cut mean steps by 1-2.
- KV-cache sharing with budget 4 did not reduce the MT-Bench score.
- Self-speculative decoding is shown qualitatively; the extraction gives no number for it.
- Latent-space analysis covers convergence, orbits, sliders and path independence (similar behaviour from different random s0).

## Limits

- A proof of concept: a single large run with no seeds; the data mixture is neither tested nor ablated; the learning rate was never cooled down and training ran just 47000 steps.
- At 800B tokens it trails industrial models and most lm-eval results of later OLMo models.
- It is not compared with reasoning models trained on chain of thought; the one matched baseline is a non-recurrent twin trained for 180B tokens.
- The model holds fewer memorised facts, so closed-book OpenBookQA is weaker than the setting where a relevant fact is supplied.
- Latent reasoning is less inspectable than verbalised chain of thought (an oversight concern raised in Appendix A).
- Self-speculative decoding and continuous chain of thought are shown only qualitatively or on MT-Bench.
- The authors leave post-training, reinforcement learning, and combination with mixture-of-experts or linear attention to future work.

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Coconut Continuous Latent Reasoning]] — related (finetunes fixed-depth models for latent reasoning; this work pretrains a recurrent model from scratch)
- [[s1 Budget Forcing]] — related
- [[Inverse Scaling in Test-Time Compute]] — related
