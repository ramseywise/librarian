---
imported_hash: 32fcc329f6b271bb
title: Using PyMC3
summary: In this assignment, we will learn how to use a library for probabilistic programming and inference called <a href="http://docs.pymc.io/">PyMC3</a>.
order: 4
kind: notebook
section: BayesianML master / Week 4
source: learn-ai-engineering/data-analytics/Bayes/BayesianML-master/week_4/Week4. Practical Assignment. MCMC.ipynb
---

> **Archival note (#37 — PyMC3 → PyMC 5):** This notebook uses PyMC3 (Theano backend). PyMC3 is incompatible with PyMC 4/5 (PyTensor backend) — no drop-in migration path exists. **Decision: pin.** To run, install: `pip install pymc3==3.11.4 theano-pymc`. A full port would require rewriting Theano ops to PyTensor, which is out of scope for this curriculum path. Use the CamDavidsonPilon `_PyMC_current` chapter notebooks for PyMC 5 equivalents.

# Using PyMC3

In this assignment, we will learn how to use a library for probabilistic programming and inference called <a href="http://docs.pymc.io/">PyMC3</a>.

### Installation
Libraries that are required for this tasks can be installed with the following command (if you use PyPI):

```bash
pip install pymc3 pandas numpy matplotlib seaborn
```

You can also install pymc3 from source using <a href="https://github.com/pymc-devs/pymc3#installation">the instruction</a>.

```python
import numpy as np
import pandas as pd
import numpy.random as rnd
import seaborn as sns
from matplotlib import animation
import pymc3 as pm
from grader import Grader
%pylab inline
```

### Grading
We will create a grader instance below and use it to collect your answers. Note that these outputs will be stored locally inside grader and will be uploaded to the platform only after running submitting function in the last part of this assignment. If you want to make a partial submission, you can run that cell anytime you want.

```python
grader = Grader()
```

## Task 1. Alice and Bob

Alice and Bob are trading on the market. Both of them are selling the Thing and want to get as high profit as possible.
Every hour they check out with each other's prices and adjust their prices to compete on the market. Although they have different strategies for price setting.

**Alice**: takes Bob's price during the **previous** hour, multiply by 0.6, add 90\$, add Gaussian noise from $N(0, 20^2)$.

**Bob**: takes Alice's price during the **current** hour, multiply by 1.2 and subtract 20\$, add Gaussian noise from $N(0, 10^2)$.

The problem is to find the joint distribution of Alice and Bob's prices after many hours of such an experiment.

### Task 1.1

Implement the `run_simulation` function according to the description above.

```python
def run_simulation(alice_start_price=300.0, bob_start_price=300.0, seed=42, num_hours=10000, burnin=1000):
    """Simulates an evolution of prices set by Bob and Alice.

    The function should simulate Alice and Bob behavior for `burnin' hours, then ignore the obtained
    simulation results, and then simulate it for `num_hours' more.
    The initial burnin (also sometimes called warmup) is done to make sure that the distribution stabilized.

    Please don't change the signature of the function.

    Returns:
        two lists, with Alice and with Bob prices. Both lists should be of length num_hours.
    """
    np.random.seed(seed)

    alice_prices = [alice_start_price]
    bob_prices = [bob_start_price]

    #### YOUR CODE HERE ####

    # Burn-in
    for burn_hour in range(1,burnin):
        alice_prices.append(compute_alice_price(bob_prices[burn_hour-1]))
        bob_prices.append(compute_bob_price(alice_prices[burn_hour]))

    for hour in range(burnin,burnin+num_hours):
        alice_prices.append(compute_alice_price(bob_prices[hour-1]))
        bob_prices.append(compute_bob_price(alice_prices[hour]))



    ### END OF YOUR CODE ###

    return alice_prices[burnin:], bob_prices[burnin:]

def compute_alice_price(bob_prev_price):
    alice_price = bob_prev_price*0.6 + 90 + np.random.normal(loc=0,scale=20)
    return alice_price

def compute_bob_price(alice_curr_price):
    bob_price = alice_curr_price*1.2 - 20 + np.random.normal(loc=0,scale=10)
    return bob_price
```

```python
alice_prices, bob_prices = run_simulation(alice_start_price=300, bob_start_price=300, seed=42, num_hours=3, burnin=1)
if len(alice_prices) != 3:
    raise RuntimeError('Make sure that the function returns `num_hours` data points.')
grader.submit_simulation_trajectory(alice_prices, bob_prices)
```

### Task 1.2
What is the average prices for Alice and Bob after the burnin period? Whose prices are higher?

```python
#### YOUR CODE HERE ####
alice_prices, bob_prices = run_simulation()
average_alice_price = np.asarray(alice_prices).mean()
average_bob_price = np.asarray(bob_prices).mean()
### END OF YOUR CODE ###
grader.submit_simulation_mean(average_alice_price, average_bob_price)
```

### Task 1.3

Let's look at the 2-d histogram of prices, computed using kernel density estimation.

```python
data = np.array(run_simulation())
sns.jointplot(data[0, :], data[1, :], stat_func=None, kind='kde')
```

Clearly, the prices of Bob and Alce are highly correlated. What is the Pearson correlation coefficient of Alice and Bob prices?

```python
#### YOUR CODE HERE ####
from scipy.stats import pearsonr
data = np.array(run_simulation(alice_start_price=100.0, bob_start_price=20.0, seed=100, num_hours=10000, burnin=1000))
correlation,p_val = pearsonr(data[0,:],data[1,:])
### END OF YOUR CODE ###
grader.submit_simulation_correlation(correlation)
```

### Task 1.4

We observe an interesting effect here: seems like the bivariate distribution of Alice and Bob prices converges to a correlated bivariate Gaussian distribution.

Let's check, whether the results change if we use different random seed and starting points.

```python
# Pick different starting prices, e.g 10, 1000, 10000 for Bob and Alice.
# Does the joint distribution of the two prices depend on these parameters?
POSSIBLE_ANSWERS = {
    0: 'Depends on random seed and starting prices',
    1: 'Depends only on random seed',
    2: 'Depends only on starting prices',
    3: 'Does not depend on random seed and starting prices'
}

idx = 3
answer = POSSIBLE_ANSWERS[idx]
grader.submit_simulation_depends(answer)
```

## Task 2. Logistic regression with PyMC3

Logistic regression is a powerful model that allows you to analyze how a set of features affects some binary target label. Posterior distribution over the weights gives us an estimation of the influence of each particular feature on the probability of the target being equal to one. But most importantly, posterior distribution gives us the interval estimates for each weight of the model. This is very important for data analysis when you want to not only provide a good model but also estimate the uncertainty of your conclusions.

In this task, we will learn how to use PyMC3 library to perform approximate Bayesian inference for logistic regression.

This part of the assignment is based on the logistic regression tutorial by Peadar Coyle and J. Benjamin Cook.

### Logistic regression.

The problem here is to model how the probability that a person has salary $\geq$ \$50K is affected by his/her age, education, sex and other features.

Let $y_i = 1$ if i-th person's salary is $\geq$ \$50K and $y_i = 0$ otherwise. Let $x_{ij}$ be $j$-th feature of $i$-th person.

Logistic regression models this probabilty in the following way:

$$p(y_i = 1 \mid \beta) = \sigma (\beta_1 x_{i1} + \beta_2 x_{i2} + \dots + \beta_k x_{ik} ), $$

where $\sigma(t) = \frac1{1 + e^{-t}}$

#### Odds ratio.
Let's try to answer the following question: does a gender of a person affects his or her salary? To do it we will use the concept of *odds*.

If we have a binary random variable $y$ (which may indicate whether a person makes \$50K) and if the probabilty of the positive outcome $p(y = 1)$ is for example 0.8, we will say that the *odds* are 4 to 1 (or just 4 for short), because succeding is 4 time more likely than failing $\frac{p(y = 1)}{p(y = 0)} = \frac{0.8}{0.2} = 4$.

Now, let's return to the effect of gender on the salary. Let's compute the **ratio** between the odds of a male having salary $\geq $ \$50K and the odds of a female (with the same level of education, experience and everything else) having salary $\geq$ \$50K. The first feature of each person in the dataset is the gender. Specifically, $x_{i1} = 0$ if the person is female and $x_{i1} = 1$ otherwise. Consider two people $i$ and $j$ having all but one features the same with the only difference in $x_{i1} \neq x_{j1}$.

If the logistic regression model above estimates the probabilities exactly, the odds for a male will be (check it!):
$$
\frac{p(y_i = 1 \mid x_{i1}=1, x_{i2}, \ldots, x_{ik})}{p(y_i = 0 \mid x_{i1}=1, x_{i2}, \ldots, x_{ik})} = \frac{\sigma(\beta_1 + \beta_2 x_{i2} + \ldots)}{1 - \sigma(\beta_1 + \beta_2 x_{i2} + \ldots)} = \exp(\beta_1 + \beta_2 x_{i2} + \ldots)
$$

Now the ratio of the male and female odds will be:
$$
\frac{\exp(\beta_1 \cdot 1 + \beta_2 x_{i2} + \ldots)}{\exp(\beta_1 \cdot 0 + \beta_2 x_{i2} + \ldots)} = \exp(\beta_1)
$$

So given the correct logistic regression model, we can estimate odds ratio for some feature (gender in this example) by just looking at the corresponding coefficient. But of course, even if all the logistic regression assumptions are met we cannot estimate the coefficient exactly from real-world data, it's just too noisy. So it would be really nice to build an interval estimate, which would tell us something along the lines "with probability 0.95 the odds ratio is greater than 0.8 and less than 1.2, so we cannot conclude that there is any gender discrimination in the salaries" (or vice versa, that "with probability 0.95 the odds ratio is greater than 1.5 and less than 1.9 and the discrimination takes place because a male has at least 1.5 higher probability to get >$50k than a female with the same level of education, age, etc."). In Bayesian statistics, this interval estimate is called *credible interval*.

Unfortunately, it's impossible to compute this credible interval analytically. So let's use MCMC for that!

#### Credible interval
A credible interval for the value of $\exp(\beta_1)$ is an interval $[a, b]$ such that $p(a \leq \exp(\beta_1) \leq b \mid X_{\text{train}}, y_{\text{train}})$ is $0.95$ (or some other predefined value). To compute the interval, we need access to the posterior distribution $p(\exp(\beta_1) \mid X_{\text{train}}, y_{\text{train}})$.

Lets for simplicity focus on the posterior on the parameters $p(\beta_1 \mid X_{\text{train}}, y_{\text{train}})$ since if we compute it, we can always find $[a, b]$ such that $p(\log a \leq \beta_1 \leq \log b \mid X_{\text{train}}, y_{\text{train}}) = p(a \leq \exp(\beta_1) \leq b \mid X_{\text{train}}, y_{\text{train}}) = 0.95$

### Task 2.1 MAP inference

Let's read the dataset. This is a post-processed version of the [UCI Adult dataset](http://archive.ics.uci.edu/ml/datasets/Adult).

```python
data = pd.read_csv("adult_us_postprocessed.csv")
data.head()
```

Each row of the dataset is a person with his (her) features. The last column is the target variable $y$. 1 indicates that this person's annual salary is more than $50K.

First of all let's set up a Bayesian logistic regression model (i.e. define priors on the parameters $\alpha$ and $\beta$ of the model) that predicts the value of "income_more_50K" based on person's age and education:

$$
p(y = 1 \mid \alpha, \beta_1, \beta_2) = \sigma(\alpha + \beta_1 x_1 + \beta_2 x_2) \\
\alpha \sim N(0, 100^2) \\
\beta_1 \sim N(0, 100^2) \\
\beta_2 \sim N(0, 100^2), \\
$$

where $x_1$ is a person's age, $x_2$ is his/her level of education, y indicates his/her level of income, $\alpha$, $\beta_1$ and $\beta_2$ are paramters of the model.

```python
with pm.Model() as manual_logistic_model:
    # Declare pymc random variables for logistic regression coefficients with uninformative
    # prior distributions N(0, 100^2) on each weight using pm.Normal.
    # Don't forget to give each variable a unique name.

    x_1 = np.asarray(data['age'])
    x_2 = np.asarray(data['educ'])
    target = np.asarray(data['income_more_50K'])

    num_samples = x_1.shape[0]

    #### YOUR CODE HERE ####

    alpha = pm.Normal('alpha',mu=0,sd=100)
    beta_1 = pm.Normal('beta_1',mu=0,sd=100)
    beta_2 = pm.Normal('beta_2',mu=0,sd=100)

    ### END OF YOUR CODE ###

    # Thansform these random variables into vector of probabilities p(y_i=1) using logistic regression model specified
    # above. PyMC random variables are theano shared variables and support simple mathematical operations.
    # For example:
    # z = pm.Normal('x', 0, 1) * np.array([1, 2, 3]) + pm.Normal('y', 0, 1) * np.array([4, 5, 6])`
    # is a correct PyMC expression.
    # Use pm.invlogit for the sigmoid function.

    #### YOUR CODE HERE ####

    y_lin = alpha + beta_1*x_1 + beta_2*x_2
    y_log = pm.invlogit(y_lin)

    ### END OF YOUR CODE ###

    # Declare PyMC Bernoulli random vector with probability of success equal to the corresponding value
    # given by the sigmoid function.
    # Supply target vector using "observed" argument in the constructor.

    #### YOUR CODE HERE ####
    likelihood_dist = pm.Bernoulli('L_hood',p=y_log,observed=target)

    ### END OF YOUR CODE ###

    # Use pm.find_MAP() to find the maximum a-posteriori estimate for the vector of logistic regression weights.
    map_estimate = pm.find_MAP()
    print(map_estimate)
```

Sumbit MAP estimations of corresponding coefficients:

```python
with pm.Model() as logistic_model:
    # There's a simpler interface for generalized linear models in pymc3.
    # Try to train the same model using pm.glm.GLM.from_formula.
    # Do not forget to specify that the target variable is binary (and hence follows Binomial distribution).

    #### YOUR CODE HERE ####
    pm.glm.GLM.from_formula('income_more_50K ~ age + educ',data,family=pm.glm.families.Binomial())

    ### END OF YOUR CODE ###
    map_estimate = pm.find_MAP()
    print(map_estimate)
```

```python
beta_age_coefficient = 0.04348259
beta_education_coefficient = 0.36210894
grader.submit_pymc_map_estimates(beta_age_coefficient, beta_education_coefficient)
```

### Task 2.2 MCMC

To find credible regions let's perform MCMC inference.

```python
# You will need the following function to visualize the sampling process.
# You don't need to change it.
def plot_traces(traces, burnin=2000):
    '''
    Convenience function:
    Plot traces with overlaid means and values
    '''

    ax = pm.traceplot(traces[burnin:], figsize=(12,len(traces.varnames)*1.5),
        lines={k: v['mean'] for k, v in pm.summary(traces[burnin:]).iterrows()})

    for i, mn in enumerate(pm.summary(traces[burnin:])['mean']):
        ax[i,0].annotate('{:.2f}'.format(mn), xy=(mn,0), xycoords='data'
                    ,xytext=(5,10), textcoords='offset points', rotation=90
                    ,va='bottom', fontsize='large', color='#AA0022')
```

#### Metropolis-Hastings
Let's use Metropolis-Hastings algorithm for finding the samples from the posterior distribution.

Once you wrote the code, explore the hyperparameters of Metropolis-Hastings such as the proposal distribution variance to speed up the convergence. You can use `plot_traces` function in the next cell to visually inspect the convergence.

You may also use MAP-estimate to initialize the sampling scheme to speed things up. This will make the warmup (burnin) period shorter since you will start from a probable point.

```python
with pm.Model() as logistic_model:
    # Since it is unlikely that the dependency between the age and salary is linear, we will include age squared
    # into features so that we can model dependency that favors certain ages.
    # Train Bayesian logistic regression model on the following features: sex, age, age^2, educ, hours
    # Use pm.sample to run MCMC to train this model.
    # To specify the particular sampler method (Metropolis-Hastings) to pm.sample,
    # use `pm.Metropolis`.
    # Train your model for 400 samples.
    # Save the output of pm.sample to a variable: this is the trace of the sampling procedure and will be used
    # to estimate the statistics of the posterior distribution.

    #### YOUR CODE HERE ####
    pm.glm.GLM.from_formula('income_more_50K ~ sex + age + age*age + educ',data,family=pm.glm.families.Binomial())
    step = pm.Metropolis()
    trace = pm.sample(400,step=step,init='MAP')


    ### END OF YOUR CODE ###
```

```python
plot_traces(trace, burnin=200)
```

#### NUTS sampler
Use pm.sample without specifying a particular sampling method (pymc3 will choose it automatically).
The sampling algorithm that will be used in this case is NUTS, which is a form of Hamiltonian Monte Carlo, in which parameters are tuned automatically. This is an advanced method that we hadn't cover in the lectures, but it usually converges faster and gives less correlated samples compared to vanilla Metropolis-Hastings.

Since the NUTS sampler doesn't require to tune hyperparameters, let's run it for 10 times more iterations than Metropolis-Hastings.

```python
ages_data = data['age']
data['age_squared'] = ages_data**2
data.head()
```

```python
with pm.Model() as logistic_model:
    # Train Bayesian logistic regression model on the following features: sex, age, age_squared, educ, hours
    # Use pm.sample to run MCMC to train this model.
    # Train your model for *4000* samples (ten times more than before).
    # Training can take a while, so relax and wait :)



    #### YOUR CODE HERE ####

    pm.glm.GLM.from_formula('income_more_50K ~ sex + age + age_squared + educ + hours',data,family=pm.glm.families.Binomial())
    step = pm.NUTS()
    trace = pm.sample(4000,step=step,init='MAP')


    ### END OF YOUR CODE ###
```

```python
plot_traces(trace)
```

#### Estimating the odds ratio
Now, let's build the posterior distribution on the odds ratio given the dataset (approximated by MCMC).

```python
# We don't need to use a large burn-in here, since we initialize sampling
# from a good point (from our approximation of the most probable
# point (MAP) to be more precise).
burnin = 100
b = trace['sex[T. Male]'][burnin:]
plt.hist(np.exp(b), bins=20, normed=True)
plt.xlabel("Odds Ratio")
plt.show()
```

Finally, we can find a credible interval  (recall that credible intervals are Bayesian and confidence intervals are frequentist) for this quantity. This may be the best part about Bayesian statistics: we get to interpret credibility intervals the way we've always wanted to interpret them. We are 95% confident that the odds ratio lies within our interval!

```python
lb, ub = np.percentile(b, 2.5), np.percentile(b, 97.5)
print("P(%.3f < Odds Ratio < %.3f) = 0.95" % (np.exp(lb), np.exp(ub)))
```

```python
# Submit the obtained credible interval.
grader.submit_pymc_odds_ratio_interval(np.exp(lb), np.exp(ub))
```

### Task 2.3 interpreting the results

```python
# Does the gender affects salary in the provided dataset?
# (Note that the data is from 1996 and maybe not representative
# of the current situation in the world.)
POSSIBLE_ANSWERS = {
    0: 'No, there is certainly no discrimination',
    1: 'We cannot say for sure',
    2: 'Yes, we are 95% sure that a female is *less* likely to get >$50K than a male with the same age, level of education, etc.',
    3: 'Yes, we are 95% sure that a female is *more* likely to get >$50K than a male with the same age, level of education, etc.',
}

idx = 2
answer = POSSIBLE_ANSWERS[idx]
grader.submit_is_there_discrimination(answer)
```

# Authorization & Submission
To submit assignment parts to Cousera platform, please, enter your e-mail and token into variables below. You can generate token on this programming assignment page. <b>Note:</b> Token expires 30 minutes after generation.

```python
STUDENT_EMAIL = "<redacted>"
STUDENT_TOKEN = "<redacted>"
grader.status()
```

If you want to submit these answers, run cell below

```python
grader.submit(STUDENT_EMAIL, STUDENT_TOKEN)
```

# (Optional) generating videos of sampling process
For this (optional) part you will need to install ffmpeg, e.g. by the following command on linux

    apt-get install ffmpeg

or the following command on Mac

    brew install ffmpeg

## Setting things up
You don't need to modify the code below, it sets up the plotting functions. The code is based on [MCMC visualization tutorial](https://twiecki.github.io/blog/2014/01/02/visualizing-mcmc/).

```python
from IPython.display import HTML

# Number of MCMC iteration to animate.
samples = 400

figsize(6, 6)
fig = plt.figure()
s_width = (0.81, 1.29)
a_width = (0.11, 0.39)
samples_width = (0, samples)
ax1 = fig.add_subplot(221, xlim=s_width, ylim=samples_width)
ax2 = fig.add_subplot(224, xlim=samples_width, ylim=a_width)
ax3 = fig.add_subplot(223, xlim=s_width, ylim=a_width,
                      xlabel='male coef',
                      ylabel='educ coef')
fig.subplots_adjust(wspace=0.0, hspace=0.0)
line1, = ax1.plot([], [], lw=1)
line2, = ax2.plot([], [], lw=1)
line3, = ax3.plot([], [], 'o', lw=2, alpha=.1)
line4, = ax3.plot([], [], lw=1, alpha=.3)
line5, = ax3.plot([], [], 'k', lw=1)
line6, = ax3.plot([], [], 'k', lw=1)
ax1.set_xticklabels([])
ax2.set_yticklabels([])
lines = [line1, line2, line3, line4, line5, line6]

def init():
    for line in lines:
        line.set_data([], [])
    return lines

def animate(i):
    with logistic_model:
        if i == 0:
            # Burnin
            for j in range(samples): iter_sample.__next__()
        trace = iter_sample.__next__()
#     import pdb; pdb.set_trace()
    line1.set_data(trace['sex[T. Male]'][::-1], range(len(trace['sex[T. Male]'])))
    line2.set_data(range(len(trace['educ'])), trace['educ'][::-1])
    line3.set_data(trace['sex[T. Male]'], trace['educ'])
    line4.set_data(trace['sex[T. Male]'], trace['educ'])
    male = trace['sex[T. Male]'][-1]
    educ = trace['educ'][-1]
    line5.set_data([male, male], [educ, a_width[1]])
    line6.set_data([male, s_width[1]], [educ, educ])
    return lines
```

## Animating Metropolis-Hastings

```python
with pm.Model() as logistic_model:
    # Again define Bayesian logistic regression model on the following features: sex, age, age_squared, educ, hours

    #### YOUR CODE HERE ####

    ### END OF YOUR CODE ###
    step = pm.Metropolis()
    iter_sample = pm.iter_sample(2 * samples, step, start=map_estimate)
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=samples, interval=5, blit=True)
HTML(anim.to_html5_video())
# Note that generating the video may take a while.
```

## Animating NUTS
Now rerun the animation providing the NUTS sampling method as the step argument.
