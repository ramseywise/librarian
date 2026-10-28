---
title: The Untested Copy Wins
tags: [infra, llm, pattern]
summary: Logic that exists in two places drifts, and the copy nobody tests is the one that actually runs — a publish gate whose tested half had zero callers while the live rule sat ungraded in a script, three index-page detectors, a rater vocabulary pasted from the enrichment vocabulary — with the inverse fix being a single primitive every consumer inherits from.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/research/2026-08-29-multimarket-platform.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-27-n8n-port-parity.md
  - data/raw/claude-docs/playground/docs/research/2026-08-27-n8n-port-parity.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-28-src-scripts-review.md
  - data/raw/claude-docs/playground/docs/research/2026-08-28-src-scripts-review.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-29-frontend-quality-audit.md
  - data/raw/claude-docs/playground/docs/research/2026-08-29-frontend-quality-audit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-02-dis58-a11y-reaudit.md
  - data/raw/claude-docs/playground/docs/research/2026-09-02-dis58-a11y-reaudit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-29-multimarket-platform.md
  - data/raw/claude-docs/playground/docs/archived/langgraph-adk-compat.md
  - data/raw/claude-docs/playground/docs/archived/librarian-rag-upgrade/plan.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b67-publish-gate-merge.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b67-publish-gate-merge.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b67-publish-gate-merge.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b67-publish-gate-merge.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b67-publish-gate-merge.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b67-publish-gate-merge.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b67-publish-gate-merge.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-b72-src-restructure.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-b72-src-restructure.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-b72-src-restructure.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-b72-src-restructure.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-b72-src-restructure.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-b72-src-restructure.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-b72-src-restructure.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis28-kappa-rater-study.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis28-kappa-rater-study.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis28-kappa-rater-study.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis28-kappa-rater-study.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis28-kappa-rater-study.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis28-kappa-rater-study.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis28-kappa-rater-study.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis241-poll-event-hydration.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis241-poll-event-hydration.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis241-poll-event-hydration.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-dis241-poll-event-hydration.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-dis241-poll-event-hydration.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-dis241-poll-event-hydration.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-dis241-poll-event-hydration.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-dis241-poll-event-hydration.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-dis241-poll-event-hydration.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-dis241-poll-event-hydration.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis241-poll-event-hydration.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis241-poll-event-hydration.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis241-poll-event-hydration.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis241-poll-event-hydration.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-28-dis416-venue-priority-wiring.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-28-dis416-venue-priority-wiring.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-28-dis416-venue-priority-wiring.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-28-dis416-venue-priority-wiring.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-28-dis416-venue-priority-wiring.md
---

# The Untested Copy Wins

A read-only layering audit of a Next.js + Postgres repo (diskoe, 2026-08) kept finding the
same shape under different names. The rule it ended with: **logic in two places drifts,
and the copy nobody tests is the one that wins** — because the tested copy is the one
that is safe to leave uncalled.

## The instances

- **A publish gate split in two, with the tested half dead.** `validateEventPublishability()`
  carried 50+ lines of publish policy and eight passing test cases — and zero non-test
  callers. The real decision lived inline in an ops script, ungraded, and was the *only*
  place a QC-verdict block existed. The resolver that was supposed to own the decision
  enforced four content-quality rules that never ran. Live policy that would vanish with
  the script beat every other finding in the audit.
- **Duplicate detection, same pattern.** A ~200-line resolver (URL match, external id,
  title similarity, 150m proximity, time overlap) had no callers; the dedupe that ran was a
  40-line group-by in a script. An enum value for `duplicate` existed and zero rows carried
  it.
- **Three index-page detectors, one untested.** The untested one was a verbatim-then-drifted
  fork: same threshold, different URL regex, different title tokens, missing the German
  weekday tokens the tested one had gained.
- **A rater vocabulary copy-pasted from the enrichment vocabulary** — the ground-truth
  label space for an inter-rater study (see [[Human Agreement Ceiling Protocol]]). The
  guarding test asserted only `length === 26`, which pins the duplicate rather than
  detecting drift. If the enrichment vocabulary changes, raters score against a stale
  rubric and the ceiling becomes uninterpretable. A later audit found a **third** copy, in
  the κ-compute script, already drifted: it shared only 12 of 26 tags with the canonical
  list. Its per-tag report would have reported κ = 1.0 for tags raters could never
  assign. The fix: both scripts import one constant.
- **Four divergent event write paths**, two bypassing the documented fix; two whole
  pipelines, where the tested one was unshipped.
- **A "verbatim copy" of a scorer body** inside a sensitivity-sweep script, honestly
  labelled and guarded by a parity test — the right stopgap, with the real fix being a
  `weights` parameter on the one scorer.

Across the view layer the same thing: 58 hand-styled buttons, 203 un-tokenised hex values
with three near-blacks and four warm greys, three focus-ring conventions — every screen
built as its own island.

- **Framework-comparison tools that re-implemented the agents.** In a RAG A/B harness (playground), the ADK tool wrappers re-implemented retriever, reranker and condenser logic rather than calling the shared agents. The copies lost caching, dedup and grading, and their prompts drifted, so the "ADK vs LangGraph" comparison was really "copy vs original". Separately, a dead local confidence constant (0.3) sat beside the live config value (0.4). Fix: thin adapters, one `create_agents()` factory feeding both orchestrators, and a parity test across the two wrappers.

## Why review does not catch it

The duplicate is usually *plausible*: it has tests, a sensible name, confident comments.
Nothing in a diff review reveals that the function under review has no callers, or that
the thing it duplicates is the one actually wired in. The signal is structural (call
graph, import direction), not textual.

