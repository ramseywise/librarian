---
imported_hash: 24d8a17553892611
title: Design Circular Queue — First-Principles Thinking Guide
summary: Use an array of size k with front and rear pointers.
order: 187
kind: reading
section: Dsa / Queues / Design circular queue
source: sisyphus/drills/coding/dsa/queues/design_circular_queue/THINKING.md
---

# Design Circular Queue — First-Principles Thinking Guide

## 1. Understanding the Problem

**Restate**: Implement a fixed-size circular queue with enqueue, dequeue, front, rear, isEmpty, isFull.

## 2. Key Insight (Circular Array)

Use an array of size k with `front` and `rear` pointers. The circular part: `rear = (rear + 1) % k` wraps around to the beginning when the end is reached.

## 3. Building the Solution

```text
init: array[k], front = -1, rear = -1, size = 0

enQueue(val):
    If full: return False
    rear = (rear + 1) % k
    array[rear] = val, size++

deQueue():
    If empty: return False
    front = (front + 1) % k, size--
```

## 4. Complexity

All operations: **O(1) time**, **O(k) space**.
