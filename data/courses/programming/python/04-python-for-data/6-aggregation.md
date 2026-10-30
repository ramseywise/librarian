---
imported_hash: e5d38c2ecebfa7c7
title: 6    | Data Aggregation and Group Operations
summary: ''
order: 25
kind: notebook
section: Python for data
source: learn-ai-engineering/programming/python/04-python-for-data/6_Aggregation.ipynb
---

# 6    | Data Aggregation and Group Operations

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```

### GroupBy Basics

```python
df = pd.DataFrame({'key1' : ['a', 'a', 'b', 'b', 'a'],
                   'key2' : ['one', 'two', 'one', 'two', 'one'],
                   'data1' : np.random.randn(5),
                   'data2' : np.random.randn(5)})
# create group variable to calculate aggregate summary
grouped = df['data1'].groupby(df['key1'])
grouped.mean()
```

```python
# groupby two columnes
means = df['data1'].groupby([df['key1'], df['key2']]).mean()
means
```

```python
# read as df
means.unstack()
```

```python
# get
df.groupby(['key1', 'key2']).size().unstack()
```

### Grouping with dictionaries

```python
# return key names
for name, group in df.groupby('key1'):
    print(name)
```

```python
# return means for each key name and dataset
for name, group in df.groupby('key1'):
    print(group)
```

```python
# return df of second key in dict
pieces = dict(list(df.groupby('key1')))
pieces['b']
```

```python
people = pd.DataFrame(np.random.randn(5, 5),
                      columns=['a', 'b', 'c', 'd', 'e'],
                      index=['Joe', 'Steve', 'Wes', 'Jim', 'Travis'])
people.iloc[2:3, [1, 2]] = np.nan # Add a few NA values
people
```

```python
# groupby new mapping using dict
mapping = {'a': 'red', 'b': 'red', 'c': 'blue',
           'd': 'blue', 'e': 'red', 'f' : 'orange'}
by_column = people.groupby(mapping, axis=1)
by_column.sum()
```

### Grouping by Index Levels

```python
columns = pd.MultiIndex.from_arrays([['US', 'US', 'US', 'JP', 'JP'],
                                    [1, 3, 5, 1, 3]],
                                    names=['cty', 'tenor'])
hier_df = pd.DataFrame(np.random.randn(4, 5), columns=columns)
hier_df
```

```python
hier_df.groupby(level='cty', axis=1).count()
```

```python
tips = pd.read_csv('data/tips.csv')
# Add tip percentage of total bill
tips['tip_pct'] = tips['tip'] / tips['total_bill']
tips[:6]
```

```python
# use .agg() to show multiple metrics
grouped = tips.groupby(['day', 'smoker'])
grouped_pct = grouped['tip_pct']
grouped_pct.agg([('avg', 'mean'), ('std', np.std)])
```

```python
# aggregate for both total and %
functions = ['count', 'mean', 'max']
result = grouped['tip_pct', 'total_bill'].agg(functions)
result
```

```python
# add additional agg column
grouped.agg({'tip' : np.max, 'size' : 'sum'})
grouped.agg({'tip_pct' : ['min', 'max', 'mean', 'std'],
             'size' : 'sum'})
```

```python
# remove row indices
tips.groupby(['day', 'smoker'], as_index=False).mean()
```

```python
# sort by column
def top(df, n=5, column='tip_pct'):
    return df.sort_values(by=column)[-n:]
top(tips, n=6)
```

### Quantile and Bucket Analysis

```python
# define quartiles
frame = pd.DataFrame({'data1': np.random.randn(1000),
                      'data2': np.random.randn(1000)})
quartiles = pd.cut(frame.data1, 4)
quartiles[:10]
```

```python
# return statistics for group
def get_stats(group):
    return {'min': group.min(), 'max': group.max(),
            'count': group.count(), 'mean': group.mean()}
grouped = frame.data2.groupby(quartiles)
grouped.apply(get_stats).unstack()
```

### Filling Missing Values with Group-Specific Values

```python
s = pd.Series(np.random.randn(6))
s[::2] = np.nan
s
s.fillna(s.mean())
```

```python
# create df with missing values
states = ['Ohio', 'New York', 'Vermont', 'Florida',
          'Oregon', 'Nevada', 'California', 'Idaho']
group_key = ['East'] * 4 + ['West'] * 4
data = pd.Series(np.random.randn(8), index=states)
data[['Vermont', 'Nevada', 'Idaho']] = np.nan
data
```

```python
# fill nan with mean
fill_mean = lambda g: g.fillna(g.mean())
data.groupby(group_key).apply(fill_mean)
```

```python
# or specify values
fill_values = {'East': 0.5, 'West': -1}
fill_func = lambda g: g.fillna(fill_values[g.name])
data.groupby(group_key).apply(fill_func)
```

### Group Weighted Average and Correlation

```python
# add weights based on average
df = pd.DataFrame({'category': ['a', 'a', 'a', 'a',
                                'b', 'b', 'b', 'b'],
                   'data': np.random.randn(8),
                   'weights': np.random.rand(8)})
grouped = df.groupby('category')
get_wavg = lambda g: np.average(g['data'], weights=g['weights'])
grouped.apply(get_wavg)
```
