---
title: RWKV Linear-Time Recurrent Language Model
tags: [foundations, concept]
summary: "RWKV replaces query-key attention with a channel-wise time-decay operator that runs in parallel for training and as a fixed-size-state recurrence for decoding; the paper reports parity with similar-sized transformers from 169M to 14B parameters."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-peng-2023-rwkv--2023-findings-emnlp-936.md
---

# RWKV Linear-Time Recurrent Language Model

Peng et al. ask whether an RNN formulation can match transformer quality at billions of parameters while keeping inference memory constant and still allowing transformer-style parallel training. In RWKV query-key attention gives way to a WKV operator with channel-wise time decay, plus token shift and receptance gating; training evaluates it in parallel over time and decoding runs it as a recurrence. The paper states inference space is O(d) per layer step and time O(Td), where a transformer needs O(T^2 + Td) space, and that the recurrent state is five D-vectors per layer. The paper pretrains six models, 169M to 14B parameters, on the Pile for a single epoch of 330B tokens and compares them at matched FLOPs with Pythia, OPT and BLOOM.

## Results (all self-reported)

- A linear log-log fit of loss against compute holds across 45 models and still fits when extrapolated one order of magnitude further.
- Average zero-shot accuracy over 12 tasks is on par with similar transformers, read from plots with no numeric table.
- After context finetuning to 8192 tokens, the 7B and 14B models reach lower Pile test loss as context grows.
- On Long Range Arena the average is 72.07, behind S4 (86.09) across five tasks, and Path-X fails.
- Enwik8 test bits per character 1.178 for RWKV-RNN2, against 1.137 for a 12-layer transformer (L = 12, d = 512, T = 1024).
- Generation time rises linearly in the token count for RWKV but quadratically for transformers (plots only; float32 on CPU and A100 80GB).
- With a chain-of-thought template RWKV-4-Raven-14B scores very poorly on MathQA (4.13% without one), and reordering the RTE prompt lifts its macro F1.

## Limits

- Linear attention funnels information through one vector, which may limit recall of fine detail over very long contexts; results depend more heavily on how the prompt is built than they do for transformers.
- Baselines saw similar but not identical token counts; comparisons are FLOP-matched and shown as plots. Inference benchmarks are float32 only, with no numeric table and quantization left to future work.
- Pretraining reports no seeds, variances, GPU hours or hardware, and the chat comparison does not state its decoding settings.
- Possible contradiction, flagged for review: the extraction notes that RWKV's log-log scaling conflicts with Kaplan et al.'s report that LSTMs do not follow transformer-style scaling; the two use different models and setups and this page does not resolve it.

## See Also

- [[Bi-Mamba Binarized State Space Model]] — related (another attention-free architecture)
- [[Efficient Attention Approximations]] — related
- [[Self-Attention Mechanism]] — prerequisite-for
- [[Scaling Laws for Precision]] — related
