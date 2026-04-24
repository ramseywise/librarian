# Plan — Librarian Directory Restructure

> Eliminate mid-refactor debris (duplicate `ingestion/`+`preprocessing/`, re-export stubs,
> scattered protocols) and impose a clear architectural boundary between infrastructure,
> ingestion pipeline, and the online query path.
>
> Date: 2026-04-11
> Status: Superseded — codebase was built with a different (cleaner) structure than this plan assumed.
> The assumed directories (`protocols/`, `preprocessing/`, `analysis/`, `retrieval/infra/`, `retrieval/testing/`)
> were never created. Protocols live inline in each `base.py`; pipeline modules are under `pipeline/`;
> infra lives under `tools/`. No action needed.

---

## Target Structure

```
librarian/
├── factory.py
├── schemas/          ← shared data contracts (TypedDicts, Pydantic models)
├── utils/            ← config, logging, tracing, LLM client
├── testing/          ← consolidated test fixtures (mock_embedder)
│
├── ingestion/        ← offline document processing pipeline
│   ├── base.py       ← Protocols: Chunker, ChunkerConfig (absorbed from protocols/)
│   ├── chunking/     ← from preprocessing/chunking/ (canonical; drop ingestion/chunking/)
│   ├── parsing/      ← from preprocessing/parsing/  (canonical; drop ingestion/parsing/)
│   ├── indexing/     ← from preprocessing/indexing/ (canonical; drop ingestion/indexing/)
│   ├── embeddings/   ← moved from top-level embeddings/
│   ├── loaders.py    ← kept from old ingestion/
│   ├── s3_loader.py  ← kept from old ingestion/
│   ├── pipeline.py   ← kept from old ingestion/
│   └── trace_pipeline.py
│
├── orchestration/    ← online query planning and graph execution
│   ├── analysis/     ← moved from top-level analysis/
│   ├── graph.py
│   ├── history.py
│   ├── nodes/
│   └── query_understanding.py
│
├── retrieval/        ← online retrieval logic (scoring, RRF, cache, snippet)
│   ├── base.py       ← Protocols: Embedder, Retriever, ChatModel (absorbed from protocols/)
│   ├── cache.py
│   ├── rrf.py
│   ├── scoring.py
│   └── snippet.py
│
├── reranker/         ← online reranking  [stays separate]
│   ├── base.py       ← Reranker Protocol (absorbed from protocols/)
│   ├── cross_encoder.py
│   ├── llm_listwise.py
│   └── passthrough.py
│
├── generation/       ← online LLM response generation  [stays separate]
│   ├── context.py
│   ├── generator.py
│   └── prompts.py
│
├── eval_harness/     ← evaluation tooling (separate initiative to promote later)
│
└── infra/            ← deployment + persistence infrastructure
    ├── api/          ← FastAPI app + Lambda handler (moved from top-level api/)
    ├── mcp/          ← MCP servers (moved from top-level mcp/)
    └── storage/      ← database backends (moved from top-level storage/)
        ├── vectordb/ ← Chroma, OpenSearch, DuckDB, InMemory
        ├── metadatadb/
        ├── tracedb/
        └── graphdb/
```

**Deleted:**
- `protocols/` — absorbed into `ingestion/base.py` (Chunker) and `retrieval/base.py` (Embedder, Retriever) and `reranker/base.py` (Reranker)
- `preprocessing/` — canonical implementations move into `ingestion/`; unique pipeline files already in `ingestion/`
- `embeddings/` (top-level) — moves to `ingestion/embeddings/`
- `retrieval/infra/` — re-export stub; backends now at `infra/storage/vectordb/`
- `retrieval/testing/` — moves to `testing/` (consolidate with existing stub there)
- `analysis/` (top-level) — moves to `orchestration/analysis/`
- `storage/` (top-level) — moves to `infra/storage/`
- `api/` (top-level) — moves to `infra/api/`
- `mcp/` (top-level) — moves to `infra/mcp/`

---

## Protocol placement rationale

| Protocol | New home | Reason |
|---|---|---|
| `Chunker`, `ChunkerConfig` | `ingestion/base.py` | Implementations live in `ingestion/chunking/`; only ingestion + factory use it |
| `Embedder` | `retrieval/base.py` | Used at query time by retrieval; factory injects the impl; ingestion uses concrete class directly |
| `Retriever` | `retrieval/base.py` | Already re-exported there; just remove the indirection |
| `Reranker` | `reranker/base.py` | Already re-exported there; same cleanup |
| `ChatModel` | `retrieval/base.py` | Added in hardening; stays |

