---
imported_hash: 899ce241613e2235
title: 7    | Time Series
summary: ''
order: 7
kind: notebook
source: learn-ai-engineering/programming/Python Basics/7_Time_Series.ipynb
---

# 7    | Time Series

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
```

## Datetime Basics

```python
# use datetime to get current date
now = datetime.now()
now.year, now.month, now.day
```

```python
# use datetime to subtract two dates
delta = datetime(2011, 1, 7) - datetime(2008, 6, 24, 8, 15)
delta.days
```

```python
# timedelta can be used to add or subtract time
start = datetime(2011, 1, 7)
start, start + timedelta(12)
```

```python
# convert datetime to str
stamp = datetime(2011, 1, 3)
stamp.strftime('%Y-%m-%d')
```

```python
# convert str to datetime
value = '2011-01-03'
datetime.strptime(value, '%Y-%m-%d')
```

```python
# use list comprehension for multiple strings
datestrs = ['7/6/2011', '8/6/2011']
[datetime.strptime(x, '%m/%d/%Y') for x in datestrs]
```

```python
# parse string in different framework
parse('Jan 31, 1997 10:45 PM')
```

```python
# to_datetime is a simple pandas function
datestrs = ['2011-07-06 12:00:00', '2011-08-06 00:00:00']
pd.to_datetime(datestrs)
```

## Time Series Basics

```python
# create time series data
dates = [datetime(2011, 1, 2), datetime(2011, 1, 5),
         datetime(2011, 1, 7), datetime(2011, 1, 8),
         datetime(2011, 1, 10), datetime(2011, 1, 12)]
ts = pd.Series(np.random.randn(6), index=dates)
ts
```

```python
# subset value by index
stamp = ts.index[0]
ts[stamp]
```

```python
# drop rows after specified date
ts.truncate(after='1/9/2011')
```

```python
# subset all data by month
dates = pd.date_range('1/1/2000', periods=100, freq='W-WED')
long_df = pd.DataFrame(np.random.randn(100, 4),
                       index=dates,
                       columns=['Colorado', 'Texas',
                                'New York', 'Ohio'])
long_df.loc['5-2001']
```

```python
# create data with duplicate indices
dates = pd.DatetimeIndex(['1/1/2000', '1/2/2000', '1/2/2000',
                          '1/2/2000', '1/3/2000'])
dup_ts = pd.Series(np.arange(5), index=dates)
dup_ts
```

```python
# count duplicated indices
grouped = dup_ts.groupby(level=0)
grouped.count()
```

```python
# generate date ranges
index = pd.date_range('2012-04-01', '2012-06-01')
index
```

```python
# generate data but from start or end with specified periods
pd.date_range(start='2012-04-01', periods=20)
```

```python
# generate data with weekly frequency
pd.date_range('2000-01-01', '2000-12-01', freq='W')
```

### Shifting (Leading and Lagging) Data

```python
# create random data
ts = pd.Series(np.random.randn(4),
               index=pd.date_range('1/1/2000', periods=4, freq='M'))
ts
```

```python
# shift values forward
ts.shift(1)
```

ts / ts.shift(1) - 1

```python
# shift indices backwards by month
ts.shift(-1, freq='M')
```

## Periods and Period Arithmetic

```python
# alternatively create period variable
p = pd.Period(2007, freq='Y')
p - 2
```

```python
# return first month of a year period
p = pd.Period('2007', freq='A-DEC')
p.asfreq('M', how='start')
```

### Upsampling and Interpolation

```python
# resample by adding days to df
frame = pd.DataFrame(np.random.randn(2, 4),
                     index=pd.date_range('1/1/2000', periods=2,
                                         freq='W-WED'),
                     columns=['Colorado', 'Texas', 'New York', 'Ohio'])
frame
```

```python
df_daily = frame.resample('D').asfreq()
df_daily
```

```python
# forward fill next two rows with previous values
frame.resample('D').ffill(limit=2)
```

## Moving Window Functions

```python
# read csv
close_px_all = pd.read_csv('data/stock_px_2.csv',
                           parse_dates=True, index_col=0)
close_px_all
```

```python
# plot sample and rolling mean
close_px = close_px_all[['AAPL', 'MSFT', 'XOM']]
close_px = close_px.resample('B').ffill()
close_px.AAPL.plot()
close_px.AAPL.rolling(250).mean().plot()
```

```python
# plot rolling average for column
close_px.rolling(60).mean().plot(logy=True)
```

```python
# plot correlation between percentage and returns for specific column
spx_px = close_px_all['SPX']
spx_rets = spx_px.pct_change()
returns = close_px.pct_change()
corr = returns.AAPL.rolling(125, min_periods=100).corr(spx_rets)
corr.plot()
```

```python
# plot corr for all columns
corr = returns.rolling(125, min_periods=100).corr(spx_rets)
corr.plot()
```
