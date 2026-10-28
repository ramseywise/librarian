---
imported_hash: 7e5608dc3b827112
title: Load model
summary: TRACKINGURL = "http://127.0.0.1:5000" mlflow.settrackinguri(TRACKINGURL)
order: 19
kind: notebook
section: Deployment
source: learn-ai-engineering/data-engineering/DataTalks MLOps/04-deployment/load_model.ipynb
---

```python
import mlflow

TRACKING_URL = "http://127.0.0.1:5000"
mlflow.set_tracking_uri(TRACKING_URL)
```

```python
run_id = '6dd459b11b4e48dc862f4e1019d166f6'
logged_model = f'runs:/{run_id}/model'

loaded_model = mlflow.pyfunc.load_model(logged_model)
```

```python
import mlflow
```

```python
loaded_model = mlflow.pyfunc.load_model('s3://mlflow-models-alexey/1/6dd459b11b4e48dc862f4e1019d166f6/artifacts/model/')
```

```python
request = {
    'lpep_pickup_datetime': '2021-01-01 00:15:56',
    'PULocationID': 43,
    'DOLocationID': 151,
    'passenger_count': 1.0,
    'trip_distance': 1.01
}
```

```python
features = {}
features['PU_DO'] = '%s_%s' % (request['PULocationID'], request['DOLocationID'])
features['trip_distance'] = request['trip_distance']
```

```python
loaded_model.predict(features)
```
