---
title: SAT Self-Organizing Agent Teams
tags: [harness, pattern]
summary: SAT learns a bank of team strategies offline from a few dozen problems, then runs a frozen bank of up to ten multi-phase strategies across a three-model team and a judge; on math it scored 66.7% against 48.8% for the best member (self-reported), with compute only approximately matched and the cost never reported.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-pappu-2026-self-organizing-agent-teams-learn.md
---

# SAT Self-Organizing Agent Teams

Pappu et al. (Stanford, Together AI and Emory, arXiv 2609.22682, September 2026 preprint) build a team
of different LLMs whose collaboration protocols are learned, not hand-designed. A strategy bank is
mutated offline (six mutation rounds per problem, up to three candidates per round, with validation
probes) on a tiny training set, then frozen. At test time the team runs up to ten strategies, each
with several phases, and a judge call reads all the resulting certificates. The unlearned starting
protocol is independent solves, two debate rounds and a majority vote.

## Results (self-reported)

Setup: means over 3 seeds. The math and physics team is o3-mini, Claude Sonnet 4 and DeepSeek-V3, bank learned on 15 AIME-2024
problems, evaluated on unseen items from the AIME 2024, 2025 and 2026 sets, HMMT Feb 2026 and
TheoremQA-physics. The knowledge
and logic team is Gemini-2.5-Flash, Llama-4-Maverick and GPT-4.1; its bank was learned from 25 GPQA-Diamond
problems, tested on 100 GPQA, 100 MMLU-Pro and 75 BBEH items.

- **Math team.** 66.7% average against 48.8% for the best member, 55.4% for self-consistency at
  K=10, 58.7% for linearization (the strongest member plays every role serially), 57.3% for
  Mixture of Agents, 52.7% for debate and 59.0% for a per-problem routing oracle. On AIME 2026, 71.2%
  against an oracle of 57.8%. The learned bank beat the unlearned start: 66.7 against 54.1 average on math.
- **Knowledge team.** 72.8% against an oracle of 79.6% and a best member of 65.9%; pool coverage
  87.9%, so selecting the right answer is the bottleneck. Linearization scored 72.1.
- **Heterogeneity.** Three copies of o3-mini running the same frozen strategies scored 56.0% on math
  against 66.7%; on knowledge and logic the gap was 70.9 against 72.8.
- **Demonstrability.** Ten small judge models, each shown one correct and one wrong certificate,
  gave a per-benchmark score from 0.423 to 0.687 that correlated with the team's gain over the
  best member (Spearman 0.90 with p=0.005, over 8 benchmarks); it is correlational and measured after the fact.

## Limits

- Compute is matched only by candidate count and "approximately" the team budget; no token, dollar or
  call counts are reported, and the offline learning cost is excluded. The extraction notes SAT's
  own run is likely much more than ten single samples. Self-consistency and the single-model
  baselines do not get the three-model ensemble.
- The gap to linearization on HMMT26 is zero (39.4 each), 8.0 points on average for math and 0.7 on
  knowledge and logic; the authors say the control cannot separate interaction from heterogeneity.
- Small test sets (AIME sets near 30 problems), three seeds, no confidence intervals, two rosters of
  mid-tier models chosen to leave headroom, and tiny training sets. The routing oracle uses one
  answer per member, a weaker bar than best-of-K coverage. Coverage-versus-accuracy shows richer
  generation does not guarantee correct selection.
- Extraction oddity: the discussion of the physics benchmark lists SAT 77.2 against linearization
  68.4 under a heading that says the gap is small.

## See Also
- [[Harness Orchestration]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Conductor Learned Orchestration]] — alternative-to (another learned way to compose a team)
- [[Aegean Stability-Horizon Consensus]] — related (answer selection among agents)
