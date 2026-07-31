---
title: Code Review Drill — SANYI
tags: [llm, reference]
summary: Code-review interview drill using a real SANYI review as the worked example — a two-line diff that lints clean but violates the change contract, and the reviewing method that catches it.
updated: 2026-07-17
sources:
  - raw/repos/playground/SANYI.md
---

# Code Review Drill — SANYI

Code-review interviews reward a method, not an eye. This drill uses a real contract-check run (playground, 2026-07-17) to practice the method: **review the diff against the declared contract, not against taste.**

## The diff (real, synthetic-violation test)

```python
# src/agents/rag_agent/confidence.py — should_continue_crag()
         if self.crag_delta is None:
             return True
+        if self.ensemble_top_score < 0.42:
+            return False
         return self.crag_delta >= min_improvement
```

Two lines. Type-checks, lints clean, tests pass, and the behavior is even sensible — stop CRAG iteration on hopeless retrieval scores.

## What a contract-based review catches

1. **[INFO] BN-1 — hardcoded tunable.** `0.42` is a policy threshold living in business logic. The file's own convention ten lines up is env-driven module constants (`_SCORE_DELTA_MIN = float(os.getenv(...))`). The contract's Bianyi layer says thresholds must be changeable without a deploy; this one now requires a code change. The fix is mechanical: hoist to a named, env-overridable constant.
2. **[NOTICE] UN-1 — unassigned component.** `confidence.py` matched no entry in the contract registry — the layer decision for the confidence router had never been made. A pure style review can't produce this finding at all; only diffing against a registry can. (The registry was amended on the spot: confidence.py joined the Bianyi tunables entry.)

## The method, generalized

- First question is never "is this code good?" — it's **"which declared component does this diff touch, and what does that component's contract say?"**
- The dangerous class of change is the one where **every individual line looks innocent** — a flag wrapped around a safety check, a threshold inlined "temporarily". Line-by-line reading approves these; contract-diffing flags them (BY-2 semantic downgrade is the canonical case).
- Severity comes from the layer, not the reviewer's mood: invariant touched → blocker; complexity budget pressured → warning; changeable made rigid → info; registry hygiene → notice.
- Report **new** findings only — a baseline (Debt) keeps the review loud about news and silent about history. A reviewer who re-reports known debt gets muted within weeks.

## Interview transfer

Asked to review a PR in an interview: state the invariants you'd check first (auth, data boundaries, irreversible writes), then the interfaces (schema/tool-signature drift), then tunables-in-code, then style. That ordering — consequence-ranked, contract-first — is this drill.

## See Also
- [[SANYI Change-Contract System]] — instance-of
- [[Change-Contracts Rollout]]
