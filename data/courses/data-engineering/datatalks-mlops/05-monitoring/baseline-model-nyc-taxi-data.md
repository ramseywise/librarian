---
imported_hash: 28a34779801ef7ee
title: Baseline model for batch monitoring example
summary: from evidently import ColumnMapping from evidently.report import Report from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric
order: 27
kind: notebook
section: Monitoring
source: learn-ai-engineering/data-engineering/DataTalks MLOps/05-monitoring/baseline_model_nyc_taxi_data.ipynb
---

# Baseline model for batch monitoring example

```python
import requests
import datetime
import pandas as pd

from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric

from joblib import load, dump
from tqdm import tqdm

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
```

```python
files = [('green_tripdata_2022-02.parquet', './data'), ('green_tripdata_2022-01.parquet', './data')]

print("Download files:")
for file, path in files:
    url=f"https://d37ci6vzurychx.cloudfront.net/trip-data/{file}"
    resp=requests.get(url, stream=True)
    save_path=f"{path}/{file}"
    with open(save_path, "wb") as handle:
        for data in tqdm(resp.iter_content(),
                        desc=f"{file}",
                        postfix=f"save to {save_path}",
                        total=int(resp.headers["Content-Length"])):
            handle.write(data)
```

```python
jan_data = pd.read_parquet('data/green_tripdata_2022-01.parquet')
```

```python
jan_data.describe()
```

```python
jan_data.shape
```

```python
# create target
jan_data["duration_min"] = jan_data.lpep_dropoff_datetime - jan_data.lpep_pickup_datetime
jan_data.duration_min = jan_data.duration_min.apply(lambda td : float(td.total_seconds())/60)
```

```python
# filter out outliers
jan_data = jan_data[(jan_data.duration_min >= 0) & (jan_data.duration_min <= 60)]
jan_data = jan_data[(jan_data.passenger_count > 0) & (jan_data.passenger_count <= 8)]
```

```python
jan_data.duration_min.hist()
```

```python
# data labeling
target = "duration_min"
num_features = ["passenger_count", "trip_distance", "fare_amount", "total_amount"]
cat_features = ["PULocationID", "DOLocationID"]
```

```python
jan_data.shape
```

```python
train_data = jan_data[:30000]
val_data = jan_data[30000:]
```

```python
model = LinearRegression()
```

```python
model.fit(train_data[num_features + cat_features], train_data[target])
```

```python
train_preds = model.predict(train_data[num_features + cat_features])
train_data['prediction'] = train_preds
```

```python
val_preds = model.predict(val_data[num_features + cat_features])
val_data['prediction'] = val_preds
```

```python
print(mean_absolute_error(train_data.duration_min, train_data.prediction))
print(mean_absolute_error(val_data.duration_min, val_data.prediction))
```

# Dump model and reference data

```python
with open('models/lin_reg.bin', 'wb') as f_out:
    dump(model, f_out)
```

```python
val_data.to_parquet('data/reference.parquet')
```

# Evidently Report

```python
column_mapping = ColumnMapping(
    target=None,
    prediction='prediction',
    numerical_features=num_features,
    categorical_features=cat_features
)
```

```python
report = Report(metrics=[
    ColumnDriftMetric(column_name='prediction'),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()
]
)
```

```python
report.run(reference_data=train_data, current_data=val_data, column_mapping=column_mapping)
```

```python
report.show(mode='inline')
```

```python
result = report.as_dict()
```

```python
result
```

```python
#prediction drift
result['metrics'][0]['result']['drift_score']
```

```python
#number of drifted columns
result['metrics'][1]['result']['number_of_drifted_columns']
```

```python
#share of missing values
result['metrics'][2]['result']['current']['share_of_missing_values']
```

# Evidently Dashboard

```python
from evidently.metric_preset import DataDriftPreset, DataQualityPreset

from evidently.ui.workspace import Workspace
from evidently.ui.dashboards import DashboardPanelCounter, DashboardPanelPlot, CounterAgg, PanelValue, PlotType, ReportFilter
from evidently.renderers.html_widgets import WidgetSize
```

```python
ws = Workspace("workspace")
```

```python
project = ws.create_project("NYC Taxi Data Quality Project")
project.description = "My project descriotion"
project.save()
```

```python
regular_report = Report(
    metrics=[
        DataQualityPreset()
    ],
    timestamp=datetime.datetime(2022,1,28)
)

regular_report.run(reference_data=None,
                  current_data=val_data.loc[val_data.lpep_pickup_datetime.between('2022-01-28', '2022-01-29', inclusive="left")],
                  column_mapping=column_mapping)

regular_report
```

```python
ws.add_report(project.id, regular_report)
```

```python
#configure the dashboard
project.dashboard.add_panel(
    DashboardPanelCounter(
        filter=ReportFilter(metadata_values={}, tag_values=[]),
        agg=CounterAgg.NONE,
        title="NYC taxi data dashboard"
    )
)

project.dashboard.add_panel(
    DashboardPanelPlot(
        filter=ReportFilter(metadata_values={}, tag_values=[]),
        title="Inference Count",
        values=[
            PanelValue(
                metric_id="DatasetSummaryMetric",
                field_path="current.number_of_rows",
                legend="count"
            ),
        ],
        plot_type=PlotType.BAR,
        size=WidgetSize.HALF,
    ),
)

project.dashboard.add_panel(
    DashboardPanelPlot(
        filter=ReportFilter(metadata_values={}, tag_values=[]),
        title="Number of Missing Values",
        values=[
            PanelValue(
                metric_id="DatasetSummaryMetric",
                field_path="current.number_of_missing_values",
                legend="count"
            ),
        ],
        plot_type=PlotType.LINE,
        size=WidgetSize.HALF,
    ),
)

project.save()
```

```python
regular_report = Report(
    metrics=[
        DataQualityPreset()
    ],
    timestamp=datetime.datetime(2022,1,29)
)

regular_report.run(reference_data=None,
                  current_data=val_data.loc[val_data.lpep_pickup_datetime.between('2022-01-29', '2022-01-30', inclusive="left")],
                  column_mapping=column_mapping)

regular_report
```

```python
ws.add_report(project.id, regular_report)
```
