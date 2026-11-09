---
title: Synthetic Dataset Generation for RAG Eval
tags: [eval, rag, pattern]
summary: Four-mode pipeline for generating and maintaining a versioned synthetic test dataset from a knowledge base — article fingerprinting drives incremental refresh, stable content-derived IDs make Langfuse upserts idempotent, and four query categories cover the full quality surface.
updated: 2026-11-09
sources:
  - data/raw/claude-docs/chat-agent/docs/kb-analysis/intercom_kb_analysis.md
  - data/raw/claude-docs/chat-agent/docs/eval/pipeline.md
  - data/raw/claude-docs/chat-agent/docs/plans/synthetic_dataset_generation.md
  - data/raw/claude-docs/chat-agent/docs/plans/aif32_code_review_fixes.md
  - data/raw/repos/datathon_mcp/.claude--docs--research--awo-welfare-data-harvester.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--03-eval-datasets.md
  - data/raw/papers/2026-11-05-gandhi-2023-understanding-social-reasoning-language-models.md
  - data/raw/papers/2026-11-06-driouich-2025-diverse-private-synthetic-datasets-generation.md
  - data/raw/papers/2026-11-06-zhang-2025-can-llms-ask-good-questions.md
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

**Package layout note:** the package now lives at `src/eval/` (not `eval/` at repo root), following the `src`-layout convention used by `src/agentic_rag/` — see [[PGVector Migration Pattern]] for the sibling package. With hatch's `packages = ["src/eval"]` the installed name still resolves as `eval`, so `from eval.dataset.runner import RunConfig` etc. are unchanged.

---

## Code Review Fixes (AIF-32)

A code review of the `eval/dataset/` pipeline surfaced one correctness bug and several consistency gaps, fixed in a single follow-up pass:

- **Fingerprint bug:** `_run_refresh()` only wrote refreshed fingerprints into `article_manifest` for `diff.changed`, not `diff.new` — meaning newly added articles were re-treated as "new" on every subsequent refresh. Fix: include `diff.new` in the same fingerprint-write loop (confirms the "Bug to avoid" note above).
- **Parser deduplication:** `src/agentic_rag/vector_store.py` (`_parse_intercom_chunks`) and `eval/dataset/article_parser.py` (`_parse_content`) had independently duplicated the same Intercom section-splitting/header-extraction logic. Extracted into a shared `src/agentic_rag/intercom_parser.py::parse_intercom_content()`, called by both — public interfaces of both callers unchanged.
- **Pydantic validation with backward compat:** `evaluate.py::load_test_set()` now validates via `DatasetEnvelope.model_validate_json()` first, falling back to the legacy flat-list JSON parse on exception — lets the schema evolve without breaking older test-set files.
- **Logging config placement:** `logging.basicConfig()` was called inside `runner.run()` — a library function reconfiguring the root logger as a side effect of being imported/called. Moved to the CLI entry point (`scripts/generate_dataset.py`), just before `runner.run(config)`.
- **`DATASET_GENERATION_MODEL`/`DATASET_GENERATION_API_KEY`** (see above) were originally inline `_resolve_config()` lookups duplicated in `generators/intercom.py` and `generators/out_of_scope.py` — centralised as `config.py` constants that both generators now import.

---

## Generate along dimensions (course synthesis)

Asking a model for "100 test questions" returns 100 variations of the same polite question. Instead:

1. Pick 3–4 dimensions that matter (persona, intent, complexity, channel).
2. Generate **tuples** of dimension values first (`frustrated × billing × ambiguous`) and check coverage.
3. Turn each tuple into a natural-language query in a **separate** call.

Guard against **self-preference**: if the generating model is also a candidate under test it finds its
own phrasing easy — generate with a **different model family**, then read the rows.

## Corpus-grounded generation with clustering and PII masking (Driouich et al.)

Driouich, Cao and Thomas (arXiv 2508.18929, a 2025 workshop paper) describe a LangGraph pipeline of three agents that builds a question-answer set for RAG evaluation from a private corpus. A diversity agent clusters the chunk embeddings with k-means and takes representative samples from every cluster, so topics are covered through the corpus rather than through whatever a prompt suggests. A privacy agent detects personal data in each sample and pseudonymizes it, writing a privacy report. A QA agent then writes question-answer pairs from the masked samples and a QA report. Setup: chunks of 256 tokens, text-embedding-3-small embeddings, GPT-4o for the diversity and QA agents, GPT-4.1 for the privacy agent, temperature 0.

- **Diversity, judged.** A GPT-4.1 judge saw pairs of question sets and rated variety, topical coverage and phrasing from 1 to 10. On one document (the EU AI Act), at 10 questions the pipeline scored 7.8 against 7.0 for an evolutionary baseline in the style of RAGAS and 6.2 for few-shot direct prompting; at 100 questions it scored 9.0 against 8.1 and 7.6 (self-reported). Each cell is one number, with no repeats.
- **Privacy, per label.** On three AI4Privacy datasets (PII, PWI, PHI), the privacy agent's entity accuracy was highest for JOBTYPE (0.94), LASTNAME (0.91) and DISABILITYSTATUS (0.91), and GENDER scored 0.83 (PHI), 0.88 (PWI) and 0.83 (PII) (self-reported). The paper never defines accuracy and has no baseline such as a regex or Presidio tool ([[Presidio PII Redaction for Langfuse]]).

