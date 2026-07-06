# Plan: Address Code Review Inconsistencies (AIF-32)

## Context

The code review of `AIF-32-generate-test-dataset` identified one correctness bug and several consistency gaps between the new `eval/dataset/` pipeline and the existing `src/agentic_rag/` codebase. This plan fixes the bug and closes the most meaningful inconsistencies without touching unrelated code.

All identified issues are addressed, ordered from blocking to non-blocking.

---

## Changes

### 1. Bug fix — new-article fingerprints not persisted in `_run_refresh`

**File:** `eval/dataset/runner.py` — `_run_refresh()`, line ~380

After generating items for `diff.new + diff.changed` articles, the code refreshes fingerprints only for `diff.changed`:
```python
for art_id in diff.changed:          # <-- diff.new is missing
    if art_id in envelope.article_manifest and art_id in current_fps:
        envelope.article_manifest[art_id].fingerprint = current_fps[art_id]
        envelope.article_manifest[art_id].last_seen_at = now
```

**Fix:** include `diff.new` in the same loop, so newly added articles have their fingerprint stored and aren't treated as "new" on every subsequent refresh:
```python
for art_id in diff.new + diff.changed:
    if art_id in envelope.article_manifest and art_id in current_fps:
        envelope.article_manifest[art_id].fingerprint = current_fps[art_id]
        envelope.article_manifest[art_id].last_seen_at = now
```

---

### 2. Deduplicate INTERCOM.md parsing logic

**Problem:** Both `src/agentic_rag/vector_store.py` (`_parse_intercom_chunks`) and `eval/dataset/article_parser.py` (`_parse_content`) independently implement the same section-splitting/header-extraction logic with identical code. Any format change to `INTERCOM.md` must be applied twice.

**Solution:** Extract the shared low-level parsing into a new utility function in `src/agentic_rag/` that returns structured `Article`-like data. Both callers then use it.

**New file:** `src/agentic_rag/intercom_parser.py`

```python
"""Shared low-level parser for INTERCOM.md knowledge base files."""

from dataclasses import dataclass

SECTION_SEPARATOR = "\n---\n"
ARTICLE_MARKER = "## Article:"

@dataclass
class ParsedArticle:
    id: str
    title: str
    body: str
    url: str = ""
    collection: str = "General"

def parse_intercom_content(content: str) -> list[ParsedArticle]:
    """Parse INTERCOM.md content into ParsedArticle objects.
    Shared by vector_store (for chunked embedding) and eval/dataset (for full-body generation).
    """
    # ... extracted logic from both current implementations ...
```

**Update `src/agentic_rag/vector_store.py`:** Replace the body of `_parse_intercom_chunks` to call `parse_intercom_content()` and format the result into the existing chunk dict structure it already returns. The public interface of `_parse_intercom_chunks` does not change.

**Update `eval/dataset/article_parser.py`:** Replace `_parse_content` to call `parse_intercom_content()` and map `ParsedArticle` → `Article` (one-liner field copy, `domain=""` as before). The public interface `parse_intercom_md()` does not change.

---

### 3. Add dataset generation constants to `config.py`

**File:** `src/agentic_rag/config.py`

Add two new optional env-var constants so that `DATASET_GENERATION_MODEL` and `DATASET_GENERATION_API_KEY` are discoverable alongside the other model/API-key settings:

```python
# Dataset generation (optional overrides — fall back to GEMINI_* values)
DATASET_GENERATION_MODEL: str = os.getenv("DATASET_GENERATION_MODEL") or GENERATION_MODEL
DATASET_GENERATION_API_KEY: str | None = os.getenv("DATASET_GENERATION_API_KEY") or GEMINI_API_KEY
```

**Update `eval/dataset/generators/intercom.py` and `out_of_scope.py`:** Replace the inline `_resolve_config()` / env-var lookups with an import of these config constants. This centralises the lookup without changing behavior.

---

### 4. Use Pydantic validation in `evaluate.py`

**File:** `eval/evaluate.py` — `load_test_set()`

Currently uses raw `json.load()` + manual dict access with a backward-compat fallback for the old flat format. The new code should validate using the Pydantic schema while preserving backward compat.

**Change:** Replace the `json.load()` block with `DatasetEnvelope.model_validate_json()` wrapped in a try/except that falls back to the existing flat-list path:

```python
from eval.dataset.schema import DatasetEnvelope

def load_test_set(max_samples: int = 50) -> tuple[list[dict], str]:
    raw_text = Path(config.TEST_SET_PATH).read_text(encoding="utf-8")
    try:
        envelope = DatasetEnvelope.model_validate_json(raw_text)
        dataset_version = envelope.langfuse_dataset_version
        items = [
            {
                "id": item.id,
                "instruction": item.instruction,
                "expected": item.expected_output.response,
                "category": item.metadata.category,
            }
            for item in envelope.items
        ]
    except Exception:
        # Backward compat: old flat JSON list format
        raw = json.loads(raw_text)
        dataset_version = raw.get("langfuse_dataset_version", "v1")
        raw_items = raw.get("items", raw)
        items = [...]  # existing flat-format extraction
    ...
```

