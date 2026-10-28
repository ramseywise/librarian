---
imported_hash: c09ce254472e13a2
title: ex 1
summary: 'return [] # if no solution found, return emptyt list'
order: 1
kind: notebook
source: learn-ai-engineering/programming/Leet-Code/1_ArraysHashing.ipynb
---

## Arrays & Hashing

       - 1.   Sum integers (easy)
       - 128. Longest consecutive subsequence (medium)
       - 217. Contains duplicate (easy)
       - 242. Valid Anagram (easy)
       - 271. Encode-Decode strings (medium)
       - 347. topKFreuquent (medium)

### 1. Two Sum of Indices

```python
def twoSumI(nums, target):
    """ Return the indices of two numbers in a list that equal the target."""
    values = dict() # use dict to map complement of value to index it corresponds
    for i, j in enumerate(nums): # map value j to index i
        val = target - j # calculate corresponding value
        if val > 0 and val in values: # check if value is positive and in dict
            return [values[val], i] # if so, return index position of nums for value j in dict
        values[j] = i # if corresponding value is not in dict, continue to second value in dict

    return []  # if no solution found, return emptyt list
```

```python
# ex 1
target = 9
nums = [2,7,11,15]
twoSumI(nums, target)
```

```python
# ex 2 --> no solution
nums = [4,7,11,15]
twoSumI(nums, target)
```

### Problem 1a: Sum two numbers

```python
def twoSum(nums, target):
    """ Return two numbers in a list that equal the target."""
    values = dict() # use dict to map complement of value to index it corresponds
    for i, j in enumerate(nums): # map value j to index i
        val = target - j # calculate corresponding value
        if val > 0 and val in values: # check if value is positive and in dict
            return val, j # if so, return index position of nums for value j in dict
        values[j] = i # if corresponding value is not in dict, continue to second value in dict

    return []  # if no solution found, return emptyt list
```

```python
# ex 1
target = 9
nums = [2,7,11,15]
twoSum(nums, target)
```

### 128. Longest Consecutive Sequence

```python
def longestConsecutiveSequence(nums):
    """Given an unsorted array of integers nums, return the length of the longest consecutive elements sequence."""
    # take unique elements in list
    res = 1
    fun = set(nums)
    for f in fun:
        if f+1 in fun:
            res += 1
    return res
nums = [100,4,200,1,3,2]
longestConsecutiveSequence(nums)
```

```python
nums = [0,3,7,2,5,8,4,6,0,1]
longestConsecutiveSequence(nums)
```

### 217. Contains Duplicate

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
        """Given an integer array nums, return true if any value appears at least twice in the array, and return false if every element is distinct."""
        #sort(nums)
        nums = sorted(nums) # first sort list
        for x in range(len(nums)-1): # create index of elements in list starting with 0
            if nums[x]==nums[x+1]:
                return True

        return False

nums = [1,2,3,5,78,9,2]
containsDuplicate(nums)
```

### 242. Valid Anagram

```python
def validAnagram(s,t):
    """Given two strings s and t, return true if t is an anagram of s, and false otherwise."""

    if len(s) != len(t): # strings must be same length
        return False

    elif sorted(s) == sorted(t): # sort and compare
        return True

    else:
        return False

s = "anagram"
t = "nagaram"
validAnagram(s,t)
```

```python
def validAnagram(s,t):
    """Given two strings s and t, return true if t is an anagram of s, and false otherwise."""
    if len(s) != len(t):  # strings must be same length
        return False

    countS, countT = {}, {} # create empty dict for char counts

    for i in range(len(s)): # count each char in string
        countS[s[i]] = 1 + countS.get(s[i], 0)
        countT[t[i]] = 1 + countT.get(t[i], 0)
    for c in countS:
        if countS[c] != countT.get(c, 0):
            return False
    return True


validAnagram(s,t)
```

### 271. Encode and Decode Strings

```python
def encode(strs):
    """Encode a list of strings to a string using delimiter and string length."""
    res = ""
    for s in strs:
        res += str(len(s)) + "#" + s # append each string to single result string with # delimiter
    return res

strs = ['lint','code','love','you']
encode_strs = encode(strs)
print(encode_strs)
```

```python
def decode(encode_strs):
    """Decode single string to original list of strings."""
    res, i = [], 0 # set char index to 0

    while i < len(encode_strs):
        j = i
        while encode_strs[j] != "#": # search for delimiter to separate strings
            j += 1
        length = int(encode_strs[i:j]) # get lenth of str
        res.append(encode_strs[j + 1 : j + 1 + length])
        i = j + 1 + length

    return res

decode(encode_strs)
```

### 347. Top K Frequent Elements

```python
def topKFrequent(nums,k):
    """Given an integer array nums and an integer k, return the k most frequent elements. You may return the answer in any order."""
    count = {} # create count hash map for values in nums
    freq = [[] for i in range(len(nums) + 1)] # list of list bucket sort by counts (index)

    for n in nums:
        count[n] = 1 + count.get(n, 0) # for each elem in nums, increase count (start from 0)
    for n, c in count.items():
        freq[c].append(n) # for key-value pairs n count, append as list of list, reversing key-value of count

    res = []
    for i in range(len(freq) - 1, 0, -1): # descending counts per element in list of list
        for n in freq[i]:
            res.append(n) # append values that have max counts
            if len(res) == k: # append k values
                return res

nums = [1,1,1,2,2,3]
k = 2
topKFrequent(nums,k)
```
