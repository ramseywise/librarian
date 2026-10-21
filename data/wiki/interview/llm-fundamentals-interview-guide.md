---
title: LLM Fundamentals Interview Study Guide
tags: [llm, interview, reference, foundations]
summary: Exam-prep reference for LLM theory questions — transformer architecture, training pipeline, adaptation menu, inference economics, and failure modes.
updated: 2026-10-17
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--2-llm-fundamentals--interview-guide.md
  - data/raw/pdfs/2017-06-12-attention-is-all-you-need.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--paper-canon.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--llm-fundamentals.md
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

Durable content lives in [[LLM Inference Economics]] — the prefill/decode split, the four
levers (quantization, distillation, speculative decoding, output-length discipline), and
the serving metrics (TTFT, tokens/sec, p95).

Exam cue: the follow-up is almost always "so why is *output* the expensive part?" Answer
with the mechanism — decode is sequential because token *n+1* needs token *n* — not with
the price sheet.

## Failure Modes (Know Mechanisms, Not Vibes)

- **Hallucination** — the training objective rewards plausible continuation, not truth. Mitigations: grounding/RAG + citation checking.
- **Context rot** — O(n²) attention degrades on long contexts; compression/retrieval is the fix.
- **Reward hacking** — optimization pressure finds adversarial inputs that score high on the proxy metric but not the true objective.
- **Distribution shift** — fine-tuned models fail on out-of-distribution inputs; eval on held-out domains before deployment.

## Paper Canon (Read by Lineage, Not Date)

A short, closed list of ten architecture papers an interviewer can expect you to name, date,
and explain in two sentences. Read them in lineage order, where each answers what the
previous leaves open:

1. **Transformer (2017)** — the substrate: self-attention replaces sequential RNNs.
2. **BERT (2018) → GPT-1 (2018)** — the encoder/decoder fork. Know why decoder-only won for
   generation and where encoders still live (embeddings, rerankers).
3. **LoRA (2021) → PEFT survey (2023)** — adaptation without full fine-tuning; LoRA is the one
   you will be asked to explain.
4. **RAG (2020)** — the alternative to adaptation: change the context, not the weights. The
   fine-tune-vs-RAG question is the most-asked of the set.
5. **VAE (2013) → GAN (2014) → Latent Diffusion (2022)** — each fixes the last (blurry samples
   → unstable training → compute cost).
6. **ViT (2020)** — transformers past text; the bridge to multimodal.

The canon is architecture-heavy. An AI-engineering loop dwells more on what it skips:
alignment (InstructGPT, DPO, Constitutional AI), reasoning/agents (CoT, ReAct, Reflexion,
Tree of Thoughts), eval (RAGAS, ARES, TruthfulQA), and systems reality (Hidden Technical
Debt in ML Systems).

## See Also
- [[LLM Inference Economics]] — prerequisite-for (the durable cost mechanism this round examines)
- [[Prefix Caching]] — instance-of
- [[RAG Interview Study Guide]] — extends
- [[Direct Preference Optimization]] — instance-of
- [[RLHF Pipeline]] — prerequisite-for (the three stages, asked about directly)
- [[Bradley-Terry Preference Model]] — prerequisite-for (the pairwise objective under RLHF and DPO)
- [[Reward Hacking and Overoptimization]] — extends (the failure modes a follow-up question probes)
- [[Constitutional AI and RLAIF]] — extends (RLAIF as the AI-feedback variant)
- [[Preference Optimization Algorithms]] — extends (the algorithm-choice comparison)
- [[Reinforcement Learning Foundations]] — prerequisite-for (MDP, policy, actor-critic, exploration/exploitation)
- [[Multi-Agent Reinforcement Learning]] — extends (CTDE, QMIX, MADDPG as asked about directly)
- [[RL for Retrieval Policies]] — extends (RL applied to the retrieval decision points)
- [[Transformer Architecture]] — prerequisite-for
- [[Self-Attention Mechanism]] — prerequisite-for
- [[Neural Probabilistic Language Model]] — prerequisite-for
- [[Batch Normalization]] — prerequisite-for
