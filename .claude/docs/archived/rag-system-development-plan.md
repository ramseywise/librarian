# RAG system development plan

**Last updated:** April 15, 2026  
**Purpose:** Single place for implementation sequencing, team alignment, and traceability to product/engineering commitments.  
**Audience:** Engineers implementing the stack; PM/design for scope checks.

---

## Alignment: team summary (April 15, 2026) — coverage checklist

This document **includes** all items from the team’s summarized plan. See [Traceability](#traceability-team-summary--sections) at the end for section mapping.

| Theme | Items (from summary) | Covered here |
|-------|----------------------|--------------|
| **MVP** | Deploy Bedrock Knowledge Base with Billy Web content ingestion | [§3.1](#31-mvp--bedrock-knowledge-base--billy-web), [§4 Phase B](#phase-b--ingestion--index) |
| **MVP** | Out-of-the-box retrieval with re-ranking | [§3.2](#32-retrieval--re-ranking), [§4 Phase C](#phase-c--retrieval--quality--observability) |
| **MVP** | Danish market support articles as primary source | [§3.3](#33-market--language-mvp), [§4 Phase B](#phase-b--ingestion--index) |
| **QA** | Random sampling queue for human validation / annotation | [§5.1](#51-human-in-the-loop--sampling-queue) |
| **QA** | Edge case detection (low confidence, escalations) | [§5.2](#52-edge-case--low-confidence--escalation-detection) |
| **QA** | LLM-as-Judge evaluation + DataDog dashboard | [§5.3](#53-llm-as-judge--datadog) |
| **Infra** | Coding standards, PR processes, deployment pipelines | [§6.1](#61-engineering-hygiene) |
| **Infra** | AWS access + GitHub for full team | [§6.2](#62-access--repositories) |
| **Infra** | Monitoring: query logging, performance, content gaps | [§6.3](#63-observability--content-gap-signals) |
| **Future** | Historic Intercom → draft articles | [§7.1](#71-intercom--knowledge-expansion) |
| **Future** | GDPR / PII masking layer | [§7.2](#72-gdpr--pii-masking) |
| **Future** | Multi-language + alternative RAG architectures | [§7.3](#73-multi-language--alternative-rag) |

---

## Implementation review (read before coding)

This section is a **pre-implementation** review: what is strong, what to lock, and what risks to mitigate early.

**Orchestration refactor (score policy, context builder, v1 vs v2 graph scope):** see [`rag-architecture-refactoring-plan.md`](./rag-architecture-refactoring-plan.md).

### Strengths of the current direction

- **Bedrock KB + Billy Web** is a clear ingestion anchor: managed chunking/retrieval options, AWS-native path, and one primary crawl source reduce early integration surface area.
- **Re-ranking after retrieval** matches production RAG patterns; pairing it with **confidence thresholds** supports both quality and “edge case” routing.
- **Human sampling + LLM-as-judge** is a sensible split: humans for trust and labels; automation for scale and regression detection.
- **DataDog** for dashboards fits ops maturity if the org already standardizes on it; align **metric names and dimensions** early (see §6.3).

### Gaps to close in design (before large implementation spend)

1. **API contract** — Request/response shapes for `market`, `locale`, `citations[]`, and outcomes (`answer` | `clarify` | `escalate`) should be fixed **before** the Help Center FE hard-codes assumptions.
2. **“Billy Web” scope** — Define which properties (URLs, locales, article types) are in MVP and how **Danish-only** sources interact with **DK EN UI** users (filter vs. translate is a product decision).
3. **Bedrock KB configuration** — Data source sync, embedding model, and **metadata filtering** (market/language) must be specified so retrieval matches regulatory expectations.
4. **Evaluation ownership** — Who maintains the **benchmark set**, **sampling rate**, and **LLM-judge prompts** when models change?
5. **PII / logging** — Even before a full masking layer, **default** log redaction policy avoids shipping sensitive payloads to DataDog or LangSmith.

### Sequencing recommendation

1. **Contract + observability schema** (what you log and what the FE sends).  
2. **Ingestion + KB** (Billy Web → Bedrock KB, Danish MVP).  
3. **Retrieval + rerank + confidence** wired in app.  
4. **API + streaming** for Help Center.  
5. **QA loop** (sampling queue, judges, dashboards) in parallel once events exist.  
6. **Future** items explicitly **not** in MVP scope unless resourced.

---

## Implementation status (this repository)

The following is **in place in the POC codebase** as of the **retriever_agent** line of work (see [`app/changelog.md`](../../../app/changelog.md) and the repo `README`). It supports local experimentation and aligns with Phase C’s *shape* (retrieve → rerank → policy → answer) but does **not** by itself satisfy production MVP commitments (Bedrock KB, Danish corpus, API contract, etc.).

| Theme | In repo today | Still roadmap / product |
|-------|----------------|-------------------------|
| **Orchestration** | LangGraph under `app/graph/` (`graph.py`, `routing.py`, `policy.py`, `state.py`, `runner.py`; nodes in `app/graph/nodes/`) | HTTP API, streaming, Help Center contract (Phase D) |
| **Retrieval** | `Embedder` / `Retriever` protocols; **ensemble** retriever (parallel queries, dedupe, **RRF**, score filtering); **snippet/keyword** path; **retrieval cache**; tool wrapper with Pydantic schemas | Bedrock Knowledge Base **Retrieve** as the managed baseline in prod (Phase B–C) |
| **Reranking** | `Reranker` protocol; **cross-encoder**, **LLM listwise**, **passthrough** | Standardize one reranker + thresholds for production; vendor choice (Cohere, etc.) if required |
| **Ingestion / index** | Preprocessing pipeline under `app/rag/preprocessing/` (chunking, parsing, indexing wiring; **Raptor-style** hierarchical / clustering pieces as implemented) | Billy Web → Bedrock KB sync, DK metadata filters (Phase B) |
| **Observability** | Env + logger configuration before heavy imports; embedding client noise suppression (HF/tqdm) | Structured production metrics, DataDog dashboards (§6.3, Phase C exit) |
| **Tooling** | `pyproject.toml` + `uv.lock`; **Makefile**; **pre-commit**; tests for retrieval/reranking paths | CI/CD and deployment (§6.1) |

**Traceability:** This section refines [Phase C](#phase-c--retrieval--quality--observability) and [Phase D](#phase-d--orchestration--api) — app-side retriever/rerank **patterns** exist; **managed KB + API + QA loop** remain plan-driven.

---

## Product-facing requirements (concise)

For full product context (Help Center, Copilot compatibility, conversational behavior), keep the **knowledge retrieval capability** product doc as source of truth. This plan **implements** that doc’s engineering slice and the **team summary** above; it does not replace legal/compliance sign-off for GDPR.

---

## Detailed scope

### 3.1 MVP — Bedrock Knowledge Base + Billy Web

- Provision **Amazon Bedrock Knowledge Base** with data source(s) fed by **Billy Web** crawl/export (exact mechanism: crawl pipeline vs. CMS export — confirm with whoever owns Billy Web).
- Automate **sync** on content changes where possible; document manual refresh if needed for MVP.
- Track **document/version identifiers** in retrieval results for citations and gap analysis.

### 3.2 Retrieval + re-ranking

- Use Bedrock **Retrieve** (or equivalent) as baseline retrieval.
- Add **re-ranking** (cross-encoder, Cohere, or LLM-listwise — pick one and standardize) on the candidate set.
- Expose **scores** internally for confidence and dashboards; map to **user-visible** behavior via policy (answer vs. clarify vs. escalate).

### 3.3 Market + language (MVP)

- **Primary data:** Danish market **support articles** (and agreed Billy Web surfaces).
- **Runtime context:** `market` (e.g. `DK`) + **UI language** (`da` / `en`) on each request; retrieval filters must **not** return wrong-jurisdiction guidance.
- **Future:** multi-market and broader language expansion is **out of MVP** unless explicitly pulled in (see §7.3).

---

## Phase B — Ingestion & index

| Step | Action |
|------|--------|
| B1 | Define Billy Web → staging format (HTML/markdown, URLs, locale tags). |
| B2 | Configure Bedrock KB data source + sync; validate chunk boundaries in spot checks. |
| B3 | Attach or derive **metadata**: `market`, `language`, `source`, `url`, `title`, `updated_at`, optional `product_area`. |
| B4 | Danish MVP: restrict or tag corpus so **filters** enforce DK + language rules at query time. |

**Exit:** Filtered retrieval returns only eligible chunks for a DK + `da`/`en` request profile.

---

## Phase C — Retrieval, quality & observability

| Step | Action |
|------|--------|
| C1 | Implement app-side **Retriever** wrapping Bedrock KB + **reranker**; populate structured `citations` and scores. **POC:** protocol-based ensemble retrieval, RRF, cache, and rerankers exist under `app/rag/` and are wired through orchestration; swap/embed Bedrock KB per Phase B when connecting to AWS. |
| C2 | Define **confidence policy** (thresholds + fallback to clarify/escalate). |
| C3 | Emit **structured logs** / metrics: `request_id`, latency (incl. TTFT if streaming), `chunk_ids`, scores, outcome. |

**Exit:** Every answer path can explain **which sources** were used; low-confidence paths are **detectable** (feeds QA and DataDog).

**Note:** The repository already demonstrates **C1-style** wiring (retrieve → rerank → graph); **C2–C3** and Bedrock-backed retrieval remain the gating items for MVP exit criteria.

---

## Phase D — Orchestration & API

| Step | Action |
|------|--------|
| D1 | LangGraph (or equivalent): planner → (optional Q&A clarify) → retrieve → policy → answer **or** structured clarify/escalate. **POC:** graph and CLI under `app/graph/` (`support-rag` / `make app-run`). |
| D2 | **HTTP API** for Help Center: streaming responses, thread/session id, error contract. |
| D3 | Feature-flag or separate deploy **task-execution** POC if it remains in repo — avoid conflating with Help Center MVP. |

**Exit:** FE can integrate without CLI; TTFT measurable against the &lt;2s product target.

---

## Phase E — Quality assurance (team summary)

### 5.1 Human-in-the-loop — sampling queue

- **Random sample** (configurable rate) of production or staging conversations for review.
- **Annotation UI** or export to spreadsheet/tooling: correct/incorrect, missing doc, wrong market, should escalate.
- Feedback **closes the loop** into benchmark sets and doc updates (owner TBD).

### 5.2 Edge case — low confidence & escalation detection

- **Rules:** confidence &lt; threshold, empty retrieval, policy `escalate`, user triggers “contact support.”
- **Actions:** tag conversation, optional **automatic** ticket draft (future); MVP = **visibility** in dashboards and sampling priority.

### 5.3 LLM-as-Judge + DataDog

- **Offline/batch:** LLM scores alignment with citations and helpfulness on benchmark + sampled sets.
- **Online:** DataDog metrics — e.g. latency percentiles, retrieval empty rate, escalation rate, judge scores if run async.
- **Dashboards:** one “quality” view (judge + human rates) and one “ops” view (latency, errors, volume).

---

## Phase F — Infrastructure & engineering

### 6.1 Engineering hygiene

- **Coding standards:** formatter/linter/typecheck in CI (match repo stack).
- **PR process:** required review, conventional or scoped commits as team prefers.
- **Deployment:** pipeline from main branch to **staging** then **prod**; secrets via AWS/GitHub OIDC or org standard.

### 6.2 Access & repositories

- **AWS:** IAM roles for Bedrock KB, logging, deployment; least privilege.
- **GitHub:** team access to app repo, infra as code, and (if separate) content pipeline repo.

### 6.3 Observability & content-gap signals

- **Query logging:** structured fields (see Phase C); **PII minimization** by default.
- **Performance:** p50/p95 latency, TTFT, KB sync lag.
- **Content gaps:** frequent no-result queries, high escalation topics — feed backlog for docs.

---

## Future enhancements (explicitly post-MVP unless reprioritized)

### 7.1 Intercom — knowledge expansion

- Pipeline from **historic Intercom** conversations to **draft articles** (human review before publish); **not** raw retrieval from chats without governance.

### 7.2 GDPR — PII masking

- Layer for **detecting/masking** PII in logs, training exports, and optional user content before persistence; legal review for retention.

### 7.3 Multi-language & alternative RAG architectures

- Additional markets/languages with same **metadata contract**.
- Evaluate **alternate architectures** (e.g. different chunking, graph RAG) against the **same** benchmark suite.

---

## Traceability: team summary → sections

| Summary bullet | Primary section |
|----------------|-----------------|
| Bedrock KB + Billy Web ingestion | [§3.1](#31-mvp--bedrock-knowledge-base--billy-web), [Phase B](#phase-b--ingestion--index) |
| Retrieval + re-ranking | [§3.2](#32-retrieval--re-ranking), [Phase C](#phase-c--retrieval--quality--observability), [Implementation status](#implementation-status-this-repository) |
| Danish market articles | [§3.3](#33-market--language-mvp), [Phase B](#phase-b--ingestion--index) |
| Random sampling + human annotation | [§5.1](#51-human-in-the-loop--sampling-queue) |
| Edge cases / low confidence / escalation | [§5.2](#52-edge-case--low-confidence--escalation-detection) |
| LLM-as-Judge + DataDog | [§5.3](#53-llm-as-judge--datadog) |
| Standards, PRs, deployment | [§6.1](#61-engineering-hygiene) |
| AWS + GitHub access | [§6.2](#62-access--repositories) |
| Query logging, performance, content gaps | [§6.3](#63-observability--content-gap-signals) |
| Intercom → drafts | [§7.1](#71-intercom--knowledge-expansion) |
| GDPR / PII masking | [§7.2](#72-gdpr--pii-masking) |
| Multi-language / alt RAG | [§7.3](#73-multi-language--alternative-rag) |

---

## Disclaimer

AI-generated summaries and plans can be wrong or incomplete. Treat this file as a **living** plan: update dates, owners, and decisions as they land. Product and compliance requirements remain authoritative where they conflict with engineering drafts.


If you want to go further later (optional)
Split experiment.py into modules (upload.py, run.py, langfuse_helpers.py, …) — same behavior, easier navigation (bigger refactor).
Add a make eval-help that prints the three commands + link to evals/README.md.
If you want the split of experiment.py, say so and we can do it in a focused pass.