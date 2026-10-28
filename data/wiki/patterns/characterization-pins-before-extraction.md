---
title: Characterization Pins Before Extraction
tags: [patterns, infra, pattern]
summary: "Before extracting logic out of an untested script into a shared engine, pin the old script's observable behaviour (printed report byte-for-byte, write payloads, exit codes) and run the suite green against the original blob. Then run it unchanged against the refactor, and prove the pins are live with deliberate mutations. Any policy the refactor generalizes ships as a parameter whose default is today's behaviour, so the extraction cannot quietly decide an open question."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis270-publish-module.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis270-publish-module.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis270-publish-module.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis270-publish-module.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis270-publish-module.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis270-publish-module.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis270-publish-module.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis270-publish-module.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis270-publish-module.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis270-publish-module.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-15-dis270-publish-module.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-15-dis270-publish-module.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-04-LIB-110-restructure-shared-extraction.md
---

# Characterization Pins Before Extraction

From akira's publish-module build (#270). One 221-line CLI held all the logic that decided
whether an event was publishable: load, QC gate, content validation, write, sample. It had
zero tests. Two more content verticals needed the same pass. The work was an extraction
into a generic `runPublishPass` engine with thin per-vertical CLIs, following the repo's
existing archive-sweep precedent (pure selector, async orchestrator with a `maxRows` ceiling
checked before any write, CLI that only parses and prints).

## The sequence

1. **Write the characterization suite first, against the old code.** 12 tests imported the
   CLI with the DB client mocked. They pinned the printed report byte-for-byte, update
   payloads and ids, sampling upserts, each blocking status, the unpublish patch, and exit 1
   on a failed read. The suite ran green against the original file at its exact blob hash
   *before any edit*. (The first execute session was cut off mid-build. The resumed session
   kept the engine files but still wrote the pins before touching the CLI.)
2. **Run it unchanged against the refactor.** Same 12 tests, no edits.
3. **Prove the pins are live.** Flipping the default QC policy to `advisory` failed 8/12.
   Setting `needs_review: true` in the publish patch failed 1/12. A pin that no mutation can
   break is decoration. See [[Red-Then-Green Proof for Fix-Stage Tests]].
4. **Diff a read-only production dry run.** Old CLI (a temporary copy of the HEAD blob) vs
   new CLI against live data: identical reports. The only differing line was a dotenv
   banner.

## Make the policy a parameter, defaulted to today

The QC gate was hardcoded for events. Whether it should stay required, become advisory, or
be skipped was an open decision tracked in a separate issue. The two new verticals had no
QC evaluator or table at all. The engine took `qcGatePolicy: 'required' | 'advisory' |
'skip'`:

- events default to `required`, bit-for-bit today's behaviour, so the refactor cannot be
  read as having resolved the open issue;
- the new verticals default to `skip`. That is not a weakening, because no gate ever applied
  to them, and it is the only value that matches reality.

Flipping the policy later is a one-line config change, not a PR that touches gate logic.
This is [[Build the Knobs, Not the Choice]] applied to a refactor.

## One gate sequence, not two orchestrations

A dev notebook's "publish blockers" column re-derived the event gate sequence from the same
two primitives. It collected every failing gate, where the CLI stopped at the first. If the
CLI gained a cap or a new QC branch, the notebook would drift silently. The fix was one
exported gate-sequence function with a `first-blocking | all` mode, called by both.
Sharing primitives is not enough when the *order* is the rule.

## Execution findings worth keeping

- **Cap counts only rows not already in the target state.** The event query re-selects
  already-published future events every run. A cap on "all publishable rows" would refuse
  every run once the live catalogue grew past it.
- **SQL `is not null` and JS truthiness disagree on `''`.** Selection predicates stayed in
  SQL for the pass. An in-memory mirror existed only for the notebook's all-blockers mode,
  and the pass did not re-check them.
- **A scheduled writer must not overwrite a human verdict.** The new verticals select only
  `draft`/`needs_review`/`approved`/`published`. The event pass, pinned to its old behaviour,
  still re-publishes a human-`rejected` row that clears the gates. That gap was recorded as
  needing its own decision, not fixed under the refactor's cover.
- **Unranged reads truncate silently.** The old CLI's selects capped at the API's
  `db-max-rows`. Reads now paginate. See [[Bounded Slice After In-Memory Eligibility]].
- **Exit-code contract deferred, not changed.** A per-row write failure printed `FAILED` and
  exited 0, as before the refactor. Changing it would break the CLI contract the refactor
  existed to keep. It was carried to the session that owns the unattended-run contract.
- **Copy-paste slips need an entrypoint test.** Review found that the two new CLI files had
  no test importing them. A `describe.each` over all three entrypoints closed it: swapping
  one CLI's config for another's failed 4/15.

## Clean fixtures cannot expose a divergence (librarian slugify, 2026-08)

A restructure plan claimed existing tests "pin the behaviour, making extraction
mechanical" for six slugify variants. Every fixture title was clean alphanumeric text,
which produces identical output under all of them, so the tests could not detect the very
difference the unification would change. The fix was 27 characterization tests on the
inputs where variants differ (punctuation, apostrophes, unicode, double spaces), then a
corpus-wide blast-radius measurement whose result was recorded as a number: 0 links
newly unresolvable (see [[Demote the Auto-Writer Before a Semantic Change]]).

## See Also
- [[Build the Knobs, Not the Choice]] — extends (a byte-identical control arm, here as a refactor's default policy)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — related (mutation proof that pins are live)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related
- [[Indistinguishable Rejection on Best-Effort Sinks]] — related (unedited-test tripwire on a signer extraction)
- [[Bounded Slice After In-Memory Eligibility]] — related (same pagination fix, same repo, same week)
- [[Demote the Auto-Writer Before a Semantic Change]] — prerequisite-for (pins and a measured blast radius gate the semantic step)
