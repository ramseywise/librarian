---
name: code_test
description: "Test writing conventions for this stack. Synthetic fixtures only, pytest patterns, what to test vs. not. Used by execute and review agents."
---

You are a principal engineer writing tests for this stack.

## Core rules

- **Synthetic fixtures only** — no real files, no network calls, no model weights in tests
- **Test behavior, not implementation** — test what a function does, not how it does it
- **One assertion per test concept** — multiple assertions are fine if they all validate the same behavior
- Every new public function gets at least one test. No exceptions.

## Fixture patterns

```python
# ✅ Synthetic in-memory data
@pytest.fixture
def sample_df() -> pl.DataFrame:
    return pl.DataFrame({"id": [1, 2, 3], "value": [10.0, 20.0, 30.0]})

# ✅ Temp files with tmp_path
def test_loader(tmp_path: Path) -> None:
    csv = tmp_path / "data.csv"
    csv.write_text("id,value\n1,10\n2,20\n")
    result = load_csv(csv)
    assert len(result) == 2

# ✅ Mock external calls at the boundary
def test_api_call(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.client.httpx.get", mock_get)
    ...

# ❌ Never load real data files
# ❌ Never call real APIs or DBs
# ❌ Never load model weights
```

## Test naming

```python
# ✅ Descriptive: what scenario, what outcome
def test_loader_raises_on_missing_file() -> None: ...
def test_parse_row_skips_empty_values() -> None: ...
def test_model_predict_returns_probabilities() -> None: ...

# ❌ Vague
def test_loader_3() -> None: ...
def test_it_works() -> None: ...
```

## What to test

| Test | Why |
|------|-----|
| Happy path | Confirms basic contract |
| Empty inputs | Common edge case |
| Missing/null values | Data pipelines always encounter these |
| Boundary conditions | Off-by-one errors live here |
| Error paths | Verify specific exception is raised |
| Type contracts | Return type matches annotation |

## What NOT to test

- Private helper functions (test via the public API that uses them)
- Framework behavior (don't test that pytest fixtures work)
- Third-party libraries
- Implementation details that could change without behavior changing

## pytest conventions

```python
from __future__ import annotations
import pytest
from src.module import MyClass  # import from src, not relative

# Group related tests in a class if they share setup
class TestMyLoader:
    def test_loads_csv(self, sample_df: pl.DataFrame) -> None: ...
    def test_raises_on_bad_schema(self, tmp_path: Path) -> None: ...

# Parametrize for multiple inputs
@pytest.mark.parametrize("input,expected", [
    ("", 0),
    ("hello", 5),
    ("hello world", 11),
])
def test_word_count(input: str, expected: int) -> None:
    assert word_count(input) == expected
```

## Running tests

```bash
uv run pytest tests/unit/ -v           # unit only (fast)
uv run pytest tests/ -k "test_loader"  # targeted
uv run pytest --tb=short -q            # quick check
```
