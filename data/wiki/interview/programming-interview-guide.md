---
title: Programming Interview Study Guide
tags: [interview, reference]
summary: Exam-prep reference for the coding screen — the DSA pattern checklist (hashing, two pointers, linked lists, trees, graphs, DP), the Python stdlib moves worth reaching for first, the SQL idioms that recur (window functions, dedup-latest, funnel/retention), and a question bank of answer sketches.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--0-programming--interview-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--0-programming--00-overview.md
  - data/raw/repos/sisyphus/interviewing--guides--0-programming--interview-guide.md
  - data/raw/repos/sisyphus/interviewing--guides--0-programming--00-overview.md
  - data/raw/repos/sisyphus/drills--README.md
  - data/raw/repos/sisyphus/drills--python--README.md
  - data/raw/repos/sisyphus/drills--sql--README.md
---

# Programming Interview Study Guide

Every loop has a coding screen. The bar is **pattern recognition plus clean implementation
under time pressure**, not memorised solutions: know the move, then apply it to the variant.

## Learning order: fluency before patterns

The pillar's one non-obvious claim is about sequencing. Language-fluency drills (topic by
topic: data types, strings, collections, itertools, OOP, regex) come **before** algorithmic
pattern practice, then timed mixed practice last. Conflating the two stalls both — if you are
fighting syntax you are not learning the pattern. Practice is organised **by pattern, not by
difficulty**, because each pattern teaches a reusable move rather than a one-off trick.

## DSA checklist

| Pattern | The move | Reach for it when |
|---|---|---|
| Arrays & hashing | hash map for "seen before?"; prefix sums for O(1) range sums; sort first to turn O(n²) into O(n log n) + two pointers | duplicates, frequency, pair sums |
| Two pointers | fast/slow (cycle, middle, Nth-from-end); left/right (palindrome, sorted two-sum, container); variable window | sorted structure, or a linear scan tracking two positions |
| Linked lists | save `next` before overwriting; dummy head; three-pointer reverse; Floyd's cycle (reset one pointer to head to find the start) | any pointer surgery |
| Trees | pre/in/post-order templates (inorder = sorted for a BST); BFS with a deque for levels; validate BST by passing min/max bounds down | hierarchy, level order |
| Graphs | BFS for unweighted shortest path; DFS for cycles/flood fill; topological sort (Kahn's in-degree or DFS post-order); union-find with path compression + union by rank | dependencies, components |
| Dynamic programming | optimal substructure + overlapping subproblems; write the recursion, then memoise (top-down) or tabulate (bottom-up); collapse 2D tables to one or two rows | knapsack, LCS/LIS, coin change, grid paths |

Edge cases to say out loud: empty input, single element, all duplicates, negatives.

## Python stdlib — reach for these first

`collections` (`defaultdict`, `Counter`, `deque`), `itertools` (`combinations`, `product`,
`groupby`, `accumulate`), `heapq` (`nlargest`, `nsmallest`), `bisect`. A `deque` is the
correct queue — `list.pop(0)` is O(n). `Counter.most_common(k)` and
`heapq.nlargest(k, freq, key=freq.get)` give top-K in O(n log k); bucket sort by frequency
gets O(n).

## SQL idioms that recur

- **Predict the join's row count before running it.** A LEFT JOIN returns the left table's
  count only if the key is unique on the right; duplicates on the right fan it out.
- `WHERE` filters rows before grouping; `HAVING` filters groups after.
- **Window functions** are the staple: `ROW_NUMBER` (no ties) vs `RANK` (ties, then skip) vs
  `DENSE_RANK` (ties, no skip); running totals and moving averages with frame clauses;
  `LAG`/`LEAD` instead of a self-join.
- **Dedup-latest-row idiom:** `ROW_NUMBER() OVER (PARTITION BY key ORDER BY ts DESC) = 1` in a CTE.
- Recursive CTEs for hierarchies; know one funnel, one retention, one cohort query cold.
- "Second highest" questions are really tie-handling questions — answer with `DENSE_RANK`.

## Question bank (answer sketches)

- **Two sum** — one pass, store complements in a hash map; the sorted variant uses two pointers for O(1) space.
- **Longest substring without repeats** — sliding window with a set; shrink left on duplicate.
- **Level-order traversal** — snapshot the queue length at the start of each level.
- **Coin change** — `dp[i] = min(dp[i], dp[i - coin] + 1)`, base `dp[0] = 0`.
- **Find the duplicate** — treat values as next-pointers and run Floyd's.
- **Merge intervals** — sort by start, extend or append.
- **Users active in Jan and Feb but not March** — `GROUP BY` with a `HAVING` that counts distinct months and sums a March indicator to zero.

## See Also
- [[ML Foundations Interview Study Guide]] — extends (the SQL/analytics screen continues there)
- [[AI Role Interview Loop Map]] — prerequisite-for (which loops weight the coding screen)
- [[AIE Code-Test Flaw Taxonomy]] — alternative-to (the LLM take-home variant of the coding round)
- [[Graded Rehearsal Drill Harness]] — related (the drill harness for coding questions)
- [[Coding Challenge Interview Study Guide]] — extends (round format, stdlib practicals, trap-shaped prompts)
- [[Drill Gym Tracks and Schema]] — related (where the reps live and how a drill file is shaped)
- [[Programming Curriculum]] — prerequisite-for (the course that teaches what the screen tests)
