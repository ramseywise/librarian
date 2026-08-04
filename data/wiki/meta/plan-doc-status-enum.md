---
title: Plan-Doc Status Enum
tags: [llm, reference]
summary: Nine-member Status enum for plan docs (7 in-flight, 2 terminal) with a forbid-and-relocate suffix policy — the Status line carries exactly one token, everything else moves to named fields.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/guacamayo/docs/specs/plan-doc-status-enum.md
---

# Plan-Doc Status Enum

Spec produced by GUA-73 (design-only), frozen against the plan-doc corpus as it
stood 2026-07-31. Derived empirically: every proposed member must be backed by an
observed value in the corpus or a named pipeline phase.

---

## The enum — 9 members

### In-flight

| state | meaning | written by |
|---|---|---|
| `RESEARCH` | research underway | `/workflow-research` |
| `RESEARCHED` | research complete, not yet planned | `/workflow-research` |
| `PLANNED` | plan written, not DoR-gated | `/workflow-plan` |
| `REFINED` | refined, DoR gate not yet passed | `/workflow-refine` |
| `READY` | DoR passed — executable | `/workflow-refine` |
| `IN_PROGRESS` | execution underway | `/workflow-execute` |
| `EXECUTED` | implemented, review not yet passed | `/workflow-execute` |

### Terminal

| state | meaning | written by |
|---|---|---|
| `COMPLETE` | reviewed and merged (post-`/workflow-review`) | `/workflow-review` |
| `SUPERSEDED` | replaced by another doc; off-path | manual |

`EXECUTED` and `COMPLETE` are deliberately distinct states, not synonyms: writers
already needed to distinguish "implemented" from "implemented and reviewed" —
four docs had invented a `(pending /workflow-review)` suffix to say exactly that.
Collapsing them loses the state the review gate keys on.

`SUPERSEDED` is an enum member rather than a separate field because a superseded
doc still needs *some* Status value, and its prior status no longer describes it —
the doc is not "PLANNED" or "EXECUTED" anymore, it is replaced. Enum membership is
the only representation that doesn't lie.

There is no `ABANDONED` state: no observed corpus value represents an
abandoned-without-replacement doc, and `SUPERSEDED` covers "no longer live."

---

## Suffix policy — forbid and relocate

The `Status:` line carries **exactly one enum member and nothing else.** Any
additional information moves to a named field on its own line directly below.

A constrained grammar was considered and rejected: to avoid data loss it would
have to admit free prose (one real value read `#19 PARTIAL (retries failed; needs
chrome MCP session + Ramsey input)`), at which point it is not meaningfully
constrained. Forbidding gives a one-token line any validator can check with a
set-membership test.

| kind | destination field | format | required? |
|---|---|---|---|
| release pointer | `Released:` | `<file> [<version>]` | optional |
| partial breakdown | `Outstanding:` | free prose | optional |
| pending gate | `Review:` | `pending` \| `passed` | **required on `EXECUTED`** |
| evidence / PR | `Evidence:` | free prose | optional |
| supersession | `Superseded-by:` | plan-doc filename | **required on `SUPERSEDED`** |
| bare completion date | `Completed:` | `YYYY-MM-DD` | optional |

`Review:` is required on `EXECUTED` because such a doc without it is ambiguous
between "not yet reviewed" and "reviewed, forgot to update" — the other fields are
additive detail.

```
Status: COMPLETE
Completed: 2026-07-30
Evidence: PR #83, 475 unit tests pass, lint clean
```

---

## Separator decision — `IN_PROGRESS`, not `IN PROGRESS`

Decided 2026-08-01. Underscore makes the value unambiguously a single token, so
the validator is set-membership rather than normalize-then-compare.

The cost is real and was accepted: space is what every writer emitted and what all
in-flight docs carried, so underscore is a **flag-day change** — the grep fix and
the doc rewrite must land atomically or active-doc discovery breaks *silently*.
See [[Silent Fallthrough in String-Keyed Discovery]].

---

## Detection regex

A bare `grep '^Status:'` undercounts — it misses the bold form and leading
whitespace. The tolerant form:

```sh
grep -m1 -E '^[[:space:]]*(\*\*)?Status(\*\*)?:'
```

The bold form in the corpus is `**Status**:` — colon *outside* the asterisks. A
migration script grepping the literal `**Status:**` matches **zero docs**. Both
the parent issue and the plan's research wrote it the wrong way round.

Using the wrong regex produced a wrong conformance denominator (88 instead of 93,
undercounting by 5) that propagated into the issue's success metric before being
restated.

---

## Snapshot, not a live figure

Re-running the census one day after the freeze returned 120/100 docs rather than
113/93 — seven new plan docs had landed. The enum, mapping, and suffix policy are
unaffected in substance, but **raw counts in a frozen spec must be re-measured at
migration time, never inherited.** The plan's own risk table had flagged this as
high-likelihood; it recurred at larger scale one day later.

A related constraint: plan docs are gitignored and untracked, so a pre-commit hook
can never fire on them — validation has to run elsewhere.

---

## See Also
- [[Silent Fallthrough in String-Keyed Discovery]] — extends
- [[Claude Workflow System]] — instance-of
- [[Agile Workflow Definitions]] — prerequisite-for
- [[Documentation Boundary — Machine vs Human Docs]]
- [[Deferred Decision Status]] — alternative-to (status enum for design decisions, not plan docs)
