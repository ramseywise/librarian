---
imported_hash: eea189125246e5bf
title: Pg test connection
summary: 'Source: https://www.postgresqltutorial.com/postgresql-show-tables/'
order: 10
kind: notebook
section: Docker terraform / Docker sql
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/01-docker-terraform/2_docker_sql/pg-test-connection.ipynb
---

```python
import pandas as pd
```

```bash
pip install sqlalchemy psycopg2-binary
```

```python
from sqlalchemy import create_engine
```

```python
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
```

```python
engine.connect()
```

```python
query = """
SELECT 1 as number;
"""

pd.read_sql(query, con=engine)
```

```python
query = """
SELECT *
FROM pg_catalog.pg_tables
WHERE schemaname != 'pg_catalog' AND
    schemaname != 'information_schema';
"""

pd.read_sql(query, con=engine)
```

```python
df = pd.read_csv('yellow_tripdata_2021-01.csv', nrows=100)
```

```python
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
```

```python
df.to_sql(name='yellow_tripdata_trip', con=engine, index=False)
```

```python
query = """
SELECT * FROM yellow_tripdata_trip LIMIT 10
"""

pd.read_sql(query, con=engine)
```

```sql
SELECT *
FROM pg_catalog.pg_tables
WHERE schemaname != 'pg_catalog' AND
    schemaname != 'information_schema';
```

Source: https://www.postgresqltutorial.com/postgresql-show-tables/
