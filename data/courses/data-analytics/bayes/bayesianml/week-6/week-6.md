---
imported_hash: 7f1296da7e9efbed
title: Gaussian processes and Bayesian optimization
summary: In this assignment you will learn how to use <a href="http://sheffieldml.github.io/GPy/">GPy</a> and <a href="http://sheffieldml.github.io/GPyOpt/">GPyOpt</a> libraries to deal with gaussian processes.
order: 6
kind: notebook
section: BayesianML / Week 6
source: learn-ai-engineering/data-analytics/Bayes/BayesianML/week_6/week_6.ipynb
---

# Gaussian processes and Bayesian optimization

In this assignment you will learn how to use <a href="http://sheffieldml.github.io/GPy/">GPy</a> and <a href="http://sheffieldml.github.io/GPyOpt/">GPyOpt</a> libraries to deal with gaussian processes. These libraries provide quite simple and inuitive interfaces for training and inference, and we will try to get familiar with them in a few tasks.

### Installation
New libraries that are required for this tasks can be installed with the following command (if you use Anaconda):

```bash
pip install GPy
pip install gpyopt
pip install xgboost
```

You can also follow installtaion guides from <a href="https://github.com/SheffieldML/GPy">GPy</a> and <a href="http://sheffieldml.github.io/GPyOpt/firststeps/index.html">GPyOpt</a> if you want to build them from source

You will also need following libraries: ```numpy```, ```scikit-learn```, ```matplotlib```

```python
! conda install pyqt=4
```

```python
! pip install GPy
```

```python
! pip install gpyopt
```

```python
! pip install xgboost
```

```python
import numpy as np
import GPy
import GPyOpt
import matplotlib.pyplot as plt
from sklearn.svm import SVR
import sklearn.datasets
from xgboost import XGBRegressor
from sklearn.model_selection import cross_val_score
import time
from grader import Grader
%matplotlib inline
```

### Grading
We will create a grader instace below and use it to collect your answers. Note that these outputs will be stored locally inside grader and will be uploaded to platform only after running submiting function in the last part of this assignment. If you want to make partial submission, you can run that cell any time you want.

```python
grader = Grader()
```

## Gaussian processes: GPy (<a href="http://pythonhosted.org/GPy/">documentation</a>)

We will start with a simple regression problem, for which we will try to fit a Gaussian Process with RBF kernel.

```python
def generate_points(n=25, noise_variance=0.0036):
    np.random.seed(777)
    X = np.random.uniform(-3.,3.,(n,1))
    y = np.sin(X) + np.random.randn(n,1)*noise_variance**0.5
    return X, y

def generate_noise(n=25, noise_variance=0.0036):
    np.random.seed(777)
    X = np.random.uniform(-3.,3.,(n,1))
    y = np.random.randn(n,1)*noise_variance**0.5
    return X, y
```

```python
# Create data points
X, y = generate_points()
plt.plot(X, y, '.')
plt.show()
```

To fit a Gaussian Process, you will need to define a kernel. For Gaussian (GBF) kernel you can use *GPy.kern.RBF*
function.

<b> Task 1.1: </b> Create RBF kernel with variance 1.5 and length-scale parameter 2 for 1D samples and compute value of the kernel between 6-th and 10-th points (one-based indexing system). Submit a single number.
<br><b>Hint:</b> use ```.K``` property of kernel object.

```python
kernel = GPy.kern.RBF(input_dim=1, variance=1.5, lengthscale=2.) ### YOUR CODE HERE
kernel_59 = kernel.K(X[9].reshape(1,1),X[5].reshape(1,1))
grader.submit_GPy_1(kernel_59)
```

<b> Task 1.2: </b> Fit GP into generated data. Use kernel from previous task. Submit predicted mean and vairance at position $x=1$.
<br><b>Hint:</b> use ```GPy.models.GPRegression``` class.

```python
model = GPy.models.GPRegression(X,y,kernel)### YOUR CODE HERE
X_new = np.asarray([1]).reshape(1,1)
mean,variance = model.predict(X_new)
grader.submit_GPy_2(mean, variance)
```

