---
imported_hash: e2277c140e1edf05
title: ypred = model.predict(df)
summary: spark = SparkSession.builder \ .master("local[]") \ .appName('test') \ .getOrCreate()
order: 26
kind: notebook
section: Batch / Code
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/05-batch/code/08_rdds.ipynb
---

```python
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()
```

```python
df_green = spark.read.parquet('data/pq/green/*/*')
```

```
SELECT
    date_trunc('hour', lpep_pickup_datetime) AS hour,
    PULocationID AS zone,

    SUM(total_amount) AS amount,
    COUNT(1) AS number_records
FROM
    green
WHERE
    lpep_pickup_datetime >= '2020-01-01 00:00:00'
GROUP BY
    1, 2
```

```python
rdd = df_green \
    .select('lpep_pickup_datetime', 'PULocationID', 'total_amount') \
    .rdd
```

```python
from datetime import datetime
```

```python
start = datetime(year=2020, month=1, day=1)

def filter_outliers(row):
    return row.lpep_pickup_datetime >= start
```

```python
rows = rdd.take(10)
row = rows[0]
```

```python
row
```

```python
def prepare_for_grouping(row):
    hour = row.lpep_pickup_datetime.replace(minute=0, second=0, microsecond=0)
    zone = row.PULocationID
    key = (hour, zone)

    amount = row.total_amount
    count = 1
    value = (amount, count)

    return (key, value)
```

```python
def calculate_revenue(left_value, right_value):
    left_amount, left_count = left_value
    right_amount, right_count = right_value

    output_amount = left_amount + right_amount
    output_count = left_count + right_count

    return (output_amount, output_count)
```

```python
from collections import namedtuple
```

```python
RevenueRow = namedtuple('RevenueRow', ['hour', 'zone', 'revenue', 'count'])
```

```python
def unwrap(row):
    return RevenueRow(
        hour=row[0][0],
        zone=row[0][1],
        revenue=row[1][0],
        count=row[1][1]
    )
```

```python
from pyspark.sql import types
```

```python
result_schema = types.StructType([
    types.StructField('hour', types.TimestampType(), True),
    types.StructField('zone', types.IntegerType(), True),
    types.StructField('revenue', types.DoubleType(), True),
    types.StructField('count', types.IntegerType(), True)
])
```

```python
df_result = rdd \
    .filter(filter_outliers) \
    .map(prepare_for_grouping) \
    .reduceByKey(calculate_revenue) \
    .map(unwrap) \
    .toDF(result_schema)
```

```python
df_result.write.parquet('tmp/green-revenue')
```

```python
columns = ['VendorID', 'lpep_pickup_datetime', 'PULocationID', 'DOLocationID', 'trip_distance']

duration_rdd = df_green \
    .select(columns) \
    .rdd
```

```python
import pandas as pd
```

```python
rows = duration_rdd.take(10)
```

```python
df = pd.DataFrame(rows, columns=columns)
```

```python
columns
```

```python
#model = ...

def model_predict(df):
#     y_pred = model.predict(df)
    y_pred = df.trip_distance * 5
    return y_pred
```

```python
def apply_model_in_batch(rows):
    df = pd.DataFrame(rows, columns=columns)
    predictions = model_predict(df)
    df['predicted_duration'] = predictions

    for row in df.itertuples():
        yield row
```

```python
df_predicts = duration_rdd \
    .mapPartitions(apply_model_in_batch)\
    .toDF() \
    .drop('Index')
```

```python
df_predicts.select('predicted_duration').show()
```
