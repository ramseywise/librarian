---
title: Coding Challenge Interview Study Guide
tags: [interview, reference]
summary: "Method guide for the live coding round as AIE/MLE loops now run it — project-style and AI-engineering practicals in a no-network stdlib-only browser editor, the trap-shaped prompts graded on the critique rather than the code, a cold pattern set with a 25-minute self-test, the security minimums that come up even outside an auth question, plus three newer formats: multi-level implementation rounds, NumPy-from-scratch ML coding, and debug-then-design over an unfamiliar retrieval stack."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--README.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--code-from-heart.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--code-from-heart.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--examples--README.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--examples--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--examples--auth-api-endpoint.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--examples--auth-api-endpoint.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--study-guide.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--study-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--questions.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--questions.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--sources.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--sources.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--examples--debugging-dedup.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--examples--debugging-dedup.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--examples--lru-cache.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--examples--lru-cache.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--examples--retry-decorator.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--examples--retry-decorator.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--examples--rag-pipeline-offline.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--examples--rag-pipeline-offline.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--examples--sqlite-pipeline-scaling.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--examples--sqlite-pipeline-scaling.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--examples--transaction-aggregation.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--examples--transaction-aggregation.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--coding-challenge--examples--workflow-orchestration.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--examples--workflow-orchestration.md
  - data/raw/repos/sisyphus/interviewing--rounds--coding-challenge--examples--property-search.md
---

# Coding Challenge Interview Study Guide

Present in every loop, rarely the differentiator. The 2026 shift is from algorithm recall
to **observable problem-solving process**: narrate the plan first, name complexity as you
go, never code silently, clarify inputs/edge cases/scale before typing. For the DSA pattern
checklist and SQL idioms see [[Programming Interview Study Guide]].

| Format | Duration | Graded on |
|---|---|---|
| Live coding (often project-style: "implement a rate limiter") | 45–60 min | correct + clean structure + narration |
| Debugging | 30–45 min | reproduce → bisect → root cause → fix → prevent |
| Pair programming | 45–60 min | hint integration, communication |
| AI-assisted | 30–45 min | prompt decomposition, output verification, knowing when not to trust |
| Multi-level implementation | 45–90 min | whether the level-1 design absorbs later levels without a rewrite — [[Multi-Level Implementation Round]] |
| ML coding (NumPy from scratch) | 30–45 min | implementing the maths, not the library call; shapes and numerical stability |

DS versions skew SQL/pandas; FDE versions skew practical scripting under time pressure.

## The AIE practical variant

For AIE/MLE loops the live round is increasingly an **AI-engineering practical** — build a
retrieval pipeline, orchestrate a multi-step workflow, validate structured model output.
Browser assessments usually mean **no network, no `pip install`, no AI assistant**, so the
drill must run on the standard library alone (no numpy, pandas, pydantic, or API calls).
That changes what "prepared" means: not breadth, but a small pattern set your fingers
produce without thinking, so the timebox goes to the problem. (The take-home 1h code test
assumes network and an API key instead — see [[AIE Code-Test Flaw Taxonomy]].)

**Trap-shaped prompts** hand you a tool correct for the exercise and wrong for the stated
scale; the grade is in the critique. A SQLite pipeline followed by "this serves millions of
requests a day" wants the single-writer lock named and OLTP split from OLAP. An auth prompt
wants constant-time comparison and algorithm pinning, not just a working token. **Build
correctly, then critique.**

## The cold pattern set

Aggregation (sum/collect/count per key, nested grouping); multi-key sort with opposite
directions (negate the numeric key); comprehensions; dict/set idioms; a validated
`@dataclass`; exceptions with typed fallbacks; length-normalized lexical retrieval scoring;
`csv.DictReader` over `.split(",")` (the split breaks on the first quoted comma).

Habits that read as production experience:
- Money as `Decimal` or integer cents; time as aware UTC, converted at the display edge.
- **MAD over standard deviation** for anomaly detection — one large outlier inflates σ
  enough to hide itself. Median over mean when outliers exist.
- Concurrency: "the GIL lets one thread execute bytecode at a time, but blocking I/O
  releases it" — threads/asyncio for I/O-bound, processes for CPU-bound.
- HTTP: 401 = we don't know who you are, 403 = we know and you're not allowed; 404 can hide a
  403 from probing; 422 = well-formed but invalid content; 503 retryable, 500 usually not.
- Retries need exponential backoff **with jitter** (otherwise clients retry in lockstep), only
  on idempotent operations; timeouts bound one call, a circuit breaker bounds the pattern.
  Offset pagination drifts under inserts; keyset/cursor pagination is stable.