```python
model.plot()
plt.show()
```

We see that model didn't fit the data quite well. Let's try to fit kernel and noise parameters automatically as discussed in the lecture! You can see current parameters below:

```python
model
```

<b> Task 1.3: </b> Optimize length-scale, variance and noise component of the model and submit optimal length-scale value of the kernel.
<br><b>Hint:</b> Use ```.optimize()``` function of the model and ```.lengthscale``` property of the kernel.

```python
### YOUR CODE HERE
model.optimize(messages=True)
lengthscale = kernel.lengthscale
grader.submit_GPy_3(lengthscale)
```

```python
model.plot()
plt.show()
```

As you see, process generates outputs just right. Let's see if GP can figure out itself when we try to fit it into  noise or signal.

<b> Task 1.4: </b> Generate two datasets: sinusoid wihout noise and samples from gaussian noise. Optimize kernel parameters and submit optimal values of noise component.
<br><b>Note:</b> generate data only using ```generate_points(n, noise_variance)``` and ```generate_noise(n, noise_variance)``` function!

```python
X, y = generate_noise(noise_variance=10)
### YOUR CODE HERE
model = GPy.models.GPRegression(X,y,kernel)
model.optimize(messages=True)
model.plot()
```

```python
X, y = generate_points(noise_variance=0)
### YOUR CODE HERE
model = GPy.models.GPRegression(X,y,kernel)
model.optimize(messages=True)
model.plot()
```

```python
noise =  10.143321842393293
just_signal = 1.4995254892476796e-14
grader.submit_GPy_4(noise, just_signal)
```

#### Sparce GP
Now let's consider the speed of GP. We will generate a dataset of 3000 points and measure time that is consumed for prediction of mean and variance for each point. We will then try to use indusing inputs and find optimal number of points according to quality-time tradeoff.

For sparse model with inducing points you should use ```GPy.models.SparseGPRegression``` class. You can set number of inducing inputs with parameter ```num_inducing``` and optimize their positions and values with ```.optimize()``` call.

<b>Task 1.5</b>: Create a dataset of 1000 points and fit GPRegression. Measure time for predicting mean and variance at position $x=1$. Then fit SparseGPRegression with 10 inducing inputs and repeat the experiment. Report speedup as a ratio between consumed time without and with inducing inputs.

```python
#Fit the full GP
X, y = generate_points(1000)
model = GPy.models.GPRegression(X,y,kernel)
model.optimize(messages=True)
```

```python
#Measure time
X_new = np.array([1]).reshape(1,1)
start = time.time()
### YOUR CODE HERE
mean,var = model.predict(X_new)
time_gp = time.time()-start
```

```python
#Fit Sparse GP with 10 inducing inputs
model_sp = GPy.models.SparseGPRegression(X,y,kernel=kernel,num_inducing=10)
model_sp.optimize(messages=True)
```

```python
start = time.time()
### YOUR CODE HERE
mean,var = model_sp.predict(X_new)
time_sgp = time.time()-start
```

```python
model_sp.plot()
model.plot()
plt.show()
```

```python
grader.submit_GPy_5(time_gp / time_sgp)
```

## Bayesian optimization: GPyOpt (<a href="http://pythonhosted.org/GPyOpt/">documentation</a>, <a href="http://nbviewer.jupyter.org/github/SheffieldML/GPyOpt/blob/master/manual/index.ipynb">tutorials</a>)

In this part of the assignment we will try to find optimal hyperparameters to XGBoost model! We will use data from a small competition to speed things up, but keep in mind that the approach works even for large datasets.

We will use diabetes dataset provided in sklearn package.

```python
dataset = sklearn.datasets.load_diabetes()
X = dataset['data']
y = dataset['target']
```

We will use cross validation score to estimate accuracy and our goal will be to tune: ```max_depth```, ```learning_rate```, ```n_estimators``` parameters. The baseline MSE with default XGBoost parameters is $0.2$. Let's see if we can do better. First we have to define optimization function and domains.

