---
title: RL for Retrieval Policies
tags: [rag, foundations, llm, concept]
summary: "Modelling RAG as a sequential decision process — the five decision points and their reward signals, the three optimization patterns (online RL, per-subtask modules, Self-RAG), and why reward sparsity makes end-to-end RAG RL hard."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--01-llm-fundamentals--rl.md
---

# RL for Retrieval Policies

RAG contains several decisions that are usually hardcoded: **when to retrieve** (or skip),
**how to rewrite the query**, **which evidence to use**, and **when to stop and answer**.
Framing these as a policy makes them learnable, and optimizable against **end-to-end task
quality** rather than intermediate retrieval metrics.

That last distinction is the motivation. A pipeline tuned to maximize recall@k is
optimizing a proxy; the thing you want is answer quality, and the two come apart
routinely.

## Decision points and reward signals

| Sub-task | Action space | Reward signal |
|---|---|---|
| Query rewriting | Rewritten query variants | Retrieval quality (NDCG, recall@k) |
| Evidence selection | Rank/rerank retrieved passages | Answer F1, faithfulness |
| Continue-or-stop | Stop / continue (multi-hop) | Accuracy **minus latency cost** |
| Tool use | Search / click / synthesize | Human preference or task completion |
| End-to-end | Full pipeline | QA F1 or human evaluation |

The continue-or-stop row is the one that most needs a learned policy rather than a
constant: its reward explicitly trades accuracy against latency, and the right stopping
point is query-dependent in a way a fixed hop limit cannot express.

## Pattern 1 — Online RL over retrieval and tool actions

The model acts in a retrieval or browsing environment via discrete actions, trained by
behavior cloning from demonstrations and then optimized against a reward model built from
human preferences.

**WebGPT** (OpenAI, 2021) is the canonical instance: a model using a web browser through
search, click, and quote actions, with a reward model trained on human comparisons of
browsing-augmented versus direct answers. The loop is generate action sequence → execute
in browser → collect preference over the final answer → update policy.

Structurally this **is** the [[RLHF Pipeline]] — the only changes are that the "response"
is an action sequence rather than text, and the environment is a browser rather than a
single generation step. Recognizing that equivalence is useful because every failure mode
in [[Reward Hacking and Overoptimization]] transfers directly.

## Pattern 2 — An RL module for one sub-task

Train a specialized module for a single decision (query rewriting, say), optimized on
whether the rewrite improved final quality — **not** supervised on what an ideal rewrite
looks like.

**Pro:** decomposes the problem; each module has a clear reward; far simpler to train and
debug than full-pipeline RL. **Con:** sub-optimal when sub-task reward and end-task
quality diverge — and they do: *improving query recall does not reliably improve answer
quality.*

That caveat is the same failure the component-gate approach in
[[RAG Eval Gate Contract]] is designed to surface, approached from the training side
rather than the evaluation side.

## Pattern 3 — Self-RAG, a policy without online rollouts

Self-RAG (Asai et al., 2023) trains the model to retrieve on demand and emit **reflection
tokens** — `[Retrieve]`, `[IsREL]`, `[IsSUP]`, `[IsUSE]` — that critique evidence and
generation quality at inference time.

It is not classic RL: no online rollouts, no reward model. But it **operationalizes a
policy over retrieval decisions**, learned at training time and executed at inference,
which buys inference-time controllability — retrieval off for confident factual queries,
on for uncertain claims — and substantially improves groundedness and citation accuracy
over fixed-retrieval RAG. Mechanics and the CRAG contrast are in
[[Agentic RAG — Advanced Patterns]].

## RL versus DPO for RAG

PPO-style RLHF needs **online rollouts**, and at RAG scale every rollout involves a
retrieval call — expensive and slow. DPO is increasingly the optimizer of choice instead:
collect (prompt, good-retrieval-outcome, bad-retrieval-outcome) triples and train against
the offline objective. See [[Preference Optimization Algorithms]].

## Five challenges

- **Reward sparsity** — end-task reward is a single signal at the end of a multi-step
  trajectory; intermediate retrieval actions get no direct reward. Partial mitigation is
  reward shaping with intermediate retrieval scores, which reintroduces the Pattern 2
  proxy risk.
- **Scalability** — every training step requires retrieval. Offline methods (Self-RAG, DPO
  over retrieval decisions) are faster but give up online adaptation.
- **Evaluation difficulty** — RAG quality is multi-dimensional (retrieval + faithfulness +
  answer quality + latency); a single reward scalar is an imperfect proxy for all four.
- **Reward hacking** — the model learns to retrieve passages that trigger high reward-model
  scores without genuine grounding.
- **Distribution shift** — corpus and query distributions move; policies trained on
  historical data degrade, which is the training-time face of the drift monitored in
  [[Online Eval Sampling]].

## See Also
- [[Memory-Augmented Conversational RAG]] <!-- auto-linked -->
- [[Semantic Cache for RAG Agents]] <!-- auto-linked -->
- [[Reinforcement Learning Foundations]] — part-of (RAG as a sequential decision process)
- [[Agentic RAG — Advanced Patterns]] — extends (Self-RAG vs CRAG mechanics)
- [[RLHF Pipeline]] — instance-of (WebGPT is structurally identical, with a browser as environment)
- [[Preference Optimization Algorithms]] — alternative-to (DPO as the offline optimizer at RAG scale)
- [[RAG Eval Gate Contract]] — complements (component gates as the eval-side answer to proxy divergence)
- [[Online Eval Sampling]] — complements (distribution shift, monitored in production)
