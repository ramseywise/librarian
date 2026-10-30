---
title: Heuristic Pipeline Metrics
tags: [eval, infra, observability]
summary: Automated measurement of operational health — latency, error rate, token usage, retrieval recall — that runs alongside every eval rung and is explicitly never sufficient alone, since a fast cheap wrong answer still fails.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/eval-approaches.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-07-r10-eval-metrics.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--06-evaluating-agents.md
---

# Heuristic Pipeline Metrics

Automated measurements of system *behavior*: latency (how fast?), error rate (how
reliable?), token usage (how expensive?), retrieval recall (how complete?). These measure
operational health, not answer quality.

**Use when** monitoring production health; detecting degradation before users complain;
tracking cost and performance over time; or alongside any other eval approach.

**Avoid as the only evaluation** — the governing caveat is blunt: *"a fast, cheap wrong
answer still fails."* Also unavailable pre-deployment, since there's no traffic to measure.

## Why it sits outside the ladder

The [[Eval Ladder]] rungs all measure *quality* and progress with project maturity. These
metrics measure *health* and run continuously at every rung. They're orthogonal — a system
can be green on latency and error rate while answering wrongly, and a system can be
accurate while too slow to use.

Their diagnostic value is strongest in combination: a quality regression with flat
operational metrics points at the model or prompt; one accompanied by latency and error
spikes points at infrastructure.

## Scaffold mapping

- Always available in the eval suite — latency and token tracking are built into the
  pipeline.
- `optional_features: [promptfoo]` adds HTTP-level performance testing.

## Production signals as one security-invoker view (nonprofit-success-ai)

The "drift, errors, latency, cost, staff override rate" monitoring question was answered
with one per-agent, per-day view over the run log and approvals table, with no new table:
- **Override rate = rejected ÷ (approved + rejected)**, bucketed on the day the human
  decided (`reviewed_at::date`), not the day the agent proposed. `expired` and `pending`
  are excluded from both sides. **"Edited" is not observable** while an edit is a new
  draft row rather than an approval state, so the spec says so instead of counting it.
- Error and fallback rates are counts ÷ runs. Latency is `percentile_cont` p50/p95. Cost
  is a sum over a nullable column, so the view also exposes `runs_costed` and a sum over
  a few costed rows is not mistaken for the total.
- **Drift stays out of the DB.** Judge pass rate per run already lives in the eval
  experiment log, and the view's comment points there.
- The view is `security_invoker`, so the existing RLS on the base tables decides who sees
  which org's metrics, and no new policies are needed.

## Agent efficiency metrics (course synthesis)

Log on every trial — they catch regressions pass rates miss: steps/turns to completion (rising steps at
a flat pass rate = thrashing), tool calls (total, per tool, failed), tokens (input/output/cached),
latency (p50/p95, TTFT), **cost per success** (at 50% success the real cost is 2× the per-run cost),
and convergence (optimal ÷ actual steps).

Report a **budget–capability curve, not one point**: on RE-Bench (Wijk et al. 2025) the best agent
scored ~4× human experts at a 2-hour budget, while humans pulled ahead at 8 and 32 hours. Compare at
budgets close to the real workload.

## See Also
- [[Online Eval Sampling]] <!-- auto-linked -->
- [[Eval Suite Maintenance]] <!-- auto-linked -->
- [[Manual Review as Eval Bootstrap]] <!-- auto-linked -->
- [[Eval Ladder]] — complements (orthogonal health axis)
- [[User Feedback Loops]] — complements (separates engagement shift from regression)
- [[RAG Eval Metrics Suite]] — extends (retrieval-specific metrics)
- [[Observability & Evaluation Glossary]] — related
- [[Demote Judge Findings to Keyless Gates]] — extends (judge findings that a regex can catch move into this tier)
- [[Agent Trace Anatomy]] — extends
