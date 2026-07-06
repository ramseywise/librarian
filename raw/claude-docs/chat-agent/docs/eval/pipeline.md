# Evaluation Pipeline

Two-stage pipeline: **dataset generation** builds and maintains a versioned synthetic test set; **evaluation** runs queries through the agent, scores responses, and publishes results to Langfuse.

---

## Dataset Generation

**Entry point:** `scripts/generate_dataset.py`

Parses Intercom articles from `data/knowledge_base/INTERCOM.md`, generates synthetic Q&A pairs using an LLM, and persists them as a versioned `DatasetEnvelope` in `data/test_set.json` and in Langfuse.

### Modes

| Mode | When to use | What it does |
|------|-------------|--------------|
| `init` | First run, empty dataset | Generates all item types for all articles, writes `v1` |
| `refresh` | After article changes | Fingerprints articles, regenerates only new/changed ones, deletes stale items, bumps version |
| `regenerate` | After prompt changes | Force-regenerates all items, preserves `created_at`, bumps version |
| `export` | Re-sync without regenerating | Pushes the current local `test_set.json` to Langfuse as-is |

```bash
uv run python scripts/generate_dataset.py init
uv run python scripts/generate_dataset.py refresh
uv run python scripts/generate_dataset.py regenerate
uv run python scripts/generate_dataset.py export
```

### Item types

Each test item has a `metadata.category` field:

| Category | Source | Confidence hint |
|----------|--------|-----------------|
| `simple` | Single article, direct Q&A | HIGH |
| `complex` | Cross-article synthesis (random pairs within a collection) | MEDIUM |
| `ambiguous` | Underspecified questions distributed across articles | LOW |
| `out_of_scope` | Taxonomy-driven prohibited-action queries | — (refusal expected) |

### Key options

| Flag | Default | Purpose |
|------|---------|---------|
| `--items-per-article N` | 4 | Simple + complex items per article per language |
| `--out-of-scope-count N` | 30 | Total out-of-scope items per language |
| `--ambiguous-count N` | 20 | Total ambiguous items per language |
| `--complex-pairs N` | 5 | Random same-collection article pairs per language |
| `--regenerate-static` | off | (refresh only) Also regenerate out-of-scope and ambiguous items |
| `--fetch` | off | Run `intercom_loader.py` first to refresh `INTERCOM.md` |
| `--generation-model MODEL` | `$DATASET_GENERATION_MODEL` or `gemini-2.5-flash` | Override generation model |
| `--max-articles N` | all | Limit articles processed (smoke-testing) |
| `--no-langfuse` | off | Skip Langfuse publish, write local file only |
| `--dry-run` | off | Print what would happen without writing or publishing |
| `--output PATH` | `data/test_set.json` | Local output path |
| `--dataset-name NAME` | `agentic-rag-eval` | Langfuse dataset name |

### How versioning works

- The envelope has a `langfuse_dataset_version` field (`v1`, `v2`, …) that increments on every write.
- Previous versions are backed up in `data/` before overwriting.
- Item IDs are content-derived (SHA-256 of category + language + question) so re-running with identical inputs is idempotent and Langfuse upserts are safe.
- On `refresh`, articles are fingerprinted (normalized body SHA-256). Only articles whose fingerprint changed trigger regeneration; unchanged items are preserved.

### Output schema (`data/test_set.json`)

```
DatasetEnvelope
├── schema_version: "1"
├── langfuse_dataset_name
├── langfuse_dataset_version   # "v1", "v2", …
├── created_at                 # frozen on init, preserved on regenerate
├── last_refreshed_at
├── item_count
├── article_manifest           # per-article fingerprint + list of generated item IDs
└── items[]
    ├── id                     # stable content-derived ID
    ├── instruction            # the user question
    ├── expected_output
    │   ├── response           # ground-truth answer
    │   ├── source_article_ids
    │   └── confidence_hint    # HIGH | MEDIUM | LOW
    └── metadata
        ├── category           # simple | complex | ambiguous | out_of_scope
        ├── difficulty         # easy | medium | hard
        ├── query_language     # en | fr
        ├── domain
        ├── financial_risk
        ├── generation_model
        └── generated_at
```

---

## Evaluation

> **Work in progress.** The current evaluator is a POC — it uses a single Gemini LLM judge with a 1–5 quality score as a rough signal. Proper per-metric evaluators (Answer Correctness, Faithfulness, Boundary Adherence, etc.) are being designed; see [eval_metrics.md](eval_metrics.md) for the target spec.

**Entry point:** `scripts/evaluate.py`

Loads the test set, runs each query through the live agent, judges response quality, and publishes scores and trace links to Langfuse.

```bash
uv run python scripts/evaluate.py
```

### What it does

1. Loads `data/test_set.json`, samples up to `max_samples` (default 20, seed 42).
2. For each item: calls `agent.query(instruction)`, judges the response with a Gemini LLM judge (1–5 scale), and links the trace to the Langfuse dataset item.
3. Writes `evaluation_results.json` with aggregate metrics and per-item scores.

### Output (`evaluation_results.json`)

| Field | Description |
|-------|-------------|
| `total_samples` | Items evaluated |
| `successful_runs` | Items with a valid agent response |
| `average_quality_score` | Mean judge score (1–5) |
| `classify_query_rate` | % of runs that triggered `classify_query` |
| `grade_relevance_rate` | % of runs that triggered `grade_relevance` |
| `corrections` | Count of `rewrite_query` calls (Corrective RAG activations) |
| `scores` | Per-item score list |

### Metrics spec

For a detailed description of all evaluation metrics (Faithfulness, Response Naturalness, Answer Completeness) see [eval_metrics.md](eval_metrics.md).

---

## Environment variables

| Variable | Required for |
|----------|-------------|
| ADC | Agent runtime and LLM judge — run `gcloud auth application-default login` |
| `DATASET_GENERATION_MODEL` | Generation model override (default: `gemini-2.5-flash`) |
| `LANGFUSE_PUBLIC_KEY` | Langfuse publishing |
| `LANGFUSE_SECRET_KEY` | Langfuse publishing |
| `LANGFUSE_BASE_URL` | Langfuse host |
| `LANGFUSE_PROMPT_LABEL` | Langfuse prompt origin label |
| `USE_LOCAL_PROMPTS` | Set to `true` to skip Langfuse and use hardcoded fallback prompts |
| `DATABASE_URL` | PostgreSQL / pgvector (agent runtime) |
| `INTERCOM_API_KEY` | Fetching articles (`--fetch` flag) |

Before running Langfuse-related commands, source variables from `.env`:

```bash
export LANGFUSE_PUBLIC_KEY=$(grep LANGFUSE_PUBLIC_KEY .env | cut -d= -f2 | tr -d '"')
export LANGFUSE_SECRET_KEY=$(grep LANGFUSE_SECRET_KEY .env | cut -d= -f2 | tr -d '"')
export LANGFUSE_HOST=$(grep LANGFUSE_BASE_URL .env | cut -d= -f2 | tr -d '"')
```
