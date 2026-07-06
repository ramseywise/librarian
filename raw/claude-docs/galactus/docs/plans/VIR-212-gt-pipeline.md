# Plan: GT Expansion + Conversation Pipeline + Notebook Updates (VIR-212)
Date: 2026-06-08
Based on: Direct codebase inspection + conversation context
Supersedes: VIR-212-gt-verification.md (May 30 plan — grader fixes complete; this is Phase 2)

## Goal
Extend the conversation preprocessing pipeline with category/contact_reason enrichment and feature engineering, expand the GT beyond 597 BKH items using the full May 5 Intercom corpus, and update notebooks 01–04 to use the enriched data and dual-corpus (local vs Bedrock) comparison.

## Approach
Four phases in dependency order. Phase 1 fixes the data pipeline first — everything downstream (GT expansion, notebooks) depends on having enriched conversation data. Phase 2 builds the expanded GT from the enriched output. Phases 3 and 4 update the notebooks once the data layer is stable. No structural changes to `evals/` — all new logic goes in `core/preprocessing/`.

The key pipeline shape grows from 2 stages to 4:
```
Raw CSVs (May 5 Snowflake export)
  → Stage 1: Cleaning (conv + parts, WITH category/contact_reason join)
  → Stage 2: PII Redaction (unchanged)
  → Stage 3: Feature Engineering (EDA-informed signals, intent mapping)
  → Stage 4: Dataset Stats + Drift Report (BKH vs Intercom, frequency analysis)
```

