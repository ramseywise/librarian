---
imported_hash: 53c4da38da59f30d
title: Random forest
summary: from sklearn.featureextraction import DictVectorizer from sklearn.ensemble import RandomForestRegressor from sklearn.metrics import meansquarederror
order: 25
kind: notebook
section: Deployment / Web service mlflow
source: learn-ai-engineering/data-engineering/DataTalks MLOps/04-deployment/web-service-mlflow/random-forest.ipynb
---

```python
import pickle

import pandas as pd

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
```

```python
from sklearn.pipeline import make_pipeline
```

```python
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("green-taxi-duration")
```

```python
def read_dataframe(filename: str):
    df = pd.read_parquet(filename)

    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    return df


def prepare_dictionaries(df: pd.DataFrame):
    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')
    return dicts
```

```python
df_train = read_dataframe('data/green_tripdata_2021-01.parquet')
df_val = read_dataframe('data/green_tripdata_2021-02.parquet')

target = 'duration'
y_train = df_train[target].values
y_val = df_val[target].values

dict_train = prepare_dictionaries(df_train)
dict_val = prepare_dictionaries(df_val)
```

```python
with mlflow.start_run():
    params = dict(max_depth=20, n_estimators=100, min_samples_leaf=10, random_state=0)
    mlflow.log_params(params)

    pipeline = make_pipeline(
        DictVectorizer(),
        RandomForestRegressor(**params, n_jobs=-1)
    )

    pipeline.fit(dict_train, y_train)
    y_pred = pipeline.predict(dict_val)

    rmse = mean_squared_error(y_pred, y_val, squared=False)
    print(params, rmse)
    mlflow.log_metric('rmse', rmse)

    mlflow.sklearn.log_model(pipeline, artifact_path="model")
```

```python
from mlflow.tracking import MlflowClient
```

```python
MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'
RUN_ID = 'b4d3bca8aa8e46a6b8257fe4541b1136'

client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
```

```python
path = client.download_artifacts(run_id=RUN_ID, path='dict_vectorizer.bin')
```

```python
with open(path, 'rb') as f_out:
    dv = pickle.load(f_out)
```

```python
dv
```
