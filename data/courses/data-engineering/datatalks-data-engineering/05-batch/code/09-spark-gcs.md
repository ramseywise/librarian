---
imported_hash: df698f821613b246
title: Spark gcs
summary: conf = SparkConf() \ .setMaster('local[]') \ .setAppName('test') \ .set("spark.jars", "./lib/gcs-connector-hadoop3-2.2.5.jar") \ .set("spark.hadoop.google.cloud.auth.service.account.enable", "true") \ .set("spark.hadoop.google.cloud.auth.se…
order: 27
kind: notebook
section: Batch / Code
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/05-batch/code/09_spark_gcs.ipynb
---

```python
import pyspark
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
```

```python
credentials_location = '/home/alexey/.google/credentials/google_credentials.json'

conf = SparkConf() \
    .setMaster('local[*]') \
    .setAppName('test') \
    .set("spark.jars", "./lib/gcs-connector-hadoop3-2.2.5.jar") \
    .set("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .set("spark.hadoop.google.cloud.auth.service.account.json.keyfile", credentials_location)
```

```python
sc = SparkContext(conf=conf)

hadoop_conf = sc._jsc.hadoopConfiguration()

hadoop_conf.set("fs.AbstractFileSystem.gs.impl",  "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
hadoop_conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
hadoop_conf.set("fs.gs.auth.service.account.json.keyfile", credentials_location)
hadoop_conf.set("fs.gs.auth.service.account.enable", "true")
```

```python
spark = SparkSession.builder \
    .config(conf=sc.getConf()) \
    .getOrCreate()
```

```python
df_green = spark.read.parquet('gs://dtc_data_lake_de-zoomcamp-nytaxi/pq/green/*/*')
```

```python
df_green.count()
```
