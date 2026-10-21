---
title: Design Evidence Annex
tags: [llm, meta, pattern]
summary: A design-of-record document keeps mechanisms and principles on its plates under a per-tab line budget; audit-grade evidence (probe outputs, incident detail, inventories) moves verbatim to an annex file, each figure is drawn once and referenced, and every removed anchor survives as an empty `<span id>` stub so cross-tab links and routing still resolve.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-08-31-design-evidence-annex.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-31-design-evidence-annex.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-31-design-evidence-annex.md
  - data/raw/claude-docs/playground/docs/research/2026-08-31-design-evidence-annex.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-design-doc-restructure.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-design-doc-restructure.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-design-doc-restructure.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-design-doc-restructure.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-design-doc-restructure.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-design-doc-restructure.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-design-doc-restructure.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-01-design-narrative-hierarchy.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-01-design-narrative-hierarchy.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-01-design-narrative-hierarchy.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-01-design-narrative-hierarchy.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-01-design-narrative-hierarchy.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-01-design-narrative-hierarchy.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-01-design-narrative-hierarchy.md
---

# Design Evidence Annex

A single-page HTML design document had grown to carry the architecture, the security
audit, and the evidence appendix on the same tabs. Three passes cut it back, and the
rules they settled on are reusable for any living design-of-record.

## Rules

- **Tab line budget.** Each tab has a line ceiling; a pass that adds a plate must remove
  one or compress. The Data & Trust tab went 7 plates → 3 (628 → 320 lines) by reframing
  around *control* (data as system of record, intelligence as constrained interpretation,
  trust as control of the boundary) instead of storage.
- **Mechanisms on the page, evidence in the annex.** The component plate keeps the
  principle and the mechanism; KPI rows, probe outputs, incident write-ups, and route
  inventories move **verbatim** to `annex/*.html` under an `ARCHIVED` header with their
  then-current plate numbers. Nothing is deleted, nothing is summarised on the way out.
- **Draw each figure once.** A request-path or lifecycle figure lives on one plate and is
  referenced from others; duplicated figures were the first thing to drift.
- **Anchor stubs.** Every removed anchor (`#d-evidence`, `#trust-provenance`, …) survives
  as an empty `<span id>` on the nearest surviving plate, so tab routing and cross-links
  from older docs still resolve. Plates are then renumbered globally.
- **Name containers by architecture, not implementation.** `C1 · Supabase` became
  `C1 — Data plane`; implementation names on an architecture plate are how component-level
  detail creeps back in.

## Restructuring a Heavy Design Doc (akira, 2026-08)

A design-of-record HTML whose System tab "read as heavy no matter how it was trimmed" was
not too long. It had **three competing axes in one place**: containers (where code runs),
layers (what each part is responsible for) and capability (what makes it distinctive). Four
plates described the same system on different axes. The restructure rules:

- **Pick one primary axis per tab, and give each plate exactly one home on it.** A card that
  mixes layers with containers is an axis error, not a length problem.
- **The HTML shows shape and argument. Specs hold the contract.** Every staleness bug in
  three sessions was a duplicated fact going out of date. Any number, column name, threshold
  or file path that appears in both the HTML and a spec is deleted from the HTML and linked.
- **Stage cuts, don't delete them.** Cut plates go to a review-staging tab that comes last,
  is collapsed and is labelled pending, so the staging tab can't quietly become permanent.
  Rescues happen first, **by copy**: a rescued plate exists in both places until the deletion
  pass confirms it landed.
- **Draw the absent arrow.** The strongest claim in the design was an arrow that doesn't
  exist: the offline model layer writes to the store and is never called by the request path.
  Lay the diagram out so the missing edge is visible.
- **Don't cut mechanism diagrams or honest negatives.** An earlier refactor dropped 13
  mechanism diagrams, and that was a mistake. The list of what doesn't exist yet (no
  scheduler, no personalisation, an unrun eval) is what makes the strengths believable.

## Narrative Hierarchy Pass (akira, 2026-09)

An outside reader judged the eight-tab design-of-record credible and essentially
complete. The weakness was **information hierarchy**, not content. Three narratives
competed: the product as a decision engine (primary), as an intelligence layer
(technical differentiation, secondary) and as a learning system (future compounding,
tertiary). The tertiary one opened the product tab's thesis. The reviewer's summary was
*"make the document 10–15% lighter while making the proof hierarchy 20% louder."* The
pass took the second half and mostly rejected the first.

- **State the key claim once, canonically, and link to it.** There were nine scattered
  `moat`/`compound` mentions across five tabs, and none pointed at a single wording. The
  honest version already existed: *"the asset is the measurement loop, not the data
  structure"*. It was the 8th of 9 hypothesis cards, three plates deep. The fix gave that
  card `id="the-moat"`, added a one-clause forward pointer on the overview, and turned the
  other mentions into links. A check confirms `grep -c 'id="the-moat"'` returns exactly 1
  and every `#the-moat` link resolves. Adding a tenth statement would only make it worse.
- **Grep for the sentence that should be there.** The claim the reviewer called the
  document's most important product sentence (it reduces *decision* effort, not
  *search* effort) had zero matches across the tabs. Its absence is something a grep can
  find.
- **Name the current objective.** The roadmap's single objective (close the first real
  recommendation loop) could be worked out from a band but was never stated, so the risk
  order wasn't visible.
- **Show deferred technology at a lower weight.** Explicitly deferred graph-DB plates sat
  at the same visual weight as the decision study, so they read as current work.

**Rejected review advice, recorded so a later session doesn't re-adopt it:**

1. *"Move density to the annex."* The annex directory (3,328 lines) turned out to be
   **orphaned**. The build script substitutes only `@tab` directives, and nothing renders
   the annex files. So moving content there means *deleting it from the reader's view*.
   This qualifies the rule above: an annex keeps evidence only if something builds or
   links it.
2. *"Trim forensic detail for the investor."* The same reviewer scored that tab 9.5 as a
   CTO. The written-but-unread table and the join-by-convention key are the evidence that
   the architecture is real. Trimming them optimizes for the reader who is already
   convinced.
3. *"Freeze tabs after a final pass."* This conflicts with the rule that build-state
   claims carry an expiry. A frozen tab drifts without anyone noticing.
4. *Per-tab 0–10 scores.* There was no rubric, so they weren't actionable.

## See Also
- [[Documentation Boundary — Machine vs Human Docs]] — extends (a human-consumed doc with its own hygiene rules)
- [[Three-Doc Spec Split]] — related (the same instinct — separate audiences, separate files)
- [[Workflow Pipeline Telemetry Audit]] — related (a stamp newer than its content is the failure this prevents)
