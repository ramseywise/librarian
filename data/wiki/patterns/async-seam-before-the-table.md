---
title: Async Seam Before the Table
tags: [infra, pattern]
summary: "Ship the lookup a future table will serve as a typed fixture behind the final interface: async from day one, reached only through a source interface, with null given exactly one meaning, invariants tested by enumerating the set rather than naming examples, and separate fields for display and scoring. When parallel plans each invent the resolver, one dispatcher names the canonical contract before any of them builds."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b41-operator-identity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b41-operator-identity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b41-operator-identity.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b39-operator-board.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b40-operator-tonight.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b40-operator-tonight.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b40-operator-tonight.md
---

# Async Seam Before the Table

Three UI surfaces in an events app (repo akira) needed to turn an operator code from a
QR-code URL into a name, a neighbourhood and default intake scoping. These were a guest
landing, a printable QR board and a desk-side "tonight" list. No operators table existed,
and none was planned for another phase. The minimum viable answer was a **typed
fixture**, built so the table could replace it without any caller changing.

## The shape

- **Mirror an existing swap point.** A typed record and a source interface live in one
  module, with a fixture-backed implementation as the only concrete one. Callers depend
  on the `OperatorSource` interface and never import the fixture, the same discipline
  that already kept recommendations decoupled from their database source.
- **Async even though the fixture is synchronous.** `getByCode(code): Promise<Record |
  null>` matches the existing candidate source. The later database implementation then
  needs no signature change at any call site. Every consumer was already an async server
  component, so it cost nothing.
- **Reuse the consumption seam.** The intake already had an `operator_district` field
  that it preferred over the manual district answer. The resolver only had to *produce*
  that value, not build a new path to consume it.
- **Two location fields, not one.** `neighbourhood` is display text ("Tonight in
  Mitte"). `defaultDistrict` is the canonical value fed to scoring. Conflating them puts
  display strings into a matcher that expects a closed vocabulary.
- **Normalise the key cheaply.** Lowercase and trim before lookup, so a hand-typed
  `/c/DEMO` resolves the same as the QR. Exact match only, with no fuzzy matching.

## What review added

- **Null must mean one thing before the swap.** `null` means "unknown code", and callers
  render "Link no longer exists". A table-backed implementation that also returns null on
  a timeout would show a permanently dead link during a database blip. The fixture has no
  I/O, so this was not fixed in the change. It was written down as a requirement on the
  item that owns the swap: throw on infrastructure failure, or widen the return type. See
  [[Silent Failure Catalogue]] ("fallback indistinguishable from empty").
- **Enumerate to guard an invariant.** The test that every operator's district is
  canonical named the two seeded codes. An operator added later with a bad district
  would pass. Adding `listAll()` and iterating fixed that. A further test proves the
  method returns a copy, so a caller cannot corrupt the fixture. The cost was a wider
  seam for the future table to satisfy, accepted because an admin surface would need
  enumeration anyway.

## Three plans, three resolvers

The three surfaces were planned in parallel, and **each plan designed its own resolver**.
One was sync, one async. One was a bare function, one an interface. Each had a different
file path and a single location field. A dispatcher pass named one plan's contract
canonical, quoted it verbatim into the others, listed each plan's corrections (async,
module path, interface not function, which location field to use where, do not create a
second fixture), and sequenced the 45–75-minute seam item first. The consuming plans had
correctly coded against an *assumed* interface with a bounded fallback instead of
blocking. That only works if someone reconciles the assumptions before execution. See
[[Decision-ID Reservation Across Concurrent Plans]] for the same race on shared
registries.

## See Also
- [[A Fake That Conforms to a Broken Seam]] — related (a fixture shaped to the interface inherits the interface's gaps, here the null ambiguity)
- [[Write-Only Fields and the Reader Map]] — related (the consumer side existed before the producer)
- [[Decision-ID Reservation Across Concurrent Plans]] — related (parallel plans colliding on a shared artifact)
- [[Printed URL Is a Public Contract]] — related (the QR surfaces this seam serves)
- [[Silent Failure Catalogue]] — extends
