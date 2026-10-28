---
imported_hash: 3f0fc614f96b8b9c
title: 5    | Basic Plotting and Visualization
summary: plot(randn(30).cumsum(), color='k', linestyle='dashed', marker='o')
order: 6
kind: notebook
section: Basics
source: sisyphus/drills/python/basics/5_Plotting.ipynb
---

# 5    | Basic Plotting and Visualization

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.random import rand
from datetime import datetime
import seaborn as sns
```

## Matplotlib

```python
# create figures and subplots
fig = plt.figure()
ax1 = fig.add_subplot(2, 2, 1)
ax2 = fig.add_subplot(2, 2, 2)
ax3 = fig.add_subplot(2, 2, 3)
```

```python
# plot random points
plt.plot(np.random.randn(50).cumsum(), 'k--')
```

```python
# use loop for plotting different ranges
fig, axes = plt.subplots(2, 2, sharex=True, sharey=True)
for i in range(2):
    for j in range(2):
        axes[i, j].hist(np.random.randn(500), bins=50, color='k', alpha=0.5)
plt.subplots_adjust(wspace=0, hspace=0)
```

```python
plt.figure()
plt.plot(rand(30).cumsum(), 'ko--')
plt.close('all')
```

plot(randn(30).cumsum(), color='k', linestyle='dashed', marker='o')

```python
# plot overlapping plots with different line styles
data = np.random.randn(30).cumsum()
plt.plot(data, 'k--', label='Default')
plt.plot(data, 'k-', drawstyle='steps-post', label='steps-post')
plt.legend(loc='best')
```

```python
# Add title, labels and ticks
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(np.random.randn(1000).cumsum())
ticks = ax.set_xticks([0, 250, 500, 750, 1000])
labels = ax.set_xticklabels(['one', 'two', 'three', 'four', 'five'],
                            rotation=30, fontsize='small')
ax.set_title('My first matplotlib plot')
ax.set_xlabel('Stages')
```

```python
# add legend
fig = plt.figure(); ax = fig.add_subplot(1, 1, 1)
ax.plot(rand(1000).cumsum(), 'k', label='one')
ax.plot(rand(1000).cumsum(), 'k--', label='two')
ax.plot(rand(1000).cumsum(), 'k.', label='three')
ax.legend(loc='best')
```

```python
# add annotations
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

data = pd.read_csv('data/spx.csv', index_col=0, parse_dates=True)
spx = data['SPX']
spx.plot(ax=ax, style='k-')

crisis_data = [
    (datetime(2007, 10, 11), 'Peak of bull market'),
    (datetime(2008, 3, 12), 'Bear Stearns Fails'),
    (datetime(2008, 9, 15), 'Lehman Bankruptcy')
]

for date, label in crisis_data:
    ax.annotate(label, xy=(date, spx.asof(date) + 75),
                xytext=(date, spx.asof(date) + 225),
                arrowprops=dict(facecolor='black', headwidth=4, width=2,
                                headlength=4),
                horizontalalignment='left', verticalalignment='top')

# Zoom in on 2007-2010
ax.set_xlim(['1/1/2007', '1/1/2011'])
ax.set_ylim([600, 1800])

ax.set_title('Important dates in the 2008-2009 financial crisis')
```

```python
# basic line plot from series
s = pd.Series(np.random.randn(10).cumsum(), index=np.arange(0, 100, 10))
s.plot()
```

```python
# overlapping line plots from df
df = pd.DataFrame(np.random.randn(10, 4).cumsum(0),
                  columns=['A', 'B', 'C', 'D'],
                  index=np.arange(0, 100, 10))
df.plot()
```

```python
# bar plots
fig, axes = plt.subplots(2, 1)
data = pd.Series(np.random.rand(16), index=list('abcdefghijklmnop'))
data.plot.bar(ax=axes[0], color='k', alpha=0.7)
data.plot.barh(ax=axes[1], color='k', alpha=0.7)
```

```python
# grouped bar plots with legend
df = pd.DataFrame(np.random.rand(6, 4),
                  index=['one', 'two', 'three', 'four', 'five', 'six'],
                  columns=pd.Index(['A', 'B', 'C', 'D'], name='Genus'))
df.plot.bar()
```

```python
# stacked bar plot
df.plot.barh(stacked=True, alpha=0.5)
```

## Seaborn

```python
# bar plot with confidence interval
tips = pd.read_csv('data/tips.csv')
tips['tip_pct'] = tips['tip'] / (tips['total_bill'] - tips['tip'])
tips.head()
sns.barplot(x='tip_pct', y='day', data=tips, orient='h')
```

```python
# distinguish by column value
sns.barplot(x='tip_pct', y='day', hue='time', data=tips, orient='h')
```

```python
# histogram
tips['tip_pct'].plot.hist(bins=50)
```

```python
# density graph
tips['tip_pct'].plot.density()
```

```python
# histogram with normalized density graph
comp1 = np.random.normal(0, 1, size=200)
comp2 = np.random.normal(10, 2, size=200)
values = pd.Series(np.concatenate([comp1, comp2]))
sns.distplot(values, bins=100, color='k')
```

```python
# scatter plot with regression line
macro = pd.read_csv('data/macrodata.csv')
data = macro[['cpi', 'm1', 'tbilrate', 'unemp']]
trans_data = np.log(data).diff().dropna()
sns.regplot('m1', 'unemp', data=trans_data)
plt.title('Changes in log %s versus log %s' % ('m1', 'unemp'))
```

```python
# compare distributions of features df
sns.pairplot(trans_data, diag_kind='kde', plot_kws={'alpha': 0.2})
```

```python
# facet grids for categorical data, split by time
sns.factorplot(x='day', y='tip_pct', hue='time', col='smoker',
               kind='bar', data=tips[tips.tip_pct < 1])
```

```python
# split subplots by row and time
sns.factorplot(x='day', y='tip_pct',
               row='time',
               col='smoker',
               kind='bar', data=tips[tips.tip_pct < 1])
```

```python
# boxplot with confidence intervals
sns.factorplot(x='tip_pct', y='day', kind='box',
               data=tips[tips.tip_pct < 0.5])
```
