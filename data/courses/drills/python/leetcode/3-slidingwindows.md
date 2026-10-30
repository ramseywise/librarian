---
imported_hash: 84c7202de6188ad9
title: SlidingWindows
summary: TBD.. - 424. longest repeating character replacement (medium) - 567.
order: 10
kind: notebook
section: Leetcode
source: sisyphus/drills/python/leetcode/3_SlidingWindows.ipynb
---

## Sliding Windows

        - 3. longest substring without repeating characters (easy)
        - 121. best time to buy and sell stock (medium)

        TBD..
        - 424. longest repeating character replacement (medium)
        - 567. permutation in string (medium)
        - 76.  minimum window substring (hard)
        - 239. maximum window substring (hard)

### 3. Longest Substring Without Repeating Characters

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
