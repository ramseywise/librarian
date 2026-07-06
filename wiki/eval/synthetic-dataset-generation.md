---
title: Synthetic Dataset Generation for RAG Eval
tags: [eval, rag, pattern]
summary: Four-mode pipeline for generating and maintaining a versioned synthetic test dataset from a knowledge base — article fingerprinting drives incremental refresh, stable content-derived IDs make Langfuse upserts idempotent, and four query categories cover the full quality surface.
updated: 2026-07-06
sources:
  - raw/claude-docs/chat-agent/docs/eval/pipeline.md
  - raw/claude-docs/chat-agent/docs/plans/synthetic_dataset_generation.md
---

# Synthetic Dataset Generation for RAG Eval

A repeatable pattern for generating and maintaining a held-out synthetic test set from a knowledge base (KB), without access to production traffic. The pipeline feeds offline RAG evaluation and publishes versioned datasets to Langfuse.

---

## Four Query Categories

| Category | Definition | Agent expected behavior | Target share |
|---|---|---|---|
| `simple` | Single-fact question answerable from one article | Retrieve and answer directly | ~40% |
| `complex` | Synthesis from 2+ articles | Retrieve multiple, synthesise | ~25% |
| `ambiguous` | Underspecified — missing context about situation, company size, or conditions | Ask for clarification or give scoped answer with caveats | ~15% |
| `out_of_scope` | Action requests, account-specific queries, or general knowledge — cannot be answered from a static KB | Decline and redirect to human | ~20% |

`out_of_scope` items are critical for boundary adherence evaluation and must be generated from a **fixed prohibited-action taxonomy** (not article content), so they are stable across KB changes.

---

## Four Operation Modes

| Mode | When | What it does |
|---|---|---|
| `init` | First run | Generate all items for all articles; write `v1` |
| `refresh` | After article changes | Fingerprint articles; regenerate only new/changed; delete stale items; bump version |
| `regenerate` | After prompt changes | Force-regenerate all items; preserve `created_at`; bump version |
| `export` | Re-sync without regenerating | Push current local file to Langfuse as-is |

```bash
uv run python scripts/generate_dataset.py init
uv run python scripts/generate_dataset.py refresh
uv run python scripts/generate_dataset.py regenerate --dry-run
```

---

## Article Fingerprinting and Change Detection

The dataset envelope stores an `article_manifest` mapping each `article_id` to its current content fingerprint:

```python
def article_fingerprint(body_text: str) -> str:
    normalized = " ".join(body_text.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]
```

On `refresh`:
- **New article** → generate items, add to manifest
- **Changed article** (fingerprint differs) → delete linked items, regenerate, update fingerprint
- **Removed article** → mark linked items stale and remove
- **Unchanged article** → skip

`out_of_scope` and `ambiguous` items don't depend on articles and are **not regenerated on refresh** unless `--regenerate-static` is passed.

**Bug to avoid:** After generating items for new articles, write the new fingerprints into the manifest — otherwise newly added articles are treated as "new" on every subsequent refresh run.

---

## Stable Item IDs

Item IDs are content-derived, making re-runs idempotent and Langfuse upserts safe:

```python
def item_id(category: str, language: str, question: str) -> str:
    key = json.dumps({"category": category, "language": language, "question": question}, sort_keys=True)
    return "item-" + hashlib.sha256(key.encode()).hexdigest()[:12]
```

The same question + category + language always produces the same ID. Changing the question text generates a new item and removes the old one.

---

## Dataset Envelope Schema

```
DatasetEnvelope
├── schema_version: "1"
├── langfuse_dataset_name
├── langfuse_dataset_version    # "v1", "v2", …
├── created_at                  # frozen on init, preserved on regenerate
├── last_refreshed_at
├── article_manifest            # per-article fingerprint + item IDs
└── items[]
    ├── id                      # stable content-derived ID
    ├── instruction             # the user question
    ├── expected_output
    │   ├── response            # ground-truth answer
    │   ├── source_article_ids
    │   └── confidence_hint     # HIGH | MEDIUM | LOW
    └── metadata
        ├── category            # simple | complex | ambiguous | out_of_scope
        ├── difficulty          # easy | medium | hard
        ├── query_language      # en | fr
        ├── domain              # invoicing | payments | accounts | subscriptions | …
        ├── financial_risk
        └── generation_model
```

