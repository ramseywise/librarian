---
title: Reasoning-Trace Disagreement States
tags: [graph, concept]
summary: "Wawer and Chudziak propose routing multi-agent output by four disagreement states (similar or different reasoning crossed with agreeing or split decisions) instead of a vote; a 600-item check found human disagreement ordered as predicted, but the routing policy itself was never run (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wawer-2026-consensus-strategically-insufficient.md
---

# Reasoning-Trace Disagreement States

Wawer and Chudziak (arXiv 2606.04223, June 2026, preprint). A position paper with a small empirical check. Its argument: majority voting, debate and consensus each regard disagreement as a flaw to be removed, which the authors call insufficient for value-laden tasks such as content moderation, where disagreement can reflect real normative uncertainty.

## Mechanism

Each of n agents returns four things: a confidence, a value profile, a binary decision and a reasoning trace. Mean pairwise similarity of the traces is compared with a threshold, and the share of the top decision with another threshold; both are described as policy parameters, not semantic boundaries. This gives four states with default routing:

- convergent agreement (similar reasoning, same decision): act automatically;
- divergent agreement (different reasoning, same decision): act and attach an explanation;
- divergent disagreement (different reasoning, split decision): seek more context;
- convergent disagreement (similar reasoning, split decision): escalate to a human.

The authors interpret convergent disagreement as values weighted differently over one shared account of the case, so pushing toward consensus in that state could hide a conflict, and divergent disagreement as ambiguity. This reading is interpretive and untested. Domain rules (high risk, legal requirement) can override the state defaults.

## Results (self-reported)

- Setup: five agents from one base model, differing only in system prompt (legal-framework, free-expression, community-norms, context-sensitive and harm-focused), on 600 items from the Measuring Hate Speech corpus, stratified by how much human annotators disagreed; similarity is the cosine between embedded traces.
- Mean human disagreement by state: divergent agreement 0.351 (n=118), convergent agreement 0.638 (n=24), divergent disagreement 0.751 (n=382), convergent disagreement 0.782 (n=76). The two disagreement states separate from the two agreement states with Cohen's d = 0.80.
- Predicting high human disagreement: state-based flagging F1 0.548 against 0.503 for a divergence-only baseline and 0.401 random, with precision 0.401 against a random baseline of 0.333. The authors say the ordering and gap, not the F1 numbers, carry the argument.
- The extraction notes the states are very unevenly populated (382 of 600 items in one state, 24 in another), and the 0.782 against 0.751 difference has no reported test.

## Limits

- The authors concede prompt-based perspectives may underrepresent real agent heterogeneity, embedding similarity is a coarse proxy for equivalent reasoning, the rules are hand-designed, and the check covers one domain and one corpus; they call it a sanity check, not a benchmark of the routing policy.
- The extraction notes the policy is never run end to end, outcomes are not compared with majority vote or debate, human disagreement is the only ground truth, the base model and both thresholds are not reported, and agents are clones of one model so correlated error is not addressed. The claim is scoped to value-laden tasks, not factual ones.

## See Also
- [[Multi-Agent Debate Failure Modes]] — related
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Self-MoA Single-Model Aggregation]] — alternative-to (vote-style aggregation)
