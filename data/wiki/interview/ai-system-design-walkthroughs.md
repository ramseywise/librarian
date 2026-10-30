---
title: AI System Design Walkthroughs
tags: [interview, llm, reference]
summary: "Nine phase-by-phase AI system design problems (RAG at 10M docs, live-web LLM search, chat at scale, inline coding copilot, moderation, 1M-queries/day cost, document extraction, fraud scoring, agentic workflow) reduced to a shared five-phase board layout and the one non-obvious call each problem exists to teach."
updated: 2026-10-30
sources:
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--README.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--template.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--rag-10m.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--perplexity-search.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--chatgpt-chatbot.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--coding-copilot.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--content-moderation.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--cost-optimization-1m.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--document-processing.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--fraud-detection.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--agentic-workflow.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--README.md
---

# AI System Design Walkthroughs

A set of third-party practice problems, each split into the prompts an interviewer asks
in order, with a reference answer for each. The drill is to answer each prompt out loud
before reading the reference. They complement the self-built examples in
[[System Design Interview Study Guide]] (systems you actually shipped) with the canonical
public prompts, and they are the topic pool for mock rounds run with
[[AI System Design Interviewer Rubric]].

## The board layout every walkthrough follows

| Phase | Time | What goes on the board |
|---|---|---|
| 1. Frame | 5–10 min | users and "good answer"; scale (corpus, QPS, growth, freshness); quality bar, p95, cost per query; guardrails and what the system must *not* do; assumptions confirmed |
| 2. High level | 10–15 min | the **offline ingest/index path** and the **online query path** drawn separately, then the cross-cutting layers (gateway/auth, model router, cache, input and output guardrails, observability) narrated as a request's journey, not a parts list |
| 3. Deep dive | 20–30 min | chunking and embeddings, hybrid retrieval and index choice, reranking, grounding and citations, eval, guardrails, serving |
| 4. Trade-offs and failure | 10–15 min | recall vs latency vs cost; caching; model tiering; freshness vs cost; failure modes |
| 5. Conclude | last minute | summary, biggest risks, what you would measure and improve first |

Every walkthrough's last prompt is the same: *what breaks, how do you detect it, how does
it degrade?* The answer that scores is a triple per failure mode: name it, give the
**detection signal** (index-update lag, truncation rate, override rate, queue depth), and
give the **degradation path** (abstain, smaller model, shorter context, defer to async
review). Naming a failure without a detection signal is the common miss.

## The lesson each problem teaches

