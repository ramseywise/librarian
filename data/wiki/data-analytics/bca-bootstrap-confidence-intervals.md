---
title: BCa Bootstrap Confidence Intervals
tags: [data-analytics, probability-and-statistics, concept]
summary: "Percentile, BC and BCa intervals turn bootstrap replications into confidence intervals; BCa adds a bias value z0 and an acceleration a to reach second-order accuracy, at the cost of about 2000 replications and an extra jackknife step."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch11-bootstrap-confidence-intervals.md
---

# BCa Bootstrap Confidence Intervals

Efron and Hastie (Computer Age Statistical Inference, ch. 11) ask how bootstrap replications can be turned automatically into accurate confidence intervals that do not depend on the scale a statistic is measured on. Their answer is a ladder of four algorithms: the standard interval, the percentile method, BC and BCa. The hypothesis behind the top rungs is that some monotone transformation makes the estimate normal, with bias z0 and acceleration a; the transformation need only exist, it does not have to be known.

## The ladder

- **Standard interval:** the estimate plus or minus a normal quantile times its standard error. The coverage error shrinks like 1/sqrt(n), so four times the data halves it.
- **Percentile method:** the endpoints are percentiles of the bootstrap distribution of the statistic. An interval for a transformed parameter is the transformation applied to the endpoints, which the authors call an automatic Fisher.
- **BC:** shifts the percentiles by the bias value z0 = Phi^-1(p0), where p0 is the fraction of replications below the original estimate.
- **BCa:** adds the acceleration a, a small constant capturing the rate at which the estimate's spread varies as the parameter moves. With G the bootstrap cdf, the level-alpha limit is G^-1 applied to Phi of z0 plus (z0 + z_alpha) divided by (1 - a(z0 + z_alpha)). Choosing a = 0 leaves BC, z0 = 0 leaves the percentile method, and a bootstrap histogram that looks normal leaves the standard interval.

BCa has coverage error of order 1/n (second-order accurate, a result Hall proved in 1988), whereas percentile and BC lack second-order accuracy. For one-sample nonparametric problems a is estimated from jackknife values: a sixth of the sum of cubed deviations from the jackknife mean, divided by the summed squared deviations raised to the power 1.5. Since a cannot be read off the bootstrap distribution, it needs its own computation (the jackknife, the abc shortcut, or the accel function for exponential families).

## Worked examples

Setup for the first two: Poisson, observed value 10, nominal 95% central intervals. The exact interval is (5.08, 17.82); BCa gives (5.02, 17.96) where z0 and a both equal 0.050 and each tail holds 0.023. The standard interval's lower end of 3.80 has just 0.004 of the exact tail mass above 10, against an intended 0.025. For the standard, percentile and BC intervals the tail areas above and below 10 were (.004, .055), (.007, .042) and (.010, .036).

Setup for the correlation example: Student score data, n = 22 pairs, sample correlation 0.498, 95% central intervals, exact interval from Neyman's construction (0.093, 0.751).

| Method | Parametric bootstrap | Nonparametric bootstrap (B = 2000) |
|---|---|---|
| Standard | (.17, .83) | (.18, .82) |
| Percentile | (.11, .77) | (.13, .76) |
| BC | (.08, .75) | (.13, .76) |
| BCa | (.08, .75), z0 = -0.055, a = 0.005 | (.12, .76), z0 = 0.000, a = 0.006 |

Bootstrap-t resamples the pivot (replicate estimate minus original estimate, divided by its standard error). On the correlation it gave percentiles (-1.64, 2.59) and the interval (0.051, 0.781), which sits oddly beside the others. It lacks transformation invariance and needs a standard-error formula; after a Fisher z transformation it lands close to the exact intervals. For a difference of gene-expression means in two groups (47 and 25 patients), the t interval (0.062, 0.314) and the bootstrap-t interval (0.072, 0.323) nearly coincided, which the authors take as support for normality.

## Practice

Efron and Hastie advise roughly 2000 replications for intervals but 200 or fewer for standard errors; with z0 near 0 and B = 2000 the delta-method standard error of z0 is 0.028. Even when BC or BCa is not reported they advise computing z0, which flags dangerous bias, and they urge caution once |z0| or |a| passes about 0.2. BC is a reasonable fallback when a cannot be had. The percentile method's confidence density is the bootstrap density; BCa reweights it.

## Limits

- BC and BCa work dependably only for small z0 and a, say at most 0.2. Many nuisance parameters break them: for ten normal means with squared-length estimate 20, the fraction p0 = 0.156 yields z0 = -1.01, so the BC lower limit falls at the 0.000034 bootstrap percentile.
- Bootstrap intervals are neither exact nor optimal, and in multiparameter problems the Jeffreys prior is not truly uninformative (see [[Prior Choice and Prior Predictive Checks]]).
- The eigenratio example relies on chapter 10 data and figures that the chapter does not reprint, so its Table 11.3 rows cannot be re-derived here.

## See Also
- [[Bootstrap Resampling and Its Failures]] — prerequisite-for
- [[Confidence Interval Coverage and Wilson]] — alternative-to
- [[Delta Method for Ratio Metrics]] — related (a formula-based standard error the bootstrap cross-checks)
