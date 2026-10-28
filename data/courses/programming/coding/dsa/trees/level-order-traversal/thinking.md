---
imported_hash: c70113b2e45bdb9d
title: Level Order Traversal — First-Principles Thinking Guide
summary: 'While queue is not empty: levelsize = len(queue) levelvalues = [] For each of levelsize nodes: node = queue.popleft() levelvalues.append(node.val) Enqueue left and right children result.append(levelvalues)'
order: 133
kind: reading
section: Dsa / Trees / Level order traversal
source: sisyphus/drills/coding/dsa/trees/level_order_traversal/THINKING.md
---

# Level Order Traversal — First-Principles Thinking Guide

## 1. Understanding the Problem

**Restate**: Visit all tree nodes left-to-right, one level at a time. Return each level as a separate list.

## 2. Building Intuition

**Level-by-level** = **Breadth-First Search**. BFS naturally visits nodes in level order when using a queue.

**The level boundary trick**: At the start of processing each level, `len(queue)` tells us exactly how many nodes are at the current level. Process that many nodes, and their children form the next level.

## 3. Building the Solution

```text
queue = [root]
result = []

While queue is not empty:
    level_size = len(queue)
    level_values = []
    For each of level_size nodes:
        node = queue.popleft()
        level_values.append(node.val)
        Enqueue left and right children
    result.append(level_values)
```

## 4. Complexity Analysis

**Time**: O(n) — visit every node once.
**Space**: O(n) — queue can hold up to n/2 nodes (at widest level).