| Problem | The transferable call |
|---|---|
| Document Q&A over 10M articles | Brute-force search can't meet a few-second p95 at tens of millions of chunks. Use HNSW while the index fits in RAM and IVF/IVF-PQ once it doesn't. Retrieve 50–100 candidates for recall, then rerank to 3–8 so few tokens reach the model ([[RAG Reranking]]). Enforce the user's ACLs at query time, and abstain on empty retrieval rather than generate |
| Real-time LLM search over the live web | Unlike closed-corpus RAG, the hard part is a **continuously updated index**: one engine holds text for BM25, vectors and metadata (domain authority, last-seen time), takes tens of thousands of updates per second, and lets freshness feed ranking. The grounding contract ("say nothing you did not retrieve") is what makes it a search engine and not a chatbot. Time-sensitive queries must bypass the cache |
| Chat assistant at consumer scale | Cut scope to one slice, such as serving plus memory. The model call is stateless and history lives outside it. When history overflows, keep recent turns verbatim and replace older turns with a rolling summary. Cross-conversation memory has two mechanisms, explicit saved facts and background-synthesized facts, and it must **update and forget** ("going to X in July" becomes "went to X"), with user controls to view, delete and disable. TTFT governs perceived speed and TPS the typing feel |
| Inline coding copilot | A latency problem, not a quality problem: sub-second ghost text decides the design. Use a fill-in-the-middle prompt (prefix plus suffix) with snippets from neighbouring open tabs, inside a context budget of a few thousand characters. The main cost lever is deciding whether to call the model at all ([[Completion Trigger Gate]]). Use a purpose-built FIM model, because chat models misalign inserts, and cancel in-flight requests when the user keeps typing. The north-star metric is characters retained, not just acceptance. Chat and agent mode is a different backend behind the same product |
| Content moderation | A cheap-to-expensive cascade. Fast multimodal, multilingual classifiers score every item per category. A decision layer uses per-category, per-surface thresholds ([[Three-Band Confidence Routing]]). Uncertain items go to a stronger model, the hardest ones and appeals go to humans, and every human verdict becomes a training label. Systems under-moderate coded hate and over-moderate counter-speech and reclaimed terms, so monitor error rates per group. Under latency spikes, let borderline content through to async review rather than block publishing |
| Cost at 1M queries/day | Measure first: attribute tokens per model, feature and query type through the gateway. Usual lever order is prefix caching ([[Prefix Caching]]; a 1k-token system prompt over 1M calls is ~1B repeated input tokens a day), then model routing, then token trimming and output caps, then a batch API for latency-tolerant work. Self-hosting pays off only at high, steady GPU utilization. Pair every lever with its quality guardrail ([[Semantic Cache for RAG Agents]] false matches, cheap-tier regressions, truncated answers) |
| Document extraction (payslips, IDs) | Event-driven stages: classify, OCR, schema extraction, validation, routing. Queues between stages absorb upload spikes and the OCR provider's quota limits. Per-field confidence combines with OCR confidence and business-rule checks to choose auto-accept or human review. Bounded retries (about three) end in human review, and unknown document types go to a human first. The reviewer override rate shows whether thresholds are calibrated. Idempotency on the tracking ID prevents double-processing |
| Fraud scoring with a GenAI role | Mostly classical ML. The core is sub-100ms scoring on tabular features, with cross-merchant velocity aggregates as the moat and gradient-boosted trees as the interpretable default. Add graph signals for coordinated rings. The block threshold is a **business** decision, and step-up auth gives a middle band. Labels (chargebacks) arrive weeks late, so monitor input drift as the early signal. The LLM's role is analyst-side: explaining alerts, reasoning over documents, assembling investigations. It is never the sole decider |
| Multi-step agentic workflow | The senior opening is to ask whether it needs an agent at all, since a fixed workflow is cheaper and more reliable when the steps are predictable. If it does, use orchestrator-workers with control flow **in code, not prompts**, least-privilege tools that inherit the user's permissions, a human gate on irreversible writes, and step caps. Reconcile partial progress with idempotency keys (invite sent but calendar write failed). Score task completion and step count rather than per-turn quality. Agents cost several times the tokens of chat, and multi-agent setups cost more again |

## Recurring patterns across the set

- **Two-stage retrieval**: cheap, recall-oriented retrieval followed by expensive precision ranking. It appears in RAG, search and moderation.
- **Gateway as the control point**: routing, provider fallback, PII redaction and per-request cost attribution all sit in one place. Note [[Model Gateway Is Transport, Call Site Owns Meaning]]: the gateway records cost, but the call site decides what it means.
- **Semantic cache with a named risk**: every walkthrough that proposes it also flags that a false similarity match returns a wrong answer. Proposing it without the caveat loses points.
- **Middle band to a human**: moderation, extraction and fraud all turn a score into allow / review / act, not a binary ([[Three-Band Confidence Routing]]).
- **The LLM is not the source of truth**: answers are grounded in retrieval with citations, scores come from classifiers or rules, and sensitive actions are executed by deterministic code.

## See Also
- [[System Design Interview Study Guide]] — extends (public prompts alongside self-built examples)
- [[AI System Design Interviewer Rubric]] — prerequisite-for (the rubric these are scored against)
- [[Situation-Indexed Decision Tree]] — extends (each walkthrough exercises one spine)
- [[Three-Band Confidence Routing]] — extends
- [[Completion Trigger Gate]] — extends
- [[RAG Interview Study Guide]] — extends (domain depth behind the RAG and search problems)
- [[Agents Interview Study Guide]] — extends (domain depth behind the agentic workflow)
- [[Context Engineering and Cost Interview Study Guide]] — extends (the cost walkthrough)
