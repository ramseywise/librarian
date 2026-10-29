---
imported_hash: 74de49c5f1b884dc
title: Pillar 0 — Programming Foundations (DSA, Python, SQL)
summary: 'The bedrock under everything else: write clean, efficient code, solve algorithmic problems under pressure, and translate data questions into working queries.'
order: 2
kind: reading
section: Programming
source: sisyphus/interviewing/guides/0-programming/00-overview.md
---

# Pillar 0 — Programming Foundations (DSA, Python, SQL)

The bedrock under everything else: write clean, efficient code, solve algorithmic problems
under pressure, and translate data questions into working queries. This pillar doesn't
sequence from another — it runs in parallel with or before Pillar 1. Most interview loops
include a coding screen at some stage.

## Learning path

1. **Python fluency by topic** — `drills/python/hackerrank/` works through the
   language systematically: Introduction → Basic Data Types → Strings → Collections →
   Itertools → Functional patterns → Classes → Regex → Error handling. Work in order;
   each topic builds vocabulary for the next.

2. **SQL by topic** — `drills/sql/hackerrank/` covers: Basic Select → Basic Join →
   Aggregation → Advanced Select → Advanced Join. Work all five before moving to window
   functions in the interview guide.

3. **DSA patterns** — `drills/python/leetcode/` is organized by pattern, not difficulty.
   Work in pattern order: Arrays & Hashing → Two Pointers → Sliding Windows → Linked
   Lists. Each pattern teaches a reusable move, not a one-off trick.

4. **Practice mode** — `drills/python/leetcode/NeetCodeExercsises.ipynb` has mixed
   problems. Treat it as timed self-testing after you've worked the patterns.

5. **Reference depth** — *Competitive Programmer's Handbook* (`drills/python/leetcode/`)
   covers trees, graphs, DP, and advanced combinatorics. Read chapter-by-chapter after
   the LeetCode patterns; use it as a reference, not a linear read.

## Resource map

| Resource | Type | Where | What it teaches |
|---|---|---|---|
| HackerRank Python track | code | `drills/python/hackerrank/` | Language idioms by topic: data types, strings, collections, itertools, OOP, regex |
| HackerRank SQL track | code | `drills/sql/hackerrank/` | SQL basics through advanced joins and aggregation |
| LeetCode by pattern | code | `drills/python/leetcode/` | Arrays/hashing, two pointers, sliding windows, linked lists |
| NeetCode exercises | notebook | `drills/python/leetcode/NeetCodeExercsises.ipynb` | Mixed-pattern timed practice |
| Probability Problems | notebook | `drills/python/leetcode/Probability-Problems.ipynb` | Probability math under interview pressure |
| LeetCode cheat sheet | reference | `drills/python/leetcode/LeetCodeCheat/` | Pattern templates and edge-case reminders |
| Competitive Programmer's Handbook | pdf | `drills/python/leetcode/` | Trees, graphs, DP, advanced algorithms — deep reference |

## Progression note

HackerRank → LeetCode is a deliberate ramp: HackerRank trains language fluency topic by
topic (you're not fighting Python syntax when solving an algorithm problem); LeetCode trains
algorithmic pattern recognition. Conflating the two stalls progress on both. Do HackerRank
first, then LeetCode patterns, then timed mixed practice.

## Test yourself

[interview-guide.md](interview-guide.md) — DSA checklist, Python patterns, SQL patterns,
and a question bank with answer sketches. Read it after working through the learning path
above, not before.
