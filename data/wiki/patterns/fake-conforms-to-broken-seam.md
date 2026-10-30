---
title: A Fake That Conforms to a Broken Seam
tags: [eval, pattern]
summary: Test doubles that match a port exactly will faithfully reproduce the port's defects — a prototype threw away every rendered image because the LLM port had no images parameter and 300 green tests used fakes shaped to that port — so conformance needs one shared full-signature fake per port, a contract test on the real adapter's wire shape, and caller-side identity assertions.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/galactus/skills/review-testing/SKILL.md
  - data/raw/claude-docs/galactus/skills/proto-harden/SKILL.md
---

# A Fake That Conforms to a Broken Seam

> "A fake that conforms to a broken seam certifies the break."

**Founding case (galactus prototype review-fix branch).** The vision path rendered PNGs and
then threw them away, because the `LLM` port had no `images` parameter. Every fake
matched that port exactly. 300 tests passed, and none of them could see that the model was
never shown an image. The tests checked conformance to the interface, and the interface
was the bug.

This is a hexagonal-architecture trap. Fakes stand in for a port, so they inherit the port's
shape. When the port is missing a channel, every fake is missing it too, and the suite
cannot fail on the gap.

## The checks (review-testing dimension)

- **One shared fake per port, not per module.** N hand-rolled fakes of the same Protocol
  are N places a port change gets silently missed. A port change should break one fake
  loudly, not three fakes quietly.
- **The fake records the full signature**, including optional channels (`images=`, extra
  kwargs). A fake narrower than the Protocol is a finding even when every test passes.
- **A contract test pins the real adapter's wire shape**, independent of the fake. Decode
  what the adapter actually sends (base64 back to bytes, block order, media type) and
  assert identity with the input. A fake's recording only means something if a separate
  test proves what the real adapter does with the same argument.
- **Caller-side identity assertions close the loop.** Assert that what the caller hands
  across the seam equals the real artifact, byte-exact where possible, at both unit and
  end-to-end level.
- **Fakes raise the real error types**, imported from the production module, not stand-in
  exceptions.

## Green for the wrong reason

A sibling class of test that passes without testing anything:

- preconditions that pass only because a validation is missing, so adding the validation
  breaks tests that were secretly relying on its absence;
- two runs collapsed into one by idempotency, so an assertion compares a value to itself.

When a diff adds a check, ask which existing tests depended on that check not existing.

## Duplex caveat

For streaming or duplex voice designs, the same review dimension flags tests that assert
**deterministic end-to-end replay**. Audio timing, endpointing and interruption points do
not reproduce. Components replay deterministically; the assembled pipeline has to be graded
statistically. Grade on task success rather than WER, and remember that per-turn accuracy
compounds: 90% per turn survives a 10-turn conversation only about a third of the time.

## See Also
- [[Eval Falsifiability]] — extends (the same failure inside an eval harness)
- [[Differential Parity Testing Against the Original]] — alternative-to (pin behaviour against a reference rather than a fake)
- [[TDD as Coding-Agent Harness]] — extends (green suites that certify the wrong thing)
- [[Hydration Gap Silent Input Loss]] — instance-of (another input dropped silently between layers)
- [[Prototype Hardening Pass]] — related (part of)
- [[Mocked-Away Body Hides the Defect]] — related (the patch replaces the unit itself, so its broken body never runs)
- [[Tested Decision, Untested Expression]] — extends (an invented HTML fixture would have agreed with the broken anchors)
- [[The Eval Harness Has Its Own Adapter]] — related (a harness-side adapter drifted from production)
- [[Page on a Total Order]] — instance-of (query-builder fakes that ignore range and order)
- [[Stub Backend Is Permanent Dev Infrastructure]] — related (a stub kept as permanent infrastructure has to track the production wire shape)
