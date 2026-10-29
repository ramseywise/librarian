---
imported_hash: 7996c6c3716b7692
title: Load Wisconsin Breast Cancer Dataset
summary: X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42) print(X_train.shape, X_test.shape)
order: 10
kind: notebook
section: Ch05   Text Classification
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch05 - Text Classification/Ch05a - Classification Performance Evaluation Metrics.ipynb
---

# Load Wisconsin Breast Cancer Dataset

```python
import numpy as np
from sklearn.datasets import load_breast_cancer
import matplotlib.pyplot as plt

%matplotlib inline

# load data
data = load_breast_cancer()
X = data.data
y = data.target
print(X.shape, data.feature_names)
```

# Classification Model Evaluation Metrics

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
print(X_train.shape, X_test.shape)
```

```python
from sklearn import linear_model

logistic = linear_model.LogisticRegression()
logistic.fit(X_train,y_train)
```

## Confusion Matrix

```python
import model_evaluation_utils as meu

y_pred = logistic.predict(X_test)
meu.display_confusion_matrix(true_labels=y_test, predicted_labels=y_pred, classes=[0, 1])
```

## True Positive, False Positive, True Negative and False Negative

```python
positive_class = 1
TP = 106
FP = 4
TN = 59
FN = 2
```

## Accuracy

```python
fw_acc = round(meu.metrics.accuracy_score(y_true=y_test, y_pred=y_pred), 5)
mc_acc = round((TP + TN) / (TP + TN + FP + FN), 5)
print('Framework Accuracy:', fw_acc)
print('Manually Computed Accuracy:', mc_acc)
```

## Precision

```python
fw_prec = round(meu.metrics.precision_score(y_true=y_test, y_pred=y_pred), 5)
mc_prec = round((TP) / (TP + FP), 5)
print('Framework Precision:', fw_prec)
print('Manually Computed Precision:', mc_prec)
```

## Recall

```python
fw_rec = round(meu.metrics.recall_score(y_true=y_test, y_pred=y_pred), 5)
mc_rec = round((TP) / (TP + FN), 5)
print('Framework Recall:', fw_rec)
print('Manually Computed Recall:', mc_rec)
```

## F1-Score

```python
fw_f1 = round(meu.metrics.f1_score(y_true=y_test, y_pred=y_pred), 5)
mc_f1 = round((2*mc_prec*mc_rec) / (mc_prec+mc_rec), 5)
print('Framework F1-Score:', fw_f1)
print('Manually Computed F1-Score:', mc_f1)
```

## ROC Curve and AUC

```python
meu.plot_model_roc_curve(clf=logistic, features=X_test, true_labels=y_test)
```
