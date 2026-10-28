---
imported_hash: 460bf19a9319f1c5
title: Start producer script
summary: In this document, you will be finding information about stream processing using different Python libraries (kafka-python,confluent-kafka,pyspark, faust).
order: 37
kind: reading
section: Streaming / Python
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/06-streaming/python/README.md
---

### Stream-Processing with Python

In this document, you will be finding information about stream processing
using different Python libraries (`kafka-python`,`confluent-kafka`,`pyspark`, `faust`).

This Python module can be separated in following modules.

####  1. Docker
Docker module includes, Dockerfiles and docker-compose definitions
to run Kafka and Spark in a docker container. Setting up required services is
the prerequsite step for running following modules.

#### 2. Kafka Producer - Consumer Examples
- [Json Producer-Consumer Example](json_example) using `kafka-python` library
- [Avro Producer-Consumer Example](avro_example) using `confluent-kafka` library

Both of these examples require, up-and running Kafka services, therefore please ensure
following steps under [docker-README](docker/readme.md)

To run the producer-consumer examples in the respective example folder, run following commands
```bash
# Start producer script
python3 producer.py
# Start consumer script
python3 consumer.py
```