## Out of Scope
- Live Snowflake access — all work uses May 5 CSVs
- Modifying the verified `golden_597` — augment only
- New top-level dirs under `evals/`
- Reranker implementation (comes after 03 identifies the gap)
- Bedrock re-ingestion (03 reads existing KB, doesn't repush)
- Notebooks 05–07 (crag source analysis, edge case study, alignment)

---

## Phase 1 — Conversation Pipeline Extension

**DoR:** Raw CSVs accessible (currently at `data/Intercom conv data/`, not `data/conversation/raw/`). Must resolve path before steps 1.1–1.4.

### Step 1.0: Resolve raw file paths
**Files:** `core/preprocessing/intercom/conversations/cleaning/config.py` (lines 1–8)
**What:** Update `CONVERSATION_DIR` + `CONV_FILE` / `PARTS_FILE` to point at `data/Intercom conv data/` OR create symlinks from `data/conversation/raw/` to actual files. Config approach preferred (no filesystem side-effects).
**Snippet:**
```python
# Before
CONVERSATION_DIR = Path("data/conversation/raw")
CONV_FILE = "billy_intercom_conversation_2026-05-05-0842.csv"
PARTS_FILE = "billy_intercom_conversation_part_2026-05-05-0843.csv"

# After
CONVERSATION_DIR = Path("data/Intercom conv data")
CONV_FILE = "billy_intercom_conversation_2026-05-05-0842.csv"
PARTS_FILE = "billy_intercom_conversation_part_2026-05-05-0843.csv"
```
**Test:** `python3 -c "from core.preprocessing.intercom.conversations.cleaning.config import CONVERSATION_DIR, CONV_FILE; p = CONVERSATION_DIR / CONV_FILE; print(p, p.exists())"`
**Done when:** Path resolves and file exists = True.

---

### Step 1.1: Join category + contact_reason into parts output (cleaning pipeline — future runs)
**Files:** `core/preprocessing/intercom/conversations/cleaning/main.py` (lines 40–90), `cleaning/config.py` (add constant)
**What:** After `clean_conv()` and `clean_parts()`, do a LEFT JOIN of `['id', 'custom_conversation_category', 'custom_conversation_contact_reason', 'conversation_rating_value']` from the cleaned conv table → cleaned parts on `conversation_id`. These three fields are already cleaned in `clean_conv()` (strips quotes, timestamps). The parts output gains three new columns: `category`, `contact_reason`, `conv_rating`. This step future-proofs the cleaning pipeline; Step 1.1b handles the immediate backfill into the existing PII-redacted file.

**Snippet (main.py):**
```python
# Before: clean_parts writes directly to PARTS_OUTPUT
df_parts = clean_parts(df_raw_parts, valid_conv_ids)
df_parts.to_csv(PARTS_OUTPUT, index=False)

# After: join conv-level metadata before writing
CONV_JOIN_COLS = ["id", "custom_conversation_category",
                   "custom_conversation_contact_reason", "conversation_rating_value"]
df_conv_meta = df_conv[CONV_JOIN_COLS].rename(columns={
    "id": "conversation_id",
    "custom_conversation_category": "category",
    "custom_conversation_contact_reason": "contact_reason",
    "conversation_rating_value": "conv_rating",
})
df_parts = df_parts.merge(df_conv_meta, on="conversation_id", how="left")
df_parts.to_csv(PARTS_OUTPUT, index=False)
```
**Test:** `uv run pytest tests/unit_tests/test_core/ -k "cleaning" -v` + manual spot-check: `python3 -c "import pandas as pd; df=pd.read_csv('data/conversation/cleaned/conversation_part_cleaned.csv', nrows=5); print(df[['conversation_id','category','contact_reason','conv_rating']].head())"`
**Done when:** `conversation_part_cleaned.csv` contains `category`, `contact_reason`, `conv_rating` columns with non-null values for rated conversations.

---

### Step 1.1b: Backfill category + contact_reason into existing PII-redacted file (immediate path)
**Files:** New script `core/preprocessing/intercom/conversations/cleaning/backfill_conv_meta.py`
**What:** The existing `conversation_part_pii_redacted_latest.csv` (June 1, 125M) was produced before Step 1.1 was added — it has no `category`, `contact_reason`, or `conv_rating`. These fields are NOT PII and don't need redaction, so we can join them directly from the raw conversation CSV without re-running the full pipeline (~30 min saved).

Reads:
- `data/Intercom conv data/billy_intercom_conversation_2026-05-05-0842.csv` (raw conv, authoritative — use `_latest.csv` not the May 26 version in `conv cleaned 0529/`)
- `data/Intercom conv data/conversation_part_pii_redacted_latest.csv`

Writes: `data/Intercom conv data/conversation_part_pii_redacted_enriched.csv`

**Snippet:**
```python
JOIN_COLS = ["id", "custom_conversation_category",
             "custom_conversation_contact_reason", "conversation_rating_value"]
df_conv = pd.read_csv(CONV_RAW, usecols=JOIN_COLS, low_memory=False)
df_conv["custom_conversation_category"] = df_conv["custom_conversation_category"].str.strip('"')
df_conv["custom_conversation_contact_reason"] = df_conv["custom_conversation_contact_reason"].str.strip('"')
df_conv = df_conv.rename(columns={
    "id": "conversation_id",
    "custom_conversation_category": "category",
    "custom_conversation_contact_reason": "contact_reason",
    "conversation_rating_value": "conv_rating",
})
df_parts = pd.read_csv(PII_REDACTED_LATEST, low_memory=False)
df_enriched = df_parts.merge(df_conv, on="conversation_id", how="left")
df_enriched.to_csv(ENRICHED_OUTPUT, index=False)
```
**Test:** `python3 -c "import pandas as pd; df=pd.read_csv('data/Intercom conv data/conversation_part_pii_redacted_enriched.csv', nrows=5); print(df[['conversation_id','category','contact_reason','conv_rating']].head()); assert 'category' in df.columns"`
**Done when:** `_enriched.csv` exists; `category` and `contact_reason` non-null for ≥60% of rows (some convs won't have custom fields set); `conv_rating` non-null for rated conversations; row count matches `_latest.csv` exactly (LEFT JOIN, no rows added or dropped).

---

### Step 1.2: Feature engineering module
**Files:** New `core/preprocessing/intercom/conversations/feature_engineering/__init__.py`, `features.py`, `__main__.py`
**What:** New pipeline stage (Stage 3). Reads `conversation_part_pii_redacted_enriched.csv` (output of Step 1.1b), writes `conversation_part_featured.csv`. Two sub-steps:

**Sub-step 1.2a — EDA to extract intent map inputs:**
Before defining the intent map, run a quick EDA cell to extract the top-N `contact_reason` values and their frequencies from the enriched file. This produces the raw material for the map. Without this, the map can't be defined.
```python
df = pd.read_csv(ENRICHED, usecols=["contact_reason"])
print(df["contact_reason"].value_counts().head(30).to_string())
```

**Sub-step 1.2b — Feature computation:**
Computes the following conversation-level features (aggregated per `conversation_id`, joined back to parts):

| Feature | Description | Source signal |
|---|---|---|
| `is_hc_cited` | Any admin turn in the conversation cites a HC URL (`help.shine.co` or `help.billy.dk`) | `body_redacted` URL regex |
| `is_liked` | `conv_rating >= 4` | `conv_rating` from Step 1.1b |
| `intent_cluster` | Mapped from `contact_reason` → granular intent label (defined after 1.2a EDA) | `contact_reason` |
| `is_escalation` | Any admin turn contains escalation keywords | reuse `ESCALATION_KEYWORDS` from `core/preprocessing/bkh/qa_preprocessing.py` |
| `is_greeting_only` | First user turn is a pure greeting | reuse `is_pure_greeting()` from `qa_preprocessing.py` |
| `query_token_count` | Approximate token count of first user turn | `len(body_clean.split()) * 1.3` |

**Snippet (features.py):**
```python
HC_URL_RE = re.compile(r"https?://help\.(shine\.co|billy\.dk)/\S+")

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    # Compute per-conversation signals from admin turns
    admin = df[df["author_type"] == "admin"].copy()
    admin["is_hc_cited"] = admin["body_redacted"].str.contains(HC_URL_RE, na=False)
    conv_features = admin.groupby("conversation_id")["is_hc_cited"].any().reset_index()
    # Join back to all parts
    return df.merge(conv_features, on="conversation_id", how="left")
```

**Test:** `uv run pytest tests/unit_tests/test_core/ -k "feature" -v` (write new test in `tests/unit_tests/test_core/test_features.py`)
**Done when:** `conversation_part_featured.csv` exists with all 6 feature columns; `is_hc_cited` True for ≥5% of rows (sanity check); `intent_cluster` non-null for ≥80% of rows where `contact_reason` is non-null; row count matches input exactly.

---

### Step 1.3: Dataset stats + drift report
**Files:** New `core/preprocessing/intercom/conversations/stats/__init__.py`, `report.py`, `__main__.py`
**What:** Stage 4 — reads featured output + BKH pool, produces a drift/stats report. Output: `data/conversation/stats/dataset_stats.json` + human-readable markdown `data/conversation/stats/dataset_stats.md`.

Sections:
1. **Corpus stats** — total conversations, parts, language split, date range, rating distribution
2. **Category distribution** — top-N `category` × `contact_reason` combinations
3. **Top queries by frequency** — cluster user turns by `intent_cluster`, rank by count
4. **BKH vs Intercom drift** — for overlapping `conversation_id`, compare: rating agreement, category match, HC citation rate
5. **GT coverage gap** — for each intent_cluster, what % has a golden_597 representative?

**Test:** `python3 -m core.preprocessing.intercom.conversations.stats --help` runs; JSON output parses correctly.
**Done when:** `dataset_stats.json` contains all 5 sections; markdown renders without errors.

---

### Step 1.4: Update README
**Files:** `core/preprocessing/intercom/conversations/conv_preprocessing_README.md`
**What:** Add Stage 3 (feature engineering) and Stage 4 (stats) sections. Add pipeline diagram showing all 4 stages. Note the category/contact_reason join in Stage 1. Note file location config.
**Done when:** README reflects 4-stage pipeline with run commands for each stage.

---

## Phase 2 — GT Expansion

**DoR:** `conversation_part_featured.csv` exists (Phase 1 complete). BKH pool at `data/baseline/bkh_qa.jsonl` (verified — `data/datasets/bkh/` does NOT exist, that path is wrong).

### Step 2.1: Liked conversation extraction
**Files:** New `core/preprocessing/bkh/gt_expansion.py`
**What:** From `conversation_part_featured.csv`, produce a single `discovery_hc.jsonl`:
- Filter: `is_liked=True` AND `is_hc_cited=True` AND `created_at >= 2025-06-08` (last year from today)
- Extract first user turn per conversation as query
- Extract admin HC citation URLs as `expected_urls` (the HC citation is the quality signal — BKH matching is metadata only)
- Match to BKH pool (`data/baseline/bkh_qa.jsonl`) by `conversation_id` — set `bkh_matched=True/False` (label only, doesn't change inclusion)
- Deduplicate: 0 `task_id` overlap with `golden_597/queries.jsonl`

Intent gap analysis (Step 2.2) runs directly on `conversation_part_featured.csv` grouped by `intent_cluster` — no separate query-only file needed.

Output schema:
```json
{
  "task_id": "<conv_id>_turn_1",
  "query": "...",
  "expected_urls": ["https://help.shine.co/..."],
  "category": "<contact_reason>",
  "intent_cluster": "...",
  "conv_rating": 4.0,
  "bkh_matched": true,
  "source": "intercom_liked_2025"
}
```

**Test:** `uv run pytest tests/unit_tests/test_core/ -k "gt_expansion" -v`
**Done when:** `data/baseline/discovery_hc.jsonl` exists with ≥100 items; ≥99% rows have ≥1 `expected_url`; 0 `task_id` overlaps with `golden_597/queries.jsonl`.

### Step 2.2: Intent coverage gap analysis
**Files:** `nbks/baseline/01_gt_verification.ipynb` (Section 4 replacement)
**What:** Load `golden_597/queries.jsonl` + `discovery_hc.jsonl` + group `conversation_part_featured.csv` by `intent_cluster` for the full frequency picture. For each cluster: count in 597, count in discovery_hc, total frequency in full corpus. Flag clusters with 0 coverage in 597 as `new_intent`. Output a gap table — candidates for promotion to `capability.jsonl` or `verify.jsonl` in a future GT v2. Human decision on which clusters to promote (not auto-applied).

**Test:** `jupyter nbconvert --to notebook --execute nbks/baseline/01_gt_verification.ipynb --output /tmp/01_run.ipynb 2>&1 | tail -5`
**Done when:** Notebook executes without error; gap table rendered; ≥5 `new_intent` clusters identified.

### Step 2.3: Update 01_gt_verification notebook
**Files:** `nbks/baseline/01_gt_verification.ipynb`
**What:**
- Section 1: Replace `sf_full_year_urls.csv` input with `conversation_part_featured.csv` (filtered to `is_hc_cited=True`)
- Section 2: Replace `sf_billy_parts.csv` with `conversation_part_featured.csv` (full)
- Section 3: URL matching — unchanged (still uses `kb_url_resolve`)
- Section 4: Intent gap analysis using `discovery_hc.jsonl` + `conversation_part_featured.csv` frequency distribution
- Section 5: New — BKH vs Intercom drift table from `dataset_stats.json`
- Remove: old `sf_bkh_pairs_sim.csv` embedding similarity section (superseded by `intent_cluster` grouping)

**Test:** `jupyter nbconvert --to notebook --execute nbks/baseline/01_gt_verification.ipynb --output /tmp/01_run.ipynb 2>&1 | tail -5`
**Done when:** Notebook runs top-to-bottom with no `FileNotFoundError`; both discovery files referenced; gap table and drift table render.

---

## Phase 3 — Notebook 02: Dual Corpus QA

**DoR:** `discovery.jsonl` exists (Phase 2). AWS SSO active (`aws sso login --profile billy-staging`).

### Step 3.1: Fold in billy_kb_eda content (Bedrock EDA section)
**Files:** `nbks/baseline/02_ingest_inspect.ipynb` (add Section D)
**What:** New Section D pulls from `nbks/bedrock_kb/billy_kb_eda.ipynb` — specifically:
- Full OpenSearch index pull (6,965 chunks via paginated scroll)
- Thin chunk analysis (<20 words: 25.3%)
- Duplicate chunk analysis (1,712 exact-text duplicates)
- URL taxonomy (billypedia 452, intercom 337, pricing 59-chunk outlier)
- Save as `data/conversation/bedrock_chunks.parquet` for reuse in 03

`nbks/bedrock_kb/billy_kb_eda.ipynb` → add `# DEPRECATED: content moved to 02_ingest_inspect.ipynb Section D` at top cell.

**Test:** `jupyter nbconvert --to notebook --execute nbks/baseline/02_ingest_inspect.ipynb --output /tmp/02_run.ipynb 2>&1 | tail -5` (run with SSO active)
**Done when:** Section D runs; `bedrock_chunks.parquet` written; thin chunk count ≈ 1,763 and duplicate count ≈ 1,712 (matches billy_kb_eda baseline).

### Step 3.2: Fold in bedrockkb_retrieval_validation (S1–S13 smoke tests)
**Files:** `nbks/baseline/02_ingest_inspect.ipynb` — **replace existing Section B** with updated version from `nbks/bedrock_kb/bedrockkb_retrieval_validation.ipynb`

**What:** `02_ingest_inspect` already has its own Section B with S1–S13 scenarios. The standalone `bedrockkb_retrieval_validation.ipynb` has an updated version with more scenarios and better output formatting. Action: replace Section B in 02 with the content from the standalone notebook (not append as a new section — that would duplicate). Use `discovery_hc.jsonl` + `golden_597` GT queries to drive programmatic scenarios; keep human-review scenarios (S4–S7 freshness, S12 failed-URL list) as named explicit tests unchanged.

`nbks/bedrock_kb/bedrockkb_retrieval_validation.ipynb` → add `# DEPRECATED: content moved to 02_ingest_inspect.ipynb Section B` at top cell.

**Test:** Section B cell outputs show pass/fail per scenario; S12 failed-URL comparison cell runs without KeyError.
**Done when:** Section B runs against staging KB; all auto-check scenarios print ✅/❌; S12 failed-URL list current.

### Step 3.3: Side-by-side comparison section
**Files:** `nbks/baseline/02_ingest_inspect.ipynb` (add Section F)
**What:** For the same 20 GT queries sampled from `discovery_hc.jsonl` (covering all intent clusters):
- Retrieve top-3 from local DuckDB (OverlappingChunker 256 + e5-large)
- Retrieve top-3 from Bedrock KB
- Side-by-side table: query | local top-1 URL | bedrock top-1 URL | match? | local chunk preview | bedrock chunk preview
- Flag pricing page explicitly — show where each corpus truncates the chunk

Output: gap table saved as `nbks/baseline/rag_opt_results/corpus_comparison.json` (reused by 03).

**Test:** Gap table renders and JSON file written; assert `len(results) == 20`.
**Done when:** Section F produces the side-by-side table; at least one pricing page query shows chunk cutoff difference between corpora; `corpus_comparison.json` written.

---

## Phase 4 — Notebooks 03 + 04 Updates

**DoR:** `corpus_comparison.json` exists (Phase 3). `bedrock_chunks.parquet` exists.

### Step 4.1: Add Bedrock as third retrieval backend in 03
**Files:** `nbks/baseline/03_rag_optimization.ipynb` (Section B — retrieval methods)
**What:** Add a `bedrock_retrieve(query, top_k)` notebook helper that wraps the existing async `retrieve()` from `src/clients/bedrock_kb.py`. The actual interface is async and takes a list — wrap it correctly:

```python
import asyncio
from src.clients.bedrock_kb import retrieve as _bedrock_retrieve

def bedrock_retrieve(query: str, top_k: int = 5):
    passages = asyncio.run(_bedrock_retrieve([query]))
    return passages[:top_k]
```

`BEDROCK_KNOWLEDGE_BASE_ID` must be set in env (staging: `IZIPVEXDSF`). Extend the metrics table with a Bedrock row alongside `dense`, `bm25`, `hybrid_rrf`. Grid: `[dense, bm25, hybrid_rrf, bedrock]` × top-k `[3, 5, 10]`.

Key constraint: Bedrock calls cost money — cap at 50 queries for the Bedrock column (use `discovery_hc.jsonl[:50]`).

**Test:** `jupyter nbconvert --to notebook --execute nbks/baseline/03_rag_optimization.ipynb --output /tmp/03_run.ipynb 2>&1 | tail -5`
**Done when:** Metrics table has 4 retrieval rows; Bedrock MRR/P@3 computed from `discovery_hc.jsonl[:50]`.

### Step 4.2: Add data source grid search
**Files:** `nbks/baseline/03_rag_optimization.ipynb` (new Section G)
**What:** Grid over which data sources to include in local corpus (compared against Bedrock as a fixed reference point):
- `corpus_v1`: help_en + help_da + pricing (current Bedrock default)
- `corpus_v2`: v1 + billypedia
- `corpus_v3`: v1 + billypedia + blog (blog has `bedrock_id=None` — local DuckDB only; excluded from Bedrock comparison)

For each: MRR on `discovery_hc.jsonl`. Decision output: which corpus config to recommend for Bedrock re-sync (documented as a markdown cell, not auto-applied).

**Test:** Grid table renders with 3 rows; MRR values computable.
**Done when:** Data source grid table rendered; recommendation markdown cell written.

### Step 4.3: Reframe 04_ablation_analysis baseline
**Files:** `nbks/baseline/04_ablation_analysis.ipynb` (Section A — baseline definition)
**What:** Update baseline definition from "no features" to "Bedrock retrieval, no reranker, no CRAG". Each feature delta measured against this. Add a `delta_vs_bedrock` column to all ablation result tables. Add a row for "local pipeline best (from 03)" vs "bedrock" as the first ablation comparison row.

**Test:** `jupyter nbconvert --to notebook --execute nbks/baseline/04_ablation_analysis.ipynb --output /tmp/04_run.ipynb 2>&1 | tail -5`
**Done when:** Ablation table has `delta_vs_bedrock` column; "local best vs bedrock" row is the first row in the table.

---

## Test Plan
| Phase | Command | Pass threshold |
|---|---|---|
| 1.0 | `python3 -c "from core.preprocessing.intercom.conversations.cleaning.config import CONVERSATION_DIR, CONV_FILE; p = CONVERSATION_DIR / CONV_FILE; print(p.exists())"` | `True` |
| 1.1 | `uv run pytest tests/unit_tests/test_core/ -k "cleaning" -v` | All 103 core tests pass |
| 1.1b | `python3 -c "import pandas as pd; df=pd.read_csv('data/Intercom conv data/conversation_part_pii_redacted_enriched.csv', nrows=5); assert 'category' in df.columns; print('ok')"` | `ok` |
| 1.2–1.3 | `uv run pytest tests/unit_tests/test_core/ -k "feature" -v` | New feature tests pass |
| 1.4 | README renders without broken links | Visual check |
| 2.1 | `python3 -c "import json; hc=open('data/baseline/discovery_hc.jsonl').readlines(); assert all(json.loads(l).get('expected_urls') for l in hc); print(len(hc), 'items ok')"` | ≥100 items; all have expected_urls; 0 overlap with 597 |
| 2.2–2.3 | `jupyter nbconvert --to notebook --execute nbks/baseline/01_gt_verification.ipynb --output /tmp/01_run.ipynb` | No execution errors |
| 3.1–3.3 | `jupyter nbconvert --to notebook --execute nbks/baseline/02_ingest_inspect.ipynb --output /tmp/02_run.ipynb` | Runs with SSO active; `corpus_comparison.json` written |
| 4.1 | `jupyter nbconvert --to notebook --execute nbks/baseline/03_rag_optimization.ipynb --output /tmp/03_run.ipynb` | 4-row metrics table rendered |
| 4.2–4.3 | `jupyter nbconvert --to notebook --execute nbks/baseline/04_ablation_analysis.ipynb --output /tmp/04_run.ipynb` | `delta_vs_bedrock` column present |

## Risks & Rollback
| Risk | Mitigation |
|---|---|
| `conversation_part_featured.csv` too large for notebook (125M + features) | Use chunked pandas reads in notebooks; store `bedrock_chunks.parquet` separately |
| AWS SSO expires mid-session (8h TTL) | Run Phase 3 (Sections D–F) in one sitting after fresh `aws sso login --profile billy-staging` |
| `_enriched.csv` join produces wrong category values (raw CSV quotes not stripped) | Step 1.1b snippet explicitly strips quotes before join; verify with spot-check test |
| `discovery_hc.jsonl` too small for meaningful retrieval grid (<50 items) | Relax date filter to `>= 2024-01-01` if needed; document the threshold used |
| Blog corpus (287 docs) has `bedrock_id=None` | Step 4.2 grid makes this explicit; excluded from Bedrock column; decision in markdown cell |
| Bedrock `retrieve()` is async — conflicts with notebook event loop | Use `asyncio.run()` wrapper in Step 4.1 snippet; if Jupyter already has a running loop, use `nest_asyncio.apply()` |
| Section B replacement in 02 (Step 3.2) loses existing passing scenarios | Before replacing, confirm which scenarios in existing Section B pass and carry them over |

## Open Questions
1. **Config path (Step 1.0)**: Update `config.py` (permanent, clean) or use env-var override? Config update is preferred — env-var approach means every run needs the var set. Close this before executing Step 1.0.

2. **Snowflake access for future refreshes**: Once SSO is available again, `core/ingestion/intercom/conversations/main.py` is the refresh path. Document this in the README (Step 1.4) so the next refresh doesn't need this plan.

3. **GT v2 promotion**: After Step 2.2 produces the gap table, which `new_intent` clusters get promoted into `capability.jsonl` or `verify.jsonl`? This is a human decision — leave the gap table output as a candidate list, not auto-promoted.
