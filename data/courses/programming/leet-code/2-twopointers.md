---
imported_hash: 0adc7e9ad1ddc6cc
title: ex 1
summary: tbd.. - 42. trapping rain water (hard)
order: 2
kind: notebook
source: learn-ai-engineering/programming/Leet-Code/2_TwoPointers.ipynb
---

## Two Pointers

       - 9. check if Palindrome (easy)
       - 11. container holds max water (medium)
       - 15. 3Sum
       - 167. two sum II

       tbd..
       - 42. trapping rain water (hard)

### Problem 9: Check if Palindrome with integer only

```python
def isPalindrome(x):
    """Assert whether number reads the same backwards and forwards using math.log."""
    temp=x # store integer as temporary value
    rev=0 # create reverse variable
    while(x>0):
        dig=x%10 # % modulus operator stores last digit of number
        rev=rev*10+dig # last digit stored as reverse
        x=x//10 # // divides number and rounds quotient to whole number

    return print(temp==rev) # convert to str, count down beginning to end by 1
```

```python
# ex 1
x = 1223221
isPalindrome(x)
```

### Problem 9a: Palindrome with string

```python
def isPalindrome(x):
    """Assert whether number reads the same backwards and forwards."""

    return str(x) == str(x)[::-1] # convert to str, count down end to beginning by 1
```

```python
# ex 2
x = "abbac"
isPalindrome(x)
```

```python
# ex 3
x = -121
isPalindrome(x)
```

### Problem 9b: every odd number

```python
def everyOdd(x):
    """Assert whether number reads the same backwards and forwards."""

    return str(x)[::2] # convert to str, count down beginning to end by 2
```

```python
x = 12345678910
everyOdd(x)
```

### 11. Container with most water

```python
def containerMaxWater():
    """You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i])."""

height = [1,8,6,2,5,4,8,3,7]
```

```python
class Solution:
    def maxArea(self, height: List[int]) -> int:
        l, r = 0, len(height) - 1
        res = 0

        while l < r:
            res = max(res, min(height[l], height[r]) * (r - l))
            if height[l] < height[r]:
                l += 1
            elif height[r] <= height[l]:
                r -= 1
        return res
```

## 15. 3Sum

### 42. Trapping Rain Water

```python
def TrappingRainWater():
    """Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining."""

height = [0,1,0,2,1,0,1,3,2,1,2,1]
```

## 167. Two Sum II - Input Array Is Sorted

```python
def twoSum(numbers, target):
    left, right = 0, len(numbers) - 1
    sum_num = numbers[left] + numbers[right]
    while sum_num != target:
        if numbers[right] > target:
            right -= 1
        else:
            left += 1
        sum_num = numbers[left] + numbers[right]
    return (left+1, right+1)
```

```python
numbers = [2,7,11,15]
target = 9
print(twoSum(numbers, target))
```

```python
numbers = [2,3,4]
target = 6
print(twoSum(numbers, target))
```
