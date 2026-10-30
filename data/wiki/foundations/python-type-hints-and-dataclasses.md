---
title: Python Type Hints and Dataclasses
tags: [foundations, concept]
summary: "Type hints are checked by tools, not Python: type every signature (loose in, specific out, `X | None` to force None handling, `object` over `Any`), use Protocols for checker-understood duck typing, frozen dataclasses for trusted internal data, and Pydantic to validate untrusted data at every boundary."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--python--03-language-for-engineers--notes--05-types-and-dataclasses.md
---

# Python Type Hints and Dataclasses

Type hints are checked by tools (mypy, pyright), not by Python at runtime. Add them to every
function signature and let the checker find bugs before users do. Dataclasses remove the
boilerplate from classes that are mostly data; Pydantic validates data that comes from outside.
(Sources: Python `typing` and `dataclasses` docs; Pydantic docs.)

## Hints you'll write daily

```python
from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import Literal, TypedDict

def top(scores: Mapping[str, float], n: int = 3) -> list[tuple[str, float]]: ...
def find(name: str) -> User | None: ...                  # callers must check for None
def apply(fn: Callable[[str], int], xs: Iterable[str]) -> Iterator[int]: ...
Role = Literal["user", "assistant"]
class Message(TypedDict):
    role: Role
    content: str

def first[T](xs: list[T]) -> T: ...                        # generic (3.12 syntax)
```

- **Accept the loosest type that works** (`Iterable`, `Mapping`) and **return the most specific** (`list`, `dict`).
- `X | None` forces the checker to make callers handle `None` — most of the value of typing.
- `Any` turns checking off. Prefer `object` and narrow with `isinstance` (the same move as `unknown` in [[TypeScript any Escapes]]).
- Run a checker (`uv run mypy src/` or `pyright`); hints alone enforce nothing.

## Protocols: structural typing

```python
from typing import Protocol

class SupportsClose(Protocol):
    def close(self) -> None: ...

def shutdown(things: list[SupportsClose]) -> None:
    for t in things:
        t.close()
```

Any class with a matching `close()` fits, with no inheritance — duck typing the checker
understands. Useful for depending on a capability rather than a concrete class.

## Dataclasses

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class Chunk:
    doc_id: str
    text: str
    score: float = 0.0
    tags: tuple[str, ...] = ()
    meta: dict[str, str] = field(default_factory=dict, compare=False)

    def __post_init__(self):
        if not self.text:
            raise ValueError("empty chunk")
```

- Generated `__init__`, `__repr__`, `__eq__`; `order=True` adds comparisons in field order.
- `frozen=True` makes instances immutable **and hashable**, so they work as dict keys and set members — the clean answer to the `__eq__`/`__hash__` pairing rule in [[Python Data Model and Idioms]].
- Mutable defaults need `field(default_factory=…)` — the mutable-default trap again.
- `dataclasses.replace(c, score=0.9)` makes a modified copy of a frozen instance; `asdict(c)` converts to a dict.
- `__post_init__` can enforce simple invariants, but a dataclass otherwise **trusts its inputs**: no type coercion or validation.

## Pydantic: validate at the boundary

A dataclass trusts its inputs. Pydantic validates and converts them at runtime, which is what a
boundary needs: JSON from an API, config, LLM output.

```python
from pydantic import BaseModel, Field

class Review(BaseModel):
    rating: int = Field(ge=1, le=5)
    summary: str

Review.model_validate_json('{"rating": "4", "summary": "ok"}')   # rating coerced to 4
Review.model_validate({"rating": 9, "summary": "x"})              # ValidationError
```

**The rule: dataclasses inside the program, a validator at every edge** — validate once on
entry, then trust the data afterwards. It is the same rule as Zod in TypeScript
([[Runtime Validation with Zod]]). For LLM output specifically, a schema guarantees shape, not
truth ([[Structured Output]]). Note that Pydantic's default coercion (`"4"` → `4`) is lenient.

## See Also
- [[Python Data Model and Idioms]] — prerequisite-for (hashability and the mutable-default trap)
- [[Runtime Validation with Zod]] — alternative-to (the TypeScript boundary validator)
- [[TypeScript any Escapes]] — related (`unknown` + narrowing mirrors `object` + `isinstance`)
- [[Structured Output]] — related (validating LLM output with a schema)
- [[Settings Field Names Are a Shared Env Namespace]] — related (a pydantic-settings pitfall at the config boundary)
- [[Programming Curriculum]] — related (course map)
