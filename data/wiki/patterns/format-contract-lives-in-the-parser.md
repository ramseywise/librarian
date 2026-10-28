---
title: Format Contract Lives in the Parser
tags: [patterns, infra, pattern]
summary: When a model writes log files via Edit/Write and the skills barely specify the format, the real format contract is the downstream parsers' positional regexes, and drift shows up as "no data" rather than as a parse failure.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-03-observability-data-layer.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-03-observability-data-layer.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-06-gua-92-retire-pulse.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-06-gua-92-retire-pulse.md
---

# Format Contract Lives in the Parser

Source: the guacamayo observability data-layer audit, plus the follow-up that retired a
dead reporting script (GUA-92).

## Mechanism

The ledgers and logs (growth entries, funnel headers, verdict logs) are written by the
model through Edit and Write. The skills that ask for them say almost nothing about the
format. The format that actually matters is implied by whatever reads the files:
dashboard ledger parsers, funnel counters, a ~400-line verdict grammar, a fail-closed
ledger-gate hook, and a shell pulse report. Each one does positional regex matching.

When a parse fails, the parsers call `log.warning` and move on. A dashboard card then
shows **"no data"**, which looks like a quiet week, not a broken parser (see
[[Silence Reads as Clean]]).

## What the audit found

- **A fail-closed gate was already blocking every write.** The ledger-gate hook required
  `^\d{4}-\d{2}-\d{2} \[`, but the outcome-tag format being written did not match it. So
  every edit to growth.md was rejected.
- **Three definitions of a growth entry disagreed.** They were unified to
  `^(- \[|[0-9]{4}-[0-9]{2}-[0-9]{2} \[)`.
- **3 of 4 funnel regexes were dead** against the live header.
- **A typed JSON tier had zero consumers.** It had been built and never read. The daily
  series should be a `GROUP BY date` projection over the fact store, not a sidecar file
  produced by the on-demand report.
- **A hand-maintained DATA blob was a second clock.** It sat beside the generated regions
  and drifted from them.

## Rules

- **Migrate markdown to JSON consumer-first.** Fix the silent wrong answers first, so the
  baseline you measure against is honest ([[Read-Every-Consumer Migration]]).
- **One writer per dashboard marker region.** A region with two writers has no owner.
- **Region injection must be idempotent.** Run the generator twice; the second diff must
  be empty.
- **To loosen a guard, execute the block case.** Do not reason that the loosened regex
  "should still block". Run an input that must be blocked and watch it get blocked.

## Retiring dead readers (GUA-92)

The pulse script was one of the parsers whose regexes no longer matched. It was
**deleted rather than resurrected**. The deletion came with:
- A regression guard test: a word-boundary grep that fails if the script or its make
  target reappears. Its proof was a planted defect.
- The rule "rollback means reopening the decision; the failing test forces that
  conversation."
- A caller-visible failure: Make's "No rule to make target" is louder than a script that
  silently reports nothing.

## See Also
- [[Silence Reads as Clean]] — instance-of
- [[Read-Every-Consumer Migration]] — extends
- [[Byte-Diffable Vendor-and-Move Migration]] — prerequisite-for
- [[Always-Red Check Carries No Signal]] — extends
