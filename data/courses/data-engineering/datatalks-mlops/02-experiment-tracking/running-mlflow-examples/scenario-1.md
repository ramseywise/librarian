---
imported_hash: 227665ce2e369a6b
title: Scenario 1
summary: 'MLflow setup:  Tracking server: no  Backend store: local filesystem  Artifacts store: local filesystem'
order: 8
kind: notebook
section: Experiment tracking / Running mlflow examples
source: learn-ai-engineering/data-engineering/DataTalks MLOps/02-experiment-tracking/running-mlflow-examples/scenario-1.ipynb
---

## Scenario 1: A single data scientist participating in an ML competition

MLflow setup:
* Tracking server: no
* Backend store: local filesystem
* Artifacts store: local filesystem

The experiments can be explored locally by launching the MLflow UI.

```python
import mlflow
```

```python
print(f"tracking URI: '{mlflow.get_tracking_uri()}'")
```

```python
mlflow.list_experiments()
```

### Creating an experiment and logging a new run

```python
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score

mlflow.set_experiment("my-experiment-1")

with mlflow.start_run():

    X, y = load_iris(return_X_y=True)

    params = {"C": 0.1, "random_state": 42}
    mlflow.log_params(params)

    lr = LogisticRegression(**params).fit(X, y)
    y_pred = lr.predict(X)
    mlflow.log_metric("accuracy", accuracy_score(y, y_pred))

    mlflow.sklearn.log_model(lr, artifact_path="models")
    print(f"default artifacts URI: '{mlflow.get_artifact_uri()}'")
```

```python
mlflow.list_experiments()
```

### Interacting with the model registry

```python
from mlflow.tracking import MlflowClient


client = MlflowClient()
```

```python
from mlflow.exceptions import MlflowException

try:
    client.list_registered_models()
except MlflowException:
    print("It's not possible to access the model registry :(")
```