---

## Step 1 — Create `infra/` and move `api/`, `mcp/`, `storage/`

**What moves:**
```
api/           → infra/api/
mcp/           → infra/mcp/
storage/       → infra/storage/
```

**Also:** delete `retrieval/infra/` (its backends are now at `infra/storage/vectordb/`).

**Import updates — source:**

| File | Old import | New import |
|---|---|---|
| `factory.py` | `agents.librarian.storage.metadata_db` | `agents.librarian.infra.storage.metadata_db` |
| `factory.py` | `agents.librarian.storage.snippet_db` | `agents.librarian.infra.storage.snippet_db` |
| `factory.py` | `agents.librarian.retrieval.infra.chroma` | `agents.librarian.infra.storage.vectordb.chroma` |
| `factory.py` | `agents.librarian.retrieval.infra.duckdb` | `agents.librarian.infra.storage.vectordb.duckdb` |
| `factory.py` | `agents.librarian.retrieval.infra.inmemory` | `agents.librarian.infra.storage.vectordb.inmemory` |
| `factory.py` | `agents.librarian.retrieval.infra.opensearch` | `agents.librarian.infra.storage.vectordb.opensearch` |
| `ingestion/pipeline.py` | `agents.librarian.storage.metadata_db` | `agents.librarian.infra.storage.metadata_db` |
| `ingestion/pipeline.py` | `agents.librarian.storage.snippet_db` | `agents.librarian.infra.storage.snippet_db` |
| `retrieval/snippet.py` | `agents.librarian.storage.snippet_db` | `agents.librarian.infra.storage.snippet_db` |
| `infra/api/app.py` | (internal — moves with the package, no change) | — |
| `infra/api/routes.py` | (internal) | — |

**Import updates — tests:**

| File | Old import | New import |
|---|---|---|
| `unit/conftest.py` | `retrieval.infra.inmemory` | `infra.storage.vectordb.inmemory` |
| `unit/test_api.py` | `agents.librarian.api` | `agents.librarian.infra.api` |
| `unit/test_factory.py` | `retrieval.infra.inmemory` | `infra.storage.vectordb.inmemory` |
| `unit/test_ingestion.py` | `retrieval.infra.inmemory` | `infra.storage.vectordb.inmemory` |
| `unit/test_ingestion.py` | `storage.metadata_db` | `infra.storage.metadata_db` |
| `unit/test_ingestion.py` | `storage.snippet_db` | `infra.storage.snippet_db` |
| `unit/test_mcp_librarian.py` | `agents.librarian.mcp` | `agents.librarian.infra.mcp` |
| `unit/test_mcp_s3.py` | `agents.librarian.mcp.s3_server` | `agents.librarian.infra.mcp.s3_server` |
| `unit/test_mcp_snowflake.py` | `agents.librarian.mcp.snowflake_server` | `agents.librarian.infra.mcp.snowflake_server` |
| `unit/test_retrieval.py` | `retrieval.infra.inmemory` | `infra.storage.vectordb.inmemory` |
| `unit/test_retrieval_subgraph.py` | `retrieval.infra.inmemory` | `infra.storage.vectordb.inmemory` |
| `unit/test_s3_trigger.py` | `agents.librarian.api.s3_trigger` | `agents.librarian.infra.api.s3_trigger` |
| `unit/test_storage.py` | `storage.metadata_db` | `infra.storage.metadata_db` |
| `unit/test_storage.py` | `storage.snippet_db` | `infra.storage.snippet_db` |
| `evalsuite/conftest.py` | `retrieval.infra.inmemory` | `infra.storage.vectordb.inmemory` |
| `evalsuite/regression/test_retrieval_metrics.py` | `retrieval.infra.inmemory` | `infra.storage.vectordb.inmemory` |
| `evalsuite/capability/test_pipeline_capability.py` | `retrieval.infra.inmemory` | `infra.storage.vectordb.inmemory` |

**Note on `storage/__init__.py`:** Currently re-exports `MetadataDB` from `metadatadb.duckdb` and mistakenly re-exports `SnippetDB` from `tracedb.duckdb` (likely a copy-paste bug — `SnippetDB` should come from `snippet_db`, not `tracedb`). Carry the re-exports into `infra/storage/__init__.py` as-is; do not fix the naming bug here (separate issue).

**Risk:** Medium — many import paths change, but no logic changes. Tests will catch regressions.

**Estimate:** ~2h

**Verification:** `uv run pytest tests/librarian/unit/test_api.py tests/librarian/unit/test_storage.py tests/librarian/unit/test_mcp_librarian.py -q`

