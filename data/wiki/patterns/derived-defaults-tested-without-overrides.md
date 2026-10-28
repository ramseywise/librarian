---
title: Test Derived Defaults Without Overrides
tags: [infra, pattern]
summary: A derived scaffold default is only verified when the render is run *without* the `-d` override that would supply its value — three separate falsely-green checks in one template session (a CI row that forced the wrong flag, a declaration-order bug, an explicit override masking the broken derivation) all came from testing the override instead of the derivation.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-two-root-scaffold-decision-tree.md
---

# Test Derived Defaults Without Overrides

When most of a scaffold's decision tree is derived rather than asked (see
[[Asked vs Derived Scaffold Variables]] — 54 of 68 variables were `when: false` in the
audited template), the derivation expressions *are* the product. But every convenient way
of exercising a render supplies values from the outside, and a supplied value hides a
broken derivation completely.

## Three ways the same check went green while the feature was broken

All three were found in one cleanup session on the ai-project-template MCP tree, and all
three are the same mistake wearing different clothes:

1. **A CI matrix row that never tested what its name said.** The `mcp-ts` row set
   `mcp_server_language=typescript` but not `include_mcp_server=true`. That flag is
   derived and defaults OFF for the default project type, so the row rendered no
   `mcp_servers/` at all, and its `working-directory` step pointed at a directory that
   did not exist. The row passed for as long as it existed. A restructure that broke the
   MCP tree shipped unnoticed because the only check covering it was checking nothing.

2. **Declaration order silently reintroduced the symptom being fixed.** Copier evaluates
   `default:` expressions in declaration order. Slug variables declared *before* the
   language variable they derived from resolved to empty; neither language branch
   matched, both trees got the "unchosen" suffix, and both were pruned — producing an
   `mcp_servers/` containing only a README, exactly the defect under repair. It was
   caught only because the minimal derived case (`-d include_mcp_server=true`, nothing
   else) was re-run after the fix.

3. **An explicit override masked the derived path.** The first `mcp-py` verification
   passed `mcp_server_language=python` explicitly. The render was green; the derivation
   that would have chosen `python` on its own was still broken.

## The rule

> Derived defaults must be tested WITHOUT the `-d` override that would supply them.

Concretely, for every derived variable that gates a tree:

- keep one render configuration that sets *only the upstream inputs* and asserts the
  derived output appeared (the tree exists, no `__unchosen_*` residue survived);
- make CI rows that claim to test a feature **force the gate flag on** rather than rely
  on the derivation — and have a *separate* row that relies on it;
- treat "the render passed" as evidence only once the variables it depends on are
  known to be defined — an undefined variable can render as a loud non-zero exit or as a
  silently empty path depending on where it is consumed, and the audit should not
  assume which.

## Why it is easy to get wrong

Derived defaults are invisible at the prompt. Nobody answers them, so nobody notices
when a dead flag controls documentation but no files, or when a derived flag is OFF in
the configuration a CI row happens to use ([[Derived-and-Hidden Design Decisions]]). The
only place the derivation is observable is in a render that did not override it.

## See Also
- [[Asked vs Derived Scaffold Variables]] — extends (the asked/derived split this verifies)
- [[Derived-and-Hidden Design Decisions]] — extends (why derived flags go unnoticed)
- [[Read-Every-Consumer Migration]] — related (same session; a different class of falsely-green render)
- [[Verified Runtime Capability Constraint]] — related (a control counts only if the runtime demonstrably enforces it)
- [[AI Project Template Scaffold]] — instance-of
- [[Execute Every Toggle Configuration]] — extends (render and run each toggle combination, not just the default)
- [[Gate Coupled Features on the Producer, Not the Label]] — related
- [[Changing a Derived Default Is a Migration]] — extends (derived defaults are re-derived on every update)
