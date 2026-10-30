---
imported_hash: 9a051efea0c21116
title: 4 | DataFrames and Relational Data (Pandas)
summary: 'Some basic topics covered here include: - Series vs DataFrame - Descriptive Functions - Indexing and Sorting - Slicing and Subsetting - Joining DataFrames'
order: 23
kind: notebook
section: Python for data
source: learn-ai-engineering/programming/python/04-python-for-data/4_DataFrames.ipynb
---

# 4 | DataFrames and Relational Data (Pandas)

   > **`pandas`** is a Python package providing fast, flexible, and expressive data structures designed to make working with “relational” or “labeled” data both easy and intuitive.

Some basic topics covered here include:
   - Series vs DataFrame
   - Descriptive Functions
   - Indexing and Sorting
   - Slicing and Subsetting
   - Joining DataFrames

*Resources*:
- **Coursera Data Analysis and Interpretation** (Wesleyan)
- **Python for Data Analytics** - Mckinney (O'Reilly)

```python
import sys
import json
import numpy as np
import pandas as pd
```

### Series vs Dataframes

```python
#return list to series (array with index)
animals = ['Tiger', 'Bear', 'Moose']
pd.Series(animals)
```

```python
#return dictionary as series
sports = {'Basketball': 'USA',
          'Golf': 'Scotland',
          'Sumo': 'Japan',
          'Soccer': 'Germany'}
s=pd.Series(sports)
s
```

```python
# concat series along axis
s1 = pd.Series([0, 1], index=['a', 'b'])
s2 = pd.Series([2, 3, 4], index=['c', 'd', 'e'])
s3 = pd.Series([5, 6], index=['f', 'g'])
pd.concat([s1, s2, s3])
```

```python
pd.concat([s1, s2, s3], axis=1)
```

```python
# return nested dictionary as DF with columns and index
transactions = pd.DataFrame({
    'TransactionID': np.arange(10)+1,
    'TransactionDate': pd.to_datetime(['2010-08-21', '2011-05-26', '2011-06-16', '2012-08-26', '2013-06-06',
                              '2013-12-23', '2013-12-30', '2014-04-24', '2015-04-24', '2016-05-08']).date,
    'UserID': [7, 3, 3, 1, 2, 2, 3, np.nan, 7, 3],
    'ProductID': [2, 4, 3, 2, 4, 5, 4, 2, 4, 4],
    'Quantity': [1, 1, 1, 3, 1, 6, 1, 3, 3, 4]
})
```

```python
# preview output as csv comma deliniated
transactions.to_csv(sys.stdout, index=False, header=True)

#save as csv
transactions.to_csv('data_example.csv', index=False, header=True)
```

### Dataframe Descriptives

```python
transactions.head()
```

```python
# Full summary
transactions.info()
```

```python
# Convert date columns to Date type
transactions['TransactionDate'] = pd.to_datetime(transactions.TransactionDate)
transactions.TransactionDate
```

```python
print('column names:',transactions.columns.values)
print('row names:',transactions.index.values)
print('number of columns:',transactions.shape[1])
print('number of rows:',transactions.shape[0])
```

### Indexing and Sorting

```python
transactions.set_index(['UserID', 'TransactionID'])
```

```python
# Order the rows of transactions by TransactionID descending
transactions.sort_values('TransactionID', ascending=False)  # use argument inplace=TRUE to keep the changes
```

```python
# Order the rows of transactions by Quantity ascending, TransactionDate descending
transactions.sort_values(['Quantity', 'TransactionDate'], ascending=[True, False])
```

```python
#Order columns based on index
transactions.sort_index(axis=1, ascending=False)
```

```python
# Set the column order of transactions as ProductID, Quantity, TransactionDate, TransactionID, UserID
transactions[['ProductID', 'Quantity', 'TransactionDate', 'TransactionID', 'UserID']]
```

```python
# Make UserID the first column of transactions
transactions[pd.unique(['UserID'] + transactions.columns.values.tolist()).tolist()]
```

```python
# Change the name of columns ProductID and UserID to PID and UID respectively
transactions.rename(columns={'ProductID': 'PID', 'UserID': 'UID'})
```

### Slicing and Subsetting

```python
# Subset by columns 1 and 3
transactions.iloc[:, [0, 2]]
```

```python
# Subset by column name
transactions[['TransactionID','UserID']]
```

```python
# Subset columns excluding a variable list of column names
cols = ["TransactionID", "UserID", "Quantity"]
transactions.drop(cols, axis=1)
```

```python
# Subset rows based on index
transactions.iloc[[0,2,5]]
```

```python
# Subset rows exlcuding 1, 3, and 6
transactions.drop([0,2,5], axis=0)
```

```python
# Subset the first 3 rows
transactions[:3]
```

```python
# Subset rows excluding the first 3 rows
transactions[3:]
```

```python
# Subset rows with conditions based on column values
transactions[transactions.Quantity > 1]
```

```python
# Subset rows where TransactionID > 5 and subset columns by TransactionID and TransactionDate
transactions.loc[transactions.TransactionID > 5, ['TransactionID', 'TransactionDate']]
```

## Joining DataFrames

```python
#create 2 dfs
df1 = pd.DataFrame({'key': ['b', 'b', 'a', 'c', 'a', 'b'],
                    'data1': range(6),
                    'key2': ['one', 'two', 'one','three','two','two']})
df2 = pd.DataFrame({'key': ['a', 'b', 'a', 'b', 'd'],
                    'data2': range(5),
                    'key2': ['one', 'two', 'one','three','two']})
df1
```

```python
# combine dfs based on conditionality
df1[~df1['key'].isin(df2['key'])]
```

```python
# append dfs
df1.append(df2)
```

```python
# merge dfs
pd.merge(df1, df2, on='key', how='left', suffixes=('_left', '_right'))
```

```python
pd.merge(df1, df2, on='key', how='right')
```

```python
pd.merge(df1, df2, on='key', how='inner')
```

```python
pd.merge(df1, df2, on='key', how='outer')
```

```python
pd.merge(df1, df2, on=['key', 'key2'], how='left')
```

```python
#concat dfs
pd.concat([df1, df2], axis=1, keys=['level1', 'level2'])
```

```python
# pivot wide-to-long format on key
pd.melt(df1, ['key'])
```
