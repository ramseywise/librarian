---
imported_hash: 1272a743d9bc9f73
title: 3 | Arrays and Vectorization (NumPy)
summary: 'Some basic topics we cover here include: - Array indexing, slicing - Boolean array - Array operations'
order: 3
kind: notebook
source: learn-ai-engineering/programming/Python Basics/3_Arrays.ipynb
---

# 3 | Arrays and Vectorization (NumPy)

   > **`numpy`** is a Linear Algebra Library for Python. Almost all of the libraries in the PyData Ecosystem rely on Numpy as one of their main building blocks. Numpy is also incredibly fast, as it has bindings to C libraries.

Some basic topics we cover here include:
- Array indexing, slicing
- Boolean array
- Array operations

*Resources*:
- **Coursera Python for Informatics** (University of Michigan)
- **Coursera Applied Data Science in Python** (University of Michigan)
- **Python for Data Analytics** - Mckinney (O'Reilly)

```python
# import numpy as a library
import numpy as np
```

```python
# Generate some random data
data = np.random.randn(2, 3)
data
```

```python
# get #rows, #cols
data.shape
```

```python
# save and load array file
np.save('array_archive.npy', data)
arch = np.load('array_archive.npy')
arch
```

```python
# save and load array as io wrapper
np.savez('array_archive.npz', data)
arch = np.load('array_archive.npz')
arch
```

### Array Indexing and Slicing

```python
# compare times for range and np.arange
my_arr = np.arange(1000000)
my_list = list(range(1000000))

%time for _ in range(10): my_arr2 = my_arr * 2
%time for _ in range(10): my_list2 = [x * 2 for x in my_list]
```

```python
# array slicing
arr = np.arange(10)
# print 5 element in array
print(arr[5])
# print range of elements in array as list
print(arr[5:8])
```

```python
# select first two elements from left
arr[:2]
```

```python
# select first two elements from right
arr[-2:]
```

```python
# select from first two elements from right
arr[2:]
```

```python
# replace all elements
arr[:] = 64
arr
```

```python
# create empty array and fill rows
arr = np.empty((8, 4))
for i in range(8):
    arr[i] = i
arr
```

```python
# keep specified rows
arr[[4, 3, 0, 6]]
```

```python
# create array and reshape to 8 rows, 4 cols
arr = np.arange(32).reshape((8, 4))
arr
```

```python
# keep specified rows, but reorder using index
arr[[1, 5, 7, 2], [0, 3, 1, 2]]
arr[[1, 5, 7, 2]][:, [0, 3, 1, 2]]
```

```python
# transform rows orders cols across rows
arr.T
```

```python
# arithmetic with arrays
arr = np.array([[1., 2., 3.], [4., 5., 6.]])
arr * arr
```

```python
# sq root and exponential
np.sqrt(arr)
np.exp(arr)
```

```python
# replace value with np.where
np.where(arr > 3, 2, arr) # set values over 3 to 2
```

### Sorting

```python
# get unique items in array
names = np.array(['Bob', 'Joe', 'Will', 'Bob', 'Will', 'Joe', 'Joe'])
np.unique(names)
ints = np.array([3, 3, 3, 2, 2, 1, 1, 4, 4])
np.unique(ints)
```

```python
# sort ascending
arr = np.random.randn(6)
arr.sort()
arr
```

```python
# sort across (axis=1)
arr = np.random.randn(5, 3)
arr.sort(1)
arr
```

```python
# return 5% quantile
large_arr = np.random.randn(1000)
large_arr.sort()
large_arr[int(0.05 * len(large_arr))]
```

```python
# use ravel or flatten to reshape all values into one row
arr.ravel()
```

```python
#concat arrays
arr1 = np.array([[1, 2, 3], [4, 5, 6]])
arr2 = np.array([[7, 8, 9], [10, 11, 12]])
np.concatenate([arr1, arr2], axis=0)
np.concatenate([arr1, arr2], axis=1)
```

## Broadcasting

```python
arr = np.random.randn(4, 3)
arr
```

```python
# get mean across rows and columns
arr.mean()
```

```python
# get mean across columns (axis=0)
arr.mean(0)
```

```python
# get mean across rows (axis=1)
arr.mean(1)
```

```python
# create array with broadcasting
col = np.array([1.28, -0.42, 0.44, 1.6])
arr[:] = col[:, np.newaxis]
arr
```

```python
# replace first two rows with two values
arr[:2] = [[-1.37], [0.509]]
arr
```
