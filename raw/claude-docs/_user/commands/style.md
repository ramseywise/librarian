# Style Rules

## Python

- `uv` only (`uv add`, `uv run`, `uv sync`) — never pip or poetry
- Pydantic v2 for all models and settings
- ruff for lint/format — run before committing
- pyright for type checking when configured per project
- `from __future__ import annotations` in all modules
- Type annotations on all function signatures
- f-strings over `.format()` or `%`

## Data

- **Polars not pandas** — lazy frames for large data, eager for small
- **DuckDB** for local analytics and joins — avoid loading full tables into memory
- Parquet for cached intermediate data; never CSV for processed outputs
- Column names: `snake_case`

## API / IO

- `httpx` not `requests`; async-first for I/O
- Always close connections (context managers or explicit `.close()`)
- Pydantic models at API boundaries, not raw dicts

## Don'ts

- No hardcoded paths, secrets, or hyperparameters — config files / env vars only
- No pandas, no stdlib `logging`, no `print()` in `src/`
- No mutable default arguments
- No bare `except` clauses
- No notebooks committed with output cells
