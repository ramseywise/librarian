---
title: Harness-IF
tags: [eval, reference]
summary: "A benchmark of rule-level instruction following in multi-turn coding agents that scores against-prior rules (ones the model would not follow by default) separately; across 12 models accuracy ran 72.1% to 85.9% but against-prior accuracy was lower for every model, by 3.6 to 7.4 points (mean 5.81), and a small pilot found tool and skill descriptions lose instruction conflicts (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-huang-2026-harness-if.md
---

# Harness-IF

Huang et al. (arXiv 2608.11727, 2026) argue that aggregate instruction-following scores overstate compliance, because an agent may follow a rule it was going to follow anyway. Harness-IF scores each rule and also reports **AP-Acc**, accuracy on against-prior rules only. Prior labels come from a 9-build zero-injection probe or from curation, which the authors call behavioural strata, not training provenance. It also covers where an instruction sits: system prompt, project file, and tool and skill descriptions.

## Results (self-reported)

Main panel: 12 models, 60 multi-turn coding items, 3 rounds (2,160 runs, 40,104 verdict rows, 19,449 of the 37,616 eligible rows against-prior), metric per-rule pass rate.

- **Accuracy and AP-Acc.** Accuracy ranged from 72.1% (StepFun-3.5) to 85.9% (Claude Opus 4.7); AP-Acc from 66.1% (Seed-2.0-Pro) to 78.6% (Opus 4.7). The gap was positive for all 12, from +3.6 (GLM-5.1) to +7.4 (Seed-2.0-Pro). Opus 4.7 scored 85.9 against 78.6; GPT-5.5 scored 83.1 against 77.0.
- **Ranking.** Controlling for the prior left the top model unchanged and swapped three adjacent rank pairs (2-3, 4-5, 11-12). Item-clustered 95% intervals on the gap stayed positive for each model on common support (2,430 of 3,342 keys); adjacent-model comparisons were unresolved.
- **Where failures fall.** Shortfall rules (require, minimum) carried 77.1% of the 8,440 failures and overstep rules 20.8%; fail rates were similar (23.8% against 20.8%), so the skew reflects exposure. Output control was the hardest family (70.9% against 82.6% for quantitative rules). Commanding rules scored 76.0% against 90.6% for preferences.
- **Surface precedence pilot (E0).** Nine older model builds, four synthetic conflict pairs, 916 runs, deterministic scoring. Surfaces labelled SP, PF and UI tied at mean rank 2.22, TD scored 3.78 and SD 4.56 (the extraction does not expand the labels; it reports that tool and skill descriptions lose conflicts). The full ordering held in 9,652 of 10,000 bootstrap resamples, but only 6 of 9 individual builds reproduced it. The authors say the user instruction only tying for first is inconsistent with a prompt-depth account.

## Limits

Deterministic checks cover 13.3% of verdicts; a GPT-5.2 judge with a three-vote majority covers the rest. Test-retest ICC was 0.725 across models and 0.599 across agent-item cells; agreement under a judge swap was 62.1% (kappa 0.163, 116 paired verdicts); an earlier human audit gave 69.0% (kappa 0.515, 919 rows). Absolute levels are instrument-specific, so the authors rest claims on cross-model patterns. Surfaces are assigned by admissibility, not randomised, so the main panel supports only descriptive stratification; E0 is small, synthetic and run on older builds. Items were chosen from 80 candidates for difficulty and discrimination (the authors call this selection optimism), and the prior-probe cohort overlaps the evaluated panel (5 of 9 share an identifier). All 12 models ran in one harness setup, so the paper does not compare the same model across harnesses, and the non-coding panel is not pooled.

## See Also
- [[Holistic Agent Leaderboard (HAL)]] — related (scaffold effects, the comparison Harness-IF does not make)
- [[Skill Authoring Discipline]] — related (where skill descriptions sit among instruction surfaces)
- [[Skill Lift Evaluation]] — related (skills as one instruction surface)
- [[LLM Judge Biases]] — related (judge dependence of the absolute levels)