## What unconstrained question generation produces (Zhang et al.)

Zhang, Liu and colleagues (arXiv 2501.03491, a 2025 preprint) compare the questions of four models (GPT-4o, DeepSeek-V3, Claude-3.7-Sonnet and the Llama-3.3-70B-Instruct model) with those in two human-built QA sets, TriviaQA and HotpotQA. Setup for the LLM side: WikiText contexts, 1,024 questions per model from a shared 256 contexts, temperature 0, one run, with GPT-4o assigning each question one of 10 hand-built types.

- **Question type.** In the type table the descriptive type was 27.1 for Llama, 44.7 for DeepSeek, 29.4 for Claude and 37.1 for GPT-4o, against 3.0 for TriviaQA and 1.5 for HotpotQA. The identity-or-attribution type ran the other way: 34.2 and 39.7 for the two human sets, 9.3 to 14.8 for the models (self-reported).
- **Answer length.** Human gold answers average 2.0 words (TriviaQA) and 2.2 (HotpotQA). Model answers given the context ran 24.4 to 35.0 words, and 7.3 to 13.7 after a shortening step with a concise-answer prompt (self-reported).
- **Question length.** Model questions averaged 15.3 to 23.6 words with a standard deviation of 3.6 to 5.6, against 18.0 +/- 10.0 for HotpotQA and 14.0 +/- 6.5 for TriviaQA (self-reported).
- **Judge check.** The GPT-4o judge correlated 0.76 (Pearson) with 300 manual annotations; the paper gives no annotator count or method.

The authors conclude that model-written questions suit RAG testing and hallucination detection; the extraction notes this is asserted, not tested.

## Limits

Driouich et al.: the extraction finds no check of question quality (correctness, answerability or groundedness), no human review and no RAG system run over the questions. Diversity is tested on a single document and privacy on separate synthetic text, so leaked personal data in the generated questions is never checked. One model family writes the data and also judges diversity (GPT-4.1), there is no ablation, and the gaps of about one rating point rest on single runs. The extraction notes two inconsistencies: the paper says lower cosine-based values mean more spread, yet the pipeline's value is the least negative at every size, so that column does not back the diversity claim and only the judge column clearly favours the pipeline; and the dataset-size table's sentence and entity columns look swapped. The extraction also notes that the abstract's "robust" masking sits beside label accuracies of 0.83 to 0.91, that only the top labels are reported in the text, and that the rise in diversity with set size is partly built in because more samples cover more clusters. It also notes that the datasets are named "...-Masking-200K" while only 1,600 to 1,800 samples of each are used, and that the baselines converge on the same value (-0.33) at n=100.

Zhang et al.: the human and model question sets come from different contexts (HotpotQA uses multi-paragraph evidence, WikiText a single paragraph), so differences in type are mixed up with task design and the annotation brief. GPT-4o generates questions and also classifies types, selects covered sentences and rates answers, with one run per model and no confidence intervals. "Good" questions are never defined by human preference or downstream use, which the extraction says leaves the title stronger than the findings. The extraction notes inconsistencies: Llama's question length is 23.6 in one table and 18.5 in another for the main prompt; GPT-4o's type shares differ between the main table (45.8 and 53.4) and the prompt-variant table (58.0 and 41.2); and GPT-4o's T9 share is 14.1 in one table and 14.7 in another. The "three variations" check has only two independent variants, since the first is the main prompt; the shortened-answer standard deviations in Table 4 exceed the means; and Appendix B cites "Figure 5c" for what are three panels.

## See Also
- [[RAG Eval Metrics Suite]]
- [[RAG Evaluation]]
- [[Langfuse Platform]]
- [[LLM Grader Calibration Insights]]
- [[Eval Harness]]
- [[PGVector Migration Pattern]]
- [[Synthesize the Cheap Half]] — extends (which half of an evaluation is safe to synthesize)
- [[Consequence-Flagged KB Audit]] — extends (upstream audit that is the source of the financial_risk stratum and authoritative-article choices)
- [[Answer Criteria with Named Wrong Answers]] — related (per-topic fail-if lists for the same bot)
- [[Proxy Schema Overfits the Guess]] — extends (a synthetic source whose guessed fields hardened into required ones)
- [[Diversity Seeding for Synthetic Data]] — extends (combinatorial, hierarchical and audience seeding; Promptagator query generation)
- [[BigToM Model-Generated Benchmark]] — related (a model fills a causal template to write test items)
- [[Silicon Sampling and Algorithmic Fidelity]] — related (simulating human respondents with a model; a different synthetic-data use)
- [[PII Masking Approaches]] — related (masking source text before generating test items)
- [[Promptagator Few-Shot Synthetic Retrieval Data]] — related
- [[ARES Automated RAG Evaluation]] — related
- [[Model-Written Evaluations]] — related (another model-generated test set pipeline)
