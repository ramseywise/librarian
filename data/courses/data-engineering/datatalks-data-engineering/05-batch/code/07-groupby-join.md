---
imported_hash: a4b79a4f4e26af1c
title: Groupby join
summary: spark = SparkSession.builder \ .master("local[]") \ .appName('test') \ .getOrCreate()
order: 25
kind: notebook
section: Batch / Code
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/05-batch/code/07_groupby_join.ipynb
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
df_green.registerTempTable('green')
```

```python
df_green_revenue = spark.sql("""
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
""")
```

```python
df_green_revenue \
    .repartition(20) \
    .write.parquet('data/report/revenue/green', mode='overwrite')
```

```python
df_yellow = spark.read.parquet('data/pq/yellow/*/*')
df_yellow.registerTempTable('yellow')
```

```python
df_yellow_revenue = spark.sql("""
SELECT
    date_trunc('hour', tpep_pickup_datetime) AS hour,
    PULocationID AS zone,

    SUM(total_amount) AS amount,
    COUNT(1) AS number_records
FROM
    yellow
WHERE
    tpep_pickup_datetime >= '2020-01-01 00:00:00'
GROUP BY
    1, 2
""")
```

```python
df_yellow_revenue \
    .repartition(20) \
    .write.parquet('data/report/revenue/yellow', mode='overwrite')
```

```python
df_green_revenue = spark.read.parquet('data/report/revenue/green')
df_yellow_revenue = spark.read.parquet('data/report/revenue/yellow')
```

```python
df_green_revenue_tmp = df_green_revenue \
    .withColumnRenamed('amount', 'green_amount') \
    .withColumnRenamed('number_records', 'green_number_records')

df_yellow_revenue_tmp = df_yellow_revenue \
    .withColumnRenamed('amount', 'yellow_amount') \
    .withColumnRenamed('number_records', 'yellow_number_records')
```

```python
df_join = df_green_revenue_tmp.join(df_yellow_revenue_tmp, on=['hour', 'zone'], how='outer')
```

```python
df_join.write.parquet('data/report/revenue/total', mode='overwrite')
```

```python
df_join = spark.read.parquet('data/report/revenue/total')
```

```python
df_join
```

```python
df_zones = spark.read.parquet('zones/')
```

```python
df_result = df_join.join(df_zones, df_join.zone == df_zones.LocationID)
```

```python
df_result.drop('LocationID', 'zone').write.parquet('tmp/revenue-zones')
```
