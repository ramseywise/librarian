---
title: Python Packaging and Tooling
tags: [foundations, reference]
summary: "A modern Python project is a `pyproject.toml`, a `src/` layout and `tests/`, run with uv (envs, deps, lockfile), ruff (lint + format) and pytest (plain asserts, parametrize, fixtures) — and most import bugs come from `sys.path` and stdlib-shadowing filenames, fixed by installing the project rather than editing paths."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--python--03-language-for-engineers--notes--06-modules-packaging-tooling.md
---

# Python Packaging and Tooling

A modern Python project is a `pyproject.toml`, a `src/` folder, `tests/`, and three tools:
**uv** for environments and dependencies, **ruff** for lint and format, **pytest** for tests.
(Sources: *A Whirlwind Tour of Python* ch. 13; uv, Ruff and pytest docs.)

## Modules and imports

- A **module** is a `.py` file; a **package** is a folder of modules (with `__init__.py`).
- `import pkg.mod` runs the module **once** and caches it in `sys.modules`; later imports reuse it.
- `if __name__ == "__main__":` guards code that should run only when the file is executed, not imported.
- Avoid `from x import *`.
- **Shadowing trap**: naming your file after a stdlib module (`json.py`, `random.py`) shadows the real one.
- Python finds modules via `sys.path`, which starts with the script's directory — the source of "works when I run it from here" bugs. Install the project (`uv sync`) instead of editing `sys.path`.

## Project layout

```text
my-tool/
├── pyproject.toml
├── src/my_tool/
│   ├── __init__.py
│   └── core.py
└── tests/
    └── test_core.py
```

```toml
[project]
name = "my-tool"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["httpx>=0.27"]

[project.scripts]
my-tool = "my_tool.core:main"

[dependency-groups]
dev = ["pytest", "ruff", "mypy"]

[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

## uv

| Command | Does |
|---|---|
| `uv init my-tool --package` | Scaffold the layout above |
| `uv add httpx` / `uv add --dev pytest` | Add a (dev) dependency, update `uv.lock` |
| `uv run pytest` | Run inside the project env, creating it if needed |
| `uv run python -m my_tool.core` | Run a module |
| `uvx ruff check .` | Run a tool without installing it into the project |
| `uv python install 3.13` | Manage Python versions |

**Commit `uv.lock`.** It pins every transitive version, so CI and teammates get the same environment.

## ruff and pytest

- `ruff check --fix .` lints (replaces flake8, isort, pyupgrade…); `ruff format .` formats (replaces black).
- `pytest -q`; `pytest -k parse -x` runs tests matching "parse" and stops at the first failure.

```python
@pytest.mark.parametrize("raw, expected", [("$1.50", 1.5), ("2", 2.0)])
def test_parse_price(raw, expected):
    assert parse_price(raw) == expected

def test_parse_price_rejects_garbage():
    with pytest.raises(ValueError, match="price"):
        parse_price("abc")

def test_writes_file(tmp_path):            # fixtures are injected by parameter name
    out = tmp_path / "out.csv"
```

- Plain `assert` is enough: pytest rewrites it to show both sides on failure.
- The built-in fixtures used most: `tmp_path`, `monkeypatch`, `capsys`.
- `pytest.raises(..., match=...)` checks the error message as well as the type — pairs with the custom exception hierarchy in [[Python Exceptions and Context Managers]].

## See Also
- [[Python Foundations Reference]] — prerequisite-for
- [[Python Type Hints and Dataclasses]] — related (mypy/pyright run as a dev-group tool)
- [[Python Exceptions and Context Managers]] — related (testing error paths with `pytest.raises`)
- [[Programming Curriculum]] — related (course map)
