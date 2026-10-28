---
title: Argued Carve-Out with a Stop Condition
tags: [patterns, pattern]
summary: "When a layering rule flags code that has exactly one caller and no consumer wanting anything different, the right fix can be a written exception where the rule lives — named file, reason, and the condition that would end it — not a new abstraction (reporter injection, generators) built for a consumer that doesn't exist."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-07-dis184-importer-progress-layering.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-07-dis184-importer-progress-layering.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-07-dis184-importer-progress-layering.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-07-dis184-importer-progress-layering.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-07-dis184-importer-progress-layering.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-07-dis184-importer-progress-layering.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-07-dis184-importer-progress-layering.md
---

# Argued Carve-Out with a Stop Condition

A hardening ticket (repo akira) flagged that a library function, the batch importer, printed
operator progress itself (15 `logger.info/warn` sites) instead of returning it for a CLI
layer to render. The ticket was filed as a `refactor` and named three options: (a)
generator-yielded progress, (b) an injected reporter, (c) a documented carve-out. It said
outright that (c) "is a legitimate outcome, not a failure".

## Evidence that decided it

- **One caller, and a trivial one.** The CLI wrapper registered shutdown handlers,
  delegated, and mapped errors to exit codes 0/1/2. It had no logic that could receive
  progress events.
- **The speculative second consumer already existed and didn't need anything new.** The
  scheduled-ingestion workflow reused the same CLI and exit-code contract rather than
  calling the library directly.
- **No test asserted on progress content.** The CLI test mocked the importer as an opaque
  `Promise<void>`.
- **No reporter or generator idiom existed anywhere in the tree.** Either option would have
  introduced a new idiom for one already-satisfied caller. Option (a) also meant restructuring
  a per-source `try/catch/finally` loop around `yield` points.
- **There was precedent.** The repo's README already handled two similar cases as "this
  file's constraint differs, for this stated reason", written next to the rule itself.

## The shape

1. **Record the exception where the rule lives.** It went in the module README's `cli/`
   rules paragraph, as "named file + reason", next to the existing exceptions. Not in a
   ticket comment.
2. **State the stop condition.** "This exemption stops applying the moment a second caller
   exists that needs different progress presentation." An exception without an end
   condition becomes permanent by default.
3. **Keep the fallback sketch.** The rejected-but-preferred code option, an optional
   `reporter` parameter whose default wraps the existing logger, is backward-compatible and
   leaves the `Promise<void>` and exit-code contract alone. It was kept inline, so reopening
   the decision doesn't start from zero.
4. **Show the mismatch up front.** The job type said "refactor" but the diff was docs-only.
   The plan's header says so, so a reviewer isn't surprised by the diff.
5. **No-regression proof sized to the change.** The planned live before/after diff of
   operator output couldn't run without credentials. The executor used a weaker fallback and
   **said so in writing**. It added the stronger direct proof: zero bytes changed in the
   importer or the CLI file.

Distinguish narration from diagnostics. The library's own failure reporting (fatal
per-source error, spend-cap warning) was never part of the carve-out. A library reporting
its own failure is not operator narration.

## See Also
- [[Named-Trigger Deferral]] — extends (the stop condition is a named trigger attached to an exception instead of a parked issue)
- [[No-Placeholder Plan Discipline]] — related (plans that state what they did not do rather than leaving it implicit)
