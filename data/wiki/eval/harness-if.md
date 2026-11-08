---
title: Harness-IF
tags: [eval, reference]
summary: "A benchmark of rule-level instruction following in multi-turn coding agents that scores against-prior rules (ones the model would not follow by default) separately; across 12 models accuracy ran 72.1% to 85.9% but against-prior accuracy was lower for every model, by 3.6 to 7.4 points (mean 5.81), and a small pilot found tool and skill descriptions lose instruction conflicts (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-huang-2026-harness-if.md
---

# Harness-IF

Huang et al. (arXiv 2608.11727, 2026) argue that pooled instruction-following scores overstate compliance, since an agent may be obeying a rule it would have obeyed regardless. Harness-IF scores each rule and also reports **AP-Acc**, accuracy on against-prior rules only. Prior labels come from a probe of nine builds run with no injected rule, or from curation; the authors call them behavioural strata, not training provenance. It also covers where an instruction sits: system prompt, project file, and tool and skill descriptions.

## Results (self-reported)

Main panel: 12 models on 60 multi-turn coding items over three rounds, giving 2,160 runs and 40,104 verdict rows (37,616 eligible, of which 19,449 against-prior); the metric is per-rule pass rate.

- **Accuracy and AP-Acc.** Accuracy was lowest for StepFun-3.5 (72.1%) and highest for Claude Opus 4.7 (85.9%); AP-Acc was lowest for Seed-2.0-Pro (66.1%) and highest for Opus 4.7 (78.6%). Every model's gap was positive, between +3.6 (GLM-5.1) and +7.4 (Seed-2.0-Pro). Opus 4.7 scored 85.9 against 78.6; GPT-5.5 scored 83.1 against 77.0.
- **Ranking.** Controlling for the prior left the top model unchanged and swapped three adjacent pairs of ranks (2-3, 4-5 and 11-12). On the 2,430 of 3,342 keys with common support, item-clustered 95% intervals for the gap stayed above zero for each model; adjacent-model comparisons were unresolved.
- **Where failures fall.** Shortfall rules (require, minimum) carried 77.1% of the 8,440 failures and overstep rules 20.8%; fail rates were similar (23.8% against 20.8%), so the skew reflects exposure. Output control was the hardest family (70.9% against 82.6% for quantitative rules). Commanding rules scored 76.0% against 90.6% for preferences.
- **Surface precedence pilot (E0).** Nine older model builds, four synthetic conflict pairs, 916 runs, deterministic scoring. Surfaces labelled SP, PF and UI tied at mean rank 2.22, TD scored 3.78 and SD 4.56 (the extraction does not expand the labels; it reports that tool and skill descriptions lose conflicts). The overall ordering recurred in 9,652 of 10,000 resamples, though just 6 of the 9 builds reproduced it individually. The authors say the user instruction only tying for first is inconsistent with a prompt-depth account.

## Limits

Deterministic checks decide 13.3% of verdicts and a GPT-5.2 judge (three-vote majority) the remainder. Test-retest ICC was 0.725 across models but 0.599 across agent-item cells. Swapping the judge gave 62.1% agreement (kappa 0.163 on 116 paired verdicts), and an earlier human audit gave 69.0% (kappa 0.515 on 919 rows). Absolute levels are instrument-specific, so the authors rest claims on cross-model patterns. Surfaces were assigned by what was admissible rather than at random, so the main panel supports only a descriptive breakdown by surface; E0 is small, synthetic and used older builds. Items were picked from 80 candidates for difficulty and discrimination (the authors call this selection optimism), and the probe cohort overlaps the evaluated panel (an identifier is shared by 5 of the 9). All 12 models ran in one harness setup, so the paper does not compare the same model across harnesses, and the non-coding panel is not pooled.

## See Also
- [[Holistic Agent Leaderboard (HAL)]] — related (scaffold effects, the comparison Harness-IF does not make)
- [[Skill Authoring Discipline]] — related (where skill descriptions sit among instruction surfaces)
- [[Skill Lift Evaluation]] — related (skills as one instruction surface)
- [[LLM Judge Biases]] — related (judge dependence of the absolute levels)