---

### 5. Fix logging configuration placement

**Problem:** `eval/dataset/runner.py` calls `logging.basicConfig(level=logging.INFO, ...)` inside the `run()` function body. Calling `basicConfig` inside a library function is bad practice — it configures the root logger as a side effect of importing/calling library code, which can interfere with any other logger in the process.

**Fix:** Move the `logging.basicConfig(...)` call out of `runner.run()` and into the CLI entry point where it belongs:
- Remove it from `eval/dataset/runner.py:run()`
- Add it to `scripts/generate_dataset.py` just before `runner.run(config)` is called

No behavior change for CLI users. Callers that import `runner.run()` programmatically will no longer have their root logger silently reconfigured.

**Note:** The `src/agentic_rag/` codebase uses `print()` rather than the `logging` module. Standardizing `src/` is a larger refactor left to a future PR — `eval/` using the `logging` module is the better practice and should stay as-is.

---

### 6. Move `eval/` under `src/` to follow project layout convention

**Problem:** `src/agentic_rag/` follows the `src`-layout convention (package code lives under `src/`, not at the repo root). `eval/` sits at the repo root, making it inconsistent and exposing it to accidental import without installation.

**Fix:** Move the directory from `eval/` → `src/eval/` and update `pyproject.toml`.

With hatch's build system, `packages = ["src/eval"]` strips the `src/` prefix when building the wheel, so the installed package name stays `eval` and **all existing `from eval.dataset.*` imports remain unchanged** — no other files need updating.

**Change to `pyproject.toml`:**
```toml
# Before
packages = ["src/agentic_rag", "eval"]

# After
packages = ["src/agentic_rag", "src/eval"]
```

**File moves:**
- `eval/` → `src/eval/` (entire directory, no renames within)

---

## Files Modified

| File | Change |
|---|---|
| `eval/dataset/runner.py` | Bug fix: add `diff.new` to fingerprint-refresh loop |
| `src/agentic_rag/intercom_parser.py` | **New file:** shared `ParsedArticle` + `parse_intercom_content()` |
| `src/agentic_rag/vector_store.py` | Delegate to `parse_intercom_content()` inside `_parse_intercom_chunks` |
| `eval/dataset/article_parser.py` | Delegate to `parse_intercom_content()` inside `_parse_content` |
| `src/agentic_rag/config.py` | Add `DATASET_GENERATION_MODEL`, `DATASET_GENERATION_API_KEY` |
| `eval/dataset/generators/intercom.py` | Use `config.DATASET_GENERATION_*` instead of inline env-var lookup |
| `eval/dataset/generators/out_of_scope.py` | Same as above |
| `eval/evaluate.py` | Use `DatasetEnvelope.model_validate_json()` with flat-format fallback |
| `eval/dataset/runner.py` | Remove `logging.basicConfig()` from `run()` body |
| `scripts/generate_dataset.py` | Add `logging.basicConfig()` at CLI entry point |
| `eval/` → `src/eval/` | Move entire directory to follow `src`-layout |
| `pyproject.toml` | Update packages from `"eval"` to `"src/eval"` |

---

## Verification

1. **Bug fix:** Run `scripts/generate_dataset.py refresh` twice in a row on an unchanged `INTERCOM.md` — second run should print "No changes detected." (currently it re-processes all new articles).
2. **Parser deduplication:** Run `uv run build-index` to confirm `vector_store` still loads and embeds articles correctly. Run `scripts/generate_dataset.py init --max-articles 3 --dry-run` to confirm `article_parser` produces the same article count and titles as before.
3. **Config constants:** Verify `from agentic_rag import config; print(config.DATASET_GENERATION_MODEL)` resolves to the default `gemini-2.5-flash` without the env var, and to the override value when set.
4. **Pydantic validation:** Run `scripts/evaluate.py` with the current `data/test_set.json` — confirm it loads and scores without error. Intentionally corrupt a field in a test copy to confirm the Pydantic error surfaces cleanly.
5. **Logging placement:** Run `scripts/generate_dataset.py init --dry-run` and confirm INFO-level log lines still appear in the terminal.
6. **Package move:** After moving `eval/` to `src/eval/`, run `uv sync` and confirm `from eval.dataset.runner import RunConfig` still resolves. Run `uv run python scripts/generate_dataset.py --help` to confirm the CLI entry point works.
