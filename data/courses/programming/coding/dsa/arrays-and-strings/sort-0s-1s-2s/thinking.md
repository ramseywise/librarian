---
imported_hash: 49aed7b44e660bd8
title: Sort 0s, 1s, and 2s (Dutch National Flag) — First-Principles Thinking Guide
summary: 'Use three pointers: low, mid, high.'
order: 38
kind: reading
section: Dsa / Arrays and strings / Sort 0s 1s 2s
source: sisyphus/drills/coding/dsa/arrays_and_strings/sort_0s_1s_2s/THINKING.md
---

# Sort 0s, 1s, and 2s (Dutch National Flag) — First-Principles Thinking Guide

## 1. Understanding the Problem

**Restate**: Sort an array containing only 0, 1, and 2 in a single pass.

## 2. Key Insight (Dutch National Flag Algorithm)

Use three pointers: `low`, `mid`, `high`.

- [0, low): all 0s
- [low, mid): all 1s
- (high, end]: all 2s

Scan with `mid`: swap 0s to `low`, swap 2s to `high`, skip 1s.

## 3. Building the Solution

```text
low = mid = 0, high = n-1
While mid <= high:
    If arr[mid] == 0: swap(arr[low], arr[mid]), low++, mid++
    If arr[mid] == 1: mid++
    If arr[mid] == 2: swap(arr[mid], arr[high]), high--
```

## 4. Complexity

**Time**: O(n) — single pass.
**Space**: O(1) — in-place.
