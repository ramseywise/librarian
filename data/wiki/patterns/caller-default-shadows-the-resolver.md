---
title: Caller Default Shadows the Resolver
tags: [llm, infra, pattern]
summary: "When a resolver correctly lets an explicit argument win (`opts.model ?? resolved`), any caller that fills an unset flag with a hard-coded default turns \"unset\" into \"explicit\" and the provider-aware resolver is never consulted — fix the callers by routing them through the one resolver helper, not by weakening the precedence rule."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis435-cli-model-default.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis435-cli-model-default.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis435-cli-model-default.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis435-cli-model-default.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis435-cli-model-default.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis397-model-call-ledger.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis397-model-call-ledger.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis397-model-call-ledger.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis397-model-call-ledger.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis397-model-call-ledger.md
---

# Caller Default Shadows the Resolver

A model gateway resolved the model id with `opts.model ?? creds.model`, where
`creds.model` came from a provider-aware resolver. That precedence is right: an explicit
model should win. But two dev CLIs in akira (#435) defaulted an unset `--model` flag to a
hard-coded constant naming an OpenAI model. To the gateway, every call looked explicit, so
the resolver never ran.

With the provider switched to Bedrock and no flag passed, each call sent an OpenAI model id
to the Bedrock endpoint and got HTTP 400. The e2e CLI's cost estimate was worse: it priced
the wrong model and said nothing.

## Mechanism

- The resolver is correct, and so is the precedence rule. The defect is that a **caller
  turns "unset" into "explicit"** before the value reaches the precedence check.
- A helper already did the right resolution: `enrichmentModel()`, which tries the resolver
  and falls back to the constant only if it throws. It had been introduced by an earlier
  change (#214) that fixed the same re-derivation inside the enrichment stage, but that
  change **migrated only the one call site it was looking at**. Three CLI call sites kept
  their own copy of `FLAG || DEFAULT_CONSTANT`.
- The same shape was found in the model-call ledger work (#397): a ledger row recording
  `opts.model ?? creds.model` faithfully records whatever the caller passed, so a shadowing
  default shows up as a wrong-but-plausible model name. See [[A Trace Is Not a Number of Record]].

## Fix

- **Change the callers, not the gateway.** The fix was an import swap at three call sites
  to the existing helper. The gateway line was left unchanged, because weakening
  "explicit wins" would break callers that pin a model on purpose.
- **One seam, not a second re-derivation.** The project's naming rule is that the
  resolution lives in exactly one helper. A new `ENV || CONSTANT` at a call site repeats the
  defect the helper exists to remove. A [[Single-Definition Grep Guard]] over the constant's
  name outside the helper turns that rule into a check.
- **Check the dependency direction before importing.** The CLI layer may import from the
  agents layer, and the helper's module had no top-level side effects, so importing it did
  not pull a model call into the CLI's module scope.
- **A path that already fails loudly needs a test, not new code.** The batch client already
  threw a named error under Bedrock, before any request, whatever model string it was
  given. It had zero test coverage for the provider flip, so the plan added the test and no
  production code.

## Where to look for it

Any `flag ?? CONSTANT`, `ENV || CONSTANT` or argument-parser `default:` that sits upstream
of a resolver with its own fallback. The constant only matches the resolver's output under
the default provider, so the bug is invisible until someone flips the provider.

## See Also
- [[Model Gateway Is Transport, Call Site Owns Meaning]] — extends (the gateway's precedence rule stays; callers own what they pass)
- [[A Trace Is Not a Number of Record]] — related (a ledger records the shadowed value faithfully)
- [[Single-Definition Grep Guard]] — related (enforcing one resolver helper)
- [[A Partial Fix of a Duplicated Doc Is Worse Than None]] — related (a fix that migrated one of several copies)