---

## Step 2 — Absorb `protocols/` and consolidate `ingestion/` + `preprocessing/`

This step has two sub-parts that must be done together — they both touch the same module boundary.

### 2a: Absorb `protocols/`

**Chunker/ChunkerConfig → `ingestion/base.py`:**
- Copy the `Chunker` Protocol and `ChunkerConfig` dataclass from `protocols/chunker.py` directly into `ingestion/base.py` (replacing the existing re-export shim)
- Remove `from agents.librarian.protocols.chunker import ...` from `ingestion/base.py`

**Embedder, Retriever, ChatModel → `retrieval/base.py`:**
- Copy `Embedder` Protocol from `protocols/embedder.py` into `retrieval/base.py` (replacing re-export)
- Copy `Retriever` Protocol from `protocols/retriever.py` into `retrieval/base.py` (replacing re-export)
- `ChatModel` is already defined directly there from the hardening step — no change needed

**Reranker → `reranker/base.py`:**
- Copy `Reranker` Protocol from `protocols/reranker.py` into `reranker/base.py` (replacing re-export)

**Then delete `protocols/` entirely.**

**factory.py import update:**
```python
# Before
from agents.librarian.protocols import Chunker, Embedder, Reranker, Retriever

# After
from agents.librarian.ingestion.base import Chunker
from agents.librarian.retrieval.base import Embedder, Retriever
from agents.librarian.reranker.base import Reranker
```

### 2b: Consolidate `preprocessing/` → `ingestion/`

`preprocessing/` holds the canonical implementations; `ingestion/` holds unique pipeline files.
The merge makes `ingestion/` the single package.

**Move (keep `preprocessing/` content):**
```
preprocessing/base.py        → ingestion/base.py    (already updated in 2a)
preprocessing/chunking/      → ingestion/chunking/  (replace old ingestion/chunking/)
preprocessing/parsing/       → ingestion/parsing/   (replace old ingestion/parsing/)
preprocessing/indexing/      → ingestion/indexing/  (replace old ingestion/indexing/)
```

**Keep (already in ingestion/):** `loaders.py`, `s3_loader.py`, `pipeline.py`, `trace_pipeline.py`

**Delete:** `ingestion/chunking/` (old duplicate), `ingestion/parsing/` (old duplicate), `ingestion/indexing/` (old duplicate), `preprocessing/` (entire old folder)

### 2c: Move `embeddings/` → `ingestion/embeddings/`

```
embeddings/embedders.py → ingestion/embeddings/embedders.py
```

Delete `preprocessing/embedding/` stub and top-level `embeddings/`.

**Import updates:**

| File | Old import | New import |
|---|---|---|
| `factory.py` | `preprocessing.chunking.html_aware` | `ingestion.chunking.html_aware` |
| `factory.py` | `preprocessing.embedding.embedders` | `ingestion.embeddings.embedders` |
| `ingestion/pipeline.py` | `preprocessing.base` | `ingestion.base` |
| `ingestion/chunking/*.py` | `protocols.chunker` | `ingestion.base` |
| `ingestion/indexing/indexer.py` | `protocols.chunker` | `ingestion.base` |
| `ingestion/indexing/indexer.py` | `preprocessing.chunking.*` | `ingestion.chunking.*` |
| `ingestion/indexing/indexer.py` | `preprocessing.parsing.*` | `ingestion.parsing.*` |
| `retrieval/base.py` | `protocols.embedder`, `protocols.retriever` | (defined directly — remove re-export) |
| `reranker/base.py` | `protocols.reranker` | (defined directly — remove re-export) |
| `unit/test_preprocessing.py` | `preprocessing.base` | `ingestion.base` |
| `unit/test_preprocessing.py` | `preprocessing.chunking.*` | `ingestion.chunking.*` |
| `unit/test_ingestion.py` | `preprocessing.chunking.strategies` | `ingestion.chunking.strategies` |

**Risk:** Medium-high — most import churn in this step. Internal `preprocessing/` self-references all need updates. Verify there is no logic difference between `ingestion/chunking/*.py` and `preprocessing/chunking/*.py` before deleting (they should be identical; confirm with `diff`).

**Estimate:** ~2.5h

**Verification:** `uv run pytest tests/librarian/unit/test_preprocessing.py tests/librarian/unit/test_ingestion.py tests/librarian/unit/test_factory.py -q`

---

## Step 3 — Move `analysis/` → `orchestration/analysis/`

**What moves:**
```
analysis/          → orchestration/analysis/
```

**Import updates — source:**

