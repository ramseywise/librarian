---
title: Python Generators and Lazy Iteration
tags: [foundations, concept]
summary: "Iterators are single-use and generators run only on demand, so chained generator pipelines process arbitrarily large inputs in constant memory — but a second pass over an exhausted iterator silently yields nothing, and a generator's open `with` block lives until it is consumed."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--python--03-language-for-engineers--notes--02-generators-and-iteration.md
---

# Python Generators and Lazy Iteration

An iterator hands out values one at a time and remembers where it is. A generator is the easiest
way to write one. Laziness lets you process a 10 GB log file in constant memory — the basis of the
rule of thumb "iterate lazily over anything that might be large" ([[Python Foundations Reference]]).

## The iteration protocol

```python
it = iter([10, 20])   # calls __iter__
next(it)              # 10
next(it)              # 20
next(it)              # raises StopIteration — a for loop catches this for you
```

- An **iterable** can produce an iterator (`list`, `dict`, `str`, files).
- An **iterator** is **single-use**: once exhausted it stays empty. Looping twice over a generator or a `map` object **silently yields nothing** the second time — no error, just an empty result.

This is the `for` row of the dunder table in [[Python Data Model and Idioms]].

## Comprehensions

```python
squares = [x * x for x in range(10)]
evens   = [x for x in nums if x % 2 == 0]
lookup  = {u["id"]: u for u in users}
letters = {c.lower() for c in text if c.isalpha()}
total   = sum(x * x for x in range(10**6))   # generator expression: no list built
```

Read them left to right as the loop they replace. Stop at two `for` clauses; beyond that a plain
loop is clearer. Passing a generator expression straight into `sum`/`max`/`any` avoids
materialising a list.

## Generators

```python
def read_records(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                yield line.rstrip("\n").split(",")

def take(n, it):
    for i, x in enumerate(it):
        if i == n:
            return
        yield x
```

- A function containing `yield` returns a generator object. Its body runs only as values are requested, pausing at each `yield`.
- Chain stages into a pipeline: `parse(filter(read(path)))`. Each stage holds one item at a time.
- `yield from other` delegates to another iterable.
- **Resource lifetime trap**: a `with` block inside a generator stays open until the generator finishes or is garbage-collected. Consume it fully, or the file stays open longer than you expect. (Context managers: [[Python Exceptions and Context Managers]].)

## itertools: the parts you'll use

| Function | Does |
|---|---|
| `islice(it, n)` | First n items of any iterator |
| `chain(a, b)` / `chain.from_iterable(xs)` | Concatenate / flatten one level |
| `groupby(it, key)` | Groups **consecutive** equal keys — sort first, or you get split groups |
| `batched(it, n)` (3.12+) | Tuples of n |
| `pairwise(it)` | `(a, b), (b, c), …` |
| `accumulate(it)` | Running totals |
| `product`, `permutations`, `combinations` | Combinatorics |
| `count`, `cycle`, `repeat` | Infinite streams — pair with `islice` or `zip` |

`collections` adds `Counter`, `defaultdict`, `deque` (fast at both ends; `maxlen` gives a
sliding window) and `namedtuple`.

## See Also
- [[Python Data Model and Idioms]] — prerequisite-for (the iteration protocol is a dunder pair)
- [[Python Foundations Reference]] — prerequisite-for (loop patterns and files)
- [[Python Exceptions and Context Managers]] — related (generator-based `@contextmanager` and resource lifetime)
- [[Programming Interview Study Guide]] — related (`deque`, `Counter` and itertools on the coding screen)
- [[Programming Curriculum]] — related (course map)
