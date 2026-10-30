---
title: LLM Fundamentals Interview Study Guide
tags: [llm, interview, reference, foundations]
summary: Exam-prep reference for LLM theory questions — transformer architecture, training pipeline, adaptation menu, inference economics, and failure modes.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--2-llm-fundamentals--interview-guide.md
  - data/raw/pdfs/2017-06-12-attention-is-all-you-need.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--paper-canon.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--llm-fundamentals.md
  - data/raw/repos/sisyphus/interviewing--guides--2-llm-fundamentals--interview-guide.md
  - data/raw/repos/sisyphus/interviewing--guides--2-llm-fundamentals--00-overview.md
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

## Post-training follow-ups (answer sketches)

*Provisional:* condensed from the reference answers to the chapter questions in *AI Agents in Depth* (Li), which the book itself flags as AI-drafted with light human review. Treat these as answer shapes to check, not settled claims.

- **Fine-tuning broke general tool calling.** Mix roughly a fifth general data back in, stop SFT once the
  format is stable, keep LoRA rank small (8–32) with a KL penalty under RL, one adapter per task, and
  regression-test general benchmarks.
- **Train it in or put it in context?** Facts go to retrieval, language-expressible principles to
  prompts/Skills, hard constraints to code. Train only what symbols cannot carry (tone, implicit policy,
  perception), and only once the approach is proven at volume. Hard rules never rest on weights alone.
- **Why is distilling an agentic model harder than a chat model?** Chat distils an input→output style;
  reasoning needs full traces with wrong answers filtered; agentic needs a live environment, must not
  learn the environment-returned tokens, and offline data suffers learner–sampler mismatch, hence
  on-policy distillation.
- **Credit assignment over a long trajectory.** Outcome reward plus per-action signals from
  deterministic rules (penalise invalid tool calls) and process rewards where steps are judgeable; this
  restores variance in all-pass or all-fail groups.
- **Lucky success vs correct-process failure.** Lucky success is the dangerous one: shortcuts such as
  editing the tests inflate success and seed [[Reward Hacking and Overoptimization|reward hacking]].
  Reward outcomes, penalise bad actions, keep process constraints sparse so exploration survives.
- **Weak supervising strong.** Yes, as a *verifier* not a demonstrator: verification is easier than
  generation, and SFT on a weak demonstrator caps you at its level.
- **When SFT stops and RL starts.** Tool calls parse and execute reliably enough to compute rewards,
  more demonstrations stop improving out-of-distribution performance, and validation starts to slip.
  Over-trained SFT collapses onto its distribution and RL cannot recover it.
- **Training on an agent benchmark.** Reuse environments, not questions, and hold out whole templates
  or domains — see [[Parameterised Benchmark Instances]].
- **Reward hacking against simulated users or search.** Sycophancy, over-promising, facts the simulator
  will not check, verbose judge-pleasing answers. Anchor rewards to verifiable state, calibrate the
  simulator against production traces, gate releases on online metrics only.
- **Long-tail rollouts idle the cluster.** Decouple rollout from training and pipeline them
  asynchronously ([[Training-Agent Disaggregation]]), batch continuously, shape overlong rewards to
  shrink the tail.
- **Per-user LoRA instead of a memory store?** Usually no: LoRA memorises facts poorly and cannot reason
  multi-hop over them; changing or auditable facts belong in retrieval.

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
- [[Parameterised Benchmark Instances]] — extends (train on environments, not questions)
