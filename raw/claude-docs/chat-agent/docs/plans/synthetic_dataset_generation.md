# Plan: Synthetic Test Dataset Generation Script

**Branch:** AIF-32-generate-test-dataset  
**Date:** 2026-04-15  
**Status:** Draft

---

## 1. Context and Goals

We need a script (`scripts/generate_dataset.py`) that produces and maintains a held-out test dataset for offline evaluation of the Agentic RAG chatbot. The dataset is consumed by `scripts/evaluate.py` and published to Langfuse as a versioned dataset.

### What already exists

- `data/knowledge_base/INTERCOM.md` — all Intercom articles in markdown
- `scripts/evaluate.py` — runs queries through the agent and scores them
- Six eval metrics defined in `docs/eval/eval_metrics.md`, requiring specific fields in the dataset

### What this plan adds

A script that:
1. Parses Intercom articles (already stored in `INTERCOM.md`) and generates synthetic Q&A pairs using an LLM
2. Covers four query categories, two languages, and three difficulty levels
3. Detects new, changed, or removed articles and refreshes only affected items
4. Publishes the dataset to Langfuse and versions it
5. Is structured to accommodate a future second source: historical conversation data

### Source of article content

The generation script reads from `data/knowledge_base/INTERCOM.md`, the same file the vector store ingests from. Three alternatives were considered:

| Option | Verdict | Reason |
|---|---|---|
| **INTERCOM.md** (chosen) | Use this | Full article bodies in one place; works offline; same source the vector store uses; good for generation prompts |
| Intercom API directly | Avoid | Duplicates `intercom_loader.py` logic; adds network/API dependency; rate-limited; fails offline |
| Vector DB | Avoid | DB stores chunks, not full articles; reconstructing articles from chunks is fragile; adds DB dependency to a script that only needs text |

The main risk of `INTERCOM.md` is staleness. This is mitigated by a `--fetch` flag (see CLI section) that runs `intercom_loader.py` before generation as part of a single command, and by the `refresh` workflow making the file-freshness dependency explicit.

---

## 2. Dataset Schema

Each test case must carry enough information to compute all six eval metrics.

### Item-level fields

```json
{
  "id": "sha256-based stable ID",
  "instruction": "The user query (string)",
  "expected_output": {
    "response": "Reference answer string",
    "source_article_ids": ["13390711"],
    "confidence_hint": "HIGH | MEDIUM | LOW | null"
  },
  "metadata": {
    "category": "simple | complex | ambiguous | out_of_scope",
    "domain": "invoicing | payments | accounts | subscriptions | ...",
    "difficulty": "easy | medium | hard",
    "query_language": "en | fr",
    "source": "intercom | conversation_history",
    "source_article_ids": ["13390711"],
    "article_fingerprints": {"13390711": "sha256-of-article-body"},
    "financial_risk": true,
    "verified": false,
    "generation_model": "gemini-2.5-flash",
    "generated_at": "2026-04-15T12:00:00Z",
    "notes": "Optional freeform notes"
  }
}
```

**Field rationale:**

- `instruction` + `expected_output.response` → Metric 1 (Answer Correctness F1)
- `metadata.category == "out_of_scope"` → Metric 3 (Boundary Adherence) test cases
- The remaining metrics (Faithfulness, Naturalness, Calibration) are runtime- or trace-derived and require no additional dataset fields
- `expected_output.confidence_hint` is an optional hint used by the evaluator script for Metric 6 calibration analysis; it is **never** passed to the agent
- `metadata.domain` classifies which product area the item covers (e.g. `invoicing`, `payments`, `accounts`, `subscriptions`). Enables per-domain quality breakdowns in Langfuse. Populated by the LLM during generation for in-scope items, or from the out-of-scope taxonomy for out-of-scope items
- `metadata.source` enables future merging of conversation-history-derived items without schema changes
- `metadata.article_fingerprints` enables the refresh logic to invalidate items when an article body changes
- `verified: false` always — human review is a future step and not gated in the current pipeline

### Dataset-level envelope (local JSON)

