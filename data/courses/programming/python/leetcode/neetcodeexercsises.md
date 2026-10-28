---
imported_hash: f05d5c470a4c0e30
title: Neet Code Exercises
summary: nums = [1,2,3,5,78,9,2] containsDuplicate(nums)
order: 13
kind: notebook
section: Leetcode
source: sisyphus/drills/python/leetcode/NeetCodeExercsises.ipynb
---

# Neet Code Exercises

### 217.Contains Duplicate

```python
# get unique numbers
nums = [1,4,5,1,2,3,1]
set(nums)
```

```python
# indexing with enumerate --> returns iterator object (index, element)
presidents = ["Washington", "Adams", "Jefferson", "Madison", "Monroe", "Adams", "Jackson"]
for i in enumerate(presidents, start=1):
    print(i)
```

```python
# indexing with range() --> index [i] and element presidents[i] are separate
presidents = ["Washington", "Adams", "Jefferson", "Madison", "Monroe", "Adams", "Jackson"]
for i in range(len(presidents)):
    print("President {}: {}".format(i + 1, presidents[i]))
```

```python
# sort elements in list
sorted(presidents)
```

```python
# get unique elements in list
set(presidents)
```

```python
    def containsDuplicate(nums):
        #sort(nums)
        nums = sorted(nums) # first sort list
        for x in range(len(nums)-1): # create index of elements in list starting with 0
            if nums[x]==nums[x+1]:
                return True

        return False

nums = [1,2,3,5,78,9,2]
containsDuplicate(nums)
```

### ??? | Merge Sort

```python
## Adrian's solution. Great Job!
def mergeSort(array):
    "Returns sorted array."
    # split the big array into halves and populate them
    n = len(array)
    if(n<=1):
        return
    mid = n // 2
    left = array[:mid]
    right = array[mid:]

    # call the functions recursively for each half
    mergeSort(left)
    mergeSort(right)

    # merge arrays based on sorting algorithm below
    result = merge(left, right)

    return result

def merge(left, right):
    "Merge arrays as already sorted least to greatest."
    xl = len(left)
    xr = len(right)
    leftPointer = 0
    rightPointer = 0
    resultPointer = 0
    result = [None] * n # create empty matrix with same n elements as original array

    while (leftPointer < xl | rightPointer < xr): # if there are still elements to look through in either half
        if (leftPointer < xl & rightPointer < xr): # if there are still elements to look through in both halves
            if (left[leftPointer] < right[rightPointer]): # compare elements of left & right arrays
                result[resultPointer] = left[leftPointer]
                resultPointer += 1
                leftPointer += 1
            else:
                result[resultPointer] = right[rightPointer]
                resultPointer += 1
                rightPointer += 1

        elif (leftPointer < xl): # if left array still has elements
            result[resultPointer] = left[leftPointer]
            resultPointer += 1
            leftPointer += 1

        else: # if right array still has elements, i.e. (rightPointer < xr)
            result[resultPointer] = right[rightPointer]
            resultPointer += 1
            rightPointer += 1

    return result
```

```python
array = [234, 23, 23, 1, 435, 634, 2342, 2654, 3]
mergeSort(array)

# is not working!!
```

```python
# online example from https://www.educative.io/edpresso/merge-sort-in-python
def mergeSort(myList):
    if len(myList) > 1:
        mid = len(myList) // 2
        left = myList[:mid]
        right = myList[mid:]

        # Recursive call on each half
        mergeSort(left)
        mergeSort(right)

        # Two iterators for traversing the two halves
        i = 0
        j = 0

        # Iterator for the main list (this does not create a new empty list but repopulates the old)
        k = 0

        while i < len(left) and j < len(right): # as long as there are still elements in both arrays
            if left[i] <= right[j]: # <=, not just <
                # The value from the left half has been used, move the left iterator forward
                myList[k] = left[i]
                i += 1
            else: # move the left iterator forward
                myList[k] = right[j]
                j += 1
            # Move main list iterator to the next slot
            k += 1

        # For all the remaining values in either array
        while i < len(left):
            myList[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            myList[k]=right[j]
            j += 1
            k += 1

myList = [54,26,93,17,77,31,44,55,20]
mergeSort(myList)
print(myList)
```

### 121. Best Time to Buy and Sell Stock

```python
def maxProfit(prices):
    bestBuyPrice = prices[0]
    bestBuyDay = 0
    bestSellPrice = prices[0]
    bestSellDay = 0
    result = 0
    for i in range(len(prices)):
        if prices[i] < bestBuyPrice:
            bestBuyPrice = prices[i]
            bestBuyDay = i
            print('new buy', bestBuyPrice, bestBuyDay)
        if (prices[i] > bestSellPrice) | (bestSellPrice - bestBuyPrice > result):
            bestSellPrice = prices[i]
            bestSellDay = i
            print('new sell', bestSellPrice, bestSellDay)
        if (bestSellPrice - bestBuyPrice > result) & (bestSellDay > bestBuyDay):
            result = bestSellPrice - bestBuyPrice
            print('new maxProfit', result)
    return result

prices = [7,6,4,3,1]
print('end result', maxProfit(prices))
```

```python
def maxProfit(prices):
    l,r = 0,1 #left=buy, right=sell
    maxP = 0
    while r < len(prices):
        if prices[l] < prices[r]: # buy low, sell high = profit
            profit = prices[r] - prices[l]
            maxP = max(maxP, profit)
        else:
            l += 1 # increase left window if not profitable
        r += 1 # increase right window

    return maxP
```

```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        res = 0

        l = 0
        for r in range(1, len(prices)):
            if prices[r] < prices[l]:
                l = r
            res = max(res, prices[r] - prices[l])
        return res
```

## 3. Longest Substring Without Repeating Characters

```python
def longestSubstring(s):
    left, right = 0, 0
    subs = s[0]
    result = 1
    chars = set(subs)
    for right in range(1, len(s)):
        if s[right] not in chars:
            chars.add(s[right])
    print(chars)
    return

longestSubstring('dsgsdfsd')
```

```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        charSet = set()
        l = 0
        res = 0

        for r in range(len(s)):
            while s[r] in charSet:
                charSet.remove(s[l])
                l += 1
            charSet.add(s[r])
            res = max(res, r - l + 1)
        return res
```
