---
imported_hash: 6384fbd064151050
title: Scenario 2
summary: 'MLflow setup: - tracking server: yes, local server - backend store: sqlite database - artifacts store: local filesystem'
order: 9
kind: notebook
section: Experiment tracking / Running mlflow examples
source: learn-ai-engineering/data-engineering/DataTalks MLOps/02-experiment-tracking/running-mlflow-examples/scenario-2.ipynb
---

## Scenario 2: A cross-functional team with one data scientist working on an ML model


MLflow setup:
- tracking server: yes, local server
- backend store: sqlite database
- artifacts store: local filesystem

The experiments can be explored locally by accessing the local tracking server.

To run this example you need to launch the mlflow server locally by running the following command in your terminal:

`mlflow server --backend-store-uri sqlite:///backend.db`

```python
import mlflow


mlflow.set_tracking_uri("http://127.0.0.1:5000")
```

```python
print(f"tracking URI: '{mlflow.get_tracking_uri()}'")
```

```python
mlflow.list_experiments()
```

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


client = MlflowClient("http://127.0.0.1:5000")
```

```python
client.list_registered_models()
```

```python
run_id = client.list_run_infos(experiment_id='1')[0].run_id
mlflow.register_model(
    model_uri=f"runs:/{run_id}/models",
    name='iris-classifier'
)
```