```json
{
  "schema_version": "1",
  "langfuse_dataset_name": "agentic-rag-eval",
  "langfuse_dataset_version": "v1",
  "created_at": "2026-04-15T12:00:00Z",
  "last_refreshed_at": "2026-04-15T12:00:00Z",
  "item_count": 120,
  "article_manifest": {
    "13390711": {
      "title": "La Réforme de la Facturation Électronique",
      "fingerprint": "sha256-abc123",
      "last_seen_at": "2026-04-15T12:00:00Z",
      "item_ids": ["item-uuid-1", "item-uuid-2"]
    }
  },
  "items": []
}
```

**Local file path:** `data/test_set.json`

---

## 3. Query Category Coverage

### Category definitions

| Category | Definition | Agent expected behavior | Target share | Notes |
|---|---|---|---|---|
| `simple` | Single-fact question answerable from one article | Retrieve article, answer directly | ~40% | en + fr variants |
| `complex` | Question requiring synthesis of 2+ articles | Retrieve multiple articles, synthesise | ~25% | Generated from article pairs |
| `ambiguous` | Underspecified question with multiple valid interpretations | Ask for clarification or give a scoped answer with caveats | ~15% | Tests that agent doesn't hallucinate when context is unclear |
| `out_of_scope` | Request the bot cannot fulfil (process a refund, access account data, general knowledge) | Decline and redirect to human agent | ~20% | Critical for Metric 3 (Boundary Adherence) |

### Target item count

Following Langfuse's recommendation of 100+ items per confidence tier for Metric 6 (Confidence Calibration) to be statistically meaningful, the target total is **~300 items**:
- `simple`: ~120 items (60 en + 60 fr)
- `complex`: ~75 items (mixed language)
- `ambiguous`: ~45 items (mixed language)
- `out_of_scope`: ~60 items (30 en + 30 fr)

### Language distribution

Each generated item has a `query_language` of `en` or `fr`. For `simple` and `complex` categories, generate both language variants from the same source article(s). For `ambiguous` and `out_of_scope`, generate the primary language first, then translate the question (not the answer) into the other language.

### Difficulty mapping

- `simple`: easy / medium (depending on how much inference is needed)
- `complex`: medium / hard
- `ambiguous`: medium (no difficulty variation needed)
- `out_of_scope`: easy (clear refusal) or medium (subtle edge cases)

---

## 4. Article Fingerprinting and Change Detection

A **manifest** is stored inside the dataset envelope (`article_manifest`). It maps each `article_id` to its current content fingerprint (SHA-256 of the article body text, normalised).

### On `init` (first run)

1. Parse `INTERCOM.md` → extract all articles with their IDs, titles, bodies, and inferred domains
2. Compute fingerprint for each article
3. Populate the manifest
4. Run generation for all articles
5. Write `data/test_set.json` and push to Langfuse

### On `refresh` (subsequent runs after article updates)

1. Parse `INTERCOM.md` → extract current articles
2. Compare against stored manifest:
   - **New article** (ID not in manifest): generate items, add to manifest
   - **Changed article** (fingerprint differs): delete all items linked to this article ID, regenerate, update manifest fingerprint
   - **Removed article** (ID in manifest but not in current): mark linked items as `stale` and remove them, remove from manifest
   - **Unchanged article**: skip
3. Increment dataset version, push delta to Langfuse, update local file

### Out-of-scope items and `refresh`

Out-of-scope items do not depend on articles. By default, `refresh` does **not** regenerate them. Pass `--regenerate-static` to force regeneration of out-of-scope and ambiguous items (e.g. after prompt changes).

### Fingerprint computation

```python
import hashlib

def article_fingerprint(body_text: str) -> str:
    normalized = " ".join(body_text.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]
```

---

## 5. LLM Generation Pipeline

### Model configuration

The generation model uses **dedicated environment variables**, separate from the agent's Gemini config, to allow independent tuning:

```
DATASET_GENERATION_API_KEY=<key>   # Defaults to GEMINI_API_KEY if unset
DATASET_GENERATION_MODEL=<model>   # Defaults to GEMINI_MODEL_NAME if unset
```

Currently both resolve to Gemini (`gemini-2.5-flash`). The separation means a different model can be plugged in later without touching the agent configuration. The model used is recorded in each item's `metadata.generation_model`.

At generation time the model is also configurable via `--generation-model` CLI flag (overrides env var).