```python
# Score. Optimizer will try to find minimum, so we will add a "-" sign.
def f(parameters):
    parameters = parameters[0]
    score = -cross_val_score(
                XGBRegressor(learning_rate=parameters[0],
                              max_depth=int(parameters[2]),
                              n_estimators=int(parameters[3]),
                              gamma=int(parameters[1]),
                              min_child_weight = parameters[4]),
                X, y, scoring='neg_mean_squared_error').mean()
    score = np.array(score)
    return score

def f_svr(parameters):
    parameters = parameters[0]
    score = -cross_val_score(
                SVR(gamma = parameters[0],
                    C = parameters[1],
                    epsilon = parameters[2]),
                X, y, scoring='neg_mean_squared_error').mean()
    score = np.array(score)
    return score
```

```python
baseline = -cross_val_score(XGBRegressor(), X, y, scoring='neg_mean_squared_error').mean()
baseline
```

```python
# Bounds (NOTE: define continuous variables first, then discrete!)
bounds = [
            {'name': 'learning_rate', 'type': 'continuous', 'domain': (0, 1)},
            {'name': 'gamma', 'type': 'continuous', 'domain': (0, 5)},
            {'name': 'max_depth', 'type': 'discrete', 'domain': (1, 50)},
            {'name': 'n_estimators', 'type': 'discrete', 'domain': (1, 300)},
            {'name': 'min_child_weight', 'type': 'discrete', 'domain': (1, 10)}
         ]
```

```python
np.random.seed(777)
optimizer = GPyOpt.methods.BayesianOptimization(f=f, domain=bounds,
                                                acquisition_type ='MPI',
                                                acquisition_par = 0.1,
                                                exact_eval=True)
```

```python
max_iter = 50
max_time = 60
optimizer.run_optimization(max_iter, max_time)
```

```python
optimizer.plot_convergence()
```

Best values of parameters:

```python
optimizer.X[np.argmin(optimizer.Y)]
```

```python
print('MSE:', np.min(optimizer.Y), 'Gain:', baseline/np.min(optimizer.Y)*100)
```

We were able to get 9% boost wihtout tuning parameters by hand! Let's see if you can do the same.

<b>Task 2.1:</b> Tune SVR model. Find optimal values for three parameters: ```C```, ```epsilon``` and ```gamma```. Use range (1e-5, 1000) for ```C```, (1e-5, 10) for ```epsilon``` and ```gamma```. Use MPI as acquisition function with weight 0.1. Submit optimal value of epsilon that was found by a model.

```python
bounds_svr = [
                {'name': 'gamma','type':'continuous','domain':(1e-5,10)},
                {'name': 'C','type':'continuous','domain':(1e-5,1000)},
                {'name': 'epsilon','type':'continuous','domain':(1e-5,10)}
             ]
```

```python
#Compute baseline for SVR
baseline_svr = -cross_val_score(SVR(), X, y, scoring='neg_mean_squared_error').mean()
print(baseline_svr)
```

```python
# Perform Bayesian Opt for hyper-params
np.random.seed(777)
optimizer_svr = GPyOpt.methods.BayesianOptimization(f=f_svr, domain=bounds_svr,
                                                    acquisition_type ='MPI',
                                                    acquisition_par = 0.1,
                                                    exact_eval=True)
```

```python
max_iter = 100
max_time = 60
optimizer_svr.run_optimization(max_iter, max_time)
```

```python
optimizer_svr.plot_convergence()
```

```python
best_epsilon = optimizer_svr.X[np.argmin(optimizer_svr.Y)][2]
```

```python
### YOUR CODE HERE
grader.submit_GPyOpt_1(best_epsilon)
```

<b>Task 2.2:</b> For the model above submit boost in improvement that you got after tuning hyperparameters (output percents) [e.g. if baseline MSE was 40 and you got 20, output number 200]

```python
performance_boost = (baseline_svr/np.min(optimizer.Y))
print(performance_boost)
grader.submit_GPyOpt_2(performance_boost*100)
```

### Authorization & Submission
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
