---
title: NatureBench
tags: [eval, reference]
summary: "A benchmark of 90 containerised tasks built from Nature-family papers with the source method withheld, scored by the gap to the published result; the top agent matched it on 47.8% of tasks, and successes were mostly recast as generic prediction or engineering problems (self-reported, one run per agent)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wang-2026-naturebench.md
---

# NatureBench

NatureBench (Wang et al., arXiv 2606.24530, 2026) asks whether coding agents can reach the published state of the art of Nature-family papers. Its construction pipeline, NatureGym, turns a paper into a containerised task with the source method withheld. The authors extend PaperBench from understanding and coding toward discovery, and PostTrainBench from engineering toward science.

## Scoring

Each task has one or more instances (333 in total across 90 tasks). The metric is a SOTA-normalised gap, the direction-adjusted difference between the agent's metric and the published one divided by the published value, averaged over instances; an instance with nothing valid scores -1.0. An evaluator on the host gives the agent exact scores, and afterwards a Claude Sonnet 4.6 judge marks runs it finds to be shortcuts. The paper reports Surpass (gap above 0.1) and Match (gap at or above 0) rates, plus medians, because the mean has heavy negative tails.

## Results (self-reported)

Setup: 90 tasks, 12 agent configurations (Claude Code with nine models, Codex CLI with two, Gemini CLI with one), web search off, 4 hours and one GPU per task, default reasoning effort, one run per agent per task.

- Claude Opus 4.7 in Claude Code surpassed the published result on 17.8% of tasks and matched it on 47.8%. The next Surpass rates were 15.6% (two agents) and 14.4% (GPT-5.5); MiniMax-M2.7 had 1.1% Surpass and 13.3% Match.
- Opus 4.7 averaged $21.65 per case, from 24.25M input and 179.3K output tokens. Output tokens for third-party models are estimated from text length.

Setup for the method analysis: 10 agents on all 90 tasks, 900 runs, annotated by comparing the paper's method family with the agent's.

- Match-SOTA was 32.2% overall. Among successful runs, 45.5% were supervised proxy prediction, 17.6% optimisation or tuning, 11.0% engineering pipelines and 8.6% pretraining or scaling, which the paper totals at 82.7%; domain-reasoned alternatives were 8.3% and method-aligned solutions 9.0%.
- Matching the paper's method family gave 37.7% Match-SOTA, against 29.6% for a different family.
- Of the 67.8% of runs that failed or had no valid score, 61.1% failed at the method layer (wrong method choice 45.1%) and 28.7% at the execution layer (budget or time 24.4%); understanding failures were 3.1% and strategy failures 7.0%.
- Consensus Match-SOTA ran from 60.0% (Relational, 5 tasks) to 17.9% (Biomedical, 14 tasks), and every agent ordered the domains similarly (rank correlation 0.71 to 1.00).

The authors conclude that agents succeed mainly by translating the science into familiar supervised prediction problems, not by inventing a method.

## Limits

- Each agent ran each task once; no seeds or intervals are given.
- Model and harness effects are entangled: nine of the twelve configurations run inside Claude Code, non-Anthropic models among them.
- The 900 runs carry method-family and failure-layer labels, but the annotator is not identified and no agreement figures are given.
- The discovery framing is not shown: an appendix case of a successful agent records that it proposed no new method.
- The extraction notes that about 160 tasks were built, of which 45 were dropped and 17 repaired after reproduction runs with two models, and reproduction success of 30 of 90 and 21 of 90 suggests some anchors are partly unreachable in four hours.
- Public task data raises the possibility of leakage, exact scores invite gaming of the scorer, and one primary metric can be over-optimised.
- Cost appears only as a descriptive table unrelated to success. Tasks are scientific machine learning only, 92.2% with static labels.

## See Also
- [[PaperBench]] — prerequisite-for (the paper-based task design this benchmark extends)
- [[MLE-bench]] — related (used for optimisation tasks)
- [[ScienceAgentBench]] — related
- [[Eval Contamination Defenses]] — related (public task data and exact-score feedback)
- [[AutoLab]] — related (long-horizon research and engineering tasks)
