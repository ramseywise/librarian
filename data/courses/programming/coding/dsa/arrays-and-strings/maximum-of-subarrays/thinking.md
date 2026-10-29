---
imported_hash: c644591f5ea05cce
title: Maximum of All Subarrays of Size K — First-Principles Thinking Guide
summary: Use a deque that stores indices in decreasing order of their values.
order: 26
kind: reading
section: Dsa / Arrays and strings / Maximum of subarrays
source: sisyphus/drills/coding/dsa/arrays_and_strings/maximum_of_subarrays/THINKING.md
---

# Maximum of All Subarrays of Size K — First-Principles Thinking Guide

## 1. Understanding the Problem

**Restate**: Given an array and window size K, find the maximum element in each window of size K.

## 2. Key Insight (Monotonic Deque)

Use a deque that stores indices in decreasing order of their values. The front always holds the index of the maximum in the current window.

## 3. Building the Solution

```text
deque = []
result = []

For each index i:
    Remove indices from back while arr[deque.back] <= arr[i]
    Add i to back
    Remove front if it's out of window (i - K)
    If i >= K-1: result.append(arr[deque.front])
```

## 4. Complexity

**Time**: O(n) — each element added/removed from deque at most once.
**Space**: O(K) — deque size.
