---
title: RL for Retrieval Policies
tags: [rag, foundations, llm, concept]
summary: "Modelling RAG as a sequential decision process — the five decision points and their reward signals, the three optimization patterns (online RL, per-subtask modules, Self-RAG), and why reward sparsity makes end-to-end RAG RL hard."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--01-llm-fundamentals--rl.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--rl.md
  - data/raw/papers/2026-11-06-chen-2025-improving-retrieval-augmented-generation-through.md
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

## Paper evidence: joint training of RAG modules, and alternatives to RL

All numbers are self-reported by the papers.

- **Multi-agent PPO over a RAG pipeline (MMOA-RAG, NeurIPS 2025).** A query rewriter, a document selector and a generator are trained together with MAPPO on one shared F1 reward, after an SFT warm start. Setup: every method uses Llama-3-8B-Instruct with a Contriever retriever, ten documents go to the selector, and the authors re-implemented the baselines. HotpotQA F1 was 48.29 against 46.49 for the best baseline; MAPPO added about 3 points over the same modules after SFT alone on multi-hop sets (HotpotQA 44.69 to 48.29) and around 2 on AmbigQA. Dropping any one agent from joint training lowered results. Untrained Llama-3-8B gained nothing from retrieved documents (HotpotQA F1 31.18 without RAG, 30.67 with); SFT on the RAG format lifted it to 44.49.
- **End-to-end RL over a graph store.** Graph-R1 trains the agent with GRPO; the ablation shows removing RL cost the most, which is covered in [[Graph-R1 Agentic GraphRAG]].
- **A straight-through gradient instead of RL.** CLaRa trains retrieval and generation jointly with a differentiable top-k and calls RL-based sampling unstable and inefficient; see [[Soft Context Compression for RAG (CLaRa and REFRAG)]]. REFRAG, in the same page, instead uses a GRPO-style policy to choose which compressed chunks to expand.
- **Tuning the LM and the retriever separately.** [[RA-DIT Dual Instruction Tuning]] updates the query encoder from the LM's preferences without online rollouts.

## Limits

- MMOA-RAG's baselines were re-implemented by its authors; its ablation labels are read from plot labels (the extraction notes the series assignment is inferred). The reported gains are 1 to 3 F1 points, from one run.
- The extraction notes the reference numbering for Contriever, BGE and E5 in the Table 7 caption differs from the main text, so the caption is not reliable for attribution.

## See Also
- [[Memory-Augmented Conversational RAG]] <!-- auto-linked -->
- [[Semantic Cache for RAG Agents]] <!-- auto-linked -->
- [[Reinforcement Learning Foundations]] — related (part of; RAG as a sequential decision process)
- [[Agentic RAG — Advanced Patterns]] — extends (Self-RAG vs CRAG mechanics)
- [[RLHF Pipeline]] — instance-of (WebGPT is structurally identical, with a browser as environment)
- [[Preference Optimization Algorithms]] — alternative-to (DPO as the offline optimizer at RAG scale)
- [[RAG Eval Gate Contract]] — related (component gates as the eval-side answer to proxy divergence)
- [[Online Eval Sampling]] — related (distribution shift, monitored in production)
- [[Graph-R1 Agentic GraphRAG]] — instance-of (end-to-end RL with a graph retriever)
- [[Soft Context Compression for RAG (CLaRa and REFRAG)]] — alternative-to (a differentiable top-k rather than RL for joint training)
- [[RA-DIT Dual Instruction Tuning]] — alternative-to (staged supervised tuning of LM and retriever)
- [[AgentIR Reasoning-Aware Retrieval]] — related (retriever trained on an agent's reasoning trace)
- [[DeepDive Knowledge-Graph Search Agent Training]] — instance-of (multi-turn RL for a search agent)