| File | Old import | New import |
|---|---|---|
| `orchestration/query_understanding.py` | `agents.librarian.analysis.analyzer` | `agents.librarian.orchestration.analysis.analyzer` |
| `orchestration/query_understanding.py` | `agents.librarian.analysis.expansion` | `agents.librarian.orchestration.analysis.expansion` |
| `orchestration/query_understanding.py` | `agents.librarian.analysis.routing` | `agents.librarian.orchestration.analysis.routing` |
| `orchestration/analysis/__init__.py` | (internal — update self-references) | — |
| `orchestration/analysis/analyzer.py` | `agents.librarian.analysis.*` | `agents.librarian.orchestration.analysis.*` |
| `orchestration/analysis/routing.py` | `agents.librarian.analysis.analyzer` | `agents.librarian.orchestration.analysis.analyzer` |

**Risk:** Low — one module boundary change, small blast radius.

**Estimate:** ~0.5h

**Verification:** `uv run pytest tests/librarian/unit/test_query_understanding.py -q` (or grep for `analysis` in test files first)

---

## Step 4 — Consolidate test utilities: `retrieval/testing/` → `testing/`

`retrieval/testing/mock_embedder.py` and `testing/mock_embedder.py` both exist. Confirm they are identical (or that `testing/mock_embedder.py` is the superset), then:

- Delete `retrieval/testing/`
- The canonical location is already `testing/mock_embedder.py`

**Import updates — all test files:**

| File | Old import | New import |
|---|---|---|
| `unit/conftest.py` | `retrieval.testing.mock_embedder` | `testing.mock_embedder` |
| `unit/test_factory.py` | `retrieval.testing.mock_embedder` | `testing.mock_embedder` |
| `unit/test_ingestion.py` | `retrieval.testing.mock_embedder` | `testing.mock_embedder` |
| `unit/test_retrieval.py` | `retrieval.testing.mock_embedder` | `testing.mock_embedder` |
| `unit/test_retrieval_subgraph.py` | `retrieval.testing.mock_embedder` | `testing.mock_embedder` |
| `evalsuite/conftest.py` | `retrieval.testing.mock_embedder` | `testing.mock_embedder` |
| `evalsuite/regression/test_retrieval_metrics.py` | `retrieval.testing.mock_embedder` | `testing.mock_embedder` |
| `evalsuite/capability/test_pipeline_capability.py` | `retrieval.testing.mock_embedder` | `testing.mock_embedder` |

**Risk:** Low — test-only change.

**Estimate:** ~0.5h

**Verification:** `uv run pytest tests/librarian/ -q --co` (collection-only — confirms all imports resolve)

---

## Execution order

| Step | Depends on | Est. | Risk |
|---|---|---|---|
| 1. Create `infra/` | None | 2h | Medium |
| 2. Absorb `protocols/` + consolidate `ingestion/` | Step 1 (storage paths resolved first) | 2.5h | Medium-high |
| 3. Move `analysis/` → `orchestration/analysis/` | None (independent) | 0.5h | Low |
| 4. Consolidate `testing/` | None (independent) | 0.5h | Low |

Steps 3 and 4 are independent of each other and of step 2. Recommended:

```
Step 1 → Step 2       (serial — 2 depends on 1 being stable)
Step 3 \
Step 4  > (can run in parallel with each other, or interleaved with steps 1-2)
```

**Total estimate:** ~5.5h

---

## Verification (full suite)

After all steps:

1. `uv run pytest tests/librarian/ -q` — all green
2. `uv run pytest tests/librarian/ -q --co` — no import errors
3. `uv run pyright src/agents/librarian/factory.py` — no unresolved imports
4. `grep -r "agents\.librarian\.protocols" src/ tests/` — empty (protocols/ fully absorbed)
5. `grep -r "agents\.librarian\.preprocessing" src/ tests/` — empty (preprocessing/ removed)
6. `grep -r "retrieval\.infra" src/ tests/` — empty (retrieval/infra/ removed)
7. `grep -r "agents\.librarian\.storage" src/ tests/` — only `infra.storage.*` references remain
8. `grep -r "agents\.librarian\.analysis" src/ tests/` — only `orchestration.analysis.*` references remain

---

## Out of scope

- `eval_harness/` promotion to a top-level `evals/` agent — separate initiative, requires its own plan
- Fixing the `storage/__init__.py` naming bug (`SnippetDB` re-exported from `tracedb.duckdb`) — separate fix
- Finishing the hardening plan Step 2 (`langchain-core` dev dep removal) — tracked in `librarian-hardening.md`
