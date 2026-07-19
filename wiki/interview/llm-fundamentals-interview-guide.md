---
title: LLM Fundamentals Interview Study Guide
tags: [llm, interview, reference, foundations]
summary: Exam-prep reference for LLM theory questions — transformer architecture, training pipeline, adaptation menu, inference economics, and failure modes.
updated: 2026-07-19
sources:
  - raw/repos/learn-ai-engineering/interviewing--guides--2-llm-fundamentals--interview-guide.md
  - raw/pdfs/attention-is-all-you-need.md
---

# LLM Fundamentals Interview Study Guide

The breadth/theory round. Target: explain each concept in 60 seconds with one level of depth in reserve (the follow-up is where the signal is).

## Architecture Core

- **Tokenization** — BPE/SentencePiece subwords. Token ≠ word matters for cost, truncation, multilingual inflation, arithmetic weirdness. Hands-on: `nn-zero-to-hero/nanogpt` builds this from scratch.
- **Attention** — `softmax(QKᵀ/√d)V`. Self-attention = every token attends to every other (O(n²) — why long context is expensive and "context rot" exists). Multi-head = parallel subspace views. Positional info: learned, RoPE, ALiBi.
- **Transformer block** — attention + MLP + residuals + layer norm. Decoder-only for GPT-family (causal mask); encoder-only for BERT (bidirectional); encoder-decoder for translation.
- **KV cache** — decode-time cache of past keys/values; the mechanism under prefix caching. See [[Prefix Caching]].
- **Sampling** — temperature, top-p/top-k. Temperature 0 is still not fully deterministic in production (batching, floating point, MoE routing).

## Training Pipeline (Tell It as a Story)

1. **Pretraining** — next-token prediction at scale. Scaling laws: params/data/compute trade-off. LLaMA's insight: train smaller models longer.
2. **SFT** — instruction-following on curated demonstrations.
3. **Preference alignment**:
   - **RLHF** — reward model from human preference pairs + PPO. Failure mode by name: reward hacking. PPO's role: clipped policy updates for stability.
   - **DPO** — skips the reward model, optimizes preference pairs directly. More stable, cheaper, the common industry default now.
   - **Constitutional AI / RLAIF** — AI feedback guided by principles; critique-and-revise loop.
4. **RL fundamentals** — MDP: agent/environment/state/action/reward/policy. Exploration vs exploitation. Value-based (DQN) vs policy-gradient (PPO) vs actor-critic. MARL (CTDE, QMIX, MADDPG) exists but is not what production LLM stacks use.

## Adaptation Menu (RAG vs Fine-Tuning Ladder)

Prompting → few-shot → RAG → **PEFT/LoRA** (low-rank adapters; QLoRA = quantized base) → full fine-tune.

Decision axes: knowledge freshness (RAG), behavior/format/style (fine-tune), data volume, budget, provenance requirements. They compose — a fine-tuned model inside a RAG system is common. API-only models: no DPO/weights access — preference data goes into prompts/evals instead.

## Inference Economics

- **Prefill** — prompt processing, parallel, cheap/token
- **Decode** — output generation, sequential, expensive/token
- Why output-length discipline and streaming matter
- Quantization (8/4-bit) trades quality for memory/latency
- Distillation for the 80% of traffic a small model can serve
- Speculative decoding as a latency trick
- Serving metrics: TTFT, tokens/sec, p95

## Failure Modes (Know Mechanisms, Not Vibes)

- **Hallucination** — the training objective rewards plausible continuation, not truth. Mitigations: grounding/RAG + citation checking.
- **Context rot** — O(n²) attention degrades on long contexts; compression/retrieval is the fix.
- **Reward hacking** — optimization pressure finds adversarial inputs that score high on the proxy metric but not the true objective.
- **Distribution shift** — fine-tuned models fail on out-of-distribution inputs; eval on held-out domains before deployment.

## See Also
- [[Prefix Caching]] — instance-of
- [[RAG Interview Study Guide]] — extends
- [[Direct Preference Optimization]] — instance-of