> **Independence note:** Ideally the generation model should differ from the agent's model to reduce self-confirmation bias (as noted in the eval metrics doc). When access to a second model provider is available, swap `DATASET_GENERATION_MODEL` and `DATASET_GENERATION_API_KEY` without touching the script.

### Generation prompts

#### 5.1 Simple items

**Input:** Single article body + instructions  
**Output:** JSON array of Q&A pairs

```
System:
You are generating evaluation test cases for a customer support chatbot. The chatbot answers questions about Shine's financial services product based on help center articles.

User:
Given the following article, generate [N] simple question-answer pairs. Each question must be answerable from this article alone.

Rules:
- Answers must be specific: cite exact values, dates, percentages, or conditions from the article
- Do not generate generic answers like "yes you can" — always include the relevant detail
- Generate questions in [LANGUAGE]. Generate answers in [LANGUAGE].
- Assign a domain from: invoicing, payments, accounts, subscriptions, banking, other

Return a JSON array:
[
  {
    "question": "...",
    "answer": "...",
    "difficulty": "easy|medium",
    "domain": "...",
    "financial_risk": true|false,
    "notes": "what this tests"
  }
]

Article (ID: [ARTICLE_ID]):
[ARTICLE BODY]
```

#### 5.2 Complex items

**Input:** Two article bodies + instructions  

```
Given the following two articles, generate [N] question-answer pairs where answering correctly requires information from BOTH articles.

Rules:
- The question must be unanswerable from either article alone
- Answers must synthesise specific details from both articles
- Generate questions in [LANGUAGE]. Generate answers in [LANGUAGE].
- Assign a domain that best represents the overlap between the two articles

Return a JSON array:
[
  {
    "question": "...",
    "answer": "...",
    "source_article_ids": ["id1", "id2"],
    "difficulty": "medium|hard",
    "domain": "...",
    "financial_risk": true|false,
    "notes": "what cross-article inference this tests"
  }
]
```

#### 5.3 Ambiguous items

**Input:** Single article body + instructions  

```
Generate [N] ambiguous questions based on the following article. Each question should be genuine but underspecified — missing context about the user's situation, company size, time frame, or applicable conditions. The question must NOT be clearly out of scope.

Generate questions in [LANGUAGE].
```

#### 5.4 Out-of-scope items

**No article input** — generated from a fixed taxonomy of prohibited action categories:

```
Generate [N] out-of-scope questions that a customer might ask but that a static knowledge base chatbot cannot answer. Draw from these categories:
- Action requests: cancel subscription, process refund, change email address, update payment method
- Account-specific queries: "why was I charged X", "when will my card arrive", "show me my invoices"
- Live data queries: "what is my current balance", "has my payment been received"
- General knowledge: "what is the best accounting software", "how do French taxes work"
- Legal advice: "am I legally required to", "can I sue if"

Assign a domain per question from: invoicing, payments, accounts, subscriptions, banking, general, legal.
Generate questions in [LANGUAGE]. Questions should sound like real customer messages.
```

### Item ID generation

Each item gets a stable ID derived from its content, enabling idempotent re-runs:

```python
import hashlib, json

def item_id(category: str, language: str, question: str) -> str:
    key = json.dumps({"category": category, "language": language, "question": question}, sort_keys=True)
    return "item-" + hashlib.sha256(key.encode()).hexdigest()[:12]
```

---

## 6. Langfuse Integration

### Dataset lifecycle

```python
from langfuse import Langfuse

langfuse = Langfuse()

# First run: create dataset
langfuse.create_dataset(
    name="agentic-rag-eval",
    description="Synthetic test dataset for Agentic RAG chatbot",
    metadata={"schema_version": "1", "langfuse_dataset_version": "v1"}
)

# Add / upsert items (stable ID makes this idempotent)
langfuse.create_dataset_item(
    dataset_name="agentic-rag-eval",
    input={"query": item["instruction"]},
    expected_output=item["expected_output"],
    metadata=item["metadata"],
    id=item["id"]
)
```

### Versioning in Langfuse

