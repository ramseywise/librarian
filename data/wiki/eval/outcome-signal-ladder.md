---
title: Outcome Signal Ladder
tags: [eval, pattern]
summary: Interaction events (open, save, click, share) are proxies for interest, not evidence that a recommendation helped; rank the candidate outcome signals by cost and strength, ship the cheapest one that can be logged from the first serve, and name in the decision record that the first round is measured on a proxy.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-29-beta-outcome-signal.md
  - data/raw/claude-docs/akira/docs/research/2026-09-29-beta-outcome-signal.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-29-beta-outcome-signal.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-beta-outcome-signal.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-beta-outcome-signal.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-beta-outcome-signal.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-beta-outcome-signal.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-beta-outcome-signal.md
---

# Outcome Signal Ladder

From research on defining "the event that means a slate helped" before a beta (repo
akira, 2026-09-29). The interaction log had six kinds (`card_open`, `save`,
`cta_click`, `share`, `poll_vote`, `dismiss`). All six were proxies for interest. None
meant "this person actually went, and it helped."

## The ladder

| Rung | Signal | Cost | Strength | Blocker |
|---|---|---|---|---|
| 1 | Split the CTA click by kind (ticket/reserve vs. "official page") | cheapest, no new UI | commitment intent | none; silent for free events |
| 2 | Add-to-calendar (`.ics`) as a logged interaction | cheap, new UI | stronger intent, covers free events | none |
| 3 | Self-reported attendance the next day | expensive | the real outcome | needs email infrastructure + a privacy-notice update |

**Recommendation:** ship rung 1 from the very first serve, layer rung 2 if free events
are common, and treat rung 3 as the target end state. Write into the decision row that
**the first beta round is measured on a proxy** and its data will need re-reading once
rung 3 lands. Name that limitation going in, rather than discovering it afterwards.

## Structural constraints the research checked

- **The serve log cannot hold the outcome.** The result-set log is written once, before
  the response, describing what was served. "Did it help" is unknowable until later. The
  outcome must be a separate, after-the-fact event joined to the serve (see
  [[Frozen Version Stamps on Logged Results]]).
- **A vote is not a resolution, and a resolution is not attendance.** A poll vote is a
  preference. The poll's winner being chosen is closer to an outcome but answers "did the
  group agree", not "did anyone go". It's worth logging cheaply, but never as a
  substitute.
- **Channel reality.** No push or SMS channel existed, so a next-day prompt really did
  depend on email.
- **Denominator is part of the definition.** Per result set or per session was left
  open, and it changes what the rate means.

## Testing a best-effort beacon

The interaction route returns 202 always — a beacon must never break the page — and a
new kind rides the same route, so it inherits that resilience for free. The flip side: a
"done" test can't assert a hard failure on the serve path. The testable shape is two
halves: the schema accepts the new kind/field, and the UI actually emits the beacon with
it (same finding in the diskoe copy of the research).

## Who defines it

The project's lifecycle gate read "outcome signal defined [by the product owner] ·
engineering logs". The definition of "helped" is a product call. Research frames the
options and does not choose. Logging is engineering's job.

## Poll votes as relevance judgments (akira, 2026-09-24)

A later plan turned group-poll votes into rows for the relevance-judgment corpus, the
strongest relevance signal the product produced and had been throwing away. What made it
usable, and what review caught:

- **Carry serving context or the vote is unattributable.** Polls had been built from their
  own event query, not from a served result set. The fix threaded the signed result-set
  token through the "poll with friends" link, so each option records `result_set_id` and
  `served_position`. Polls started without a token still work and write null.
- **Never accept serving context from the client.** The first build verified the token on
  the page, then passed the id and a position map to the form as plain hidden fields. A
  caller could pair a real result-set id with a fabricated position map, and the forged
  row would reach the judgment export looking like a genuine served ballot. The fix carries
  the signed token through and re-resolves positions server-side.
- **Served position as rank carries position bias.** Using `final_rank = served_position`
  needs the caveat written into the corpus documentation (see
  [[Explore Slice for Position Bias]]).
- **One pseudonym scheme, extracted to a neutral module.** Poll participants reuse the
  versioned salted-HMAC pseudonym registry that saves use. It was moved out of the saves
  feature, so polls do not import a sibling feature.
- **Don't plan the consumer before the corpus exists.** The ranking signal meant to use
  these judgments had a gate of 30 or more judgments across at least 5 moments, and the
  corpus had 0 rows. It was written up as out of scope rather than planned against
  fixtures. Planning it early would have repeated the "ranker graded against its own
  oracle" trap ([[UNGATED Metric Convention]]).

## From research to plan: the call site did not exist (akira, 2026-09-29)

Planning against the research above changed the size of the work:

- **"Extend one call site" was new instrumentation.** The research had flagged that the
  client component firing the CTA-click beacon "was not located". In planning, a grep for
  the event kind found it only in the schema and types. The result card fired only
  card-open and save. Both outbound CTA links on the detail page were plain anchors with
  no beacon. The cheapest option ("one schema field, one client call site") therefore meant
  wiring a beacon onto two silent links, plus a migration. When research leaves a call site
  "not located", grep for it before costing an option on the assumption it exists.
- **The enum stays 1:1 with the resolver.** The new `cta_kind` field mirrors all six values
  of the CTA resolver's type, `info` included, even though `info` renders as text and never
  fires. A type-level `satisfies` pin keeps the two from drifting silently.
- **No result-set token, no signal.** The interaction route rejects events without a
  result-set id, so a CTA click fires only on a served visit (`?rs=` token). A bookmarked or
  direct visit cannot log one. The plan accepted that rather than minting a synthetic id.
- **A silent drop via a default.** Attribution for a tagged tester requires an exact
  (item, served position) match. If the position lookup fails, for example because the
  result set has expired, the beacon omits the position, the route defaults it to 0, and a
  click at any non-zero position is dropped as `202 {recorded: 0}`. That is not a 400, and
  nobody sees it. The best-effort contract (a malformed optional field is dropped, never
  rejected) was deliberately kept for the new field too. See
  [[Silence Reads as Clean]].
- **Log before the definition is decided.** The plan shipped decision-agnostic logging
  first, so that whichever outcome definition the product owner chooses, the data that
  would support it is already accumulating.

## See Also
- [[Trajectory Over Outcome]] — related (process signals vs the terminal outcome)
- [[User Feedback Loops]] — extends (which feedback event counts as the outcome)
- [[Explore Slice for Position Bias]] — related (outcome rates need a counterfactual for position)
- [[Kiez Project]] — instance-of
- [[Write-Time Deterministic Holdout]] — related (the pseudonym and holdout key poll judgments reuse)
