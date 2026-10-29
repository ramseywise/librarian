---
imported_hash: 24c685057dfb57b6
title: 5    | Statistical Analysis
summary: np.random.seed(42) plt.rcParams['figure.figsize'] = (10, 4)
order: 3
kind: notebook
source: learn-ai-engineering/data-analytics/5_Statistical_Analysis.ipynb
---

# 5    | Statistical Analysis

- **Part 1: Probability Distributions** — normal, binomial, Poisson; PDF/CDF; sampling
- **Part 2: Hypothesis Testing** — t-tests, chi-square, ANOVA, multiple comparisons
- **Part 3: A/B Testing** — experiment design, power analysis, confidence intervals, pitfalls
- **Part 4: Correlation and Causation** — Pearson vs Spearman, Simpson's paradox, confounders

*Resources*:
- **Practical Statistics for Data Scientists** — Bruce & Bruce (O'Reilly) — `0-cross-stats/`
- **Statistics Done Wrong** — Reinhart — `0-cross-stats/`

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

np.random.seed(42)
plt.rcParams['figure.figsize'] = (10, 4)
```

## Part 1: Probability Distributions
### Normal Distribution
The normal (Gaussian) distribution is defined by its mean μ and standard deviation σ.
~68% of values fall within 1σ, ~95% within 2σ, ~99.7% within 3σ (the 68-95-99.7 rule).

```python
# normal distribution: PDF and sampling
mu, sigma = 0, 1
x = np.linspace(-4, 4, 200)

pdf = stats.norm.pdf(x, mu, sigma)
cdf = stats.norm.cdf(x, mu, sigma)

fig, axes = plt.subplots(1, 2)
axes[0].plot(x, pdf)
axes[0].set_title('Normal PDF (μ=0, σ=1)')
axes[0].set_xlabel('x')
axes[0].set_ylabel('Density')

axes[1].plot(x, cdf)
axes[1].set_title('Normal CDF')
axes[1].set_xlabel('x')
axes[1].set_ylabel('Cumulative Probability')
plt.tight_layout()
plt.show()

# probability that a value falls within 1 standard deviation
p_within_1sd = stats.norm.cdf(1) - stats.norm.cdf(-1)
print(f'P(-1 < X < 1): {p_within_1sd:.4f}')
```

```python
# sample from a normal distribution and check it looks right
samples = np.random.normal(mu, sigma, 1000)

plt.hist(samples, bins=40, density=True, alpha=0.7, label='Samples')
plt.plot(x, pdf, 'r-', label='True PDF')
plt.title('1000 samples vs theoretical PDF')
plt.legend()
plt.show()

print(f'Sample mean: {samples.mean():.3f}  (true: {mu})')
print(f'Sample std:  {samples.std():.3f}  (true: {sigma})')
```

### Binomial Distribution
Models the number of successes in *n* independent trials each with probability *p*.
Example: flipping a coin 20 times — how many heads?

```python
# binomial: n trials, p probability of success
n, p = 20, 0.5
k = np.arange(0, n + 1)

pmf = stats.binom.pmf(k, n, p)

plt.bar(k, pmf)
plt.title(f'Binomial PMF (n={n}, p={p})')
plt.xlabel('Number of Successes')
plt.ylabel('Probability')
plt.show()

# probability of getting exactly 10 heads
print(f'P(X=10): {stats.binom.pmf(10, n, p):.4f}')
# probability of getting 10 or more heads
print(f'P(X>=10): {stats.binom.sf(9, n, p):.4f}')
```

### Poisson Distribution
Models the number of events occurring in a fixed interval when events happen at a constant rate λ.
Example: customer arrivals per hour, server errors per day.

```python
# Poisson distribution with different rate parameters
k = np.arange(0, 20)

fig, ax = plt.subplots()
for lam in [1, 4, 8]:
    ax.plot(k, stats.poisson.pmf(k, lam), 'o-', label=f'λ={lam}')

ax.set_title('Poisson PMF for different λ')
ax.set_xlabel('k (number of events)')
ax.set_ylabel('P(X=k)')
ax.legend()
plt.show()

# if a server averages 3 errors/hour, P(more than 5 errors in an hour)?
lam = 3
print(f'P(X > 5 | λ=3): {stats.poisson.sf(5, lam):.4f}')
```

## Part 2: Hypothesis Testing

The framework:
1. **H₀ (null hypothesis)** — the default assumption (no effect, no difference)
2. **H₁ (alternative hypothesis)** — what you want to detect
3. **p-value** — probability of observing data this extreme *if H₀ were true*
4. **α (significance level)** — threshold for rejection, conventionally 0.05

If p < α, reject H₀. This does NOT mean H₁ is true — it means the data are unlikely under H₀.
*(Ref: Statistics Done Wrong, ch. 1-2)*

```python
# one-sample t-test: is this sample mean significantly different from a known value?
# scenario: average adult height is 170cm. Is our sample from a different population?
known_mean = 170
sample = np.random.normal(loc=173, scale=8, size=50)  # slightly taller population

t_stat, p_value = stats.ttest_1samp(sample, known_mean)

print(f'Sample mean: {sample.mean():.2f} cm')
print(f't-statistic: {t_stat:.3f}')
print(f'p-value:     {p_value:.4f}')
print(f'Reject H₀ at α=0.05: {p_value < 0.05}')
```

```python
# two-sample t-test: do two groups have different means?
# scenario: does a new study method improve test scores?
control = np.random.normal(loc=72, scale=10, size=40)
treatment = np.random.normal(loc=76, scale=10, size=40)

t_stat, p_value = stats.ttest_ind(control, treatment)

print(f'Control mean:   {control.mean():.2f}')
print(f'Treatment mean: {treatment.mean():.2f}')
print(f't-statistic:    {t_stat:.3f}')
print(f'p-value:        {p_value:.4f}')
print(f'Reject H₀ at α=0.05: {p_value < 0.05}')
```

### Chi-Square Test
Tests whether two categorical variables are independent.
Example: does product preference depend on age group?

```python
# chi-square test of independence
# observed counts: product preference (A vs B) across two age groups
observed = np.array([[30, 20],   # under 30: 30 prefer A, 20 prefer B
                     [15, 35]])  # over 30:  15 prefer A, 35 prefer B

chi2, p_value, dof, expected = stats.chi2_contingency(observed)

print('Observed:')
print(pd.DataFrame(observed, index=['Under 30', 'Over 30'], columns=['Product A', 'Product B']))
print()
print('Expected (under independence):')
print(pd.DataFrame(expected.round(1), index=['Under 30', 'Over 30'], columns=['Product A', 'Product B']))
print()
print(f'Chi-square: {chi2:.3f}, df={dof}, p-value={p_value:.4f}')
print(f'Preference depends on age group: {p_value < 0.05}')
```

### ANOVA — Multiple Group Comparison
One-way ANOVA tests whether the means of 3+ groups differ.
H₀: all group means are equal. If rejected, follow up with post-hoc tests to find which pairs differ.

```python
# one-way ANOVA: do three teaching methods produce different outcomes?
method_a = np.random.normal(loc=75, scale=8, size=30)
method_b = np.random.normal(loc=80, scale=8, size=30)
method_c = np.random.normal(loc=74, scale=8, size=30)

f_stat, p_value = stats.f_oneway(method_a, method_b, method_c)

print(f'Group means: A={method_a.mean():.2f}, B={method_b.mean():.2f}, C={method_c.mean():.2f}')
print(f'F-statistic: {f_stat:.3f}')
print(f'p-value:     {p_value:.4f}')
print(f'Groups differ at α=0.05: {p_value < 0.05}')
```

### Multiple Comparisons — Bonferroni Correction
Running many tests inflates the false-positive rate. If α=0.05 and you run 20 tests,
you expect 1 false positive by chance. Bonferroni: adjust α downward by dividing by the number of tests.
*(Ref: Statistics Done Wrong, ch. 3)*

```python
# simulate multiple comparison problem
# 20 tests, all under true H₀ — how many false positives at α=0.05?
n_tests = 20
alpha = 0.05

p_values = [stats.ttest_ind(
    np.random.normal(0, 1, 30),
    np.random.normal(0, 1, 30)
).pvalue for _ in range(n_tests)]

# uncorrected rejections (false positives — H₀ is always true here)
uncorrected = sum(p < alpha for p in p_values)

# Bonferroni correction: divide alpha by number of tests
bonferroni_alpha = alpha / n_tests
corrected = sum(p < bonferroni_alpha for p in p_values)

print(f'Tests run:              {n_tests}')
print(f'α (uncorrected):        {alpha}')
print(f'α (Bonferroni):         {bonferroni_alpha:.4f}')
print(f'False positives (uncorrected): {uncorrected}')
print(f'False positives (corrected):   {corrected}')
```

## Part 3: A/B Testing

A/B testing is hypothesis testing applied to product experiments:
randomly assign users to control (A) or treatment (B), then test whether observed differences are real.

Key design decisions before running the test:
- What metric? (conversion rate, revenue, time-on-page)
- Minimum detectable effect (MDE) — smallest change worth detecting
- Power (1-β) — probability of detecting a real effect, conventionally 0.80
- Required sample size (calculate first, peek never)

*(Ref: Statistics Done Wrong, ch. 4-5)*

```python
# sample size calculation via power analysis
# scenario: baseline conversion 5%, want to detect a 1pp lift (to 6%), α=0.05, power=0.80
from scipy.stats import norm

p_control = 0.05
p_treatment = 0.06
alpha = 0.05
power = 0.80

# pooled standard deviation for proportions
p_pooled = (p_control + p_treatment) / 2
effect_size = abs(p_treatment - p_control) / np.sqrt(p_pooled * (1 - p_pooled))

# z-scores for alpha (two-tailed) and beta
z_alpha = norm.ppf(1 - alpha / 2)
z_beta = norm.ppf(power)

n = ((z_alpha + z_beta) / effect_size) ** 2

print(f'Baseline conversion:      {p_control:.1%}')
print(f'Target conversion:        {p_treatment:.1%}')
print(f'Minimum detectable effect: {p_treatment - p_control:.1%}')
print(f'Required sample per group: {int(np.ceil(n))}')
```

```python
# simulate an A/B test
n_per_group = int(np.ceil(n))

# generate conversion outcomes (1 = converted, 0 = did not)
control_conversions = np.random.binomial(1, p_control, n_per_group)
treatment_conversions = np.random.binomial(1, p_treatment, n_per_group)

rate_a = control_conversions.mean()
rate_b = treatment_conversions.mean()

# two-proportion z-test
count = np.array([control_conversions.sum(), treatment_conversions.sum()])
nobs = np.array([n_per_group, n_per_group])

from statsmodels.stats.proportion import proportions_ztest
z_stat, p_value = proportions_ztest(count, nobs)

print(f'Control conversion:   {rate_a:.3%}')
print(f'Treatment conversion: {rate_b:.3%}')
print(f'Relative lift:        {(rate_b - rate_a) / rate_a:.1%}')
print(f'z-statistic: {z_stat:.3f}, p-value: {p_value:.4f}')
print(f'Significant at α=0.05: {p_value < 0.05}')
```

```python
# confidence intervals for the difference in conversion rates
diff = rate_b - rate_a
se = np.sqrt(rate_a * (1 - rate_a) / n_per_group + rate_b * (1 - rate_b) / n_per_group)
ci_low = diff - 1.96 * se
ci_high = diff + 1.96 * se

print(f'Observed lift:    {diff:.4f} ({diff:.2%})')
print(f'95% CI:           [{ci_low:.4f}, {ci_high:.4f}]')
print(f'CI excludes zero: {ci_low > 0 or ci_high < 0}')

# visualize
plt.figure(figsize=(6, 3))
plt.errorbar(x=[1], y=[diff], yerr=[[diff - ci_low], [ci_high - diff]],
             fmt='o', capsize=6, color='steelblue')
plt.axhline(0, color='red', linestyle='--', label='No effect')
plt.xticks([1], ['B minus A'])
plt.ylabel('Difference in conversion rate')
plt.title('95% Confidence Interval for Lift')
plt.legend()
plt.tight_layout()
plt.show()
```

### Common A/B Testing Pitfalls

1. **Peeking** — checking results before you reach the planned sample size inflates false-positive rate.
   The p-value is only valid at the pre-specified stopping point.
2. **Multiple metrics** — testing 10 metrics at α=0.05 expects ~0.5 false positives. Pre-specify your primary metric.
3. **Novelty effect** — users react differently to anything new; give the experiment time to stabilize.
4. **Interference** — if users in A can interact with users in B, the independence assumption breaks.

```python
# demonstrate peeking: run a test under H₀ and check p-value after each observation
np.random.seed(7)
n_obs = 500

# both groups same true conversion rate — H₀ is true
a = np.random.binomial(1, 0.10, n_obs)
b = np.random.binomial(1, 0.10, n_obs)

p_values_over_time = []
for i in range(20, n_obs + 1, 10):
    _, pv = proportions_ztest(
        [a[:i].sum(), b[:i].sum()],
        [i, i]
    )
    p_values_over_time.append((i, pv))

ns, pvs = zip(*p_values_over_time)
plt.plot(ns, pvs, label='p-value over time')
plt.axhline(0.05, color='red', linestyle='--', label='α=0.05')
plt.xlabel('Observations per group')
plt.ylabel('p-value')
plt.title('Peeking problem: p-value fluctuates under true H₀')
plt.legend()
plt.show()

# how many times does it dip below 0.05?
crossings = sum(pv < 0.05 for pv in pvs)
print(f'Times p < 0.05 (false positive if we stopped early): {crossings}')
```

## Part 4: Correlation and Causation
### Pearson vs Spearman Correlation
**Pearson** measures linear association. Sensitive to outliers and assumes normality.
**Spearman** measures monotonic association using ranks. More robust to outliers and non-linear relationships.

```python
# Pearson vs Spearman — effect of outliers
x = np.linspace(1, 10, 30)
y_clean = x + np.random.normal(0, 0.5, 30)
y_outlier = y_clean.copy()
y_outlier[-1] = 50  # add one extreme outlier

for label, y in [('Clean', y_clean), ('With outlier', y_outlier)]:
    r_pearson, _ = stats.pearsonr(x, y)
    r_spearman, _ = stats.spearmanr(x, y)
    print(f'{label:15} | Pearson r={r_pearson:.3f} | Spearman ρ={r_spearman:.3f}')
```

```python
# visualize the correlation matrix on a synthetic dataset
df = pd.DataFrame({
    'age':     np.random.normal(35, 8, 200),
    'income':  np.random.normal(60000, 15000, 200),
    'spend':   np.random.normal(500, 120, 200),
    'tenure':  np.random.normal(5, 3, 200)
})
# add some structure: older → higher income, higher income → higher spend
df['income'] += df['age'] * 800
df['spend']  += df['income'] * 0.003

plt.figure(figsize=(6, 4))
sns.heatmap(df.corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.title('Pearson Correlation Matrix')
plt.tight_layout()
plt.show()
```

### Simpson's Paradox
A trend that appears in combined data can reverse or disappear when the data is split by a subgroup.
Classic case: UC Berkeley admissions — overall acceptance rate favored men, but within each department it favored women (or was neutral). The aggregation obscured the confound (department applied to).

```python
# Simpson's paradox: synthetic example
# Group A (small sample, high success rate) and Group B (large sample, lower rate)
# Treatment appears worse overall but is better within each subgroup

data = pd.DataFrame({
    'subgroup':   ['Mild'] * 100 + ['Severe'] * 100 + ['Mild'] * 40 + ['Severe'] * 160,
    'treatment':  ['Control'] * 200 + ['Treatment'] * 200,
    'recovered':  (
        [1]*90 + [0]*10 +    # control, mild: 90%
        [1]*30 + [0]*70 +    # control, severe: 30%
        [1]*39 + [0]*1  +    # treatment, mild: 97.5%
        [1]*80 + [0]*80      # treatment, severe: 50%
    )
})

# aggregate (misleading)
agg = data.groupby('treatment')['recovered'].mean()
print('Overall recovery rate (aggregated):')
print(agg.round(3))
print()

# disaggregated (true picture)
disagg = data.groupby(['treatment', 'subgroup'])['recovered'].mean().unstack()
print('Recovery rate by subgroup:')
print(disagg.round(3))
```

### Confounding Variables
Correlation between X and Y may be driven entirely by a third variable Z that causes both.
Observing the correlation does not establish that X causes Y.

```python
# confounding: ice cream sales and drowning both correlate with temperature
n = 365  # one year of daily data
temperature = np.random.normal(20, 8, n)  # daily temperature

# both caused by temperature, not each other
ice_cream = 100 + 3 * temperature + np.random.normal(0, 10, n)
drownings = 2  + 0.1 * temperature + np.random.normal(0, 1, n)

r_naive, p_naive = stats.pearsonr(ice_cream, drownings)

# partial correlation (control for temperature) using residuals
def residuals(y, x):
    slope, intercept, *_ = stats.linregress(x, y)
    return y - (slope * x + intercept)

ice_cream_resid = residuals(ice_cream, temperature)
drownings_resid = residuals(drownings, temperature)

r_partial, p_partial = stats.pearsonr(ice_cream_resid, drownings_resid)

print(f'Naive correlation (ice cream vs drownings):          r={r_naive:.3f}, p={p_naive:.4f}')
print(f'Partial correlation (controlling for temperature):   r={r_partial:.3f}, p={p_partial:.4f}')
print()
print('The naive correlation is spurious — temperature drives both.')
```
