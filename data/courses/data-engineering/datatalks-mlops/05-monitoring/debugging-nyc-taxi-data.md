---
imported_hash: 7dbe97c877d0240a
title: Debugging with Evidently Test Suites and Reports
summary: from evidently import ColumnMapping from evidently.report import Report from evidently.metricpreset import DataDriftPreset
order: 28
kind: notebook
section: Monitoring
source: learn-ai-engineering/data-engineering/DataTalks MLOps/05-monitoring/debugging_nyc_taxi_data.ipynb
---

# Debugging with Evidently Test Suites and Reports

```python
import datetime
import pandas as pd

from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

from evidently.test_suite import TestSuite
from evidently.test_preset import DataDriftTestPreset

from joblib import dump, load

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
```

## Load data and model

```python
ref_data = pd.read_parquet('data/reference.parquet')
```

```python
current_data = pd.read_parquet('data/green_tripdata_2022-02.parquet')
```

```python
with open('models/lin_reg.bin', 'rb') as f_in:
    model = load(f_in)
```

```python
# data labeling
target = "duration_min"
num_features = ["passenger_count", "trip_distance", "fare_amount", "total_amount"]
cat_features = ["PULocationID", "DOLocationID"]
```

```python
problematic_data = current_data.loc[(current_data.lpep_pickup_datetime >= datetime.datetime(2022,2,2,0,0)) &
                               (current_data.lpep_pickup_datetime < datetime.datetime(2022,2,3,0,0))]
```

## Generate Test Suite and Report

```python
column_mapping = ColumnMapping(
    prediction='prediction',
    numerical_features=num_features,
    categorical_features=cat_features,
    target=None
)
```

```python
problematic_data['prediction'] = model.predict(problematic_data[num_features + cat_features].fillna(0))
```

```python
test_suite = TestSuite(tests = [DataDriftTestPreset()])
test_suite.run(reference_data=ref_data, current_data=problematic_data, column_mapping=column_mapping)
```

```python
test_suite.show(mode='inline')
```

```python
report = Report(metrics = [DataDriftPreset()])
report.run(reference_data=ref_data, current_data=problematic_data, column_mapping=column_mapping)
```

```python
report.show(mode='inline')
```
