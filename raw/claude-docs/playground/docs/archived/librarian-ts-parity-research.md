# Research: Librarian Production Standard — ts_google_adk Parity Analysis

Date: 2026-04-15
Context: Librarian stays as a RAG-only help-assistant service. Goal is to reach the same
engineering standard as ts_google_adk, adopting patterns that transfer cleanly without
expanding scope (no copilot, no polyglot orchestration — that's a separate thread).

---

## TL;DR

Librarian is already **more** production-ready than ts_google_adk in CI/CD, observability,
error handling, and testing. The gaps run the other direction: ts_google_adk has cleaner
patterns at the **API surface and retrieval input layer** that librarian should adopt:

1. **`queries: List[str]` as a first-class API input** — the LLM explicitly sends 2-3
   reformulations; the service runs them in parallel and merges. Librarian's multi-query
   expansion is internal (term expansion from the plan agent); the LLM can't drive it.

2. **Fingerprint-based global dedup** — ts_google_adk deduplicates across all query
   results using `url|content[:200]` as a fingerprint (keeps highest-scoring copy).
   Librarian deduplicates within ensemble retrieval via SHA256 chunk ID, but not across
   parallel query runs.

3. **Pydantic response schema enforced at the HTTP layer** — the response contract
   (`passages`, `retrieval_strategy`, `latency_ms`, `query_count`) is typed and validated
   before it leaves the service. Currently only enforced by LangGraph state shape.

---

## Side-by-side: production readiness

| Dimension | Librarian (Python) | ts_google_adk (TypeScript) | Verdict |
|---|---|---|---|
| **CI/CD** | GitHub Actions (tests → lint → deploy) | Manual Docker / aws-vault | Librarian wins |
| **Observability** | structlog + LangFuse (opt-in) | console.error only | Librarian wins |
| **Error handling** | Custom exception hierarchy (`ProcessingError → ClientError → ...`) | Inline try-catch, no types | Librarian wins |
| **Testing** | pytest unit + integration + eval suite | Custom integration runner, no coverage | Librarian wins |
| **Pre-commit / linting** | ruff + pre-commit hooks | ESLint (no CI enforcement) | Librarian wins |
| **Output schema** | LangGraph state shape (internal) | Zod schema (enforced at agent boundary) | ts_google_adk wins |
| **Multi-query API surface** | Internal term expansion (LLM can't drive it) | `queries: List[str]` — LLM controls query count | ts_google_adk wins |
| **Global dedup** | SHA256 per chunk (within ensemble) | Fingerprint across all query results | ts_google_adk wins |
| **Score threshold** | CRAG confidence gate (0.3, hardcoded) | `SCORE_THRESHOLD = 0.4` (constant, not param) | Tie — both need parameterization |
| **Latency transparency** | LangFuse traces (opt-in) | Not in response contract | Neither — add to response |

---

## Pattern 1: Multi-query API surface

**ts_google_adk implementation** (`src/agents/tools/support-knowledge.ts`):

```typescript
// Tool input schema — the LLM fills this
parameters: z.object({
  queries: z.array(z.string()).min(1).max(3)
    .describe("1-3 search queries covering different angles of the user question")
})

// Parallel execution
const resultsNested = await Promise.all(queries.map(retrieveFromKbRaw));
const allResults = resultsNested.flat();
const uniqueResults = getUniqueResults(allResults);
```

**What librarian has today:**
- `RetrievalSubgraph.run()` already handles multiple queries (from plan agent's term expansion)
- But the `/query` HTTP endpoint takes a single `query: str` — the LLM caller can't pass 2-3 queries
- The plan agent's term expansion is rule-based (synonym dict), not LLM-driven

**What to add:**
The `/query` endpoint should accept `queries: List[str]` (1-3). Each query runs through
the full LangGraph CRAG graph independently (or the retrieval subgraph directly for
latency), results are merged via global dedup, then re-ranked.

---

## Pattern 2: Fingerprint-based global dedup

**ts_google_adk implementation:**

```typescript
function getUniqueResults(results: KnowledgeBaseRetrievalResult[]) {
  // 1. Sort by score descending — keep highest-scoring copy of any duplicate
  const sorted = [...results].sort((a, b) => (b.score ?? 0) - (a.score ?? 0));

  // 2. Fingerprint = url + normalized content prefix
  const fingerprint = `${url}|${content.slice(0, 200).replace(/\s+/g, '').toLowerCase()}`;

  // 3. First-seen wins (highest score, due to pre-sort)
  if (!seenFingerprints.has(fingerprint)) {
    unique.push(res);
    seenFingerprints.add(fingerprint);
  }
}
```

**What librarian has today:**
- SHA256 chunk ID dedup inside `EnsembleRetriever` (catches same chunk from multiple retrievers)
- CRAG grader deduplicates by chunk ID within a single query's results
- No cross-query dedup — if query 1 and query 2 both retrieve chunk X, it appears twice

**What to add:**
After merging results from N parallel queries, apply fingerprint dedup at the service layer
before returning. Keep chunk ID as the primary key (more precise than content prefix),
fall back to content fingerprint for chunks that lack stable IDs.

Python equivalent:

```python
def dedup_global(passages: list[Passage]) -> list[Passage]:
    passages.sort(key=lambda p: p.score, reverse=True)
    seen: set[str] = set()
    unique: list[Passage] = []
    for p in passages:
        # Prefer chunk_id if available (stable); fallback to content fingerprint
        key = p.chunk_id or f"{p.url}|{p.text[:200].lower().replace(' ', '')}"
        if key not in seen:
            unique.append(p)
            seen.add(key)
    return unique
```

---

## Pattern 3: Pydantic response schema at the HTTP layer

**ts_google_adk approach:** Zod schema on the agent's output forces the LLM to return a
typed JSON blob. For a standalone HTTP service like librarian, the equivalent is a Pydantic
response model on the FastAPI endpoint.

**Current state:** The `/query` endpoint returns whatever the LangGraph state contains.
The contract is implicit.

**Target state:**

```python
class Passage(BaseModel):
    text: str
    url: str | None
    title: str | None
    score: float

class QueryResponse(BaseModel):
    passages: list[Passage]
    retrieval_strategy: str          # "crag" | "snippet" | "bedrock"
    query_count: int
    latency_ms: int
```

This makes the contract explicit, validates it at runtime, and auto-generates OpenAPI docs.
It also makes the ts_google_adk tool's type alignment trivial — the `Passage` type in TS
mirrors this Python model exactly.

---

## Engineering standard items (shared conventions)

These are conventions ts_google_adk follows that librarian should match for ease of read:

| Item | ts_google_adk | Librarian to-do |
|---|---|---|
| Score threshold | `SCORE_THRESHOLD = 0.4` constant | Move from CRAG gate into `QueryRequest` param (default 0.3, overridable) |
| Per-query result count | `numberOfResults: 5` in config | Expose as `top_k_per_query: int` in `QueryRequest` |
| Strategy in response | Not in response | Add `retrieval_strategy` to `QueryResponse` |
| Latency in response | Not in response | Add `latency_ms` to `QueryResponse` for debugging |
| Hybrid search type | `overrideSearchType: 'HYBRID'` explicit | Already default; expose as `search_mode: str` param |

---

## What NOT to port

| ts_google_adk pattern | Reason to skip |
|---|---|
| Next.js / React UI | Librarian is API-only |
| MikroORM session persistence | Librarian is stateless — sessions are the copilot's concern |
| Zod agent output schema | FastAPI Pydantic models are the Python equivalent — already planned |
| Google ADK `LlmAgent` | Librarian uses LangGraph CRAG — better fit for retrieval pipelines |
| Inline console.error error handling | Librarian's exception hierarchy is superior — keep it |

---

## Existing librarian docs that feed this work

| Doc | What it covers | Still current? |
|---|---|---|
| `reference/librarian-stack-audit.md` | All 5 agent internals in detail | Yes — comprehensive |
| `scope/librarian-architecture/research-bedrock-kb.md` | Bedrock KB vs LangGraph quality comparison | Yes |
| `scope/librarian-architecture/research-adk-orchestration.md` | LangGraph vs ADK mental models | Yes |
| `build/librarian-architecture/plan.md` | 3-option architecture tradeoffs | Yes — `/query` endpoint design is in here |
| `archive/librarian-prod-hardening/plan.md` | P0/P1/P2 hardening tasks | Archived — P0 items done |
| `reference/rag-tradeoffs.md` | Component decision log (chunker, embedder, retriever, reranker) | Yes |

**Gap confirmed:** None of the above docs address the specific ts_google_adk pattern
comparison or the production standard parity upgrade. This research fills that gap.
