---
title: Offline Pipeline Seed Harness
tags: [patterns, infra, eval, pattern]
summary: "To take an empty local stack to populated, drive the real stage functions with fixture-backed dependencies. Make the fixture fetcher throw on a cache miss and stub global fetch so any call site you forgot to thread fails loudly instead of reaching the network. Shift dates at the fetcher seam, never with a second writer. Make a per-hop counter report with ZERO-YIELD and STARVED banners the product. And re-check every 'no duplicates' assertion once real rows flow, because against zero rows it passes vacuously."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-pipeline-harness-card-extract-qc.md
---

# Offline Pipeline Seed Harness

From an akira plan. A fresh local stack had zero venues, events and enrichments, so every
review surface correctly rendered an empty set with no error anywhere. No supported path
led from empty to populated. The fix was a local-only harness that runs discovery → gate
→ HITL decisions → source plan → ingestion → enrichment → QC → publish over pinned HTML
fixtures.

## Real stage functions, extracted not forked

Every hop calls the production function with fixture-backed dependencies. Where a hop was
not callable from a script (a server action that builds its own admin client and
revalidates a path, or a CLI `main()` that holds logic), the move was to **extract the
logic, not fork it**. The server action became parse → call the extracted function →
revalidate. The CLI became thin. The action's existing tests stayed unchanged, which made
them the regression net. A forked copy would have tested the fork.

## Make every unthreaded network call fail

The importer had no seams. It imported the fetcher and robots reader directly and called
`new Date()` at eight sites. The plan threaded optional `{ fetchHtml, getRobotsRules, now }`
through five call sites. Then two guards proved nothing was missed:

- The fixture fetcher **throws on a cache miss** (`no pinned fixture for "<url>"`).
- The harness run **stubs `globalThis.fetch` to throw**.

One call site, a robots-policy persister, made "no extra network call" only because the
real fetcher had already memoised the origin. With an injected fetcher, that memo is empty
and the call would have gone live. A memoised side effect hides a network call, and only a
throwing stub finds it. The same posture applies to models: they are faked by default
through the real seams (a precomputed-output hook and an injected `generate`), so the
output still flows through sanitize → validate → gate. Fake rows are labelled
`seed_fake_v1`, and a `--live-models` flag is the only switch that can spend.

## Shift dates at the seam, not after the write

The fixtures were captured weeks earlier, so their events were in the past. One draft
rebased dates with a post-hoc `UPDATE`. It was rejected for three reasons. It is a second
writer to `events`. The slug embeds the date, so a rebased row contradicts or renames its
slug. And a re-run snaps dates back through the URL match, so idempotency fails by
construction. Instead, the fixture fetcher applies a pure `shiftFixtureDates(html, weeks)`
(whole weeks, weekday-preserving) and rows arrive already future-dated with consistent
slugs. The tier diagnostic always runs on the **unshifted** bytes, so the literal strings
are what gets asserted. A page whose date spellings defeat the shifter is swapped out of
the fixture set rather than growing the regex.

## The counter report is the product

Each hop returns `{ stage, in, out, dropped: {reason: count} }`. `in > 0 && out == 0`
prints a `ZERO-YIELD` banner naming the top drop reason and exits non-zero. `in == 0`
prints `STARVED — upstream <stage> produced nothing`. A per-page tier report runs every
extraction tier, including a shadow tier that never writes, against a hand-authored
`expected-items.json`. It is written by reading each page and never by running a tier,
because a tier cannot be its own oracle.

The first real run printed `ingestion: in=3 out=0 dropped={empty_source=3}` and then
STARVED all the way down. Root cause: only index pages had been pinned, never the per-event
detail pages that the venues' detail-page crawl mode fetches. That was a fixture-pinning
gap, reported as a plan defect rather than worked around. The tier report also overturned
the plan's theory about a missed event. All four production tiers read only the archive
list's structure, so all of them missed an event in a hero block above it. The shadow
structural tier found it. The real miss was therefore in sampling, not extraction.

## Vacuous idempotency

The harness asserted "a second run creates no duplicate rows". While enrichment and QC
were STARVED, that passed against zero rows. Once the fixtures were fixed and real rows
flowed, the assertion failed (`expected 10 to be 5`). The enrichment hop never passed a
content hash, so every row stored `content_hash: null`, the backlog selector treats a null
hash as unenriched, and each re-run re-enriched and re-QC'd everything. Any invariant
assertion over a table should also assert that the table is non-empty. This is the same
failure as [[Scan-Floor Guard Against Silent No-Op Checks]].

## Local-only by construction

The dev module never constructs a database client. The CLI does, after refusing any
non-local target, with no production override because there is no legitimate production
use. The Makefile injects the local URL and key from the local stack's status, so a
production-pointing env file cannot become the target. dotenv does not override variables
that are already set, which is what makes that injection win. Contrast
[[Production Write Guard: Explicit Override, Never Ambient]], where an override exists because production
use is legitimate.

## See Also
- [[Single-Subject End-to-End Trace]] — extends (the same real-stage walk, as a repeatable seed)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (assertions that pass on empty tables)
- [[Silence Reads as Clean]] — related (the empty stack that rendered without error)
- [[A Fake That Conforms to a Broken Seam]] — related (fakes injected through real seams)
- [[Production Write Guard: Explicit Override, Never Ambient]] — alternative-to
- [[Model Gateway Is Transport, Call Site Owns Meaning]] — related (the extraction tier added its own gateway purpose rather than mislabelling spend as `judge`)
