---
title: Agent Laboratory and mle-solver
tags: [harness, pattern]
summary: "Agent Laboratory runs literature review, experiments and report writing with role-prompted agents and optional human feedback, at $2.33 per paper with a gpt-4o backend (self-reported); its mle-solver edits code against an LLM reward, and automated reviewer scores far exceed human ones."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-schmidgall-2025-agent-laboratory.md
---

# Agent Laboratory and mle-solver

Agent Laboratory (2025 preprint) starts from a human-given ML research idea and runs three phases with agents prompted as PhD, Postdoc, ML Engineer, SW Engineer and Professor roles on top of off-the-shelf models. Literature review uses arXiv search; experimentation uses **mle-solver**, which repeatedly EDITs or REPLACEs Python code and scores each candidate with an LLM reward model; report writing uses **paper-solver**, the same loop applied to LaTeX, scored by an automated conference-style reviewer. A human can give feedback after each phase (co-pilot mode).

## Results (self-reported)

- **Cost and time.** Per full workflow, API cost only: gpt-4o at $2.33, o1-mini at $7.51, o1-preview at $13.10; wall-clock 1165.4 s, 3616.8 s and 6201.3 s on a laptop. The claimed 84% saving is against the roughly $15 per paper reported for The AI Scientist, copied not rerun, and holds only for gpt-4o.
- **Success.** Mean subtask success is 94.3 (gpt-4o), 92.8 (o1-mini) and highest for o1-preview; literature review was lowest at 60%, 70% and 80%.
- **Quality.** 15 autonomous papers (5 topics, 3 backends): human reviewers averaged 3.8/10 overall (gpt-4o 3.5, o1-mini 3.8, o1-preview 4.0), about 2.05 below the average accepted NeurIPS 2024 paper; the automated reviewer scored them far higher. Ten PhD students rated 3 papers each: for gpt-4o papers: 2.6 on experiments, 3.0 on the report, 4.0 on usefulness (1-5 scale).
- **Co-pilot.** External evaluators rated co-pilot papers above autonomous ones (+0.58 overall); researchers' own score was 4.13/10 against 4.38 from externals. Rater counts are not stated.
- **mle-solver.** On 10 of the 75 MLE-Bench challenges (low-complexity text and tabular), scored on a 20% dev split: four medals against two each for OpenHands and AIDE and none for MLAB; it was above the median human result on six of the ten. Backend and run count for mle-solver are not stated.

## Limits

- No significance tests, confidence intervals or standard deviations; raters were not blinded to AI authorship.
- The $2.33 covers autonomous gpt-4o API calls only, while the co-pilot study used o1-mini, and human labour and failed runs are not costed.
- Pipeline starts from a human idea; ML topics only; fixed section structure, at most two figures, no repository-level code.
- gpt-4o papers contained hallucinated experimental details; the authors themselves say the reports read as weaker than The AI Scientist's despite higher automated scores.
- Backends and prices are dated.

## See Also

- [[AI Scientist Automated Research Pipeline]] — prerequisite-for
- [[AgentRxiv Shared Preprint Server]] — related
- [[CodeScientist Semi-Automated Discovery]] — alternative-to
- [[LLM-as-Judge Evaluation]] — related
