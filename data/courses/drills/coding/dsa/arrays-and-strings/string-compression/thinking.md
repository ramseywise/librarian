---
imported_hash: 64e8d220b2ea6b50
title: String Compression — First-Principles Thinking Guide
summary: Use a read pointer to count consecutive characters and a write pointer to write the compressed form back into the same array.
order: 130
kind: reading
section: Dsa / Arrays and strings / String compression
source: sisyphus/drills/coding/dsa/arrays_and_strings/string_compression/THINKING.md
---

# String Compression — First-Principles Thinking Guide

## 1. Understanding the Problem

**Restate**: Compress a character array in-place. Consecutive duplicates become char + count (only if count > 1).

## 2. Key Insight (Two Pointer In-Place)

Use a read pointer to count consecutive characters and a write pointer to write the compressed form back into the same array.

## 3. Building the Solution

```text
write = 0, read = 0
While read < len(chars):
    char = chars[read], count = 0
    While read < len and chars[read] == char:
        read++, count++
    chars[write++] = char
    If count > 1:
        Write each digit of count
Return write (new length)
```

## 4. Complexity

**Time**: O(n) — single pass.
**Space**: O(1) — in-place modification.
