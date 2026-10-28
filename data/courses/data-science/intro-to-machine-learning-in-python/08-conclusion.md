---
imported_hash: d18a816785e2a672
title: Conclusion
summary: 'class MyTransformer(BaseEstimator, TransformerMixin): def init(self, firstparamter=1, secondparameter=2): # all parameters must be specified in the init function self.firstparamter = 1 self.secondparameter = 2'
order: 9
kind: notebook
source: learn-ai-engineering/data-science/Intro to Machine Learning in Python/08-conclusion.ipynb
---

## Outlook
### Approaching a machine learning problem
### Humans in the loop

### From prototype to production

### Testing production systems

### Building your own estimator

```python
from sklearn.base import BaseEstimator, TransformerMixin

class MyTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, first_paramter=1, second_parameter=2):
        # all parameters must be specified in the __init__ function
        self.first_paramter = 1
        self.second_parameter = 2

    def fit(self, X, y=None):
        # fit should only take X and y as parameters
        # even if your model is unsupervised, you need to accept a y argument!

        # Model fitting code goes here
        print("fitting the model right here")
        # fit returns self
        return self

    def transform(self, X):
        # transform takes as parameter only X

        # apply some transformation to X:
        X_transformed = X + 1
        return X_transformed
```

### Where to go from here
#### Theory
#### Other machine learning frameworks and packages
#### Ranking, recommender systems, time series, and other kinds of learning
#### Probabilistic modeling, inference and probabilistic programming

#### Neural Networks

#### Scaling to larger datasets

#### Honing your skills

#### Conclusion
