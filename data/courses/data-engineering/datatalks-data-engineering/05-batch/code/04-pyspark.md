---
imported_hash: f3a0037d267fe4a5
title: Pyspark
summary: SELECT  FROM df WHERE hvfhslicensenum = HV0003
order: 22
kind: notebook
section: Batch / Code
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/05-batch/code/04_pyspark.ipynb
---

```python
import pyspark
from pyspark.sql import SparkSession
```

```python
spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()
```

```python
!wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhvhv/fhvhv_tripdata_2021-01.csv.gz
```

```python
!gzip -dc fhvhv_tripdata_2021-01.csv.gz
```

```python
!wc -l fhvhv_tripdata_2021-01.csv
```

```python
df = spark.read \
    .option("header", "true") \
    .csv('fhvhv_tripdata_2021-01.csv')
```

```python
df.schema
```

```python
!head -n 1001 fhvhv_tripdata_2021-01.csv > head.csv
```

```python
import pandas as pd
```

```python
df_pandas = pd.read_csv('head.csv')
```

```python
df_pandas.dtypes
```

```python
spark.createDataFrame(df_pandas).schema
```

Integer - 4 bytes
Long - 8 bytes

```python
from pyspark.sql import types
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
    .csv('fhvhv_tripdata_2021-01.csv')
```

```python
df = df.repartition(24)
```

```python
df.write.parquet('fhvhv/2021/01/')
```

```python
df = spark.read.parquet('fhvhv/2021/01/')
```

```python
df.printSchema()
```

SELECT * FROM df WHERE hvfhs_license_num =  HV0003

```python
from pyspark.sql import functions as F
```

```python
df.show()
```

```python
def crazy_stuff(base_num):
    num = int(base_num[1:])
    if num % 7 == 0:
        return f's/{num:03x}'
    elif num % 3 == 0:
        return f'a/{num:03x}'
    else:
        return f'e/{num:03x}'
```

```python
crazy_stuff('B02884')
```

```python
crazy_stuff_udf = F.udf(crazy_stuff, returnType=types.StringType())
```

```python
df \
    .withColumn('pickup_date', F.to_date(df.pickup_datetime)) \
    .withColumn('dropoff_date', F.to_date(df.dropoff_datetime)) \
    .withColumn('base_id', crazy_stuff_udf(df.dispatching_base_num)) \
    .select('base_id', 'pickup_date', 'dropoff_date', 'PULocationID', 'DOLocationID') \
    .show()
```

```python
df.select('pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID') \
  .filter(df.hvfhs_license_num == 'HV0003')
```

```python
!head -n 10 head.csv
```
