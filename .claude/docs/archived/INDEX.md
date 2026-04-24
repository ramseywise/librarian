# .claude/docs Index

Last updated: 2026-04-15 (agentic-rag-copilot research added)

## Lifecycle

```
backlog/<topic>/      ← research notes, deferred plans, standalone reviews
      ↓ plan written + active
in-progress/<topic>/  ← must have a plan; research optional but lives here too
      ↓ review written + verdict Approved
archived/<topic>/     ← plan + review done
```

---

## in-progress/ — Active (plan required)

| Topic | Artifacts | Status |
|-------|-----------|--------|
| [orchestration-rollout](in-progress/orchestration-rollout/) | plan + review | Review open — 3 blocking (tools, observability, `_extract_latest_query`) |
| [terraform-restructure](in-progress/terraform-restructure/) | research + plan + CHANGELOG | Executed — awaiting review |
| [librarian-architecture](in-progress/librarian-architecture/) | research (×2) + plan | Awaiting review |
| [librarian-ts-parity](in-progress/librarian-ts-parity/) | research + plan | Awaiting review |
| [langgraph-adk-compat](in-progress/langgraph-adk-compat/plan.md) | plan | Draft — precursor to orchestration-rollout; never executed |

---

## backlog/ — Not actively being built

| Topic | Artifacts | Notes |
|-------|-----------|-------|
| [infra-interfaces](backlog/infra-interfaces/review.md) | review | **BLOCKER** — 10 blocking findings; gates orchestration-rollout + terraform-restructure |
| [github-cicd-pipeline](backlog/github-cicd-pipeline/plan.md) | plan | ✅ Workflows written — pending GH App `workflows` permission grant |
| [ts-copilot](backlog/ts-copilot/) | research + plan | Deferred — plan ready to execute |
| [py-copilot](backlog/py-copilot/) | research + plan | Deferred — cites ts-copilot research |
| [rag-agent-template](backlog/rag-agent-template/research.md) | research | Unplanned — RAG template patterns; candidate to feed orchestration-rollout |
| [codebase-dedup](backlog/codebase-dedup/research.md) | research | Unplanned — D3+ findings open |
| [skills-audit](backlog/skills-audit/research.md) | research | Unplanned — actionable findings |
| [agentic-rag-copilot](backlog/agentic-rag-copilot/research.md) | research | Unplanned — A2A, Self-RAG, GraphRAG, memory types, LangGraph advanced, Plan-and-Execute, agentic eval |

---

## reference/ — Evergreen (no lifecycle)

- [rag-tradeoffs](reference/rag-tradeoffs.md) — RAG approach decision log
- [librarian-stack-audit](reference/librarian-stack-audit.md) — Architectural reference

---

## archived/ — Plan + review complete

Items marked **legacy** predate the review workflow (plan only, no review).

| Topic | Artifacts | Note |
|-------|-----------|------|
| [docs-restructure](archived/docs-restructure/research.md) | research | Done — executed directly from research this session |
| [librarian-hardening](archived/librarian-hardening/) | plan + review | 2 non-blocking findings — not blocking |
| [librarian-prod-hardening](archived/librarian-prod-hardening/plan.md) | plan | legacy |
| [librarian-rag-upgrade](archived/librarian-rag-upgrade/plan.md) | plan | legacy |
| [retrieval-pipeline-prod](archived/retrieval-pipeline-prod/plan.md) | plan | legacy |
| [infra-security-triage](archived/infra-security-triage/plan.md) | plan | legacy — informs terraform-restructure context |
| [research-agent-refactor](archived/research-agent-refactor/) | research + plan | legacy — executed, no review |
| [visualizer-improvements](archived/visualizer-improvements/) | research + plan | legacy — executed, no review |
| [mvp-feedback-eval](archived/mvp-feedback-eval/plan.md) | plan | legacy |
| [librarian-restructure](archived/librarian-restructure/plan.md) | plan | legacy — superseded |
| [rag-core-infra](archived/rag-core-infra/review.md) | review | legacy — orphaned |
