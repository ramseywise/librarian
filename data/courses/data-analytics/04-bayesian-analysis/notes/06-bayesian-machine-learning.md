---
imported_hash: f57491be84108716
title: 6 — Bayesian Machine Learning
summary: The earlier chapters of this pillar estimate a handful of parameters and make a decision.
order: 9
kind: reading
section: Notes
tier: practitioner
depth: core
depth_sections:
  Where this sits: intro
  Ordered categories, zero inflation and over-dispersion: deep
source: learn-ai-engineering/data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning.md
---

# 6 — Bayesian Machine Learning

The earlier chapters of this pillar estimate a handful of parameters and make a decision. Machine learning asks the same questions at a different scale: thousands of parameters, a hidden variable for every data point, and posteriors far too large for the sampler of [chapter 2](02-mcmc-and-pymc.md). Expectation-maximisation gives up the posterior over parameters and keeps a point estimate. This chapter builds it small enough to run, then fits a Bayesian logistic regression by MCMC, and ends on the likelihood choices and the overfitting checks that decide whether a fitted model can be trusted. It maps these onto the BayesianML coursework in this pillar. The two ideas that scale furthest, variational inference and Gaussian processes, are in [chapter 6b](06b-variational-inference-and-gaussian-processes.md).

```python
import numpy as np, pymc as pm, arviz as az
from scipy import stats
SAMPLE = dict(chains=4, cores=1, progressbar=False, random_seed=7)
```

## Where this sits

The coursework is HSE's *Bayesian Methods for Machine Learning*, taken on Coursera. BMH's own ch. 7 was never finished. Its outline (Bayesian answers to overfitting, Salimans' *Don't Overfit* Kaggle solution, predictive distributions, model fitting with BIC, Gaussian processes) is close to the syllabus below.


| Coursework | Topic | Inference method | Key idea |
|---|---|---|---|
| [week_2](../practice/bayesianml/week-2) | Gaussian mixture model | Expectation-maximisation | latent cluster labels, soft assignments |
| [week_4](../practice/bayesianml/week-4) | Markov chains, Bayesian logistic regression | MCMC (Metropolis, NUTS) in PyMC3 | odds ratio with a credible interval |

