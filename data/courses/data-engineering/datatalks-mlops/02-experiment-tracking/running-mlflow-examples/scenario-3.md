---
imported_hash: d5a4175eb3be7043
title: Scenario 3
summary: 'MLflow setup:  Tracking server: yes, remote server (EC2).'
order: 10
kind: notebook
section: Experiment tracking / Running mlflow examples
source: learn-ai-engineering/data-engineering/DataTalks MLOps/02-experiment-tracking/running-mlflow-examples/scenario-3.ipynb
---

## Scenario 3: Multiple data scientists working on multiple ML models

MLflow setup:
* Tracking server: yes, remote server (EC2).
* Backend store: postgresql database.
* Artifacts store: s3 bucket.

The experiments can be explored by accessing the remote server.

The exampe uses AWS to host a remote server. In order to run the example you'll need an AWS account. Follow the steps described in the file `mlflow_on_aws.md` to create a new AWS account and launch the tracking server.

```python
import mlflow
import os

os.environ["AWS_PROFILE"] = "" # fill in with your AWS profile. More info: https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/setup.html#setup-credentials

TRACKING_SERVER_HOST = "" # fill in with the public DNS of the EC2 instance
mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")
```

```python
print(f"tracking URI: '{mlflow.get_tracking_uri()}'")
```

```python
mlflow.search_experiments() # list_experiments API has been removed, you can use search_experiments instead.()
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
mlflow.search_experiments()
```

### Interacting with the model registry

```python
from mlflow.tracking import MlflowClient


client = MlflowClient(f"http://{TRACKING_SERVER_HOST}:5000")
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
