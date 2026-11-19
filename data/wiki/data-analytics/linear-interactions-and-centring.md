---
title: Linear Interactions and Centring
tags: [data-analytics, probability-and-statistics, pattern]
summary: "McElreath makes a slope its own linear model to let an association depend on another variable, centres continuous predictors so main effects keep their meaning, and plots posterior predictions in place of reading a table of means."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistical-rethinking-ch07-interactions.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch04-linear-models.md
---

# Linear Interactions and Centring

Chapter 7 of *Statistical Rethinking* (first edition, pp. 209-239) builds an interaction by extending the linear-model strategy to a parameter inside the linear model: a slope is defined as a linear model of another variable. The chapter also states the symmetry: the association of ruggedness with log-GDP depending on continent is the same model as the effect of continent depending on ruggedness, and both readings should be plotted.

## Dummy variable versus interaction

Setup: the rugged-terrain data, log GDP per head in 2000 regressed on terrain ruggedness for every country with GDP figures, fitted with `map`. Adding an Africa indicator yields a parallel line: only the intercept can shift. The linear interaction model m7.5 takes most of the WAIC weight over the dummy-only model; its rugged-by-Africa coefficient bAR has SD 0.13 and a 5.5% to 94.5% interval of 0.14 to 0.55. Read from the other side, an African location cuts expected log GDP by roughly 2 at the least rugged end and has almost no effect at the top ruggedness of 6.2. The slope inside Africa is gamma = bR + bAR; compute such derived quantities from posterior samples so their uncertainty is kept. Fitting the subsets separately would force separate sigmas, weaken model comparison and stop information flowing between groups, which the chapter offers as the motive for multilevel models ([[Partial Pooling and Multilevel Models]]).

## Centring

Setup: tulips, 27 rows (bed by treatment), bloom size on water and shade, N(.,100) priors. With raw predictors the intercept differs wildly between the main-effects and interaction fits and the shade effect changes sign once the interaction enters (WAIC 296.4 for the interaction model m7.7 versus 305.8 for m7.6). With centred predictors the main effects hold steady whether or not the interaction is present, and the intercept is the grand mean. At average water, moving from least to most shade roughly halves blooms; at the highest water it cuts them by about two thirds (97% interval of the mean). Chapter 4 gives the same advice for a single predictor: centring weight made the intercept equal the mean height (154.60) and removed an intercept-slope correlation of -0.99 (setup: !Kung adults, n=352).

Further practices: pass explicit start values to the optimiser, and when a MAP fit fails, try Nelder-Mead or raise the iteration count; for continuous interactions plot a triptych with the other variable held at several values; never infer an interaction from a table of means; and compute a difference's distribution directly, because overlapping marginal densities do not test it.

## Limits

- Edition: first edition with `map`; the chapter says a more capable conditioning engine comes in the next chapter, and the code is dated against `ulam` and `quap`.
- Priors on the tulips are flat, which the author does not recommend; only 27 tulip rows exist, and the Africa interaction depends on a handful of African countries (the dSE between m7.5 and m7.4 is nearly as large as their dWAIC).
- WAIC is contested here because nobody resamples nations. The tulip analysis leaves out the bed (cluster) variable.
- The author describes a linear interaction as a descriptive epicycle, with a mechanistic model preferable. The extraction does not print the source of the rugged data.

## See Also
- [[Partial Pooling and Multilevel Models]] — related (the chapter describes multilevel models as massive interaction models)
- [[WAIC, KL Divergence and Akaike Weights]] — prerequisite-for
- [[Functional Form Misspecification]] — related