Weeks 5 and 6 and the final assignment (variational inference, Gaussian processes, Bayesian optimisation) are in [chapter 6b](06b-variational-inference-and-gaussian-processes.md#where-this-sits).

**Runnability:** the coursework is legacy. The environment in `bayesian.yml` pins Python 3.7, TensorFlow 1.15, Keras 2.3.1, `pymc3==3.11.4` and `theano-pymc==1.1.2`, and week 6 adds GPy, GPyOpt and xgboost by pip. Every notebook imports the Coursera `grader` module, which is not included, and none has saved outputs. Read them for the method, and port to current PyMC with [chapter 2's map](02-mcmc-and-pymc.md#pymc3-to-current-pymc) before running. The code in this chapter runs on current NumPy, PyMC and scikit-learn; blocks marked `# illustrative` show the coursework's pinned libraries, and need that conda environment.

## EM for Gaussian mixtures (week 2)

Take [chapter 2's mixture](02-mcmc-and-pymc.md#worked-example-a-two-cluster-mixture), fitted by optimisation instead of sampling. Each point x_i has a hidden label t_i ∈ {1..C}, and the parameters are mixture weights π, means μ_c and covariances Σ_c. If you knew the labels, the parameters would be simple averages. If you knew the parameters, the labels would follow from Bayes' rule. Expectation-maximisation ([Dempster, Laird and Rubin, *JRSS B*, 1977](https://doi.org/10.1111/j.2517-6161.1977.tb01600.x)) alternates between the two.

| Step | Computes | Formula |
|---|---|---|
| E-step | responsibilities γ_ic = P(t_i = c given x_i) | γ_ic ∝ π_c · N(x_i; μ_c, Σ_c), normalised over c |
| M-step | parameters given responsibilities | π_c = mean of γ_·c; μ_c = Σ γ_ic x_i / Σ γ_ic; Σ_c the γ-weighted covariance |
| Loss | lower bound on the log-likelihood | rises monotonically; stop when it plateaus |

The week 2 notebook leaves these as graded functions. Here they are in NumPy, in log space to avoid underflow (the [log-sum-exp trick](../../../programming/computer-science/notes/04-numbers-and-memory.md#log-sum-exp) explains `logaddexp`):

```python
def log_gauss(X, mu, cov):
    d = X - mu
    sign, logdet = np.linalg.slogdet(cov)
    return -0.5 * (np.sum(d * np.linalg.solve(cov, d.T).T, axis=1) + logdet + X.shape[1] * np.log(2 * np.pi))

def e_step(X, pi, mu, cov):
    log_r = np.stack([np.log(pi[c]) + log_gauss(X, mu[c], cov[c]) for c in range(len(pi))], axis=1)
    log_norm = np.logaddexp.reduce(log_r, axis=1, keepdims=True)    # log space avoids underflow
    return np.exp(log_r - log_norm), log_norm.sum()                 # responsibilities, log-likelihood

def m_step(X, r):
    Nk = r.sum(axis=0)
    pi = Nk / len(X)
    mu = (r.T @ X) / Nk[:, None]
    cov = [((r[:, c, None] * (X - mu[c])).T @ (X - mu[c])) / Nk[c] + 1e-6 * np.eye(X.shape[1])
           for c in range(r.shape[1])]
    return pi, mu, np.array(cov)

def train_em(X, C, seed, tol=1e-4, max_iter=200):
    rng = np.random.default_rng(seed)
    pi = np.ones(C) / C
    mu = X[rng.choice(len(X), C, replace=False)]
    cov = np.array([np.cov(X.T)] * C)
    trace = []
    for _ in range(max_iter):
        r, ll = e_step(X, pi, mu, cov)
        trace.append(ll)
        if len(trace) > 1 and abs(trace[-1] - trace[-2]) < tol * abs(trace[-1]):
            break
        pi, mu, cov = m_step(X, r)
    return pi, mu, cov, trace
```

Now fit three clusters of unequal size, from ten random starts:

```python
rng = np.random.default_rng(0)
true_mu = np.array([[0, 0], [6, 1], [1, 6]])
X = np.vstack([rng.multivariate_normal(m, np.eye(2) * s, n)
               for m, s, n in zip(true_mu, (1.0, 0.5, 2.0), (150, 100, 50))])
fits = [train_em(X, C=3, seed=s) for s in range(10)]
final = [f[3][-1] for f in fits]
print("final log-likelihood by restart:", np.round(final, 1))
pi, mu, cov, trace = fits[int(np.argmax(final))]
print("always rising:", all(np.diff(trace) >= -1e-8), " iterations:", len(trace))
print("weights", pi.round(2))
print("means  ", mu.round(2).tolist())
```

```text
final log-likelihood by restart: [-1107.8 -1107.8 -1107.8 -1107.8 -1107.8 -1107.8 -1186.9 -1268.1 -1107.8
 -1107.8]
always rising: True  iterations: 28
weights [0.33 0.5  0.17]
means   [[5.99, 1.01], [-0.14, 0.09], [1.1, 5.85]]
```

Eight restarts agree, and two end far lower, stuck in local optima with different clusters. The log-likelihood rises at every step, as the theory promises, but it only promises a local peak. So run several restarts and keep the best. The fitted weights match the 150, 100 and 50 points by share (0.5, 0.33 and 0.17), and the means are close to those simulated, though the labels are in a different order, which is the label problem from chapter 2 again.

EM vs MCMC on the same model:

| | EM | MCMC ([chapter 2](02-mcmc-and-pymc.md)) |
|---|---|---|
| Output | a point estimate (MAP or MLE) of the parameters | samples from the full posterior |
| Speed | fast, deterministic per restart | slower |
| Uncertainty | none on the parameters | full |
| Failure | local optima, collapsing covariances | slow mixing, label switching |

The `1e-6 * np.eye` in `m_step` guards against the collapsing-covariance failure, where a component shrinks onto a single point and the likelihood rises without limit. Bishop names this a singularity of maximum likelihood that a prior removes (*PRML*, ch. 9, pp. 434 and 441).


## MCMC and Bayesian logistic regression (week 4)

**Task 1, Alice and Bob.** Two sellers set prices from each other's last price plus Gaussian noise. Simulate it from very different starts, discard a burn-in, and compare:

```python
def run_simulation(alice=300.0, bob=300.0, seed=42, hours=10000, burnin=1000):
    rng = np.random.default_rng(seed)
    a_all, b_all = [], []
    for _ in range(burnin + hours):
        alice = 0.6 * bob + 90 + rng.normal(0, 20)         # uses Bob's previous price
        bob = 1.2 * alice - 20 + rng.normal(0, 10)         # uses Alice's current price
        a_all.append(alice); b_all.append(bob)
    return np.array(a_all[burnin:]), np.array(b_all[burnin:])
for start, seed in ((300, 42), (1000, 7), (10, 99)):
    a, b = run_simulation(start, start, seed)
    print(f"start {start:>4}  Alice {a.mean():.1f} (sd {a.std():.1f})  Bob {b.mean():.1f} (sd {b.std():.1f})  corr {np.corrcoef(a, b)[0, 1]:.2f}")
print(f"long-run mean by algebra: Alice {(90 - 0.6 * 20) / (1 - 0.6 * 1.2):.1f}  Bob {1.2 * (90 - 0.6 * 20) / (1 - 0.6 * 1.2) - 20:.1f}")
```

```text
start  300  Alice 279.2 (sd 30.1)  Bob 315.2 (sd 37.6)  corr 0.96
start 1000  Alice 277.9 (sd 30.1)  Bob 313.5 (sd 37.5)  corr 0.96
start   10  Alice 279.0 (sd 29.6)  Bob 314.8 (sd 36.8)  corr 0.96
long-run mean by algebra: Alice 278.6  Bob 314.3
```

Starting at 10 or at 1,000 makes no difference once burn-in is discarded, and the long-run means match the algebra. A stationary distribution that does not depend on where you start is exactly what makes MCMC valid.

**Task 2, logistic regression on US census income.** Does sex affect P(income > $50K), controlling for age, age², education and hours? The coursework's file, `adult_us_postprocessed.csv`, is not included, so we simulate 2,000 rows with a known true odds ratio.

```python
rng = np.random.default_rng(1)
n = 2000
male = rng.binomial(1, 0.6, n)
age = rng.uniform(18, 70, n)
educ = rng.normal(11, 2.5, n)
hours = rng.normal(40, 10, n)
age_z, educ_z, hours_z = [(v - v.mean()) / v.std() for v in (age, educ, hours)]
log_odds = -1.8 + 0.7 * male + 0.9 * age_z - 0.5 * age_z**2 + 0.8 * educ_z + 0.5 * hours_z
y = rng.binomial(1, 1 / (1 + np.exp(-log_odds)))
print(f"simulated rows {n}, share above the line {y.mean():.2f}, true odds ratio {np.exp(0.7):.2f}")
design = np.column_stack([male, age_z, age_z**2, educ_z, hours_z])
```

The week 4 notebook writes the model in PyMC3 through a formula interface that no longer exists:

```python
# illustrative: week_4 coursework, needs the pinned conda env (pymc3==3.11.4, theano-pymc==1.1.2)
with pm.Model() as logistic_model:
    pm.glm.GLM.from_formula(
        "income_more_50K ~ sex + age + age_squared + educ + hours",
        data, family=pm.glm.families.Binomial())
    trace = pm.sample(4000)                      # NUTS chosen automatically

# odds ratio for sex = exp(coefficient); credible interval from the samples
b = trace["sex[T. Male]"][100:]                # short burn-in: sampling started at the MAP
lb, ub = np.percentile(b, 2.5), np.percentile(b, 97.5)
np.exp(lb), np.exp(ub)
```

Current PyMC writes it out directly. [bambi](https://bambinos.github.io/bambi/) offers a formula interface again, though we have not run it here.

```python
def logistic(step=None, draws=1000):
    with pm.Model():
        b0 = pm.Normal("b0", 0, 5)
        b = pm.Normal("b", 0, 2.5, shape=design.shape[1])
        pm.Bernoulli("y", logit_p=b0 + design @ b, observed=y)
        return pm.sample(draws, tune=1000, step=step() if step else None, **SAMPLE)
nuts = logistic()
s = nuts.posterior["b"].sel(b_dim_0=0).values.flatten()
lo, hi = np.exp(np.percentile(s, [2.5, 97.5]))
print(f"odds ratio for male: {np.exp(s).mean():.2f}, 95% interval [{lo:.2f}, {hi:.2f}]")
```

```text
odds ratio for male: 1.65, 95% interval [1.27, 2.12]
```

The true odds ratio is 2.01, and this interval misses it. That isn't a bug. A 95% interval from one simulated dataset leaves out the truth sometimes, and quoting the interval without knowing that would be overconfident. Simulation is the one place you get to see it happen.

The exercise compares Metropolis-Hastings with NUTS:

```python
metro = logistic(step=pm.Metropolis)
for name, idata in (("Metropolis", metro), ("NUTS", nuts)):
    e = az.ess(idata, var_names=["b"])["b"].values
    r = az.rhat(idata, var_names=["b"])["b"].values
    print(f"{name:10s} min ESS {e.min():6.0f} of 4000   max r_hat {r.max():.3f}")
```

```text
Metropolis min ESS    155 of 4000   max r_hat 1.041
NUTS       min ESS   3306 of 4000   max r_hat 1.001
```

From the same number of draws, NUTS has about twenty times the effective samples. It is the same comparison as Challenger in chapter 2, with more dimensions. The coursework ends on the point [chapter 1](01-bayesian-inference.md) makes: a credible interval can be read the way people wish they could read a confidence interval.


## Likelihoods and links: maximum entropy, counts and mixtures

The models above all used a Gaussian or a Bernoulli likelihood without saying why. McElreath's answer is maximum entropy: given what you know about an outcome (its support, its mean or variance), choose the distribution that can be realised in the most ways and so assumes the least more (*Statistical Rethinking*, ch. 9). Ten pebbles tossed into five buckets can make the flat arrangement (two per bucket) 113,400 ways, more than any other, and its entropy is the largest possible, log 5 = 1.609. The Gaussian has the highest entropy of any distribution on the real line with a given variance; the binomial has it for two unordered outcomes with a constant expected value; the Poisson is the binomial's large-n, small-p limit and shares the constraints. He checks the binomial claim by brute force: of 100,000 random distributions over two draws with expected value 1.4, the largest entropy found is 1.221728, against 1.221729 for the binomial with p = 0.7.

![Distribution of entropies of 100,000 random distributions with expected value 1.4, with the binomial at the maximum](../assets/sources/images/statistical-rethinking-fig9-4.png)
*Image Source: McElreath, *Statistical Rethinking* (CRC Press), Fig. 9.4*

Two consequences matter in practice. First, a link function (logit for probabilities, log for rates) keeps predictions in range, but then no coefficient gives a constant change on the outcome scale: a half-unit rise in log-odds from 0 moves probability by about 0.25, and further up the curve the same step moves it far less. Second, WAIC cannot compare models with different outcome distributions, because deviance includes the normalising constants (*Statistical Rethinking*, ch. 9).

### Binomial regression and Simpson's paradox

The UC Berkeley admissions data has 12 rows (6 departments by gender) standing for 4,526 applications; 38.8% were admitted. Re-run in PyMC:

```python
with pm.Model():                                   # department intercepts plus a gender term
    a = pm.Normal("a", 0, 1.5, shape=6)
    bm = pm.Normal("bm", 0, 1)
    pm.Binomial("admit", n=applications, logit_p=a[dept] + bm * male, observed=admitted)
```

```text
pooled (no department):  bm +0.61 (sd 0.07), odds ratio 1.84
with department:         bm -0.10 (sd 0.08), odds ratio 0.91
department intercepts:   [ 0.68  0.64 -0.58 -0.61 -1.06 -2.64]
```

Ignoring department, men have 1.84 times the odds of admission; within departments the sign reverses, because women applied more to the departments with low admission rates (intercepts down to -2.64). That is the book's result (his bm: +0.61, then -0.10), and the pooled model beats the intercept-only model by 91.5 WAIC points while still fitting each department badly (*Statistical Rethinking*, ch. 10). With department intercepts WAIC ties with and without gender (5200.9 and 5201.4), so the data cannot say whether gender matters within departments.

![Posterior validation for the department-intercept model: observed admission proportions against predictions for the six departments](../assets/sources/images/statistical-rethinking-fig10-6.png)
*Image Source: McElreath, *Statistical Rethinking* (CRC Press), Fig. 10.6*

Two warnings from the same chapter. A large coefficient need not be a large effect: a log-odds slope of 0.61 multiplies the odds by 1.84, but from an intercept of 4 it moves the probability from 0.982 to 0.990. And with near-perfect separation flat-prior `glm` returned a slope of 11.43 with a standard deviation of 2,955 and no warning, while a Normal(0, 10) prior gave 4.02 (*Statistical Rethinking*, ch. 10). Counts should never be converted to proportions first, which discards the sample size; a Poisson model for rates observed over different exposures takes log(exposure) as an offset (his monastery simulation recovers 1.61 against a true 1.5 and 0.59 against 0.5). His Oceanic tools example, ten societies with a Poisson likelihood, adds a warning about correlated parameters: contact and the contact-by-population interaction both overlap zero (correlation -0.99), yet 95.27% of posterior mass says a high-contact island at log-population 8 has more tools.

### Ordered categories, zero inflation and over-dispersion

An ordered logit gives K categories K-1 cutpoints on the log-cumulative-odds scale, and a linear predictor is subtracted from all of them at once. With the 9,930 trolley-problem responses (1 to 7) the intercept-only cutpoints are the logit of the cumulative proportions, so they can be checked by eye.

![Re-describing the response histogram as cumulative proportions and then log-cumulative-odds](../assets/sources/images/statistical-rethinking-fig11-1.png)
*Image Source: McElreath, *Statistical Rethinking* (CRC Press), Fig. 11.1*

The data is not in the repo, so the re-run simulates 9,930 responses from the book's cumulative proportions and fits `pm.OrderedLogistic("y", eta=0.0, cutpoints=c)` with an ordered transform:

```text
logit of the cumulative proportions: [-1.92 -1.27 -0.72  0.25  0.89  1.77]
OrderedLogistic recovers:            [-1.91 -1.26 -0.73  0.23  0.87  1.74]
```

In the book's interaction model, WAIC is 36,929.4 against 37,090.3 for the additive one (difference 160.8, standard error 25.80), and the contact-by-intention slope of -1.27 is the largest (*Statistical Rethinking*, ch. 11).

A zero-inflated Poisson mixes two processes: a zero comes from not working (probability p) or from working and producing none, with likelihood p + (1 - p) exp(-lambda). A simulation of 365 days with p = 0.2 and rate 1.0 is recovered closely in his run (0.1994 and 1.05). In ours, seed 11 gave 184 zero days and estimates of 0.13 (true 0.20) and 0.85 (true 1.00): the two sources of zeros are only weakly identified, so one run can miss by this much.

Over-dispersed counts get a mixture too. A beta-binomial gives each row its own probability from a Beta distribution with mean pbar and concentration theta. On the Berkeley data without department, the book has theta 2.77 (sd 0.96) and our re-run gives pbar 0.41 and theta 2.77 (sd 0.95), a close reproduction. WAIC is unsafe with these models (he falls back on DIC), and an Exponential(1) prior on theta samples better than a half-Cauchy at the same inference.

GLM mechanics, the link-function table and the Poisson offset belong with [regression and GLMs](../../02-probability-and-statistics/notes/06b-logistic-regression-and-poisson-glms.md); the multilevel versions of these models are in [chapter 7](07-multilevel-models-and-partial-pooling.md) and [7b](07b-varying-slopes-measurement-error-and-missing-data.md).


## Overfitting and information criteria

Everything above fits a model and asks how well it explains the data it saw. McElreath's chapter on overfitting makes the point that this question has the wrong answer built in: fit to the sample improves with every parameter. Polynomials of degree 1 to 6 fitted to brain volume against body mass for seven hominin species reach R^2 of 0.49 at degree 1, 0.99 at degree 5 and 1.00 at degree 6, where seven parameters pass through seven points and the curve predicts a negative brain size near 58 kg (*Statistical Rethinking*, ch. 6).

Deviance, minus twice the log-likelihood, makes the same point on held-out data. This is the chapter's simulation, re-run: y ~ Normal(mu, 1) with mu = 0.15 x1 - 0.4 x2, so the true model has three parameters; models with one to five parameters are fitted by least squares to a training sample and scored on a fresh one of the same size.

```python
def dev(y, mu):                       # -2 * log-likelihood, sigma fixed at 1
    return (np.log(2 * np.pi) + (y - mu) ** 2).sum()

def one_run(n, k, rng):
    X = rng.normal(size=(2 * n, 4))
    y = 0.15 * X[:, 0] - 0.4 * X[:, 1] + rng.normal(size=2 * n)
    A = np.c_[np.ones(2 * n), X[:, :k - 1]]           # intercept + first k-1 predictors
    b = np.linalg.lstsq(A[:n], y[:n], rcond=None)[0]
    return dev(y[:n], A[:n] @ b), dev(y[n:], A[n:] @ b)   # train, test
```

```text
N=20   params=1  train 59.3  test 61.5  gap 2.2
N=20   params=2  train 57.5  test 62.3  gap 4.8
N=20   params=3  train 53.7  test 60.3  gap 6.6
N=20   params=4  train 52.8  test 61.9  gap 9.1
N=20   params=5  train 51.8  test 63.9  gap 12.1
N=100  params=1  train 300.3  test 303.0  gap 2.7
N=100  params=3  train 280.9  test 286.9  gap 6.0
N=100  params=5  train 279.1  test 289.3  gap 10.2
```

(5,000 runs per row; the book used 10,000 and prints slightly different gaps, 2, 4.1, 5.3, 7.6, 9.7 at N = 20.) Training deviance falls with every parameter, and test deviance is lowest at three, the true model. At N = 20 the two-parameter model is worse out of sample than the one-parameter one. The gap between test and train is close to twice the number of parameters, which is the idea behind AIC = D_train + 2p. AIC is reliable only with flat priors, a near-Gaussian posterior and N much larger than the parameter count. Regularising priors break the first condition, which is why [chapter 3](03-priors-and-bandits.md) pairs them with a different criterion.

![Training and test deviance against number of parameters at N = 20 and N = 100](../assets/sources/images/statistical-rethinking-fig6-7.png)

*Image Source: McElreath, *Statistical Rethinking* (CRC Press), Fig. 6.7*

WAIC is the criterion that needs no Gaussian assumption. It is computed pointwise from the posterior draws: WAIC = -2(lppd - pWAIC), where lppd sums over observations the log of the average likelihood across draws, and pWAIC sums over observations the variance across draws of the log-likelihood. In the book's simulation with Normal(0, 100) and Normal(0, 0.5) priors on the slopes, DIC and WAIC land within about 1 deviance point of the true average test deviance in most settings, WAIC the closer. The same book's own caveats apply: the criteria assume test data come from the process that made the training data, WAIC is hard to define for dependent data such as time series, and none of them is consistent for picking the true model.

Read a comparison by its difference and that difference's standard error, not by the ranking. On the primate milk data, with models fitted to the 17 species with complete cases, the model with neocortex and log body mass has WAIC -15.0 and an Akaike weight of 0.93, against -8.3 for the intercept-only model. The difference is 6.7 with a standard error of 7.26, and the chapter's own simulation of that difference puts the chance the ranking reverses at 0.18. A weight is the probability the model predicts best, conditional on the set compared. Averaging predictions across models, not parameters, barely moves the mean but widens the interval enough to include a zero slope for neocortex. The criteria answer a predictive question only: In a simulated plant experiment, the model that includes a post-treatment variable (fungus) fits better and still hides a treatment slope of 1.07 behind an estimate of -0.27 (*Statistical Rethinking*, ch. 5). The python route is `az.compare` on `InferenceData` objects that carry `log_likelihood`.


## Pitfalls

| Pitfall | What goes wrong | Fix |
|---|---|---|
| One EM start | Two of ten restarts above ended in worse optima | Restart and keep the best bound |
| Running the coursework on current packages | PyMC3, Theano, TF 1 and `grader` are not there | Use the pinned environment, or port with chapter 2's map |

---

## Try it

1. In `em_run`, change `C` to 4. What should happen to the final log-likelihood, and does that mean four clusters is correct?

<details>
<summary>Answers</summary>

1. KL(prior ‖ prior) is zero by definition. The ELBO is then just the expected reconstruction (−3.42), and it is the worst of the four.

</details>

---

## Interview checklist

| Prompt | Answer |
|---|---|
| What does EM do? | Alternates between computing responsibilities and re-fitting parameters; the likelihood never falls, but it finds a local optimum |
| EM or MCMC for a mixture? | EM for a fast point estimate; MCMC when you need parameter uncertainty |

---

## Further reading

| Topic | Source |
|---|---|
| EM, VI and GPs alongside the frequentist toolkit | Efron and Hastie, *Computer Age Statistical Inference* ([book site](https://hastie.su.domains/CASI/)) |
| Bayesian regression and multilevel models in depth | McElreath, [*Statistical Rethinking* lectures](https://www.youtube.com/playlist?list=PLDcUM9US4XdPz-KxHM4XHt7uUVGWWVSus) |
| Modern PyMC | [pymc.io examples gallery](https://www.pymc.io/projects/examples/en/latest/gallery.html), [bambi](https://bambinos.github.io/bambi/) |


---

## Next

[Chapter 6b: Variational Inference and Gaussian Processes](06b-variational-inference-and-gaussian-processes.md) takes the same questions to posteriors too large to sample: variational inference, the VAE, Gaussian processes and Bayesian optimisation. It is a specialist extension and can be skipped. [Chapter 7: Multilevel Models and Partial Pooling](07-multilevel-models-and-partial-pooling.md) returns to the Larkspur experiment with many markets in it: how much to trust each market's own number, what partial pooling does to the winning segment's effect, when it does not help, and when clustered standard errors or fixed effects are the better tool.
