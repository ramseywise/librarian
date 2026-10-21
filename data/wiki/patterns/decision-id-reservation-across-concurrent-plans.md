---
title: Decision-ID Reservation Across Concurrent Plans
tags: [llm, meta, pattern]
summary: When several plans running at once each add rows to a shared decision registry (`D-NN`), a plan must re-grep the highest existing ID immediately before editing — not at planning time — and never reuse a retired number; the companion rule is that the specs are the registry and the human-readable decisions doc is a rendering, so edits flow spec → doc, never the reverse.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/design-system/SKILL.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-04-dis62-desktop-decision.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-04-dis62-desktop-decision.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-04-dis145-record-canon-decisions.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-04-dis145-record-canon-decisions.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-04-dis62-desktop-decision.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-04-dis62-desktop-decision.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-04-dis145-record-canon-decisions.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-04-dis145-record-canon-decisions.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b8-concierge-landing.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b8-concierge-landing.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b8-concierge-landing.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b8-concierge-landing.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b8-concierge-landing.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b8-concierge-landing.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b8-concierge-landing.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis341-representation-baseline.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis341-representation-baseline.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis341-representation-baseline.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis341-representation-baseline.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis341-representation-baseline.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis349-preview-to-review-rename.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis349-preview-to-review-rename.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis349-preview-to-review-rename.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis349-preview-to-review-rename.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis349-preview-to-review-rename.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dsk-355-a1-detail-places-similar.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dsk-355-a1-detail-places-similar.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dsk-355-a1-detail-places-similar.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dsk-355-a1-detail-places-similar.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dsk-355-a1-detail-places-similar.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis316-foursquare-os-places.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis316-foursquare-os-places.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis316-foursquare-os-places.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis316-foursquare-os-places.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis316-foursquare-os-places.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis318-enrichment-prompt-input-type.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis318-enrichment-prompt-input-type.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis318-enrichment-prompt-input-type.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis318-enrichment-prompt-input-type.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis318-enrichment-prompt-input-type.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis343-venue-open-facts.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis343-venue-open-facts.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis343-venue-open-facts.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis343-venue-open-facts.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis343-venue-open-facts.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis336-accommodation-census.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis336-accommodation-census.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-venue-discovery-relevance.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-venue-discovery-relevance.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-venue-discovery-relevance.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-venue-discovery-relevance.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-venue-discovery-relevance.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis374-data-platform-maturity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis274-judge-kappa-vocab-phase2.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis274-judge-kappa-vocab-phase2.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis274-judge-kappa-vocab-phase2.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis274-judge-kappa-vocab-phase2.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis274-judge-kappa-vocab-phase2.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--delta-namespace-decision.md
---

# Decision-ID Reservation Across Concurrent Plans

The akira repo kept design decisions as `D-NN` rows in a registry that several plans
appended to. Two plans written the same day both needed new IDs.

## The collision mechanism

A plan drafted at 10:00 sees `D-41` as the highest and writes "add D-42". A sibling plan
drafted at 10:30 sees the same and also writes "add D-42". Whichever executes second
either overwrites or produces two D-42s. The plan text is stale the moment another plan
lands.

## The rules

1. **Reserve by re-grep at edit time.** The plan step reads: *"grep the highest `D-`
   ID in the registry now; your IDs are highest+1 onward"* — the plan does not hard-code
   the numbers it computed when written.
2. **IDs are never reused.** A retired decision keeps its number with a `superseded by`
   note; the gap is the record. Reusing a number makes every old reference ambiguous.
3. **Claims copied from research are re-checked at plan time.** One plan step had to be
   marked CORRECTED because it restated a research doc's claim about an existing
   decision without opening the registry; the registry had moved. Research is an input to
   the plan, not an authority the plan can cite in place of the file.

## Registry vs rendering

