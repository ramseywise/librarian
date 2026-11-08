---
title: AlphaEval
tags: [eval, reference]
summary: "A benchmark of 94 tasks taken from 7 companies that deploy agents commercially, scoring whole agent products rather than bare models; the best configuration (Claude Code with Opus 4.6) scored 64.41 of 100, the same model ranged from 53.45 to 64.41 across four scaffolds, and a 27-company survey found 63.0% had low confidence that a model update improved their product (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lu-2026-alphaeval.md
---

# AlphaEval

Lu et al. (arXiv 2604.12162, 2026) build tasks from requirements gathered at seven partner companies instead of from retrospectively curated research problems. There are 94 tasks across 6 O*NET domains, and each task is scored by at least two grader types (2.8 on average) combined with expert-set weights. The unit scored is an agent product (Claude Code, Codex, Copilot, Cursor) paired with a model.

## Construction

The authors report roughly a month with each company, weekly meetings, and three to four rounds of refinement. A task is packaged as `query.md`, `task.yaml`, an input `files/` folder and an `.eval/rubric.py`. Task scores lie in [0, 1]; domain scores are unweighted task means and the overall score is the unweighted mean of six domains. The authors note partners raised their quality bars mid-study.

## Results (self-reported)

Setup: 94 tasks, 14 model-scaffold configurations at default API settings, one run each except the best configuration (three runs); LLM-judged parts use Claude Opus 4.6.

- **Best configuration.** Claude Code with Opus 4.6 scored 64.41.
- **Scaffold moves one model.** Opus 4.6 scored 64.41 in Claude Code, 61.85 in Cursor, 61.31 in Copilot and 53.45 in Codex. GPT-5.2 scored 39.47 in Claude Code and 54.91 in Copilot. Codex versions differed by model: 0.111.0 for GPT-5.2 and Opus, 0.80.0 for GLM-5 and Kimi.
- **Domains differ.** Domain means were 62.0 (Technology Research), 61.7 (Procurement and Operations), 56.3 (SE), 55.8 (F&I), 38.6 (H&LS) and 30.0 (Human Resources); the paper does not spell out the three abbreviations.
- **Repeat runs, best configuration only.** Overall 64.41 with an interval of ±1.83 over three runs.
- **Judge agreement.** On 20 random LLM-judged tasks and 1,000 rubric-point judgments, agreement was 84.7% between the two human experts (kappa 0.691), 85.0% between expert A and the judge (0.697) and 89.7% between expert B and the judge (0.780). The authors describe expert A as strict and B as lenient.
- **Score and value differ.** Weighting score by expert-calibrated labour cost (2,420 professional hours, $154K to $231K for the 94 tasks), Codex with Opus 4.6 (53.45) outscored Claude Code with Gemini 3 Pro (50.78) on score but delivered less estimated value ($86K to $129K against $89K to $133K).
- **Practitioner survey.** Of 27 of 50 accelerator companies responding (December 2025 to January 2026), 63.0% reported low confidence that a model update improved their product, 25.9% had no explicit evaluation criteria, 70.4% treated testing as a developer side task and 11.1% had structured test sets with automated pipelines.
- **Failure modes the authors describe.** on procurement problems with no feasible solution, most responses invent a best-effort answer rather than declaring infeasibility; reports could contradict themselves across sections; and tasks with quantifiable criteria scored 2 to 3 times higher than holistic ones.

## Limits

Stated: only six domains from seven companies (no legal, education or creative); one snapshot in time; the economic value depends on assumptions about benefit multipliers and wages (the value band widens 61% across the 10th to 90th wage percentile); four scaffolds and 14 of 24 possible pairings. The extraction adds: 13 of 14 configurations ran once, so gaps of 1 to 4 points among the top configurations are within the best configuration's three-run noise; the judge model equals the top-scoring model and self-preference is not tested; the judge meta-evaluation covers 20 tasks and five unnamed configurations; scaffold versions differ so scaffold effect is confounded with version; tasks are proprietary so the benchmark cannot be fully audited; many domain cells hold 11 to 23 tasks; partner rubrics were validated with frontier agents, so difficulty is partly tuned to tested models; and failure percentages come from about 130 results with no stated labelling protocol.

Internal inconsistencies noted by the extraction: the "Std" column in the repeat-run table equals the interval half-width in every row, and a t-based interval on three runs would be about 2.5 times wider, so the "narrow intervals" claim is overstated; a figure says 15 configurations where text and table say 14; healthcare hours are 86 to 132 in one appendix and 154 in a table; the survey says 15 questions but numbers Q1 to Q16; and the "scaffold matters as much as model" claim is supported cleanly only by the Opus case.

## See Also
- [[Holistic Agent Leaderboard (HAL)]] — related (scaffold and cost effects across nine benchmarks)
- [[TheAgentCompany]] — related (another benchmark of workplace tasks)
- [[SWE-Lancer]] — related (value-weighted scoring of real work)
- [[LLM-as-Judge Evaluation]] — related (judge agreement against two experts)
- [[Online Eval Sampling]] — related (evaluating production traffic, the other direction)
