---
title: Validated Concept vs Unmeasured System
tags: [eval, pattern]
summary: A user-test number everyone quotes (77.8% Top-5 hit rate) was a validation of the concept — human-curated sets, N=6, a pre-specified answer key — not of the automated system, which had never been measured against it; the same confusion shows up as roadmap rows marked BUILT on the strength of specifications and as launch gates "asserted in every document and tested in none", and the cure is to label every number with what produced it.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/docs/open-questions.md
  - data/raw/claude-docs/akira/docs/onboarding-comments.md
  - data/raw/claude-docs/kiez-archive/docs/onboarding-comments.md
  - data/raw/claude-docs/akira/docs/open-questions.md
  - data/raw/claude-docs/kiez-archive/docs/open-questions.md
  - data/raw/claude-docs/akira/docs/product-feasibility.md
  - data/raw/claude-docs/kiez-archive/docs/product-feasibility.md
  - data/raw/claude-docs/akira/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/diskoe/docs/onboarding-comments.md
  - data/raw/claude-docs/playground/docs/onboarding-comments.md
  - data/raw/claude-docs/diskoe/docs/open-questions.md
  - data/raw/claude-docs/diskoe/docs/product-feasibility.md
  - data/raw/claude-docs/playground/docs/product-feasibility.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/playground/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/diskoe/docs/notion/user-test.md
  - data/raw/claude-docs/playground/docs/notion/user-test.md
  - data/raw/claude-docs/akira/skills/design-initiative/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-initiative/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-initiative/SKILL.md
  - data/raw/claude-docs/akira/skills/design-system/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-system/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-system/SKILL.md
  - data/raw/claude-docs/akira/skills/git-issue/SKILL.md
  - data/raw/claude-docs/diskoe/skills/git-issue/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/git-issue/SKILL.md
  - data/raw/claude-docs/playground/skills/git-issue/SKILL.md
  - data/raw/repos/nonprofit-success-ai/.claude--skills--git-issue--SKILL.md
---

# Validated Concept vs Unmeasured System

Three instances of one confusion from an events-discovery product's planning record
(repo akira), each caught by reading the source of a number rather than the number.

## The quoted metric was a curation ceiling

The 77.8% Top-5 hit rate came from a Wizard-of-Oz test: human-curated result sets, six
participants, three clustered tasks each, and a pre-specified answer key. It shows the
*concept* works when a scene-literate human picks with the rubric in hand. The shipped
ranker had never been scored against that number. So the figure is a **ceiling for
curation**, and the open question it raises is not "how do we reach 77.8%" but "is there
a human curator at launch" — cheap, differentiating, and the only way to produce
gold-standard labels.

The test itself, for the record: N=6 participants, three clustered tasks each (18 task
runs), Top-1 hit 77.8% (14/18), mean Top-5 relevance 4.17/5, 94.4% would take the next
step. Each task had a pre-specified answer key — a desired Top-5 composition and a list of
what must *not* appear — so the number is a ceiling for "curation with the rubric in hand",
and the rubric is reusable as eval ground truth once a system exists to score against it.
The two weak task clusters failed for different reasons worth keeping apart: nightlife
(50%) is a subjective-dimension problem, restaurants (66.7%) a missing-objective-facts
problem (enrichment depth). Both stay in scope as prediction difficulty, not as
out-of-scope categories.

## Specifications were read as shipped code

A feasibility review initially concluded "much of P1 and P2 exists" from an onboarding
doc that described the *target* pipeline. Corrected four days later: the tree contained
the ingestion half plus a conventional surface. The design skills had been told to treat
the codebase as greenfield, and a document describing a pipeline in the present tense
reads as a status report. Rule adopted: a roadmap row says BUILT only when the module
exists *and is tested*, and that still does not mean the deliverable is accepted.

## Gates asserted everywhere, measured nowhere

Three launch gates — coverage ≥80% vs a gold list, hard-fact correctness <2% on a
200-event audit, long-tail share ≥40% — appeared in every planning document and had been
tested in none. The schema audit found the measurement system itself was "architecturally
met and empirically untested": all seven logging fields were wired, and the eight rows in
the table predated the migration, so 0 of 8 were populated; viewport tracking described as
BUILT had produced zero rows. The closing check was one integration test: run one real
session end to end and assert the row.

## The habit

Every number in a planning doc carries its provenance inline: *measured on what, by
whom, against what key, when*. The marker set the project used — ⛔ blocker, ❓ decision,
🔍 unverified, 🔬 research — exists mostly to keep 🔍 (asserted, no evidence either way)
from being read as fact. Most 🔍 items are minutes of work to settle; the cost is in not
knowing which ones they are.

## Build-state as a pipeline stage (design skills, 2026-10)

The design skills turned this into Phase 0 of every design run: read the tree before the
docs (6 of 8 green markers were wrong), a capability with no file path is ABSENT, and states
use a fixed vocabulary — BUILT / BUILT, NOT WIRED / SPECIFIED / GAP. The issue-filing skill
adds that **states carry qualifiers and the qualifier is the work**: `BUILT (partial)` files
an issue for the named remainder only, `SPECIFIED (deferred)` asks before filing because a
ticket reopens a decision, and `OPEN — decide, don't build` files a `Decide:` issue, never a
build task.

## See Also
- [[Human Agreement Ceiling Protocol]] — related (the same scrutiny applied to agreement figures)
- [[Ship Logging Before Features]] — prerequisite-for (the unmeasured system cannot be measured retroactively)
- [[Workflow Pipeline Telemetry Audit]] — related (the BUILT-row-outran-evidence instance)
- [[Evidence Classification Model]] — related (observed vs inferred vs claimed, applied to product metrics)
- [[Plan-Doc Status Enum]] — related
- [[Four-Stage Design Pipeline with Backflow]] — extends (tree-first audit as the first design stage)
- [[Path-Verified Build State Markers]] — prerequisite-for (verify BUILT against a file path)