The same work settled a direction-of-truth question. The decisions were recorded in two
places: the structured spec files and a readable `decisions.md`. The rule adopted:
**the specs are the registry; the doc is a rendering.** Edits go into the spec and the
doc is regenerated or updated *from* it. Editing the rendering first (because it is the
one humans read) is how the two drift — the same registry-vs-copy failure as a typed gate
line in [[Derive the Gate, Don't Copy It]].

## Render the registry; never mint IDs in a second document

A design record and its component specs each minted `D1`–`D18` independently and agreed on
none of them, so no delta number in the repo was safe to cite from an issue. The fix is the
same as above: one registry file owns every ID. Every other document **renders** it, and
a missing row is added to the registry first, then cited. IDs are append-only and never
renumbered, because regenerating with fresh numbering silently rebinds every citation in
every issue and plan.

In nonprofit-success-ai the fix also **split the namespace by family**: `C{n}` for
CRM/data-model concerns and `D{n}` for platform/build items. Component specs stopped
minting IDs entirely. The 17 spec-local citations were rewritten to registry numbers **by
reading each one, not by sed**, because the same number meant different things in
different specs. A final re-verify pass checks that no spec mints a bare ID and that every
cited number resolves in the registry.

## Parallel Plans Each Design the Same Dependency (akira, 2026-08)

The same collision happens with **interfaces**, not just IDs. Three plans written in
parallel each needed to look up an operator from a short link code, and each independently
designed its own resolver. A dispatcher reconciliation pass named one plan's contract
canonical and pasted it **verbatim** (an async `OperatorSource` interface plus a fixture
implementation, marked "do NOT redefine") into the dependent plans. A consumer could then
ship against the fixture before the canonical implementation landed and swap it in without
changing call sites. The rule: when concurrent plans share a dependency, reconcile at the
**contract** before any of them builds, and record which plan owns the implementation.

## Same-Day Allocation Moved Twice (akira, 2026-09-20/21)

Two more instances of the collision. On 2026-09-20 a plan planned for `D-99` and was
recorded as `D-100`, because another plan claimed `D-99` the same day. On 2026-09-21 five
plans drafted on one day all needed decision rows while the highest *committed* ID was still
`D-111`. One plan first took `D-112`, which collided with the tracing-adoption plan. A first
correction moved it to `D-115`, which collided with a QC plan holding three IDs. Only a
coordinator pass that read every same-day plan doc produced a stable allocation table
(`D-112`..`D-119`). The table was written into each plan with the caveat that these are
reservations, not commitments, until each branch lands. The lesson: when several plans are
drafted at once, the collision is in the plan docs, not in the registry, so the re-grep must
cover the uncommitted plans too.

## Unmerged Plans Are Claimants Too (akira, 2026-09)

The re-grep rule has a blind spot. The registry is not the only place an ID gets claimed.
Every unmerged plan that drafts a decision claims an ID before its branch lands, and the
duplicate-ID gate (`make spec-numbers`) catches a collision only once both claims reach the
registry file. On one day, five concurrent plans already claimed IDs above the registry's
highest. Two claimed the same pair, and a third collided with them on one ID. A rename plan
that had drafted "D-112" by grepping only the registry was renumbered to D-117 during
refine. A later plan reserved a whole block (D-121 to D-126) and wrote in its header
that the reservation was racy and had to be re-grepped across both the registry *and*
`docs/plans/*.md` immediately before writing.

It still happened. One build's D-110 collided with main's D-110 at merge-from-main time and
was renumbered to D-120, with every reference updated and the gate re-run. The extended
rule:

- **Scan the registry plus every open plan** for claimed IDs. The next free ID is above
  the highest *claimed* one, not the highest merged one.
- **Treat claimed-but-unmerged IDs as unusable** until the owning plan lands or is
  confirmed abandoned.
- **Expect renumbering at merge.** Grep every reference to the old ID (the project
  guide's build-state table, spec rows, READMEs) and re-run the duplicate gate.
- **Do not cite a not-yet-written ID** from another phase's edit. A forward reference to a
  row that does not exist yet is dangling until that phase runs.

## Candidate IDs With a Tie-Break (akira, 2026-09-19)

Four plans drafted on the same day (three open-POI plans and a type-safety plan) each needed
new decision rows. Instead of claiming final IDs, each plan reserved **candidate** `D-`/`B-`
IDs and stated an explicit tie-break: **if two plans claim the same number, the lower issue
number keeps it** and the other re-greps at edit time. A `spec-numbers` gate in CI was the
backstop that catches any collision the rule misses.

It still moved. The type-safety plan reserved `D-82`, another plan landed first with that
number, and the decision shipped as `D-91`. The plan doc recorded the move rather than
silently renumbering.

The refine passes on these plans also caught a **fabricated citation**: one plan claimed a
sibling plan had reserved a specific ID, and the sibling said no such thing. The same passes
caught invented function names (a discovery runner cited by a name that did not exist in the
code) and a test file that did not exist. Plan-stage claims about other plans and about code
need the same grep check as claims about the registry.

## Reserved numbers expire too (akira, 2026-09-19)

A parent plan **reserved** five IDs (three `D-` and two `B-`) for a deferred child slice.
By the time the child plan was written, all five had been claimed by unrelated work
written the same day: one was a decision recorded by a venue-vocabulary plan, and one was
the parent's own roadmap row. The child plan re-grepped, found new free numbers, and was
renumbered **again overnight** when a sibling branch citing the same issue claimed one
first. A reservation written in a plan is not a lock; only the re-grep at edit time is. A
companion plan the same day applied the same rule to migration timestamps ("re-derive the
next number at execute time, do not reuse it blindly"). It also used a reserved placeholder
ID for a possible future escalation, with an instruction to mark it "not needed" rather than
leave it dangling.


## A Database Allocator Closes the Class (akira, 2026-09-23/24)

After repeated collisions, a data-platform plan moved allocation out of prose into an
append-only `governance_decisions` table:

- **The allocator is a unique constraint.** `governance:allocate --kind D --title "…"`
  inserts a row and prints the next free number. Two concurrent callers hitting a unique
  `(decision_kind, decision_number)` cannot both win, so the collision class is closed by
  construction, not by convention. The done-when fires N parallel inserts and asserts N
  distinct numbers.
- **Append-only is enforced, not conventional.** `UPDATE`/`DELETE` are revoked from every
  role, including the service role, with a no-op rule as a second guard. A reversal is a new
  row pointing at the one it supersedes.
- **The markdown stays hand-authored.** The decision rows *argue*, and a generator would not
  keep that quality. The table is checked against the markdown **in both directions**: an id
  defined in prose with no ledger row fails, and so does a ledger row with no prose
  definition. This is a separate failure class from the existing duplicate check.
- **Seed it with its own decisions.** The plan backfilled its own six decisions, so the
  ledger was not empty on day one.

Usage notes from the next two plans: the allocator writes only the ledger row, not the spec
file. Through npm it needs `--` before its flags so they are forwarded, and it needs
`--confirm-production`. Until the operator ran it, the ledger check reported the new ids
as `missingFromLedger`. A named skip env var gated that, and the handoff said so.

## See Also
- [[Derive the Gate, Don't Copy It]] — related (same registry → rendering direction)
- [[Deferred Decision Status]] — extends (the registry rows these rules protect)
- [[Derived-and-Hidden Design Decisions]] — related (a decision that never got a row at all)
- [[Claude Workflow System]] — part-of (a plan-stage rule when plans run concurrently)
- [[Documentation Boundary — Machine vs Human Docs]] — related (the rendering is the human-consumed doc)
- [[Issues Live in the Repo They Change]] — related (bare issue refs rebind on transfer: same silent-rebind class)
- [[Open POI Data Sources]] — instance-of (the parallel plans that used candidate IDs)
- [[Brand the Funnel's Output]] — instance-of (the decision that moved from D-82 to D-91)
- [[Data Clusters by Writer and Trust]] — related (the same plan's per-table contract registry, also checked both ways)
