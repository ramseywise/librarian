---
title: Computed-Correctness Lesson Loop
tags: [patterns, memory, pattern]
summary: "Close an agent's learning loop by recording what an upstream agent predicted next to what actually happened downstream, with correctness as a generated column (computed, never judged), and make human promotion through one RPC the only path by which a lesson becomes visible to the agent that consumes it."
updated: 2026-10-17
sources:
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-07-r9-lessons.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--archive--specs--design-requirements.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--dssg-second-brain.md
---

# Computed-Correctness Lesson Loop

The setup is a multi-agent pipeline. An intake agent routes a case into a bucket at the
start, and a reporting agent summarises the outcome weeks later. Without a lesson loop,
nothing records whether the intake routing held up. With a naive one, the model writes its
own "lessons" straight into memory that future routing reads. In nonprofit-success-ai the
loop is closed with three constraints.

## Mechanism

1. **One lesson candidate per case.** It is upserted when the downstream report is
   submitted, and holds three things:
   - the upstream prediction (bucket and readiness, read from the original intake row);
   - the observed outcome (derived from milestones and events);
   - `prediction_correct`, a **generated stored column** comparing the two.
   Correctness is computed, never judged. No model and no reviewer decides whether the
   prediction was right.
2. **The model may only propose factors.** Success and failure factors are suggestions
   carried on the draft row, so a replay reads them back.
3. **Promotion is an RPC, not a route or a column write.** `promote_lesson(id, notes)` is
   the only way `promoted_by` and `promoted_at` get set. A check constraint requires both
   or neither, and promotion writes an approvals row.
4. **Visibility follows promotion.** Unpromoted lessons are visible to staff and invisible
   to the consuming agent. The consuming agent reads a `promoted_lessons` view filtered
   to the bucket in question. No digest, no rubric.
5. **Promoted lessons are frozen.** A later re-submitted draft does not rewrite a promoted
   lesson. The function leaves it alone and the audit detail records `lesson_frozen: true`.
6. **The readiness gate comes before the human gate.** A thin or not-ready report is never
   promotable, regardless of approval.

## The promotion gate generalised

The requirements doc states this as a principle that can fail: *agents must not silently
promote run or conversation content into durable shared memory*. Moving from episodic to
semantic memory needs three things:
- human approval;
- an explicit scope (organisation, engagement, classification);
- provenance that survives the promotion instead of being summarised away.

## "Memory = add a retrieval tool"

When you write every agent yourself, you do not need an external memory system or proxy.
Memory is a retrieval tool over the promoted-lessons and approved-documents tables. A
memory proxy exists to inject memory into third-party agents you cannot modify. Chat-memory
extraction from conversation history was scoped out for operational cost.

## See Also
- [[Memory Lifecycle]] — instance-of
- [[Self-Learning Agents]] — instance-of
- [[Four-Source Provenance Contract]] — extends
- [[Single-Writer Transition Command]] — extends