Langfuse datasets do not natively support semantic versions. Versioning is handled as follows:
- The dataset `name` is fixed: `agentic-rag-eval`
- `metadata.langfuse_dataset_version` is updated on every `init`, `refresh`, or `regenerate` run
- The local envelope stores the current version string
- `evaluate.py` reads the version and logs it as a tag on each Langfuse evaluation run
- A breaking schema change (integer `schema_version` bump) creates a new Langfuse dataset with a suffixed name: `agentic-rag-eval-v2`

### Linking evaluation runs

`eval/evaluate.py` (updated separately) will:
1. Load items from Langfuse: `langfuse.get_dataset("agentic-rag-eval")`
2. Run the agent per item, link the trace: `item.link(trace, run_name="eval-{date}")`
3. Post metric scores to the trace via `langfuse.score()`

This is outside the scope of the generation script; the schema is designed to support it.

---

## 7. Package Structure

The dataset generation logic lives in a new top-level `eval/` package, following the same convention as `api/`, `guardrails/`, and `src/agentic_rag/`. The existing `scripts/evaluate.py` moves into `eval/` as well, so all evaluation-related code is collocated. `scripts/` retains only thin CLI entry-point wrappers — consistent with how `scripts/intercom_loader.py` is already a 3-line delegate to `agentic_rag.loaders.intercom`.

```
eval/
  __init__.py
  evaluate.py                  # Moved from scripts/evaluate.py
  dataset/
    __init__.py
    schema.py                  # Pydantic models: DatasetItem, DatasetEnvelope
    article_parser.py          # Parse INTERCOM.md → structured article dicts
    fingerprint.py             # Fingerprint computation + manifest diff logic
    versioning.py              # Version bump and backup logic
    langfuse_publisher.py      # Dataset create/upsert/version in Langfuse
    generators/
      __init__.py
      base.py                  # Abstract BaseGenerator class
      intercom.py              # Article → Q&A LLM generator (simple, complex, ambiguous)
      out_of_scope.py          # Taxonomy-driven out-of-scope generator
      # conversation.py        # FUTURE: historical conversation → Q&A generator

scripts/
  generate_dataset.py          # Thin wrapper → eval.dataset
  evaluate.py                  # Thin wrapper → eval.evaluate (or retired)
  intercom_loader.py           # Already a thin wrapper → agentic_rag.loaders.intercom
```

### Abstract Generator base class

```python
from abc import ABC, abstractmethod
from typing import Iterator
from .schema import DatasetItem

class BaseGenerator(ABC):
    """Generates DatasetItems from a given source."""

    @abstractmethod
    def generate(self, **kwargs) -> Iterator[DatasetItem]:
        """Yield DatasetItem instances."""
        ...

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Identifier stored in item metadata.source."""
        ...
```

`IntercomGenerator(BaseGenerator)` handles articles. When conversation history data becomes available, `ConversationHistoryGenerator(BaseGenerator)` is added with no changes to orchestration.

---

## 8. CLI Interface

```
uv run python scripts/generate_dataset.py [MODE] [OPTIONS]
```

### Modes

| Mode | Description |
|---|---|
| `init` | First-time run. Parses all articles, generates full dataset, creates Langfuse dataset, writes `data/test_set.json` |
| `refresh` | Detects changed/new/removed articles, regenerates only affected items, increments version. Does NOT regenerate out-of-scope or ambiguous items unless `--regenerate-static` is passed |
| `regenerate` | Force-regenerates all items (e.g. after prompt changes). Increments version |
| `export` | Re-pushes the current local `data/test_set.json` to Langfuse without regenerating |

### Options

| Flag | Default | Description |
|---|---|---|
| `--generation-model` | `$DATASET_GENERATION_MODEL` | Override the generation model for this run |
| `--items-per-article` | `4` | Simple + complex items to generate per article per language |
| `--out-of-scope-count` | `30` | Total out-of-scope items per language |
| `--ambiguous-count` | `20` | Total ambiguous items per language |
| `--regenerate-static` | flag | Force regeneration of out-of-scope and ambiguous items on `refresh` |
| `--fetch` | flag | Run `intercom_loader.py` to refresh `INTERCOM.md` before generating. Ensures articles are up-to-date without needing a separate command |
| `--dataset-name` | `agentic-rag-eval` | Langfuse dataset name |
| `--no-langfuse` | flag | Skip Langfuse publishing (local-only run) |
| `--dry-run` | flag | Print what would be generated/changed without writing anything |
| `--output` | `data/test_set.json` | Local output path |

