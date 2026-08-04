---
title: Experiment Tracking Schemas
tags: [eval, infra, rag, pattern]
summary: "The metadata contract that makes an eval run reproducible and diffable — base trace fields every agent emits, plus ExperimentRun/RagConfig/BedrockConfig/ChunkRecord dataclasses that pin the exact configuration a result came from."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--06-observability--support-agent-observability.md
---

# Experiment Tracking Schemas

A metric without its configuration is not a result. "Recall@5 was 0.71" is unusable a week
later unless you also know the chunker, chunk size, embedding model, retrieval `k`, and the
commit the code was on. These schemas exist so that every number carries the configuration
that produced it.

This is the *identity* half of observability. [[Observability and Runtime Patterns]] covers
what to monitor and alert on; this page covers what must be recorded so a run can be
**reproduced and diffed against another run**.

## What a trace must contain

For each agent run, the trace records:

```
├── Complete prompt, including system prompts
├── Complete messages[] across all interaction rounds
├── Each tool call + parameters + return value
├── Inference chain, if thinking mode is present
├── Final output
└── Token consumption + latency
```

Beyond retrieval-by-ID, **semantic retrieval over traces** is the capability that makes a
trace store useful for engineering rather than just for debugging one incident: being able
to ask *"which traces call two tools"* without exact string matching is what enables
workflow automation over the trace corpus.

## Base trace metadata

The minimal contract — every agent call emits these regardless of framework. These are what
make a trace *queryable* and a run *reproducible*.

| Field | Type | Purpose |
|---|---|---|
| `run_id` | `str` | `uuid4`, unique per invocation |
| `session_id` | `str` | conversation thread ID, passed in by the caller |
| `agent` | `str` | which agent implementation handled the turn |
| `model` | `str` | model name/ARN used for generation |
| `prompt_version` | `str` | `PROMPT_VERSION` constant from the agent module |
| `git_commit` | `str` | short SHA — ties the log entry to an exact code state |
| `latency_ms` | `float` | wall-clock, request in to response out |
| `input_tokens` / `output_tokens` | `int` | from the model response where available |
| `guardrail_triggered` | `bool` | input guard fired |
| `escalated` | `bool` | escalation path was taken |
| `retrieval_k` | `int` | passages retrieved (`0` for non-RAG agents) |
| `grounding_score` | `float \| None` | output guard score (`null` if not run) |
| `contact_support` | `bool` | the response asked the user to contact a human |

Three of these do the heavy lifting and are the ones most often missing:
**`prompt_version` + `git_commit` + `model`** are jointly the reproduction key. Without all
three, a regression cannot be attributed — a metric moved, and there is no way to tell
whether the cause was a prompt edit, a code change, or a silent model update. Note that this
also makes drift detectable: model updates are exactly the class of change invisible to CI,
which is the same gap [[Online Eval Sampling]] closes from the traffic side.

The remaining fields are **behavioural counters, not diagnostics** — `guardrail_triggered`,
`escalated`, and `contact_support` are what let you compute rates over a slice rather than
reading traces one at a time.

## ExperimentRun — top-level experiment identity

Wraps every eval invocation so runs are reproducible and diffable across ablations.

```python
@dataclass
class ExperimentRun:
    run_id: str                      # uuid4 — unique per eval invocation
    experiment_name: str             # human label, e.g. "rag-chunking-v3"
    created_at: str                  # ISO 8601 UTC
    git_commit: str                  # short SHA
    dataset: str                     # path to .jsonl eval set
    pipeline: str                    # which pipeline was under test
    rag_config: RagConfig | None = None
    bedrock_config: BedrockConfig | None = None
    notes: str = ""
```

The `dataset` field matters more than it looks: a score is only comparable against another
score computed on the *same* eval set, so the set is part of the run identity, not an
external constant. See [[Eval Suite Maintenance]].

## RagConfig — retrieval pipeline snapshot

Full configuration for a single retrieval experiment, grouped by pipeline stage:

```python
@dataclass
class RagConfig:
    # Chunking
    chunker: str = ""                # "fixed" | "semantic" | "recursive" | "hierarchical"
    chunk_size: int = 0
    chunk_overlap: int = 0
    parent_chunk_size: int = 0       # parent window (hierarchical only — 0 = flat)
    chunk_unit: str = "chars"        # "chars" | "tokens"

    # Embedding
    embedding_model: str = ""
    embedding_dim: int = 0

    # Indexing
    vector_store_backend: str = ""
    index_name: str = ""
    distance_metric: str = "cosine"
    index_created_at: str = ""

    # Retrieval
    search_strategy: str = "dense"   # "dense" | "sparse" | "hybrid"
    hybrid_alpha: float = 1.0        # 1.0 = pure dense, 0.0 = pure sparse
    retrieval_k: int = 0
    score_threshold: float = 0.0

    # Reranking
    reranker: str = ""
    reranker_top_k: int = 0
```

The stage grouping is the point. A RAG quality change can originate at any of five stages,
and the attributive fixes differ entirely — which is the same argument
[[RAG Evaluation]] makes for component gates rather than one end-to-end score. Recording the
config by stage is what lets a diff between two runs say *which stage changed*.

