---
imported_hash: 5f0dae8768b9e65f
title: Spark sql
summary: spark = SparkSession.builder \ .master("local[]") \ .appName('test') \ .getOrCreate()
order: 24
kind: notebook
section: Batch / Code
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/05-batch/code/06_spark_sql.ipynb
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

```python
df_green = df_green \
    .withColumnRenamed('lpep_pickup_datetime', 'pickup_datetime') \
    .withColumnRenamed('lpep_dropoff_datetime', 'dropoff_datetime')
```

```python
df_yellow = spark.read.parquet('data/pq/yellow/*/*')
```

```python
df_yellow = df_yellow \
    .withColumnRenamed('tpep_pickup_datetime', 'pickup_datetime') \
    .withColumnRenamed('tpep_dropoff_datetime', 'dropoff_datetime')
```

```python
common_colums = []

yellow_columns = set(df_yellow.columns)

for col in df_green.columns:
    if col in yellow_columns:
        common_colums.append(col)
```

```python
from pyspark.sql import functions as F
```

```python
df_green_sel = df_green \
    .select(common_colums) \
    .withColumn('service_type', F.lit('green'))
```

```python
df_yellow_sel = df_yellow \
    .select(common_colums) \
    .withColumn('service_type', F.lit('yellow'))
```

```python
df_trips_data = df_green_sel.unionAll(df_yellow_sel)
```

```python
df_trips_data.groupBy('service_type').count().show()
```

```python
df_trips_data.columns
```

```python
df_trips_data.registerTempTable('trips_data')
```

```python
spark.sql("""
SELECT
    service_type,
    count(1)
FROM
    trips_data
GROUP BY
    service_type
""").show()
```

```python
df_result = spark.sql("""
SELECT
    -- Reveneue grouping
    PULocationID AS revenue_zone,
    date_trunc('month', pickup_datetime) AS revenue_month,
    service_type,

    -- Revenue calculation
    SUM(fare_amount) AS revenue_monthly_fare,
    SUM(extra) AS revenue_monthly_extra,
    SUM(mta_tax) AS revenue_monthly_mta_tax,
    SUM(tip_amount) AS revenue_monthly_tip_amount,
    SUM(tolls_amount) AS revenue_monthly_tolls_amount,
    SUM(improvement_surcharge) AS revenue_monthly_improvement_surcharge,
    SUM(total_amount) AS revenue_monthly_total_amount,
    SUM(congestion_surcharge) AS revenue_monthly_congestion_surcharge,

    -- Additional calculations
    AVG(passenger_count) AS avg_montly_passenger_count,
    AVG(trip_distance) AS avg_montly_trip_distance
FROM
    trips_data
GROUP BY
    1, 2, 3
""")
```

```python
df_result.coalesce(1).write.parquet('data/report/revenue/', mode='overwrite')
```
