---
imported_hash: 8f70e0724bfa9f27
title: Detect Cycle in Linked List — First-Principles Thinking Guide
summary: 'Use two pointers: slow (moves 1 step) and fast (moves 2 steps).'
order: 175
kind: reading
section: Coding / Dsa / Linked list / Detect cycle
source: learn-ai-engineering/programming/drills/coding/dsa/linked_list/detect_cycle/THINKING.md
---

# Detect Cycle in Linked List — First-Principles Thinking Guide

## 1. Understanding the Problem

**Restate**: Determine if a linked list has a cycle.

## 2. Key Insight (Floyd's Tortoise and Hare)

Use two pointers: slow (moves 1 step) and fast (moves 2 steps). If there's a cycle, fast will eventually meet slow inside the cycle. If no cycle, fast reaches null.

## 3. Building the Solution

```text
slow = fast = head
While fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    If slow == fast: return True
Return False
```

**Why it works**: In a cycle, the gap between fast and slow decreases by 1 each step, so they must meet.

## 4. Complexity

**Time**: O(n).
**Space**: O(1).
