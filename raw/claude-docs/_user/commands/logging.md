# Logging Standard — structlog everywhere

## Setup

Always use `utils.logging` (structlog). Never use stdlib `logging` or `print()` in `src/`.
Assumes `src/utils/logging.py` exists in the project — check before using this pattern in a new project.

## Module pattern

```python
from utils.logging import get_logger

log = get_logger(__name__)  # one per file, module-level
```

## Entry point setup

Call once at startup — `main()`, app init, or notebook cell 1:

```python
from utils.logging import configure_logging

configure_logging()                    # dev: colored console
configure_logging(render_json=True)    # prod/CI: JSON lines
```

## Event naming

Dot-separated `module.action` — never free-form strings:

```python
log.info("sync.playlists", n=len(playlists))
log.info("train.gmm.fit", n_components=8, silhouette=sil)
log.info("train.classifier.skip", playlist=name, n_pos=n_pos, min_required=MIN_POSITIVES)
log.info("train.classifier.done", playlist=name, f1=f1, roc_auc=roc_auc)
log.error("etl.fetch.failed", error=str(exc), playlist_id=pid)
```

## Rules

- Bind counts and identifiers as structured fields — not f-string interpolation
- `debug` for per-item loops; `info` for phase transitions; `error` for caught exceptions
- Use `structlog.contextvars.bind_contextvars(run_id=...)` for request/session scope
- Notebooks: `setup_logging()` in the first code cell before any imports that log
- `train.py` and all ETL scripts use structlog — no `print()` exceptions
