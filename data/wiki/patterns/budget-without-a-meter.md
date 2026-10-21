---
title: Budget Without a Meter Is a Preference
tags: [eval, infra, pattern]
summary: A product budget (taps, latency, cost) that nothing measures will be silently exceeded — a ≤4-tap intake shipped at ≥6 taps — so every budget ships with its meter, and when screen and requirement disagree the requirement wins.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/design-initiative/SKILL.md
  - data/raw/claude-docs/playground/skills/design-product/SKILL.md
  - data/raw/claude-docs/akira/skills/design-product/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-product/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-product/SKILL.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-b3-smoke-import.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-b3-smoke-import.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-b3-smoke-import.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-b3-smoke-import.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-b3-smoke-import.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-b3-smoke-import.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-b3-smoke-import.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-v6-intake-budget.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-v6-intake-budget.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-v6-intake-budget.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-v6-intake-budget.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-v6-intake-budget.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-v6-intake-budget.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-v6-intake-budget.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
---

# Budget Without a Meter Is a Preference

## Finding

akira's product spec set an intake budget of **≤4 taps**. The intake shipped needing **≥6
taps**. Nobody decided to break the budget; nothing counted taps, so nobody noticed.

## Rule

A budget with no meter is a preference. Every numeric product budget — taps, latency,
tokens, cost per request — names the instrument that measures it, and the instrument ships
with the feature. When the built screen and the requirement disagree, **the requirement
wins**; the screen is the defect.

## Related product-stage rules from the same source

- **PARTIAL names its missing field.** A status of PARTIAL without the missing piece is
  unactionable. (T-0 instrumentation shipped marked BUILT with 5 of 7 version stamps.)
- **Enumerate un-exported states**: zero-state, empty-because-filtered vs
  empty-because-broken, and permission-denied rendering as "no data" — the design tool
  exports only the happy screens.
- **UNRECOVERABLE requirements** (data you cannot collect retroactively) ship in the same
  commit, with the full field list enumerated and the cost stated in time ("wait 90 days
  again"). Predict the descope: viewport tracking and randomization slices are the items
  that get cut in week three.

## Meter Computed, Then Dropped (akira smoke import, 2026-08)

akira's first paid enrichment smoke test found that token usage was computed per call and then
dropped at the handoff result, so spend could not be attributed to a run. Other findings:

- **Bound spend by human-counted invocations, not a boolean.** An "enabled" flag on an
  unbounded loop is not a budget. The smoke run used a single-row script under a policy ceiling
  of 5 calls.
- **Read what `dryRun` actually skips.** Here it still called the model and skipped only the DB
  write, so a "dry" run cost money.
- **Switching provider is a config change** (`ENRICHMENT_MODEL` / `OPENAI_BASE_URL`). The real
  cost of switching is re-establishing a quality baseline.
- Go and send-back signals were defined before the run, not read from its results afterwards.

## Building the Meter (akira intake budget, 2026-08)

An intake form was budgeted at ≤4 taps and ≤20 s; it shipped rendering six or more taps
and nothing measured either. The meter that closed the contradiction:

- **Client-side counters in refs:** mount timestamp and a tap counter incremented on
  every answer change, sent with the submit.
- **Two nullable columns that name their reader first** — the admin recommendations tab
  — because logs cannot be backfilled ([[Every Column Names Its Reader]]).
- **Pass on median *and* p95, per variant.** A median of 4 with a p95 of 9 does not pass,
  and one variant passing does not carry another.
- **Cut out the confound.** Accessibility toggles add a tap by design; report all submits
  and submits that did not touch them.
- **State the measurement's weakness.** Client wall-clock is throttled in background
  tabs; record as reported and say so.
- **Low traffic → manual walkthrough.** Walk each variant a fixed number of times with a
  timer and validate the instrumentation against it.
- **Pre-register the decision fork:** cut the form (budget wins), amend the budget
  (evidence wins), or mixed — chosen by the numbers, recorded as the closure.
- **Extract the counting logic into a pure function** so it is tested in the node
  environment without rendering the form.

## A Token Ledger Cannot Bound a Zero-Token Path (akira structural extraction, 2026-09)

akira wired a fallback extraction tier into production. When a source's normal crawl wrote
zero events, a model call tried to repair listing candidates. The call was behind an
OFF-by-default switch and shared the run's one token ledger, so it did not need a second
ledger. Review found the ledger could never stop this path. `exhausted` is
`tokens >= maxRunTokens`, but the extractor recorded `{}` (zero tokens) on every call
because the structured-generation helper discarded `usage`. The meter was dropped one layer
down, as in the smoke import above, and the budget it fed was not real.

- **Ask what each ceiling counts, and whether this path increments it.** A token budget
  bounds nothing on a path that reports zero tokens. The bound became two **call-count**
  ceilings: 20 per source and 100 per run. Both are named constants marked "deliberately
  generous, unmeasured". A cap hit is a logged `structural_spend_limit` outcome, not an
  error.
- **A per-unit cap resets per unit.** The first fix added only the per-source cap, so an
  armed run over N empty sources could still make 20 × N calls. The run-level ceiling is a
  `{calls, max}` counter on the run context, created once and mutated in place so every
  source shares it. Its test runs two invocations against one `{max: 1}` budget, with the
  per-source cap set to infinity so only the shared counter can be what stops the calls,
  and asserts one call in total.
- **Three comments claimed the run ledger closed the gap.** All three were wrong and all
  three were corrected. A comment about what bounds spend is a claim, so verify it against
  the metric the bound actually reads.
- **Forwarding real usage** from the model gateway was split out as a follow-up instead of
  being treated as done.

Other review classes from the same change: a `found` counter that counted only repaired
candidates, when the field's contract is candidates *seen*; a gateway `null` and a clean
`is_event: false` collapsed into one drop reason (now separated with a `detail` flag); and
roadmap and change-contract rows still describing the tier as "harness-only".

## A budget that is raised whenever it is exceeded (akira share metadata, 2026-09)

A complexity budget (lint ignores plus token-allowlist entries) went from `4 + 1` to
`4 + 3` in the same PR that exceeded it. The orchestrator challenged it: a budget that
rises whenever it is exceeded is not a budget. The raise stood only because it met the
contract's own bar, which says budgets grow "only with justification". Each new entry had
a recorded reason why no existing primitive could serve (a `<meta>` attribute and an
image renderer cannot resolve CSS custom properties). The reviewer's caveat is worth
keeping: the mechanism survives only as long as every future raise meets the same
standard.

## See Also
- [[Always-Red Check Carries No Signal]] — related (a meter nobody reads is the same failure one step later)
- [[Ship Logging Before Features]] — related (the UNRECOVERABLE class applied to logging)
- [[Four-Stage Design Pipeline with Backflow]] — part-of (product stage)
- [[Spend Gate Before the Model Call]] — related (gates that a meter can prove saved money)
- [[A Capped Run Is Not a Clean Run]] — related (a spend cap that fires but is never reported)
- [[Branch Gated on State Only It Writes]] — related (another guard whose input is never produced on the live path)
- [[Hoist Irreversible Decisions to the Attended Band]] — extends (unmeasured band budgets labelled as such)