### New environment variables

Add to `.env.example`:

```
# Dataset generation (independent from the agent model)
DATASET_GENERATION_API_KEY=     # Falls back to GEMINI_API_KEY
DATASET_GENERATION_MODEL=       # Falls back to GEMINI_MODEL_NAME
```

---

## 9. Versioning Strategy

| Version field | Location | Format | Increment trigger |
|---|---|---|---|
| `schema_version` | Envelope | Integer string `"1"` | Breaking schema changes only |
| `langfuse_dataset_version` | Envelope + Langfuse metadata | `"v{n}"` | Every `init`, `refresh`, or `regenerate` run |
| `article_manifest.*.last_seen_at` | Envelope | ISO datetime | Every `refresh` run, per article |

On any version increment, `data/test_set.json` is backed up to `data/test_set_previous.json` before overwrite.

---

## 10. Metric-to-Dataset Mapping

| Metric | Requires from dataset | Notes |
|---|---|---|
| 1. Answer Correctness | `instruction`, `expected_output.response` | Reference answer must be specific (not generic) |
| 2. Faithfulness | No special field — runtime | Retrieved context and response captured in Langfuse trace |
| 3. Boundary Adherence | `metadata.category == "out_of_scope"` items | Requires ~20% out-of-scope coverage |
| 4. Response Naturalness | No special field — runtime | Response-only judge |
| 5. Confidence Calibration | `expected_output.confidence_hint` | Hint used post-eval to bucket items; requires 100+ items per tier |

`confidence_hint` is populated by the generator based on category:
- `simple` + `easy` → `HIGH`
- `complex` + `hard` → `MEDIUM`
- `ambiguous` → `LOW`
- `out_of_scope` → `null`

`metadata.domain` enables per-domain quality breakdowns across all metrics in Langfuse dashboards.

---

## 11. Future Extension: Conversation History

When historical conversation data becomes available:

1. Add `scripts/dataset/generators/conversation.py` implementing `BaseGenerator`
2. The generator accepts conversation transcripts → produces `DatasetItem` objects with `metadata.source = "conversation_history"`
3. `generate_dataset.py` `init` / `refresh` modes call both generators and merge outputs
4. The schema already supports this via `metadata.source` and the abstract generator pattern

No changes to `schema.py`, `langfuse_publisher.py`, `versioning.py`, or the Langfuse dataset structure are needed.

---

## 12. Implementation Steps

1. **Schema** — `eval/dataset/schema.py`: Pydantic models for `DatasetItem` and `DatasetEnvelope`
2. **Article parser** — `eval/dataset/article_parser.py`: extract structured articles from `INTERCOM.md`, reusing logic from `src/agentic_rag/vector_store._parse_intercom_chunks`
3. **Fingerprint module** — `eval/dataset/fingerprint.py`: manifest read/write and diff logic
4. **Intercom generator** — `eval/dataset/generators/intercom.py`: LLM prompts for simple, complex, and ambiguous categories; uses `DATASET_GENERATION_MODEL` via `DATASET_GENERATION_API_KEY`
5. **Out-of-scope generator** — `eval/dataset/generators/out_of_scope.py`: taxonomy-driven prompts, frozen by default
6. **Langfuse publisher** — `eval/dataset/langfuse_publisher.py`: create/upsert/version
7. **Versioning** — `eval/dataset/versioning.py`: version bump and backup
8. **Move `evaluate.py`** — move `scripts/evaluate.py` → `eval/evaluate.py`; update `TEST_SET_PATH` to `data/test_set.json`; add Langfuse dataset run linking
9. **CLI entry points** — `scripts/generate_dataset.py` (thin wrapper → `eval.dataset`); update `scripts/evaluate.py` to a thin wrapper → `eval.evaluate`
10. **Update `.env.example`** — add `DATASET_GENERATION_API_KEY` and `DATASET_GENERATION_MODEL`
11. **Update `CLAUDE.md`** — document the `eval/` package, the new script, and its modes

Dependencies: 1 → 2 → 3 → {4, 5} (parallel) → 6 → 7 → {8, 9} (parallel) → 10 → 11