Deprioritize DP, advanced graphs, balanced trees, bit tricks — clean readable code beats a
clever one-liner on these prompts.

**25-minute self-test** (no reference): group transactions by user and day summing
`Decimal`, sorted by total desc then name asc; a dataclass with a validated enum field and
list default; parse possibly-malformed JSON to a typed fallback; rank documents by
normalized lexical overlap; sign with HMAC-SHA256 and verify in constant time.

## Security minimums

- Parameterized SQL always — never an f-string.
- `hmac.compare_digest`, never `==`, for any secret — equality short-circuits and leaks by timing.
- Slow hash + per-user salt for passwords (PBKDF2/bcrypt/scrypt/Argon2), never plain SHA-256.
- **Verify the signature before parsing any claim**, and pin the algorithm (`alg=none`, alg confusion).
- Never log secrets or PII — logs ship to systems with wider access than the database.
- Authentication ≠ authorization: object ownership (IDOR) is a separate check.

The auth worked example's graded signals: threat model first (stateless tokens scale but
can't be revoked before expiry, session ids can — hence a short TTL plus refresh token and a
`jti` for a denylist); saying "in production this is a vetted library — hand-rolled crypto
fails silently" unprompted; one opaque error message for every failure path (returning
"token expired" tells an attacker the signature was valid); rate-limiting login because a
deliberately slow hash makes it a DoS target.

## Debug-then-design over a retrieval stack

A 60-minute format: an unfamiliar FastAPI + FAISS + sentence-transformers semantic search
that runs, returns results and throws nothing, with two seeded ranking bugs, followed by a
feature-design discussion. The interviewer's rubric weights the two bugs at 30% and 25%,
design at 30%, communication at 15%.

- **Count before reading code.** Run the documented query and compare the result count
  with `max_results`; read the scores, not just the names. One bug was a `[1:]` slice on
  the FAISS results — FAISS already returns best-first, so *any* slice of its output is
  suspect, and this one silently dropped the best match.
- **Work the formula by hand for a concrete input.** A "boost cheaper listings" factor
  written as `1 − (discount × k)` goes negative for cheap items and *penalizes* exactly what
  the docstring says it boosts. Compute it for a cheap and an expensive price, check the sign
  against the docstring, fix the sign (not a clamp), and state the regression test.
- **Design half: keep hard constraints out of the embedding.** Size and price are
  structured filters (pre-filter, post-filter, or an index with metadata filtering), and
  "at least 2000" vs "around 2000" is an intent-parsing question (`>=` vs a ±10% range).
  For natural-language feature matching, compare NLP extraction (fast, free, deterministic,
  debuggable; brittle to paraphrase and prone to false positives — "pool table" matching a
  swimming pool, a verb "view" matching "city view") with LLM extraction (handles paraphrase;
  latency, per-query cost, non-determinism, data leaving the boundary, needs a fallback).
  The top-scored answer is a hybrid: LLM extraction into a fixed feature vocabulary, cached,
  temperature 0 with structured output, and a deterministic fallback.
- Pitfalls the rubric names: blaming the embedding model, stopping after one bug, "just use
  an LLM" with no latency/cost/failure mode, putting numeric filters into the embedding text.

## ML coding from scratch (NumPy)

Implement the maths, not the library call; NumPy is usually allowed, sklearn and torch
usually not — ask. Browser editors often preinstall NumPy, but check. The reported set and
what each one actually grades:

| Problem | Graded on | Pitfall |
|---|---|---|
| Stable softmax | subtract the row max (shift invariance makes it free); `axis=-1, keepdims=True`; mention log-softmax for cross-entropy | naive formula overflows on a logit of 1000; wrong axis on a batch |
| Pairwise cosine | normalize rows once with an epsilon guard, then `A_n @ B_n.T`; ask about top-k (`argpartition`, ANN) instead of the full matrix | Python loop over pairs; divide-by-zero |
| Debug an embeddings matcher | assert shapes at each boundary (`(1, d)` query vs `(N, d)` docs); normalize both sides; one matmul + `argmax` | fixing the shape bug but leaving raw dot product (magnitude bias) or the per-query loop; ask if query and index used the same model |
| Logistic regression + SGD + L2 + early stopping | derive the BCE gradient `p − y`; shuffle per epoch; regularize weights not bias; restore best weights, not last | full-batch GD called "SGD"; early stopping on training loss; `exp` overflow |
| K-means | vectorized (n, k) distance matrix, `argmin`, stop when assignments stop changing; reseed empty clusters; k-means++ and restarts | NaN centroid from an empty cluster; fixed-iteration stop only |
| Self-attention forward | shapes at every step ((L, d) → (L, L) → (L, d_v)); √d_k scaling prevents softmax saturation; causal mask to −inf *before* softmax; multi-head splits d_model | column-wise softmax; masking after softmax; O(L²) unnamed |

