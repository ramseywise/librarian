---
imported_hash: 084de42bf2cbbde2
title: Homework
summary: df.write.parquet('data/pq/fhvhv/2021/02/', compression=)
order: 29
kind: notebook
section: Batch / Code
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/05-batch/code/homework.ipynb
---

```python
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import types
```

```python
spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()
```

```python
spark.version
```

```python
!ls -lh fhvhv_tripdata_2021-02.csv
```

```python
schema = types.StructType([
    types.StructField('hvfhs_license_num', types.StringType(), True),
    types.StructField('dispatching_base_num', types.StringType(), True),
    types.StructField('pickup_datetime', types.TimestampType(), True),
    types.StructField('dropoff_datetime', types.TimestampType(), True),
    types.StructField('PULocationID', types.IntegerType(), True),
    types.StructField('DOLocationID', types.IntegerType(), True),
    types.StructField('SR_Flag', types.StringType(), True)
])
```

```python
df = spark.read \
    .option("header", "true") \
    .schema(schema) \
    .csv('fhvhv_tripdata_2021-02.csv')

df = df.repartition(24)

df.write.parquet('data/pq/fhvhv/2021/02/', compression=)
```

```python
df = spark.read.parquet('data/pq/fhvhv/2021/02/')
```

**Q3**: How many taxi trips were there on February 15?

```python
from pyspark.sql import functions as F
```

```python
df \
    .withColumn('pickup_date', F.to_date(df.pickup_datetime)) \
    .filter("pickup_date = '2021-02-15'") \
    .count()
```

```python
df.registerTempTable('fhvhv_2021_02')
```

```python
spark.sql("""
SELECT
    COUNT(1)
FROM
    fhvhv_2021_02
WHERE
    to_date(pickup_datetime) = '2021-02-15';
""").show()
```

**Q4**: Longest trip for each day

```python
df.columns
```

```python
df \
    .withColumn('duration', df.dropoff_datetime.cast('long') - df.pickup_datetime.cast('long')) \
    .withColumn('pickup_date', F.to_date(df.pickup_datetime)) \
    .groupBy('pickup_date') \
        .max('duration') \
    .orderBy('max(duration)', ascending=False) \
    .limit(5) \
    .show()
```

```python
spark.sql("""
SELECT
    to_date(pickup_datetime) AS pickup_date,
    MAX((CAST(dropoff_datetime AS LONG) - CAST(pickup_datetime AS LONG)) / 60) AS duration
FROM
    fhvhv_2021_02
GROUP BY
    1
ORDER BY
    2 DESC
LIMIT 10;
""").show()
```

**Q5**: Most frequent `dispatching_base_num`

How many stages this spark job has?

```python
spark.sql("""
SELECT
    dispatching_base_num,
    COUNT(1)
FROM
    fhvhv_2021_02
GROUP BY
    1
ORDER BY
    2 DESC
LIMIT 5;
""").show()
```

```python
df \
    .groupBy('dispatching_base_num') \
        .count() \
    .orderBy('count', ascending=False) \
    .limit(5) \
    .show()
```

**Q6**: Most common locations pair

```python
df_zones = spark.read.parquet('zones')
```

```python
df_zones.columns
```

```python
df.columns
```

```python
df_zones.registerTempTable('zones')
```

```python
spark.sql("""
SELECT
    CONCAT(pul.Zone, ' / ', dol.Zone) AS pu_do_pair,
    COUNT(1)
FROM
    fhvhv_2021_02 fhv LEFT JOIN zones pul ON fhv.PULocationID = pul.LocationID
                      LEFT JOIN zones dol ON fhv.DOLocationID = dol.LocationID
GROUP BY
    1
ORDER BY
    2 DESC
LIMIT 5;
""").show()
```
