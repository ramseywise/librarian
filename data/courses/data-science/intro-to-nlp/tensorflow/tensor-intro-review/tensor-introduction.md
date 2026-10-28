---
imported_hash: d85b441bb1e09848
title: TensorFlow Introduction
summary: A tensor is an algebraic object that describes a (multilinear) relationship between sets of algebraic objects related to a vector space.
order: 16
kind: notebook
section: tensorFlow / Tensor intro review
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/tensor-intro-review/tensor_introduction.ipynb
---

# TensorFlow Introduction

A tensor is an algebraic object that describes a (multilinear) relationship between sets of algebraic objects related to a vector space. Objects that tensors may map between include vectors and scalars, and even other tensors. Tensors are immutable - cannot update them, only create a new one. Examples of using Tensors in tensorflow:
- Basic Tensors - different ranks
- Tensor shapes
- Tensor Indexing
- Resphaping Tensors

```python
# importing packages
import tensorflow as tf
import numpy as np
```

```python
# checking version
tf.__version__
```

# Basic Tensors

### Zero rank tensor (constant)

```python
# data type is int32
rankZero = tf.constant(10)
rankZero
```

### Rank 1 tensor (vector)

```python
# data type is float32
rankOne = tf.constant([0.0, 1.0, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 21.0, 34.0])
print(rankOne)
rankOne
```

### Rank 2 tensor (matrix) - has 2 axes

```python
# data type is float64
rankTwo = tf.constant([[1, 2], [3, 4], [5, 6]], dtype=tf.float64)
print(rankTwo)
```

### Tensor with 3 axes (dimensions)

```python
# data type is int32
rankThree = tf.constant([
  [[10, 11, 12, 13, 14],
   [15, 16, 17, 18, 19]],
  [[20, 21, 22, 23, 24],
   [25, 26, 27, 28, 29]],
  [[30, 31, 32, 33, 34],
   [35, 36, 37, 38, 39]],])
print(rankThree)
```

### Convert Tensor to NumPy array

```python
# converting a tensor to a numpy array
rankThree.numpy()
```

```python
# converting tensor to a numpy array
a = np.array(rankThree)
print(type(a))
```

```python
a
```

# tf.Tensor

**tf.Tensor** class used in many datasets requires the tensors to be rectangular - along each axis, every element is the same size. **tf.Tensor** supports addition, element-wise multiplication and matrix multiplication.

```python
# creating a tensor
x = tf.constant([[1, 2], [3, 4]])
x
```

```python
# creating a tensor
y = tf.constant([[2, 3], [2, 3]])
y
```

```python
# printing calculations
print(tf.add(x, y), "\n")
print(tf.multiply(x, y), "\n")
print(tf.matmul(x, y), "\n")
```

```python
# assigning values to a tensor
z = tf.constant([[4.0, 5.0], [10.0, 1.0]])
print(z)
```

```python
# finding the index of max value
print(tf.argmax(z))
```

```python
# finding the largest value
print(tf.reduce_max(z))
```

# Tensor Shapes

- **Shape:** The length (number of elements) of each of the dimensions of a tensor.
- **Rank:** Number of tensor dimensions. A scalar has rank 0, a vector has rank 1, a matrix is rank 2.
- **Dimension or Axis:** A particular dimension of a tensor.
- **Size:** The total number of items in the tensor, the product shape vector.

Tensors and **tf.TensorShape** provide useful properties for accessing information

```python
# 4 dimension tensor initialized to zeros
rankFour = tf.zeros([3, 2, 4, 5])
```

```python
print("Type of every element:", rankFour.dtype)
print("Number of dimensions:", rankFour.ndim)
print("Shape of tensor:", rankFour.shape)
print("Elements along axis 0 of tensor:", rankFour.shape[0])
print("Elements along the last axis of tensor:", rankFour.shape[-1])
print("Total number of elements (3*2*4*5): ", tf.size(rankFour))
print("Total number of elements (3*2*4*5): ", tf.size(rankFour).numpy())
```

# Tensor Indexing

- Zero based indexing
- Can use negative indexing (counts backwards), starts with -1
- Just like python list use colons *start:stop:step*.

### Single dimension indexing

```python
print(rankOne.numpy())
```

```python
print("First:", rankOne[0].numpy())
print("Second:", rankOne[1].numpy())
print("Last:", rankOne[-1].numpy())
```

```python
# like python list slicing
print("Everything:", rankOne[:].numpy())
print("Before 4:", rankOne[:4].numpy())
print("From 4 to the end:", rankOne[4:].numpy())
print("From 2, before 7:", rankOne[2:7].numpy())
print("Every other item:", rankOne[::2].numpy())
print("Reversed:", rankOne[::-1].numpy())
```

### Multi dimension/axis indexing

```python
print(rankTwo.numpy())
```

```python
# getting single value from a 2-rank tensor
print(rankTwo[1, 1].numpy())
```

```python
print("Second row:", rankTwo[1, :].numpy())
print("Second column:", rankTwo[:, 1].numpy())
print("Last row:", rankTwo[-1, :].numpy())
print("First item in last column:", rankTwo[0, -1].numpy())
print("Skip the first row:")
print(rankTwo[1:, :].numpy(), "\n")
```

```python
print(rankThree.numpy())
```

```python
# rankThree is (3 x 2 x 5) tensor and all values at index 4 of the last axis is printed
print(rankThree[:, :, 4])
```

## Manipulating Shape

- Reshaping is very useful especially when handling images, texts data.
- **tf.reshape** is very fast and cheap operation as the data does not need to be duplicated.
- The data maintains its layout in memory and a new tensor is created, with the requested shape, pointing to the same data.

```python
# shape returns a `TensorShape` object that shows the size on each dimension
x = tf.constant([[1], [2], [3]])
print(x.shape)
```

```python
# converting this object into a Python list, too
print(x.shape.as_list())
```

```python
# reshaping a tensor to a new shape
reshaped = tf.reshape(x, [1, 3])
```

```python
print(x.shape)
print(reshaped.shape)
```

```python
print(rankThree)
```

```python
# `-1` passed in the `shape` argument says "Whatever fits"
print(tf.reshape(rankThree, [-1]))
```

```python
# reshaping to (3x2)x5
print(tf.reshape(rankThree, [6, 5]), "\n")
```

```python
# reshaping to 3x(2x5)
print(tf.reshape(rankThree, [3, -1]))
```
