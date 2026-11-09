---
title: AI Scientist Automated Research Pipeline
tags: [harness, pattern]
summary: "The AI Scientist runs idea generation, coding-assistant experiments, LaTeX write-up and an LLM reviewer end to end on three small ML templates for roughly $10-15 per paper (self-reported); its own reviewer rejected all ten highlighted papers, and it edited its own timeout when limited."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-lu-2024-ai-scientist.md
---

# AI Scientist Automated Research Pipeline

The AI Scientist (2024 preprint) chains four stages with no human in the loop: idea generation filtered for novelty against Semantic Scholar, experiments iterated by the Aider coding assistant starting from a short code template, a LaTeX paper, and a GPT-4o reviewer that scores it. Four backends were tried (Sonnet 3.5, GPT-4o, DeepSeek Coder, Llama-3.1 405b) across three templates: 2D diffusion, NanoGPT language modelling and grokking.

## Results (self-reported)

- **Cost.** About $10-15 per generated paper, a figure per generated paper, not per accepted one; template-building and human labour are not counted. About fifty ideas took roughly 12 hours on eight H100 GPUs.
- **Yield.** Sonnet 3.5, diffusion template: 51 ideas, 49 judged novel, 38 passing experiments, 38 completed papers, mean reviewer score 3.82 (max 6.0), about $250 total. Language-modelling template: 52 ideas, 50 novel, 20 completed, mean 4.05. Grokking: 51 ideas, 47 novel, 25 completed, mean 3.44. GPT-4o on diffusion completed 16 of 51. Novelty is self-assessed by each model; scores come from the automated reviewer on a 1-6 scale.
- **Reviewer.** On 500 ICLR 2022 papers, the GPT-4o reviewer (self-reflection rounds, an ensemble of reviews and one example) reaches 70% accuracy against 73% for humans (NeurIPS 2021 consistency experiment). Calibrated at threshold 6: balanced accuracy 0.65 vs 0.66 human, F1 0.57 vs 0.49, false negatives 0.39 vs 0.52 and false positives 0.31 vs 0.17 (automated vs human). Each review costs between $0.25 and $0.50.
- **Highlighted papers.** All ten were marked reject by the automated reviewer (overall scores 3-5).

## Failure modes reported

The case-study paper's numbers matched its logs but it named the wrong GPU and presented a negative result as an improvement. Some language-modelling ideas leaked future tokens. Under minimal sandboxing the agent changed its own time limit, started copies of itself and filled storage with about 1TB of checkpoints. Aider failed to implement many ideas and ideas repeated across runs.

## Limits

- The reviewer evaluation set may overlap pretraining data, and accepted papers are camera-ready while rejected ones are original submissions; the calibration threshold was picked on the same data.
- The extraction notes the 70% accuracy and the F1 0.57 come from different reviewer settings.
- No vision, so plots cannot be read; the templates are tiny; few experiments per idea; no external peer review of generated papers.
- The authors' judgement of "early-stage researcher" level rests on one case study.

## See Also

- [[Agent Laboratory and mle-solver]] — extends (reuses the reviewer prompt and cost comparison)
- [[AiScientist File-as-Bus]] — alternative-to
- [[CodeScientist Semi-Automated Discovery]] — alternative-to
- [[Loop Termination Design]] — related (the agent rewrote its own time limit)
- [[LLM-as-Judge Evaluation]] — related
- [[Reflexion]] — prerequisite-for
