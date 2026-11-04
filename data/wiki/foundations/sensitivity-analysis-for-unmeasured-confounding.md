---
title: Sensitivity Analysis for Unmeasured Confounding
tags: [foundations, pattern]
summary: "E-values and Rosenbaum bounds ask what hidden confounder would erase an effect entirely and so can look reassuring while real bias is smaller; the whiteboard bias approximation gamma times delta (hidden effect per SD times remaining imbalance) sizes the bias, and refuters only catch pipeline errors."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--05-matching-and-weighting.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--04-correlation-and-causation.md
---

# Sensitivity Analysis for Unmeasured Confounding

Nothing in observed data reveals a confounder nobody logged, so ask how strong it would have to be. Three checks, each read for what it claims.

## E-value

The minimum association (ratio scale) a hidden confounder would need with both treatment and outcome, beyond measured covariates, to explain the result away. For a ratio RR above 1: RR + sqrt(RR(RR - 1)); for non-negative outcomes apply it to the ratio of means. Examples: RR 1.10 gives 1.43; RR 2.00 gives 3.41, so small effects are most exposed. In the club data the ratio of means was 1.242 (lower interval limit 1.181), E-value 1.79 (1.64 for the limit). Intervals capture sampling noise only.

## Rosenbaum bounds

On matched pairs, suppose a hidden trait tilts one member's odds of treatment by up to Gamma. The bound asks how large Gamma must be before the signed-rank test could lose significance. On 1,972 pairs significance held until Gamma = 2.35.

## Bias arithmetic

Omitted-variable bias is about gamma x delta: the hidden trait's effect per SD times the imbalance left after adjustment. 8 pounds per SD x 0.48 SD = 3.81 against a measured 3.59 mean gap. It sizes bias well but only with the true gamma and delta, which an analyst must guess; a grid and the effects of observed covariates give benchmarks (a trait as strong as prior orders and fully out of balance would remove the effect).

## How the checks scored

- E-value 1.79 and Gamma 2.35 answered "is the effect exactly zero?" The real bias overstated the effect by about 15%; moving the estimate to the truth needed an E-value of just 1.20, an entirely plausible confounder. To ask about size, compute the E-value for a smaller effect you would care about.
- Gamma is a worst case that sets the confounder-outcome link to infinity. The true hidden odds ratio inside pairs had median 1.68 and 90th percentile 3.34, above 2.35, yet the true effect was well above zero.
- Placebo-treatment and random-common-cause refuters both passed on an estimate known to be biased: they find pipeline errors, not missing confounders. Reading an E-value of 1.79 as "robust" is the pitfall.

Report the estimate, balance table, who was kept and these checks together, and name the trait you worry about.

## See Also
- [[Matching and Weighting Estimators]] — prerequisite-for
- [[Backdoor and Front-Door Criteria]] — prerequisite-for
- [[Causal Design Selection Beyond Randomisation]] — related
