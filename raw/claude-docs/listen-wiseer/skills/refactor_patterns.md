---
name: refactor_patterns
description: "Catalog of concrete Python refactoring moves keyed to each smell. Actionable recipes with decision criteria. Used by the refactor agent during Phase 2."
---

Use this skill during Phase 2 (identify improvements) of `code_refactor`. For each smell found, locate the matching pattern below and use it to form a concrete, actionable proposal.

## Extract Function

**Smell**: Function >40 lines, or a block of code with a comment explaining what it does.

**Move**: Pull the block into its own function. Name it after what it does, not how.

```python
# Before
def process_order(order):
    # validate
    if not order.items:
        raise ValueError("empty order")
    if order.total < 0:
        raise ValueError("negative total")
    # ... 30 more lines

# After
def _validate_order(order):
    if not order.items:
        raise ValueError("empty order")
    if order.total < 0:
        raise ValueError("negative total")

def process_order(order):
    _validate_order(order)
    # ... remaining logic
```

**Decision criteria**: Extract when the block has a single clear purpose AND the parent function becomes meaningfully shorter. Do not extract one-liners or blocks that share local state extensively with the parent.

---

## Flatten Nesting with Early Return

**Smell**: Nesting >3 levels deep, often from guard conditions wrapped in `if`.

**Move**: Invert the condition and return early. The happy path stays at the left margin.

```python
# Before
def process(item):
    if item is not None:
        if item.is_active:
            if item.value > 0:
                return item.value * 2

# After
def process(item):
    if item is None:
        return None
    if not item.is_active:
        return None
    if item.value <= 0:
        return None
    return item.value * 2
```

**Decision criteria**: Apply when nesting is caused by guard conditions (not branching logic). Do not flatten complex if/elif trees — that changes readability without reducing complexity.

---

## Replace Magic Value with Named Constant

**Smell**: Literal number or string that appears multiple times, or whose meaning is not obvious from context.

**Move**: Name it at module level.

```python
# Before
if len(results) > 100:
    ...
page_size = 100

# After
MAX_RESULTS = 100

if len(results) > MAX_RESULTS:
    ...
page_size = MAX_RESULTS
```

**Decision criteria**: Apply when the value appears 2+ times OR when its meaning is non-obvious. Do not extract values that are semantically different even if numerically equal (e.g., two different timeouts that happen to both be 30).

---

## Consolidate Duplicate Logic

**Smell**: The same operation (with minor variations) appears 3+ times across the codebase.

**Move**: Extract a shared function that accepts the varying parts as parameters.

```python
# Before (3 callers doing the same thing slightly differently)
rows = [{"id": r[0], "name": r[1]} for r in cursor.fetchall()]
rows = [{"id": r[0], "email": r[1]} for r in cursor.fetchall()]
rows = [{"id": r[0], "value": r[1]} for r in cursor.fetchall()]

# After
def rows_to_dicts(cursor, keys: list[str]) -> list[dict]:
    return [dict(zip(["id", *keys], r)) for r in cursor.fetchall()]
```

**Decision criteria**: The 3-strike rule — two occurrences is coincidence, three is a pattern. Verify the variation is parameterizable before extracting. Do not force-consolidate if the callers are likely to diverge.

---

## Replace Conditional with Dispatch Dict

**Smell**: Long if/elif chain selecting behavior by a string/enum key.

**Move**: Map keys to callables.

```python
# Before
def handle(action: str, payload):
    if action == "create":
        return create(payload)
    elif action == "update":
        return update(payload)
    elif action == "delete":
        return delete(payload)
    else:
        raise ValueError(f"unknown action: {action}")

# After
_HANDLERS = {
    "create": create,
    "update": update,
    "delete": delete,
}

def handle(action: str, payload):
    handler = _HANDLERS.get(action)
    if handler is None:
        raise ValueError(f"unknown action: {action}")
    return handler(payload)
```

**Decision criteria**: Apply when each branch calls a single function with the same signature. Do not apply when branches have meaningfully different logic inline (extract functions first, then dispatch).

---

## Introduce Parameter Object

**Smell**: Function with 5+ parameters, especially when several are always passed together.

**Move**: Bundle related parameters into a Pydantic model or dataclass.

```python
# Before
def run_query(host, port, database, user, password, timeout, retries):
    ...

# After
class DBConfig(BaseModel):
    host: str
    port: int
    database: str
    user: str
    password: str
    timeout: int = 30
    retries: int = 3

def run_query(config: DBConfig):
    ...
```

**Decision criteria**: Apply when 4+ parameters are logically related AND the group appears together in multiple callers. Use Pydantic if the object crosses a boundary (config, API); dataclass for internal grouping.

---

## Remove Dead Code

**Smell**: Unreachable branches, unused imports, commented-out blocks, functions with no callers.

**Move**: Delete it. Version control is the backup.

**How to verify no callers:**
```bash
grep -rn "function_name" src/ tests/
```

**Decision criteria**: Delete if grep shows zero callers AND the function is not exported as part of a public API. For commented-out code: delete unless the comment explains *why* it was removed (i.e., it's documentation, not code).

---

## Rename for Clarity

**Smell**: Variable or function name that doesn't describe what it holds or does. Common patterns: single letters outside loops, `data`, `result`, `tmp`, `helper`, abbreviations that aren't obvious.

**Move**: Rename to describe the thing. Functions: verb phrase. Variables: noun phrase.

**Decision criteria**: Rename when the name requires reading the body to understand. Do not rename well-understood abbreviations (`df`, `i`, `n`, `exc`) or names that are conventional in the domain.

---

## Rules

- Each move must trace back to a specific smell in the code — do not apply patterns speculatively
- Propose the move with `file:line` before applying it (handled by `refactor_propose`)
- One move at a time — apply, test, then move to the next
- If a pattern requires touching more than the agreed scope, declare it before proceeding
