# Plan: Phase 3b — Training Pipeline
Date: 2026-04-04
Predecessor: Phase 3a (feature engineering)
Next: Phase 3c (agent + Chainlit)

---

## Goal

Wire `recommend/preprocessing.py` into the training and inference pipelines. Create `src/paths.py`. Retrain all models (GMM, scaler, per-playlist classifiers) on the enriched feature matrix from DuckDB. Validate the full recommend loop end-to-end.

---

## Pre-requisites

- Phase 3a complete: `preprocessing.build_feature_matrix(conn)` returns clean DataFrame
- `track_embeddings` table populated
- All new feature columns present and non-NULL

---

## Steps

### Step 1a: `src/paths.py` — path anchor

**Files created**: `src/paths.py`

```python
from __future__ import annotations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = REPO_ROOT / "models"
DATA_DIR = REPO_ROOT / "data"
DB_PATH = DATA_DIR / "listen_wiseer.db"
```

Update `src/mcp_server/server.py` and `src/recommend/engine.py` to import from `paths` instead of computing paths inline.

**Test**: `uv run pytest tests/unit/ -k paths -v`
**Done when**: No hardcoded paths remain in `server.py` or `engine.py`; existing tests still pass.

---

### Step 1: `src/paths.py` + complete training run

**Files**: `src/paths.py` (new), `src/mcp_server/server.py` (lines 22–23), `src/recommend/engine.py` (init, lines ~30–40)

**What**: Add the `src/paths.py` path anchor required by workspace CLAUDE.md convention. Update `server.py` and `engine.py` to import from it instead of computing paths inline. Then run `make train` to completion.

**Snippet**:
```python
# src/paths.py
from __future__ import annotations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # src/ → project root
MODELS_DIR = REPO_ROOT / "models"
DATA_DIR = REPO_ROOT / "data"
```

```python
# server.py — replace lines 22–23:
# Before:
_MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
# After:
from paths import MODELS_DIR as _MODELS_DIR, DATA_DIR as _DATA_DIR
```

```python
# engine.py __init__ — replace hardcoded Path("models") usage:
# Before (wherever Path("models") appears):
models_dir=Path("models")
# After (callers pass MODELS_DIR from paths):
# engine.py itself doesn't hardcode — callers (server.py, train.py) import from paths
```

**Train run**:
```bash
PYTHONPATH=src uv run python -m recommend.train
ls -lh models/   # expect gmm_corpus.pkl, scaler_corpus.pkl, ~14-32 classifier_*.pkl
```

**Smoke test** (from original PLAN.md Step 11):
```bash
PYTHONPATH=src uv run python -c "
from recommend.engine import RecommendationEngine
from recommend.schemas import RecommendRequest
from paths import MODELS_DIR, DATA_DIR

engine = RecommendationEngine(models_dir=MODELS_DIR, data_dir=DATA_DIR)
for req in [
    RecommendRequest(request_type='track', seed_id='4bJ7tMJqfYmkKgCYzaaG4B', k=5),
    RecommendRequest(request_type='genre', seed_id='zouk', k=5),
    RecommendRequest(request_type='track', seed_id='NONEXISTENT', k=5),
]:
    r = engine.recommend(req)
    print(f'{req.request_type}({req.seed_id}): {len(r.track_uris)} — {r.explanation[:60]}')
"
```

**Test**: `uv run pytest tests/unit/ --tb=short -q`

**Done when**: 190 tests pass; `models/` contains at least `gmm_corpus.pkl`, `scaler_corpus.pkl`, and ≥1 classifier pkl; smoke test prints 3 lines without exception.

---
