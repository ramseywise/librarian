---
imported_hash: cb292a963d9511f6
title: Merge Two Sorted Lists — First-Principles Thinking Guide
summary: 'While both lists have nodes: If list1.val <= list2.val: current.next = list1; list1 = list1.next Else: current.next = list2; list2 = list2.next current = current.next'
order: 176
kind: reading
section: Dsa / Linked list / Merge two sorted lists
source: sisyphus/drills/coding/dsa/linked_list/merge_two_sorted_lists/THINKING.md
---

# Merge Two Sorted Lists — First-Principles Thinking Guide

## 1. Understanding the Problem

**Restate**: Given two sorted linked lists, combine them into one sorted list using the existing nodes.

## 2. Building Intuition

**This is the merge step of merge sort**. Compare the heads of both lists, take the smaller, advance that pointer. Repeat.

**Dummy head pattern**: Using a sentinel node as the starting point eliminates edge cases for "which node is the new head?"

## 3. Building the Solution

```text
dummy = ListNode(-1)
current = dummy

While both lists have nodes:
    If list1.val <= list2.val:
        current.next = list1; list1 = list1.next
    Else:
        current.next = list2; list2 = list2.next
    current = current.next

current.next = whichever list still has nodes

return dummy.next
```

**Edge cases**: One or both lists empty → handled by the final assignment.

## 4. Complexity Analysis

**Time**: O(n + m) — each node processed once.
**Space**: O(1) — we reuse existing nodes, only create one dummy node.
