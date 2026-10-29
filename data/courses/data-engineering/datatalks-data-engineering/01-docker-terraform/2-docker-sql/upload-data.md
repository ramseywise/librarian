---
imported_hash: f5a34956b84692b1
title: Upload data
summary: df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime) df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
order: 11
kind: notebook
section: Docker terraform / Docker sql
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/01-docker-terraform/2_docker_sql/upload-data.ipynb
---

```python
import pandas as pd
```

```python
pd.__version__
```

```python
df = pd.read_csv('yellow_tripdata_2021-01.csv', nrows=100)
```

```python
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
```

```python
from sqlalchemy import create_engine
```

```python
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
```

```python
print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))
```

```python
df_iter = pd.read_csv('yellow_tripdata_2021-01.csv', iterator=True, chunksize=100000)
```

```python
df = next(df_iter)
```

```python
len(df)
```

```python
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
```

```python
df
```

```python
df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')
```

```python
%time df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
```

```python
from time import time
```

```python
while True:
    t_start = time()

    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')

    t_end = time()

    print('inserted another chunk, took %.3f second' % (t_end - t_start))
```

```python
!wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
```

```python
df_zones = pd.read_csv('taxi+_zone_lookup.csv')
```

```python
df_zones.head()
```

```python
df_zones.to_sql(name='zones', con=engine, if_exists='replace')
```
