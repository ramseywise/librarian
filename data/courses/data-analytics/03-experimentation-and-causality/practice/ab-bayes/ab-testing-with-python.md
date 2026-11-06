---
title: AB Testing
summary: 'from statsmodels.stats.proportion import proportions_ztest, proportion_confint # when to use t-test or chi 2'
order: 7
kind: notebook
section: Practice / AB Bayes
source: learn-ai-engineering/data-analytics/03-experimentation-and-causality/practice/AB-Bayes/AB_Testing_with_Python.ipynb
---

# AB Testing

```python
pip install statsmodels
```

```python
# import packages
import numpy as np
import pandas as pd
import scipy.stats as stats
import scipy as sp
import statsmodels as sm
import matplotlib.pyplot as plt

from statsmodels.stats.proportion import proportions_ztest, proportion_confint
# when to use t-test or chi 2

%matplotlib inline
```

## Basic Treatment-Control Groups

We use these tests for different reasons and under different circumstances.

`𝑧-test` assumes that our observations are independently drawn from a Normal distribution with unknown mean and known variance. A 𝑧-test is used primarily when we have quantitative data. (i.e. weights of rodents, ages of individuals, systolic blood pressure, etc.) However, 𝑧-tests can also be used when interested in proportions. (i.e. the proportion of people who get at least eight hours of sleep, etc.)

`𝑡-test` assumes that our observations are independently drawn from a Normal distribution with unknown mean and unknown variance. Note that with a 𝑡-test, we do not know the population variance. This is far more common than knowing the population variance, so a 𝑡-test is generally more appropriate than a 𝑧-test, but practically there will be little difference between the two if sample sizes are large.

With 𝑧- and 𝑡-tests, your alternative hypothesis will be that your population mean (or population proportion) of one group is either not equal, less than, or greater than the population mean (or proportion) of the other group. This will depend on the type of analysis you seek to do, but your null and alternative hypotheses directly compare the means/proportions of the two groups.

`Chi-squared test`. Whereas 𝑧- and 𝑡-tests concern quantitative data (or proportions in the case of 𝑧), chi-squared tests are appropriate for qualitative data. Again, the assumption is that observations are independent of one another. In this case, you aren't seeking a particular relationship. Your null hypothesis is that no relationship exists between variable one and variable two. Your alternative hypothesis is that a relationship does exist. This doesn't give you specifics as to how this relationship exists (i.e. in which direction the relationship goes) but it will provide evidence that a relationship does (or does not) exist between your independent variable and your groups.

`Fisher's exact test`. One drawback to the chi-squared test is that it is asymptotic. This means that the 𝑝-value is accurate for very large sample sizes. However, if your sample sizes are small, then the 𝑝-value may not be quite as accurate. As such, Fisher's exact test allows you to exactly calculate the 𝑝-value of your data and not rely on approximations that will be poor if your sample sizes are small.

```python
# read data
df = pd.read_csv('ab_data.csv')
df.head()
```

```python
# the dataset contains users that have experienced both the new and old pages.
pd.crosstab(df['group'], df['landing_page'])
```

```python
# drop duplicates
session_counts = df['user_id'].value_counts(ascending=False)
duplicates = session_counts[session_counts > 1].index
df = df[~df['user_id'].isin(duplicates)]
```

```python
# Calculate effect size based on expected rates
effect_size = sms.proportion_effectsize(0.13, 0.15)

# Calculate sample size needed
required_n = sms.NormalIndPower().solve_power(
    effect_size,
    power=0.8,
    alpha=0.05,
    ratio=1
    )
required_n = ceil(required_n)
print(required_n)

# sample users to test
control_sample = df[df['group'] == 'control'].sample(n=required_n, random_state=1)
treatment_sample = df[df['group'] == 'treatment'].sample(n=required_n, random_state=1)

ab_test = pd.concat([control_sample, treatment_sample], axis=0)
ab_test.reset_index(drop=True, inplace=True)
ab_test
```

```python
# check groups are 50-50
## check out bayesian recursive learning method of adjusting proportions after establishing prior
ab_test['group'].value_counts()
```

```python
# calculate group conversion rates
conversion_rates = ab_test.groupby('group')['converted']

std_p = lambda x: np.std(x, ddof=0)              # Std. deviation of the proportion
se_p = lambda x: stats.sem(x, ddof=0)            # Std. error of the proportion (std / sqrt(n))

conversion_rates = conversion_rates.agg([np.mean, std_p, se_p])
conversion_rates.columns = ['conversion_rate', 'std_deviation', 'std_error']


conversion_rates.style.format('{:.3f}')
```

```python
# calculate z statistic
control_results = ab_test[ab_test['group'] == 'control']['converted']
treatment_results = ab_test[ab_test['group'] == 'treatment']['converted']
n_con = control_results.count()
n_treat = treatment_results.count()
successes = [control_results.sum(), treatment_results.sum()]
nobs = [n_con, n_treat]

z_stat, pval = proportions_ztest(successes, nobs=nobs)
(lower_con, lower_treat), (upper_con, upper_treat) = proportion_confint(successes, nobs=nobs, alpha=0.05)

print(f'z statistic: {z_stat:.2f}')
print(f'p-value: {pval:.3f}')
print(f'ci 95% for control group: [{lower_con:.3f}, {upper_con:.3f}]')
print(f'ci 95% for treatment group: [{lower_treat:.3f}, {upper_treat:.3f}]')
```

```python
from scipy.stats import ttest_ind

ttest,pval = ttest_ind(control_results,treatment_results)
print('t statistic: ', ttest)
print("p-value",pval)
```

```python
from scipy.stats import chi2_contingency, chi2

contingency_table=pd.crosstab(ab_test["group"],ab_test["converted"])
Observed_Values = contingency_table.values
b=stats.chi2_contingency(contingency_table)
Expected_Values = b[3]

chi_square=sum([(o-e)**2./e for o,e in zip(Observed_Values,Expected_Values)])
chi_square_statistic=chi_square[0]+chi_square[1]
print("chi-square statistic:-",chi_square_statistic)
```
