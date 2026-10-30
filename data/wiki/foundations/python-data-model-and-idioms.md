---
title: Python Data Model and Idioms
tags: [foundations, concept]
summary: "Names are labels on objects, not boxes — which explains aliasing, the mutable-default trap and pass-by-assignment; dunder methods map syntax onto your classes; hashability rules decide what can be a key; and a short list of idioms (unpacking, EAFP, dict merge) should be reflexive."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--python--03-language-for-engineers--notes--01-data-model-and-idioms.md
---

# Python Data Model and Idioms

Everything in Python is an object with an identity, a type and a value. Names are labels stuck
on objects, not boxes holding values. Most "weird" Python behaviour follows from that one fact.
(Sources: Jake VanderPlas, *A Whirlwind Tour of Python*; the Python data model docs.)

## Names, identity and mutability

```python
a = [1, 2, 3]
b = a            # a second label on the SAME list
b.append(4)
a                # [1, 2, 3, 4]
a is b           # True: same object
```

- `==` compares values (calls `__eq__`); `is` compares identity. Use `is` only for `None`, `True`, `False` and sentinels.
- **Mutable**: `list`, `dict`, `set`, most objects. **Immutable**: `int`, `float`, `str`, `tuple`, `frozenset`, `bytes`.
- Arguments are **passed by assignment**: the function receives another label on the caller's object. Mutating it is visible to the caller; rebinding the parameter is not.

### The mutable default trap

```python
def add(item, bucket=[]):      # the [] is created ONCE, at def time
    bucket.append(item)
    return bucket

add(1); add(2)                 # [1, 2] — shared between calls

def add(item, bucket=None):    # the fix
    bucket = [] if bucket is None else bucket
```

The same trap reappears in dataclasses, where the fix is `field(default_factory=list)` — see
[[Python Type Hints and Dataclasses]].

## Dunder methods: syntax maps to methods

| You write | Python calls |
|---|---|
| `len(x)` | `x.__len__()` |
| `x[k]`, `x[k] = v` | `__getitem__`, `__setitem__` |
| `for i in x` | `iter(x)` → `__iter__`, then `__next__` |
| `a + b`, `a == b`, `a < b` | `__add__`, `__eq__`, `__lt__` |
| `if x:` | `__bool__`, else `__len__` |
| `with x:` | `__enter__`, `__exit__` |
| `x(...)` | `__call__` |
| `repr(x)`, `f"{x}"` | `__repr__`, `__str__` / `__format__` |

Implement `__len__` and `__getitem__` and the class already works with `len`, indexing, slicing
(if you handle `slice`), `in` and `for`. That is the point of the data model: objects plug into
the language instead of inventing their own method names. The iteration row is expanded in
[[Python Generators and Lazy Iteration]]; the `with` row in [[Python Exceptions and Context Managers]].

## Idioms worth having by reflex

```python
first, *rest = [1, 2, 3, 4]            # star unpacking
a, b = b, a                            # swap
for i, name in enumerate(names, 1):    # index without range(len(...))
for x, y in zip(xs, ys, strict=True):  # strict: lengths must match
best = max(rows, key=lambda r: r["score"])
if not items:                          # empty check
value = config.get("port") or 8080     # careful: 0 and "" are falsy too
merged = {**defaults, **overrides}     # or defaults | overrides
```

- **EAFP** ("easier to ask forgiveness than permission"): try the operation and catch the specific exception rather than checking first. It avoids race conditions on files and dict lookups.
- The `or` default idiom silently replaces legitimate falsy values (`0`, `""`) — a trap when `0` is a valid port or count.
- `copy.copy` is shallow (new outer container, same inner objects); `copy.deepcopy` copies all the way down. `list(x)`, `x[:]` and `dict(x)` are shallow.

## Hashability

Dict keys and set members must be **hashable**: their hash must never change.

- Immutable built-ins are hashable; lists and dicts aren't.
- A tuple is hashable only if everything inside it is.
- **If you define `__eq__` on a class, define `__hash__` too** (or use a frozen dataclass), or instances stop working as keys.

## See Also
- [[Python Foundations Reference]] — prerequisite-for
- [[Python Generators and Lazy Iteration]] — extends (the iteration protocol in depth)
- [[Python Type Hints and Dataclasses]] — extends (frozen dataclasses solve the hash/eq pairing)
- [[Python Closures and Decorators]] — related (functions as first-class objects)
- [[Programming Curriculum]] — related (course map)