`index_created_at` is the easily-forgotten field: the index is a build artifact, and a
result computed against a stale index is not reproducible from the config alone.

## BedrockConfig — request tracing for a managed backend

Captures what is needed to reproduce a Bedrock call and trace it on the provider side.
`request_id` and `latency_ms` are populated *from the response*, not the request:

```python
@dataclass
class BedrockConfig:
    model_id: str = ""               # full ARN
    anthropic_version: str = ""
    aws_region: str = ""

    max_tokens: int = 0
    temperature: float = 0.0
    top_p: float | None = None
    stop_sequences: list[str] = field(default_factory=list)

    # Knowledge Base
    knowledge_base_id: str = ""
    kb_retrieval_k: int = 0
    kb_search_type: str = ""         # "SEMANTIC" | "HYBRID"
    kb_filter: dict = field(default_factory=dict)

    # Populated from response
    request_id: str = ""             # x-amzn-requestid header
    http_status: int = 0
    latency_ms: float = 0.0
```

Capturing `request_id` is what makes a local trace joinable to the provider's own logs —
the only way to attribute a latency spike to the vendor rather than to your code.

## ChunkRecord — per-chunk document metadata

Critical for hierarchical chunking experiments, where the retrieved unit and the unit handed
to the model are deliberately different:

```python
@dataclass
class ChunkRecord:
    chunk_id: str                    # deterministic hash(doc_id + start_char)
    doc_id: str
    parent_id: str = ""              # parent chunk ID (hierarchical only)
    level: int = 0                   # 0 = leaf (retrieved), 1 = parent window

    text: str = ""
    char_start: int = 0
    char_end: int = 0
    section: str = ""

    url: str = ""
    source_type: str = ""
    scraped_at: str = ""

    embedding_model: str = ""
    embedded_at: str = ""
```

Retrieval-time structure:

```
doc_123
  └─ chunk c_abc  (level=1, parent_id="")          ← parent window returned to LLM
       ├─ chunk c_def  (level=0, parent_id="c_abc")   ← retrieved by vector search
       └─ chunk c_ghi  (level=0, parent_id="c_abc")
```

**Fetch the leaf, return `parent_id`'s text as LLM context.** Small chunks embed precisely;
large chunks read coherently — the parent pointer buys both. See
[[RAG Retrieval Strategies]].

`chunk_id` being a *deterministic* hash of `doc_id + start_char` rather than a `uuid4` is
what makes chunk-level metrics comparable across re-ingests. A random ID would make every
rebuild look like a completely new corpus.

## Instrumentation asymmetry — custom pipeline vs managed KB

A managed retrieval service hides the internals you need in order to evaluate retrieval as a
component:

| Capability | Custom pipeline | Managed KB |
|---|---|---|
| `chunk_id` / `parent_id` | can implement | opaque |
| Retrieved passage text | `sources[].text` | URL only |
| Retrieval score per chunk | `scores[]` | not exposed |
| Provider `request_id` | via HTTP header | native |
| Faithfulness / context precision | available | **impossible — no text** |
| Rerank scores | implementable | not exposed |

The load-bearing row is faithfulness. **Metrics that require the retrieved text cannot be
computed against a backend that returns only URLs** — that is a property of the integration,
not a missing feature you can work around. It means adopting a managed KB is also a decision
to give up component-level retrieval evaluation.

For a fair comparison across both, use only fields both surfaces expose: **hit rate / MRR by
URL match, latency, LLM-as-judge scores on the final answer text, and cost per query.**
Anything else compares instrumentation depth rather than retrieval quality. See
[[GCP Vertex AI Search vs AWS Bedrock KB]].

## Grounding tier promotion policy

New grounding checks are not deployed as blocking. They start as **log-only diagnostics** and
are promoted to hard failures only after observation:

> Implement → observe false-positive rate in production → promote to escalation trigger only
> after confirming the false-positive rate is acceptable.

The reasoning is that a grounding check's cost is asymmetric and *falls on users*: an overly
aggressive check in a multilingual, paraphrase-heavy setting produces excessive escalations,
which is a worse failure than the ungrounded answer it was meant to catch. The log-only phase
exists to gather the evidence needed to calibrate the threshold **before** it can affect
anyone.

This is the same shape as the `experimental` → gating grader progression in
[[Eval Maturity Ladder]]: a new check must earn the authority to block. See
[[Grounding Claim Methodology]] for what the tiers themselves verify.

## See Also
- [[Eval Non-Determinism]] <!-- auto-linked -->
- [[Observability and Runtime Patterns]] — complements (what to monitor; this page is what to record for reproducibility)
- [[Grounding Claim Methodology]] — extends (adds the promotion policy governing when a tier blocks)
- [[Eval Suite Maintenance]] — depends-on (the dataset is part of run identity)
- [[RAG Evaluation]] — implements (per-stage config capture is what makes component gates diffable)
- [[RAG Retrieval Strategies]] — instance-of (hierarchical parent/leaf, as a recorded schema)
- [[Langfuse Platform]] — implements (where these fields land as trace metadata)
- [[Online Eval Sampling]] — complements (identity for the runs; sampling decides which get scored)
