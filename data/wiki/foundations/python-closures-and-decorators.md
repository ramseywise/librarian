---
title: Python Closures and Decorators
tags: [foundations, pattern]
summary: "Functions are values: closures capture variables (not values) from their defining scope, a decorator is a function that wraps a function (always with `functools.wraps`), and a decorator with arguments adds one more level — the shape behind timing, retry and caching wrappers."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--python--03-language-for-engineers--notes--03-functions-deeper.md
---

# Python Closures and Decorators

Functions are values: you can pass them, return them and store them. Closures let a function
remember variables from where it was made. Decorators are just functions that wrap functions.
(Sources: Jake VanderPlas, *A Whirlwind Tour of Python*; `functools` docs.)

## Flexible signatures

```python
def call(model, /, *messages, temperature=1.0, **extra):
    ...
call("m", "hi", "there", temperature=0.2, top_k=5)
# model="m", messages=("hi", "there"), temperature=0.2, extra={"top_k": 5}
```

- Parameters before `/` are **positional-only**. Parameters after `*` or `*args` are **keyword-only** — a good default for flags like `temperature`, so call sites stay readable and argument order can change safely.
- `f(*xs, **kw)` spreads a sequence and a dict into a call. Wrappers use `*args, **kwargs` to forward any signature unchanged.

## Closures

```python
def counter():
    count = 0
    def inc():
        nonlocal count      # rebinding an outer variable needs nonlocal
        count += 1
        return count
    return inc

c = counter(); c(); c()     # 2
```

**Late-binding trap**: closures capture **variables, not values**.
`[lambda: i for i in range(3)]` — every lambda returns 2, because they all read the same `i`
after the loop has finished. Bind early with a default argument: `lambda i=i: i`.

## Decorators

```python
import functools, time

def timed(fn):
    @functools.wraps(fn)            # keep fn's name and docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} took {time.perf_counter() - start:.3f}s")
    return wrapper

@timed                              # same as: load = timed(load)
def load(path): ...
```

- `@timed` is pure sugar for rebinding the name to the wrapped function.
- Without `functools.wraps`, the wrapped function reports the wrapper's name and loses its docstring.
- `try/finally` makes the timing report run even when `fn` raises (see [[Python Exceptions and Context Managers]]).

### Decorator factories (decorators with arguments)

A decorator with arguments is a function that **returns** a decorator, so there is one more level:

```python
def retry(times: int):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except ConnectionError:
                    if attempt == times - 1:
                        raise
        return wrapper
    return decorate

@retry(times=3)
def fetch(url): ...
```

Note the retry only catches a transient error class and re-raises on the last attempt. The async
version with exponential backoff and jitter is in [[Python Concurrency Models]].

## functools you'll actually use

- `@functools.cache` / `@lru_cache(maxsize=…)`: memoise a pure function. Arguments must be hashable ([[Python Data Model and Idioms]]).
- `functools.partial(fn, x=1)`: pre-fill arguments; handy for callbacks.
- `functools.reduce`: usually a loop, `sum` or `max` reads better.
- `operator.itemgetter("score")` / `attrgetter("name")`: faster, clearer `key=` functions than lambdas.

## See Also
- [[Python Data Model and Idioms]] — prerequisite-for (functions are objects; `__call__`)
- [[Python Concurrency Models]] — extends (async retry with backoff builds on the retry decorator)
- [[Agent Retry Taxonomy]] — related (which failures deserve a retry wrapper at all)
- [[Programming Curriculum]] — related (course map)
