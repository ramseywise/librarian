---
imported_hash: fe0bb19f8ad6bd3f
title: Data loading
summary: 'Here we will be using the .paraquet file we downloaded and do the following: - Check metadata and table datatypes of the paraquet file/table - Convert the paraquet file to pandas dataframe and check the datatypes.'
order: 9
kind: notebook
section: Docker terraform / Docker sql
source: learn-ai-engineering/data-engineering/DataTalks Data Engineering/01-docker-terraform/2_docker_sql/data-loading-parquet.ipynb
---

# Data loading

Here we will be using the ```.paraquet``` file we downloaded and do the following:
 - Check metadata and table datatypes of the paraquet file/table
 - Convert the paraquet file to pandas dataframe and check the datatypes. Additionally check the data dictionary to make sure you have the right datatypes in pandas, as pandas will automatically create the table in our database.
 - Generate the DDL CREATE statement from pandas for a sanity check.
 - Create a connection to our database using SQLAlchemy
 - Convert our huge paraquet file into a iterable that has batches of 100,000 rows and load it into our database.

```python
import pandas as pd
import pyarrow.parquet as pq
from time import time
```

```python
# Read metadata
pq.read_metadata('yellow_tripdata_2023-09.parquet')
```

```python
# Read file, read the table from file and check schema
file = pq.ParquetFile('yellow_tripdata_2023-09.parquet')
table = file.read()
table.schema
```

```python
# Convert to pandas and check data
df = table.to_pandas()
df.info()
```

We need to first create the connection to our postgres database. We can feed the connection information to generate the CREATE SQL query for the specific server. SQLAlchemy supports a variety of servers.

```python
# Create an open SQL database connection object or a SQLAlchemy connectable
from sqlalchemy import create_engine

engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
engine.connect()
```

```python
# Generate CREATE SQL statement from schema for validation
print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))
```

Datatypes for the table looks good! Since we used paraquet file the datasets seem to have been preserved. You may have to convert some datatypes so it is always good to do this check.

## Finally inserting data

There are 2,846,722 rows in our dataset. We are going to use the ```parquet_file.iter_batches()``` function to create batches of 100,000, convert them into pandas and then load it into the postgres database.

```python
#This part is for testing


# Creating batches of 100,000 for the paraquet file
batches_iter = file.iter_batches(batch_size=100000)
batches_iter

# Take the first batch for testing
df = next(batches_iter).to_pandas()
df

# Creating just the table in postgres
#df.head(0).to_sql(name='ny_taxi_data',con=engine, if_exists='replace')
```

```python
# Insert values into the table
t_start = time()
count = 0
for batch in file.iter_batches(batch_size=100000):
    count+=1
    batch_df = batch.to_pandas()
    print(f'inserting batch {count}...')
    b_start = time()

    batch_df.to_sql(name='ny_taxi_data',con=engine, if_exists='append')
    b_end = time()
    print(f'inserted! time taken {b_end-b_start:10.3f} seconds.\n')

t_end = time()
print(f'Completed! Total time taken was {t_end-t_start:10.3f} seconds for {count} batches.')
```

## Extra bit

While trying to do the SQL Refresher, there was a need to add a lookup zones table but the file is in ```.csv``` format.

Let's code to handle both ```.csv``` and ```.paraquet``` files!

```python
from time import time
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine
```

```python
url = 'https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv'
url = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-09.parquet'

file_name = url.rsplit('/', 1)[-1].strip()
file_name
```

```python
if '.csv' in file_name:
    print('yay')
    df = pd.read_csv(file_name, nrows=10)
    df_iter = pd.read_csv(file_name, iterator=True, chunksize=100000)
elif '.parquet' in file_name:
    print('oh yea')
    file = pq.ParquetFile(file_name)
    df = next(file.iter_batches(batch_size=10)).to_pandas()
    df_iter = file.iter_batches(batch_size=100000)
else:
    print('Error. Only .csv or .parquet files allowed.')
    sys.exit()
```

This code is a rough code and seems to be working. The cleaned up version will be in `data-loading-parquet.py` file.
