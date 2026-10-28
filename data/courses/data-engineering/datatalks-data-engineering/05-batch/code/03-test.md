---
imported_hash: 5ea37c7a27ddba84
title: Test
summary: ''
order: 21
kind: notebook
section: Batch / Code
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/05-batch/code/03_test.ipynb
---

```python
import pyspark
```

```python
pyspark.__file__
```

```python
from pyspark.sql import SparkSession
```

```python
spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()
```

```python
!wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
```

```python
!head taxi+_zone_lookup.csv
```

```python
df = spark.read \
    .option("header", "true") \
    .csv('taxi+_zone_lookup.csv')
```

```python
df.show()
```

```python
df.write.parquet('zones')
```

```python
!ls -lh
```
