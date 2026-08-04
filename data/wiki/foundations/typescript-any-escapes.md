---
title: TypeScript any Escapes
tags: [foundations, reference]
summary: "The three ways out of an `any` — a real type, `unknown` with narrowing, or a generic — plus why types files are the highest-leverage place to fix them and how exhaustive-deps catches stale closures rather than style violations."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/programming--eslint.md
---

# TypeScript `any` Escapes

Most lint noise in a TypeScript codebase reduces to a small number of rules that are
actually about correctness rather than style. This page covers the two that are, and the
decision procedure for the first.

## Three escapes from `any`

When a lint rule flags `any`, there are exactly three fixes, in preference order:

| Escape | Use when | Cost |
|---|---|---|
| **A real type** | You know the shape | Write it once, get checking everywhere |
| **`unknown`** | The shape arrives at runtime — API responses, parsed JSON, caught errors | Must narrow before use |
| **A generic** | The function is genuinely shape-agnostic — it passes the value through | Signature complexity |

**`unknown` is `any` with the safety on.** Both accept anything on the way in; the
difference is that `unknown` accepts nothing on the way out until you narrow it. That is
precisely the right semantics for a value whose shape you do not control — an HTTP response
body, `JSON.parse` output, a `catch` binding. Reaching for `any` there is not a shortcut,
it is a claim you know something you do not.

The generic case is worth distinguishing because it is often mistaken for the `unknown`
case. If the function *inspects* the value, it needs `unknown` plus narrowing. If the
function only *moves* the value — a cache wrapper, a retry helper, a pipeline stage — it
needs a type parameter, because the caller knows the type and should get it back unchanged.

## Types files are the highest-leverage fix

Fixing an `any` inside a component fixes one call site. Fixing an `any` in a shared types
file fixes every consumer of that type simultaneously — and, more importantly, **surfaces
the errors that the `any` was suppressing** across the codebase.

That second effect is the reason to start there rather than to avoid it. An `any` in a
widely-imported type is not a localised untidiness; it is a hole through which unchecked
values propagate to every consumer. The apparent cleanliness of the consuming code is an
artefact of the checker having been switched off upstream.

The practical consequence is that fixing a types file is *not* a small change even though
it is a small diff — expect a wave of newly-visible errors, and treat that wave as the
actual work.

## `exhaustive-deps` is a correctness rule

The React hooks dependency-array rule is routinely disabled as pedantic. It is not a style
rule: a missing dependency produces a **stale closure**, where the effect or callback
captures the value from the render in which it was created and keeps using it after the
value has changed.

The failure is nasty because it is invisible in the common case. The captured value is
usually correct on first render, so the bug appears only after an update — and only for
whichever variable was omitted. Symptoms are "the handler is using the old state," "the
fetch sends yesterday's filter," and other effects that read like race conditions but are
deterministic.

The reason the rule gets disabled is that satisfying it sometimes causes an effect to re-run
more than intended. That is a signal the effect is doing two things, or that a dependency
should be a ref, or memoised — not that the rule is wrong. **Suppressing the warning
resolves the lint error while leaving the stale closure in place**, which is the worst of the
available outcomes: the code now asserts that the dependency list is correct.

## See Also
- [[Git Branch Triage]] — complements (the other half of the day-to-day tooling reference)
- [[Data Science Curriculum Layers]] — complements (the programming-tooling layer beneath the curriculum)
