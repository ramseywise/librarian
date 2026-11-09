---
title: HELM Holistic Evaluation
tags: [eval, reference]
summary: "HELM scores 30 language models on 42 scenarios under one standardized prompting setup across seven metric categories, so that accuracy, robustness, fairness and cost can be read side by side; the paper's own ablations show prompt format and in-context examples changing accuracy, with the best adaptation method differing by model (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-bommasani-2023-holistic-evaluation-language-models.md
  - data/raw/papers/2026-11-08-chang-2023-survey-evaluation-large-language-models.md
---

# HELM Holistic Evaluation

HELM (Holistic Evaluation of Language Models; Liang, Bommasani, Lee et al., arXiv 2211.09110,
Transactions on Machine Learning Research, August 2023) asks how to evaluate language models
across many use cases and several metrics under the same conditions, so that trade-offs and gaps
become visible. The authors publish every prompt and completion, plus a modular toolkit.

## Structure

- A **scenario** is a triple of task, domain and language. HELM runs 16 core scenarios plus 7
  targeted evaluations, 42 scenarios in all.
- Each core scenario is scored on **seven metric categories**. The extraction names accuracy,
  robustness, fairness, toxicity and energy among the measures. Of the 112 (scenario, metric) pairs, 98 are measured; the 14 skipped are mostly
  undefined, for example toxicity where nothing is generated.
- **Adaptation** is the prompting procedure that turns a model into a system for a scenario.
  Every one of the 30 models gets 5-shot prompting, at most 1,000 instances per scenario and 3
  in-context-example runs (version 0.1.0).
- Robustness is the mean over instances of the worst metric value across perturbed versions of
  the input; the perturbations include typos, casing, contractions and spacing.

## Coverage and cost (self-reported)

By the authors' count of earlier reports, models averaged 17.9% coverage of the core scenarios;
HELM reaches 96.0%. The full run is 4,939 runs, about 12.2B
tokens and 17.4M queries, costing $38,001 on commercial APIs plus roughly 19.5k GPU hours for the open
models.

## Findings (self-reported)

- **Format moves scores.** OPT (175B) on HellaSwag goes from 79.1% with a separate 0-shot
  multiple-choice prompt to 30.2% with a joint 5-shot prompt. For six models on HellaSwag the three
  multiple-choice methods rank the same way every time: separate, then separate-calibrated, then
  joint. The authors report that the best adaptation method differs across models.
  See [[Benchmark Prompt Format Sensitivity]].
- **Robustness gaps.** TNLG v2 (530B) on NarrativeQA falls from 72.6% to 38.9% under the
  perturbation composite; OPT (175B) on the CivilComments Black split falls from 51.3% to 8.8%.
- **Dialect.** On TwitterAAE, OPT (175B) scores 2.114 bits per byte for African American English
  and 1.506 for White English.
- **Unified evaluation exposes results.** On NarrativeQA, text-davinci-002 gets 74.4% ROUGE-L and
  UnifiedQA-v2 67.4%. On TruthfulQA (joint multiple-choice adaptation), text-davinci-002 gets 62.0%, ahead of the
  runner-up, the 52B Anthropic-LM v4-s3. On GSM8K, code-davinci-002 gets 52.1% and the second
  model, text-davinci-002, 35.0%.
- **Scale.** Accuracy win rates above 55% in head-to-head comparisons appear only for models with
  50B parameters or more. Across model families, bits per byte on The Pile (an upstream measure)
  predicts downstream accuracy poorly.

## A later survey of the field

Chang et al. (arXiv 2307.03109, ACM TIST) survey evaluation under the headings what, where and how.
They compile 46 benchmarks, HELM among them, and concede the list is incomplete. They say
none of the protocols or benchmarks is shown to be the most useful, and no model wins every task. They
assert that static public benchmarks are probably memorised and call dynamic evaluation the key to
fair evaluation, without measuring contamination. Their human-evaluation rubric extends the
helpful, honest, harmless rule into six criteria: accuracy, relevance, fluency, transparency,
safety and human alignment. LLM-as-judge is only mentioned in the survey, not assessed for bias.

## Limits

- Contamination is not verified: HELM flags only cases the model builders disclosed (its Table 13),
  and says the extent is unclear.
- Three seeds and 1,000 instances per scenario may leave some comparisons statistically
  insignificant.
- The closed API models are a snapshot in time, and neither PaLM nor Gopher is evaluated.
- No single fairness score is given, and how to aggregate across metrics is left to the reader.
- Toxicity relies on the Perspective API, and the dialect perturbations are approximate
  simulations. Energy and CO2 figures are rough estimates.
- The survey adds no experiments of its own; its claims depend on 2023-era models and datasets,
  and its authors expect readers to rerun on current systems. For human evaluation it
  lists factors to weigh without a procedure, and gives no agreement statistics.

## See Also
- [[BIG-bench]] — related (a community task collection; HELM's appendix compares the two)
- [[Benchmark Prompt Format Sensitivity]] — related (the HellaSwag format result is one more case)
- [[Eval Contamination Defenses]] — related
- [[Eval Error Bars and Sample Size]] — related (HELM's three-seed, 1,000-instance setup is thin)
- [[TruthfulQA]] — related (one of HELM's core scenarios)
- [[Holistic Agent Leaderboard]] — related (applies the multi-metric idea to agents)
- [[Self-Supervised LLM Evaluation by Text Transformations]] — related (a label-free complement to multi-metric benchmarks)
- [[CLUE Chinese Benchmark]] — related (GLUE-style leaderboard design)
- [[PromptBench]] — alternative-to (another evaluation framework)
