---
imported_hash: 43c8fcb3c8ecd5c0
title: Parenthesis Checker — First-Principles Thinking Guide
summary: Opening brackets push onto a stack. Closing brackets must match the most recent opening bracket (stack top).
order: 36
kind: reading
section: Dsa / Arrays and strings / Parenthesis checker
source: sisyphus/drills/coding/dsa/arrays_and_strings/parenthesis_checker/THINKING.md
---

# Parenthesis Checker — First-Principles Thinking Guide

## 1. Understanding the Problem

**Restate**: Check if brackets `{}`, `()`, `[]` are properly matched and nested.

## 2. Key Insight (Stack)

Opening brackets push onto a stack. Closing brackets must match the most recent opening bracket (stack top). If they don't match, or the stack is empty when we need to pop, it's unbalanced.

## 3. Building the Solution

```text
stack = []
matching = {')': '(', '}': '{', ']': '['}

For each char:
    If opening bracket: push
    If closing bracket:
        If stack empty or top doesn't match: return False
        Pop from stack

Return stack is empty
```

## 4. Complexity

**Time**: O(n).
**Space**: O(n) — worst case all opening brackets.
