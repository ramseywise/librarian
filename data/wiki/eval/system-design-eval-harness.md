---
title: System Design — Unified Eval Harness
tags: [eval, reference]
summary: Interview-format system design writeup of playground's eval harness — golden set → heuristic graders → LLM judges → gate, shared across three agent implementations, with HTML reporting and threshold governance.
updated: 2026-07-17
sources:
  - raw/repos/playground/CLAUDE.md
  - raw/repos/playground/SANYI.md
---

# System Design — Unified Eval Harness

Interview-format writeup of a system actually built (playground's `evals/`, shared by three parallel agent implementations over one knowledge base). Format: requirements → constraints → architecture → tradeoffs → scaling.

## Requirements

- Compare three agent architectures (LangGraph RAG service, ADK multi-agent, LangGraph CRAG) on the **same** golden set with the **same** graders — otherwise the comparison measures harness drift, not agent quality.
- Cheap deterministic signal on every run; expensive LLM judgment only where heuristics can't reach.
- Regression protection: a metric dropping below target must fail loudly.

## Constraints

- Local-first (DuckDB, no hosted eval platform required); LangFuse optional for experiment tracking.
- Fixed suite topology — graders/, metrics/, harnesses/, pipelines/, reports/, utils/ — enforced as a change-contract budget so the harness doesn't sprawl.

## Architecture

- **Golden set** (50 QA pairs, committed) is the unit of truth. Runtime outputs land outside version control.
- **Two-tier grading:** deterministic heuristic graders first (citation hallucination / missing citation / citation recall — string-matchable, free, run always), LLM-as-judge second (routing, friction, safety, schema, message quality — probabilistic, costed, run deliberately).
- **Harnesses split regression vs. capability:** regression = "did anything get worse", capability = "can it do the new thing yet". Different questions, different cadences.
- **Gate:** targets live in one config (`targets.yaml`-style); the gate command fails when a metric drops below target. Threshold *values* are tunable config (变易 Bianyi); *"the gate must run"* is the invariant (不易 Buyi) — see [[SANYI Change-Contract System]].
- **Reports:** HTML stats + suite verdicts rendered from the same run artifacts, so humans and CI read one source.

## Tradeoffs

- LLM judges are themselves ungoverned models — judge drift is real. Mitigation: heuristic tier catches the objective failures; judges are scoped to qualities with no deterministic test.
- A shared harness across three agents means the response schema is a hard interface (single `schema.py`, never duplicated) — schema convenience for one agent is entropy for all three.
- Committed golden set risks overfitting to 50 cases; capability harness and ablation notebooks (chunking, reranker, confidence-gate) are the counterweight.

## Scaling path

1. Now: local runs, HTML reports, make-target gate.
2. CI: eval-gate as a required check (the Buyi promotion).
3. Team: LangFuse experiments for run history; golden set grows by mining real failures, not by padding.

## See Also
- [[Eval-Driven Development (EDD)]] <!-- auto-linked -->
- [[project-g Eval Architecture]] <!-- auto-linked -->
- [[Anthropic Three-Tier Eval Taxonomy]] <!-- auto-linked -->
- [[RAG Eval Gate Contract]] — instance-of
- [[RAG Eval Metrics Suite]]
- [[Change-Contracts Rollout]] — extends
- [[Evals and Observability Interview Study Guide]] — prerequisite-for
- [[System Design Interview Study Guide]] — prerequisite-for
