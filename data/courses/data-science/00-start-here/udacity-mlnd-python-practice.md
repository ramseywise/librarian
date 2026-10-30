---
imported_hash: 98e62570f6e783c8
title: Connect Intensive - Machine Learning Nanodegree
summary: In this notebook, we will do some visualization on the Iris dataset.
order: 5
kind: notebook
source: learn-ai-engineering/data-science/udacity_mlnd_python_practice.ipynb
---

# Connect Intensive - Machine Learning Nanodegree

## Week 1. Python Crash Course

## Objectives

- Jupyter notebook
- Basic Python programming
- Numpy
- Pandas
- Data visualization with Matplotlib and Seaborn

## Prerequisites

 - You should have **Python 2.7** installed (if not, please [download and install Python 2.7](https://www.python.org/downloads/))
 - You should also install (and perhaps upgrade) the following packages, if you haven't already:
    - [numpy](http://www.numpy.org/)
    - [pandas](http://pandas.pydata.org/)
    - [matplotlib](http://matplotlib.org/)
    - [seaborn](http://seaborn.pydata.org)

---

## 4 | Data Visualization

In this notebook, we will do some visualization on the Iris dataset. We will learn about **pandas built-in plotting** capabilities for data visualization, which is a built-off of matplotlib, and it is built into the `.plot` method for pandas `DataFrame` and `Series`. It is used for easily create decent looking plots. We will also create some visualization with **seaborn**. Seaborn is also based on matplotlib but with much more visually appealing default aesthetics. It is also easy to use and supports a variety of plot types.

We are going to cover some common plot types with pandas built-in plotting and seaborn, including:
- Histogram
- Scatter plot
- Bar plot

We will also mention briefly about how to style your plots.

*Note*: This notebook is not intended to serve as a comprehensive overview of data visualization with Python. There are a lot more topics not covered in this notebook. You are encouraged to explore them on your own. Luckily, there are many resources available.

> **Adtional reference:**
> - Check out a Matplotlib cheat sheet [here](http://www.datasciencecentral.com/profiles/blogs/matplotlib-cheat-sheet)
> - Check out a Pandas built-in visualization tutorial [here](https://pandas.pydata.org/pandas-docs/stable/visualization.html).
> - Check out a Seaborn tutorial [here](https://seaborn.pydata.org/tutorial.html)
> - Check out a Seaborn cheatsheet [here](https://www.datacamp.com/community/blog/seaborn-cheat-sheet-python#gs.hd6oyO8).

```python
# import the libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
%matplotlib inline
```

```python
# read the iris data
data = pd.read_table('./data/iris.txt', delimiter=',')
data.head()
```

### Pandas Built-in Plot

There are many available plot types in pandas visualization, as listed below:
* data.plot.area
* data.plot.barh
* data.plot.density
* data.plot.hist
* data.plot.line
* data.plot.scatter
* data.plot.bar
* data.plot.box
* data.plot.hexbin
* data.plot.kde
* data.plot.pie

You can also just call data.plot(kind='hist') ('hist' can be replaced with other terms, e.g., 'box','barh', etc..)

**hist()**

```python
data['sepal_w'].plot.hist()
```

```python
# add axis label, title
data['sepal_w'].plot.hist() # can specify number of bins
plt.xlabel('Sepal Width (cm)')
plt.ylabel('Frequency')
plt.title('Histogram of Sepal Width')
```

**scatter()**

```python
data.plot.scatter(x='sepal_l', y='sepal_w')
```

You can use `c` to color based on another column value. Use `cmap` to indicate colormap. The available colormaps can be find [here](http://matplotlib.org/users/colormaps.html). **Run** the cell below to plot a scatter plot using `x = sepal_l`,  `y = sepal_w`, and `c = petal_w`.

```python
data.plot.scatter(x='sepal_l', y='sepal_w', c='petal_w', cmap='coolwarm')
```

Clearly, you've encoded more information to this plot than the simple scatter plot above.

**Style Sheets**

Matplotlib has [style sheets](http://matplotlib.org/gallery.html#style_sheets) you can use to make your plots look a little nicer. These style sheets include '`bmh`', '`fivethirtyeight`', '`ggplot`' and more. They basically create a set of style rules that your plots follow.

```python
# Before setting style
data['sepal_l'].plot.hist()
```

```python
# setting the style as fivethirtyeight
plt.style.use('fivethirtyeight')
data['sepal_l'].plot.hist()
```

```python
# setting the style as ggplot
plt.style.use('ggplot')
data['sepal_l'].plot.hist()
```

### Seaborn

Seaborn is a Python visualization library based on matplotlib. It provides a high-level interface for drawing attractive statistical graphics.

Seaborn aims to make visualization a central part of exploring and understanding data. The plotting functions operate on dataframes and arrays containing a whole dataset and internally perform the necessary aggregation and statistical model-fitting to produce informative plots.

> If matplotlib **“tries to make easy things easy and hard things possible”**, seaborn tries to **make a well-defined set of hard things easy** too.

**distplot()**
distplot() provides the most convenient way to take a quick look at a univariate distribution.

```python
sns.distplot(data['sepal_l'])
```

Note that the matplot style set above also affects the seaborn style.

```python
# try a different style
plt.style.use('bmh')
sns.distplot(data['sepal_l'])
```

```python
# we can remove the kde layer and just have the histogram
sns.distplot(data['sepal_l'], kde=False)
```

**joinplot()**

jointplot() allows you to match up two distplots for bivariate data. With your choice of what **kind** parameter to compare with:
* “scatter”
* “reg”
* “resid”
* “kde”
* “hex”

```python
sns.jointplot(x='sepal_l', y='sepal_w', data=data, kind='scatter')
```

**barplot & countplot**

Seaborn has the capability to plot categorical data with different plot types, and some main plot types include:

* factorplot
* boxplot
* violinplot
* stripplot
* swarmplot
* barplot
* countplot

**barplot()** and **countplot()** are two simple kinds of plots. You are encouraged to explore other plots by yourself, especially boxplot and violinplot.

```python
# barplot allows you to aggregate the categorical data based on some function, default is mean
sns.barplot(x='type', y='sepal_l', data=data)
```

```python
# countplot to count the number of occurrences of categorical data
sns.countplot(x='type', data=data)
```

**Styles**

You can set the styles for seaborn plot using `sns.set_style()`. The available options are '`white`', '`whitegrid`', '`dark`', '`darkgrid`', and '`tick`'.

```python
sns.set_style('whitegrid')
sns.distplot(data['sepal_l'])
```
