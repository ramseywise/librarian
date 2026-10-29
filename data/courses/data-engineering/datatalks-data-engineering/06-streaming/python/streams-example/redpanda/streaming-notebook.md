---
imported_hash: 2888f3aa114a25a5
title: default for startingOffsets is "latest"
summary: spark = SparkSession \ .builder \ .appName("Spark-Notebook") \ .getOrCreate()
order: 43
kind: notebook
section: Streaming / Python / Streams example / Redpanda
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/06-streaming/python/streams-example/redpanda/streaming-notebook.ipynb
---

### 0. Spark Setup

```python
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1,org.apache.spark:spark-avro_2.12:3.3.1 pyspark-shell'
```

```python
from pyspark.sql import SparkSession
import pyspark.sql.types as T
import pyspark.sql.functions as F

spark = SparkSession \
    .builder \
    .appName("Spark-Notebook") \
    .getOrCreate()
```

### 1. Reading from Kafka Stream

through `readStream`

#### 1.1 Raw Kafka Stream

```python
# default for startingOffsets is "latest"
df_kafka_raw = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092,broker:29092") \
    .option("subscribe", "rides_csv") \
    .option("startingOffsets", "earliest") \
    .option("checkpointLocation", "checkpoint") \
    .load()
```

```python
df_kafka_raw.printSchema()
```

#### 1.2 Encoded Kafka Stream

```python
df_kafka_encoded = df_kafka_raw.selectExpr("CAST(key AS STRING)","CAST(value AS STRING)")
```

```python
df_kafka_encoded.printSchema()
```

#### 1.3 Structure Streaming DataFrame

```python
def parse_ride_from_kafka_message(df_raw, schema):
    """ take a Spark Streaming df and parse value col based on <schema>, return streaming df cols in schema """
    assert df_raw.isStreaming is True, "DataFrame doesn't receive streaming data"

    df = df_raw.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

    # split attributes to nested array in one Column
    col = F.split(df['value'], ', ')

    # expand col to multiple top-level columns
    for idx, field in enumerate(schema):
        df = df.withColumn(field.name, col.getItem(idx).cast(field.dataType))
    return df.select([field.name for field in schema])
```

```python
ride_schema = T.StructType(
    [T.StructField("vendor_id", T.IntegerType()),
     T.StructField('tpep_pickup_datetime', T.TimestampType()),
     T.StructField('tpep_dropoff_datetime', T.TimestampType()),
     T.StructField("passenger_count", T.IntegerType()),
     T.StructField("trip_distance", T.FloatType()),
     T.StructField("payment_type", T.IntegerType()),
     T.StructField("total_amount", T.FloatType()),
     ])
```

```python
df_rides = parse_ride_from_kafka_message(df_raw=df_kafka_raw, schema=ride_schema)
```

```python
df_rides.printSchema()
```

```python
df_rides.show()
```

### 2 Sink Operation & Streaming Query

through `writeStream`

---
**Output Sinks**
- File Sink: stores the output to the directory
- Kafka Sink: stores the output to one or more topics in Kafka
- Foreach Sink:
- (for debugging) Console Sink, Memory Sink

Further details can be found in [Output Sinks](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#output-sinks)

---
There are three types of **Output Modes**:
- Complete: The whole Result Table will be outputted to the sink after every trigger. This is supported for aggregation queries.
- Append (default): Only new rows are added to the Result Table
- Update: Only updated rows are outputted

[Output Modes](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#output-modes) differs based on the set of transformations applied to the streaming data.

---
**Triggers**

The [trigger settings](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#triggers) of a streaming query define the timing of streaming data processing. Spark streaming support micro-batch streamings schema and you can select following options based on requirements.

- default-micro-batch-mode
- fixed-interval-micro-batch-mode
- one-time-micro-batch-mode
- available-now-micro-batch-mode

#### Console and Memory Sink

```python
def sink_console(df, output_mode: str = 'complete', processing_time: str = '5 seconds'):
    write_query = df.writeStream \
        .outputMode(output_mode) \
        .trigger(processingTime=processing_time) \
        .format("console") \
        .option("truncate", False) \
        .start()
    return write_query # pyspark.sql.streaming.StreamingQuery
```

```python
write_query = sink_console(df_rides, output_mode='append')
```

```python
def sink_memory(df, query_name, query_template):
    write_query = df \
        .writeStream \
        .queryName(query_name) \
        .format('memory') \
        .start()
    query_str = query_template.format(table_name=query_name)
    query_results = spark.sql(query_str)
    return write_query, query_results
```

```python
query_name = 'vendor_id_counts'
query_template = 'select count(distinct(vendor_id)) from {table_name}'
write_query, df_vendor_id_counts = sink_memory(df=df_rides, query_name=query_name, query_template=query_template)
```

```python
print(type(write_query)) # pyspark.sql.streaming.StreamingQuery
write_query.status
```

```python
df_vendor_id_counts.show()
```

```python
write_query.stop()
```

#### Kafka Sink

To write stream results to `kafka-topic`, the stream dataframe has at least a column with name `value`.

Therefore before starting `writeStream` in kafka format, dataframe needs to be updated accordingly.

More information regarding kafka sink expected data structure [here](https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html#writing-data-to-kafka)

```python
def prepare_dataframe_to_kafka_sink(df, value_columns, key_column=None):
    columns = df.columns
    df = df.withColumn("value", F.concat_ws(', ',*value_columns))
    if key_column:
        df = df.withColumnRenamed(key_column,"key")
        df = df.withColumn("key",df.key.cast('string'))
    return df.select(['key', 'value'])

def sink_kafka(df, topic, output_mode='append'):
    write_query = df.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092,broker:29092") \
        .outputMode(output_mode) \
        .option("topic", topic) \
        .option("checkpointLocation", "checkpoint") \
        .start()
    return write_query
```