`confidence_hint` is populated by category/difficulty and used only by the evaluator — **never passed to the agent**:
- `simple` + `easy` → `HIGH`
- `complex` + `hard` → `MEDIUM`
- `ambiguous` → `LOW`
- `out_of_scope` → `null`

---

## LLM Generation Prompts

### Simple Items
Single article input → N Q&A pairs with exact values, dates, and conditions cited. Rules: answers must be specific (not "yes you can"), always include the relevant detail.

### Complex Items
Two article inputs → N cross-article Q&A pairs. Rule: the question must be **unanswerable from either article alone**.

### Ambiguous Items
Single article input → N underspecified questions. Rule: missing context about user situation, company size, or time frame. Must not be clearly out of scope.

### Out-of-Scope Items
No article input → N questions from a fixed prohibited-action taxonomy:
- Action requests: cancel subscription, process refund, update payment method
- Account-specific: "why was I charged X", "show me my invoices"
- Live data queries: "what is my current balance"
- General knowledge, legal advice

---

## Generation Model Independence

Use dedicated env vars for the generation model, separate from the agent's model:

```
DATASET_GENERATION_API_KEY=   # Falls back to GEMINI_API_KEY
DATASET_GENERATION_MODEL=     # Falls back to GEMINI_MODEL_NAME
```

**Rationale:** Ideally the generation model differs from the agent's evaluation model to reduce self-confirmation bias. The separation allows swapping providers without touching agent config. The model used is recorded in each item's `metadata.generation_model`.

---

## Langfuse Integration

```python
# Create dataset (first run)
langfuse.create_dataset(name="agentic-rag-eval", ...)

# Upsert items (idempotent via stable ID)
langfuse.create_dataset_item(
    dataset_name="agentic-rag-eval",
    input={"query": item["instruction"]},
    expected_output=item["expected_output"],
    metadata=item["metadata"],
    id=item["id"],
)
```

Versioning: the dataset `name` is fixed; `metadata.langfuse_dataset_version` increments on every `init`, `refresh`, or `regenerate` run. A breaking schema change creates a new Langfuse dataset with a suffixed name (`agentic-rag-eval-v2`).

Evaluation runs link traces to dataset items:
```python
item.link(trace, run_name=f"eval-{date}")
```

---

## Metric-to-Dataset Mapping

| Metric | Requires from dataset |
|---|---|
| Faithfulness | No special field — runtime trace |
| Response Naturalness | No special field — runtime trace |
| Answer Completeness | `expected_output.response` |
| Contextual Recall | `expected_output.response` |
| Document Precision | `expected_output.source_article_ids` |
| Boundary Adherence | `metadata.category == "out_of_scope"` items |
| Confidence Calibration | `expected_output.confidence_hint` (requires 100+ items per tier) |

---

## Package Structure

```
eval/
  dataset/
    schema.py           # Pydantic: DatasetItem, DatasetEnvelope
    article_parser.py   # Parse KB markdown → structured article dicts
    fingerprint.py      # Fingerprint + manifest diff logic
    versioning.py       # Version bump + backup
    langfuse_publisher.py
    generators/
      base.py           # Abstract BaseGenerator
      intercom.py       # Article → Q&A (simple, complex, ambiguous)
      out_of_scope.py   # Taxonomy-driven fixed items
      # conversation.py # FUTURE: historical conversation → Q&A
```

The abstract `BaseGenerator` makes it straightforward to add a `ConversationHistoryGenerator` without schema changes — `metadata.source` already distinguishes `"intercom"` vs `"conversation_history"`.

---

## See Also
- [[RAG Eval Metrics Suite]]
- [[RAG Evaluation]]
- [[Langfuse Platform]]
- [[LLM Grader Calibration Insights]]
- [[VA Eval Harness]]