## The inverse: fix the primitive, inherit the fix

The accessibility re-audit of the same repo recorded the counter-example. A whole class of
findings ("23 inputs and 58 buttons fire `focus:ring` on mouse click") closed at once
because `Button` and `Input` primitives baked `focus-visible:ring-*` into their base
classes — every consumer inherited the fix by migrating to the primitive, not by a
per-file find-and-replace. A `grep` for the old convention then returns one deliberate hit.

The same logic drives the multimarket plan for that repo: make shared gates a single
package (stage 2) *before* splitting into services (stage 3), because the known failure
shape of the repo is duplication that drifts.

### Consolidating three copies when one diverges (akira, 2026-09-14)

Three poll pages each did the same events → source posture → enrichment read, with 11
`as` casts between them. Two were byte-identical. The third did discovery rather than
lookup, selected no price or venue columns, and hard-coded a position. The issue's metric
was "a column rename fails `tsc` once, not zero times across three copies". Some lessons
from the consolidation:

- **Export at two granularities instead of adding behaviour flags.** One
  `hydratePollEventsByIds` wrapper serves the two identical callers. The two join
  builders and the pure row mapper are exported too, so the divergent page keeps its own
  query and calls the lower-level pieces. The rejected alternative, one all-purpose
  function, would have fetched columns the third page never fetched and needed override
  flags to suppress them.
- **Check that optional fields reproduce the divergent output before adding a flag.** The
  price resolver returns `null` on `undefined`, and `row.venues?.district` collapses to
  `null` when `venues` was never selected. So typing those fields optional reproduced the
  third page's output exactly, with no flag.
- **Casts on flat selects go away. One reviewed cast stays for the embed.** Inference
  already matched the flat-select rows. The `events → venues` embed kept a single cast
  inside the shared module, following the main loader's existing idiom. The net result was
  0 casts in the pages and 1 in the module.
- **Moving duplicated code moves its silent failures too.** Review found the shared
  module discarded the query `error` on two joins, the same as all three copies had. It
  failed closed (no image, no generated text) but with no log line. Now there was one
  place to add the log.
- **Full-replacement mocks break when a module gains an export.** Two tests mocked
  `@/products/polls` with a factory that listed only the old exports, so the new import
  resolved to `undefined`. The tests that used the `importOriginal` spread were fine. The
  research pass found this before the build, not during it.

## Mitigations

1. Find zero-caller functions before trusting their tests; a tested-but-uncalled rule is a
   defect, not a reserve.
2. Derive the second copy from the first (`import`, call the real function to compute
   expectations) rather than restating it — see [[Derive the Gate, Don't Copy It]].
3. Where a copy must exist, guard it with a differential test against the original, not a
   shape check — see [[Differential Parity Testing Against the Original]].
4. Centralise at the primitive when the duplication is in consumers.
5. **Restructure move-only.** A source-tree reshuffle that also changes logic cannot be
   reviewed for this defect, because the reviewer cannot tell a moved copy from an edited
   one. akira's restructure (2026-08) made every step `git mv` + import rewrite + README,
   required the test count at the end of each phase to equal the count at the start
   (re-verified first — the recorded baseline was stale), held parity suites
   byte-identical as the proof nothing changed, and ordered phases by blast radius
   (one-folder renames first, the `agents/` split last), one commit per phase. The split
   rule it landed: in a deterministic product pipeline, `agents/` holds only the
   model-calling stages; pure ETL goes to `core/`, product features to `products/`.
6. **Leave a mirror unwired on purpose, and pin it with a test.** A venue-priority plan
   (akira, 2026-09-28) added optional coverage and out-of-scope terms to the reviewer
   scorer. The dashboard kept a priority mirror, and the review map had its own call
   site. Wiring the new terms into every copy would have widened the change past what the
   plan could verify, so both were left without the new inputs deliberately. A structural
   non-regression test asserts the mirror never supplies `coverage` or `oosSignal`, so a
   later "helpful" sync fails loudly instead of silently changing the ranking. The scorer
   ran in two passes, and pass 1 was proven byte-identical to the old scorer before
   pass 2 added the new terms.

## See Also
- [[Differential Parity Testing Against the Original]] — extends (how to guard a copy that must exist)
- [[Derive the Gate, Don't Copy It]] — extends (restated lists are copies too)
- [[Silent Fallthrough in String-Keyed Discovery]] — related (another defect class invisible to diff review)
- [[Multimarket — One Project, Market as Config]] — extends (shared package before service split, for this reason)
- [[Silent Join Miss Reads as a Finding]] — related (a retyped key format is a copy that drifts without error)
- [[Every Column Names Its Reader]] — related (the same vocabulary declared inline on four tables)
- [[Listing Pages Masquerading as Records]] — instance-of (a probe's broader JSON-LD subtype check that production never got)
- [[Stated Seams Drift, Enforced Seams Hold]] — extends
- [[Three-Level Duplicate Classification]] — related (the duplicate spec whose resolver never got callers)
- [[De-Dupe Before You Normalize]] — related (classify copies as COPY / REPO-SPECIFIC / DIVERGED-COPY before rolling out a norm)
- [[Single-Definition Grep Guard]] — related (vocabulary constants pinned to the migration CHECK text)
- [[Batch Path Through the Synchronous Chain]] — extends (a differential test keeps the batch and synchronous paths from becoming two copies)
- [[A Partial Fix of a Duplicated Doc Is Worse Than None]] — related (fixing one copy turns agreement into disagreement)
