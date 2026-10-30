---
imported_hash: 657753df5d217e35
title: Subarray Average of Size K — First-Principles Thinking Guide
summary: 'Same pattern as Maximum Average Subarray: slide a window of size K across the array.'
order: 205
kind: reading
section: Dsa / Sliding window / Subarray average size k
source: sisyphus/drills/coding/dsa/sliding_window/subarray_average_size_k/THINKING.md
---

# Subarray Average of Size K — First-Principles Thinking Guide

## 1. Understanding the Problem

**Restate**: Given an array, find the average of every contiguous subarray of size K.

## 2. Key Insight (Fixed-Size Sliding Window)

Same pattern as Maximum Average Subarray: slide a window of size K across the array. For each position, compute average = window_sum / K.

## 3. Building the Solution

```text
window_sum = 0, result = []

For i from 0 to n-1:
    window_sum += arr[i]
    If i >= K-1:
        result.append(window_sum / K)
        window_sum -= arr[i - K + 1]
```

## 4. Complexity

**Time**: O(n).
**Space**: O(n - K + 1) for results.