## The debugging loop and narration

1. **Reproduce first** with a minimal input you control — can't reproduce, don't understand it yet.
2. **Read the error honestly** — what the traceback says, not what you expect.
3. **Bisect**, don't read top-to-bottom: assert state at the midpoint, recurse up or downstream.
4. **Fix the root cause**, not the symptom — find where data first goes wrong.
5. **State regression prevention** — the invariant assertion or property test you'd add.

"Quit thinking and look": check a hypothesis the moment you have it. The canonical worked
bug is a dedup function with `seen=set()` as a default argument — correct on the first
call, empty on the second, because the default is evaluated once at definition time; the
test that catches it is "call twice with the same input, assert equal results".
Narrate *decisions*, not keystrokes; trace a small example aloud before declaring done;
never more than ~30 seconds silent ("let me write the simpler version first").

## Tests-first and AI-assisted verification

For "implement X" prompts: interface → happy-path test → edge tests (empty, single, max,
error path) → implement. Prefer **one test per distinct failure path** over many happy-path
tests — the offline RAG example ships five: ranking, empty retrieval, malformed JSON,
hallucinated citation, schema violation. When the property is "X was never called" (a cost
or safety guarantee), assert it with a spy; the return value cannot show it.

AI-assisted variants: decompose into 3–5 subtasks, one ask per prompt; read output before
running, trace it with a known input, run a test written *before* seeing the output. Distrust
it on off-by-one boundaries, concurrency, error paths, and domain specifics (timezones,
precision). The grader watches whether you caught what it got wrong; one giant prompt reads
as inability to decompose.

## More judgment moves from the worked practicals

- **Name the mechanism, then split the workload** on the scaling follow-up: both "SQLite
  doesn't scale, use Postgres" and "SQLite is fast, it's fine" fail. SQLite holds for reads
  and breaks on writes — a locked file, not a server, one writer even in WAL mode, and no
  network access for stateless replicas. Transactional ingest/serve → Postgres (MVCC);
  heavy aggregation → a columnar warehouse so reporting scans never contend with user
  writes. Don't over-correct: SQLite is right for single-writer, embedded, read-mostly, and
  test-fixture workloads. Verify index claims with `EXPLAIN QUERY PLAN` instead of asserting.
- **Put the swap seam behind an interface early** (a small store class, an isolated
  `score()` function) and say so — a later migration touches one class.
- **Separate DECLINED from FAILED** in a workflow runner: "retrieved nothing, so not
  guessing" is the system working and must not page anyone; "the classifier threw" is a
  failure. A top-level `except Exception` is acceptable only at a boundary whose job is to
  convert any failure into a status, logging the traceback and the failing step.
- **Workflow before agent**: a fixed step sequence (classify → retrieve → validate →
  generate) is a deterministic workflow; it earns an agent loop only when the step sequence
  stops being knowable in advance. Retry individual network-bound steps on transient errors
  only — re-running classify because generate failed wastes a call and can change the category.
- **Short-circuit before the model call**: empty or weak retrieval → skip generation; there
  is nothing to ground on, so the call buys a guess.
- **Grounding check on citations**: well-formed JSON can cite a document id that was never
  in context — the failure that survives every syntactic check. Validate cited ids against
  the retrieved set; treat malformed output as expected control flow (log and fall back),
  never `except: pass`.
- **Return the rejection count with aggregates** — if 40% of records failed to parse the
  totals are meaningless, and the caller must be able to know. Guard `mad == 0` and a
  minimum history length in anomaly rules.
- **Idempotent ingest**: natural key as primary key + `INSERT OR IGNORE` / `ON CONFLICT DO
  NOTHING`; batch inserts in one transaction (per-row commits pay an fsync each).

## See Also
- [[Programming Interview Study Guide]] — extends (DSA and SQL pattern half of the coding screen)
- [[Multi-Level Implementation Round]] — extends (staged-build format)
- [[ML Foundations Interview Study Guide]] — prerequisite-for (the maths behind the NumPy problems)
- [[AIE Code-Test Flaw Taxonomy]] — alternative-to (the networked take-home version)
- [[Graded Rehearsal Drill Harness]] — prerequisite-for (the coding-drill skill that rehearses these)
- [[Code Review Interview Study Guide]] — extends
- [[AI Role Interview Loop Map]] — extends
- [[Timebox-Scaled Deliverable Bar]] — alternative-to (async take-home bar vs the live-round bar)
- [[Agent Retry Taxonomy]] — extends (retry only transient errors, per step)
