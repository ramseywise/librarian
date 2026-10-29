---
imported_hash: 022bc38d861e34f8
title: Model registry
summary: MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
order: 7
kind: notebook
section: Experiment tracking
source: learn-ai-engineering/data-engineering/DataTalks MLOps/02-experiment-tracking/model-registry.ipynb
---

## MLflow's Model Registry

```python
from mlflow.tracking import MlflowClient


MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
```

### Interacting with the MLflow tracking server

The `MlflowClient` object allows us to interact with...
- an MLflow Tracking Server that creates and manages experiments and runs.
- an MLflow Registry Server that creates and manages registered models and model versions.

To instantiate it we need to pass a tracking URI and/or a registry URI

```python
client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

client.list_experiments()
```

```python
client.create_experiment(name="my-cool-experiment")
```

Let's check the latest versions for the experiment with id `1`...

```python
from mlflow.entities import ViewType

runs = client.search_runs(
    experiment_ids='1',
    filter_string="metrics.rmse < 7",
    run_view_type=ViewType.ACTIVE_ONLY,
    max_results=5,
    order_by=["metrics.rmse ASC"]
)
```

```python
for run in runs:
    print(f"run id: {run.info.run_id}, rmse: {run.data.metrics['rmse']:.4f}")
```

### Interacting with the Model Registry

In this section We will use the `MlflowClient` instance to:

1. Register a new version for the experiment `nyc-taxi-regressor`
2. Retrieve the latests versions of the model `nyc-taxi-regressor` and check that a new version `4` was created.
3. Transition the version `4` to "Staging" and adding annotations to it.

```python
import mlflow

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
```

```python
run_id = "b8904012c84343b5bf8ee72aa8f0f402"
model_uri = f"runs:/{run_id}/model"
mlflow.register_model(model_uri=model_uri, name="nyc-taxi-regressor")
```

```python
model_name = "nyc-taxi-regressor"
latest_versions = client.get_latest_versions(name=model_name)

for version in latest_versions:
    print(f"version: {version.version}, stage: {version.current_stage}")
```

```python
model_version = 4
new_stage = "Staging"
client.transition_model_version_stage(
    name=model_name,
    version=model_version,
    stage=new_stage,
    archive_existing_versions=False
)
```

```python
from datetime import datetime

date = datetime.today().date()
client.update_model_version(
    name=model_name,
    version=model_version,
    description=f"The model version {model_version} was transitioned to {new_stage} on {date}"
)
```

### Comparing versions and selecting the new "Production" model

In the last section, we will retrieve models registered in the model registry and compare their performance on an unseen test set. The idea is to simulate the scenario in which a deployment engineer has to interact with the model registry to decide whether to update the model version that is in production or not.

These are the steps:

1. Load the test dataset, which corresponds to the NYC Green Taxi data from the month of March 2021.
2. Download the `DictVectorizer` that was fitted using the training data and saved to MLflow as an artifact, and load it with pickle.
3. Preprocess the test set using the `DictVectorizer` so we can properly feed the regressors.
4. Make predictions on the test set using the model versions that are currently in the "Staging" and "Production" stages, and compare their performance.
5. Based on the results, update the "Production" model version accordingly.


**Note: the model registry doesn't actually deploy the model to production when you transition a model to the "Production" stage, it just assign a label to that model version. You should complement the registry with some CI/CD code that does the actual deployment.**

```python
from sklearn.metrics import mean_squared_error
import pandas as pd


def read_dataframe(filename):
    df = pd.read_csv(filename)

    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)

    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)

    return df


def preprocess(df, dv):
    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    train_dicts = df[categorical + numerical].to_dict(orient='records')
    return dv.transform(train_dicts)


def test_model(name, stage, X_test, y_test):
    model = mlflow.pyfunc.load_model(f"models:/{name}/{stage}")
    y_pred = model.predict(X_test)
    return {"rmse": mean_squared_error(y_test, y_pred, squared=False)}
```

```python
df = read_dataframe("data/green_tripdata_2021-03.csv")
```

```python
client.download_artifacts(run_id=run_id, path='preprocessor', dst_path='.')
```

```python
import pickle

with open("preprocessor/preprocessor.b", "rb") as f_in:
    dv = pickle.load(f_in)
```

```python
X_test = preprocess(df, dv)
```

```python
target = "duration"
y_test = df[target].values
```

```python
%time test_model(name=model_name, stage="Production", X_test=X_test, y_test=y_test)
```

```python
%time test_model(name=model_name, stage="Staging", X_test=X_test, y_test=y_test)
```

```python
client.transition_model_version_stage(
    name=model_name,
    version=4,
    stage="Production",
    archive_existing_versions=True
)
```
