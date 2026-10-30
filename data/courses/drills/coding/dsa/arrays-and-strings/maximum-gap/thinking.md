---
imported_hash: 1180a1caecfa72a2
title: Maximum Gap — First-Principles Thinking Guide
summary: ''
order: 114
kind: reading
section: Dsa / Arrays and strings / Maximum gap
source: sisyphus/drills/coding/dsa/arrays_and_strings/maximum_gap/THINKING.md
---

# Maximum Gap — First-Principles Thinking Guide

## 1. Understanding the Problem

**Restate**: Find the maximum difference between successive elements in sorted form of an unsorted array.

## 2. Key Insight

**Sorting approach**: Sort and scan adjacent pairs → O(n log n).
**Optimal**: Pigeonhole/bucket sort principle can achieve O(n), but sorting approach is clean and practical for interviews.

## 3. Building the Solution

```text
Sort the array
max_gap = 0
For i from 1 to n-1:
    max_gap = max(max_gap, nums[i] - nums[i-1])
```

## 4. Complexity

**Time**: O(n log n) with sorting.
**Space**: O(1) extra (in-place sort).
