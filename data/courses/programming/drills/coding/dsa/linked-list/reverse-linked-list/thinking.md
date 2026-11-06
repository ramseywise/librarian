---
title: Reverse Linked List — First-Principles Thinking Guide
summary: Iterate through the list. At each node, reverse its next pointer to point to the previous node.
order: 179
kind: reading
section: Coding / Dsa / Linked list / Reverse linked list
source: learn-ai-engineering/programming/drills/coding/dsa/linked_list/reverse_linked_list/THINKING.md
---

# Reverse Linked List — First-Principles Thinking Guide

## 1. Understanding the Problem

**Restate**: Reverse a singly linked list in-place.

## 2. Key Insight (Three Pointers)

Iterate through the list. At each node, reverse its `next` pointer to point to the previous node. Need three pointers: `prev`, `current`, `next_temp`.

## 3. Building the Solution

```text
prev = None, current = head
While current:
    next_temp = current.next   ← save next
    current.next = prev        ← reverse pointer
    prev = current             ← advance prev
    current = next_temp        ← advance current
Return prev  ← new head
```

## 4. Complexity

**Time**: O(n).
**Space**: O(1).
