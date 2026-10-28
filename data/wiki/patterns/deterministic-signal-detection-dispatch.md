---
title: Deterministic Signal Detection for Dispatch
tags: [patterns, llm, pattern]
summary: Replacing the LLM question "is this agent code?" with a fixed set of content and path regexes whose hits are guidance for which specialist reviewers to dispatch — accepting a medium false-negative risk because the cost of a false positive (extra scrutiny) is benign and the cost of non-determinism is an unauditable review.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-27-signal-detection.md
---

# Deterministic Signal Detection for Dispatch

A multi-dimension review needs to decide which specialist checklists apply to a given
change — does this diff touch agent orchestration, tool definitions, prompt text? The
obvious implementation is to ask the model. The guacamayo signal-detection research
rejected that in favour of a deterministic detector, modelled on the Parallax review
system's `profile_detection.py`: **11 content regexes and 2 path regexes**, each
mapping to a named signal.

## Why regex over the model

- **Reproducibility.** The same diff always raises the same signals, so a verdict can
  be recomputed and a dispatch decision audited. An LLM classifier's answer varies with
  phrasing, temperature, and context length, and a review whose scope depends on it
  cannot be reproduced.
- **Cost.** Detection runs before any reviewer is spawned; a model call here is paid on
  every review, including the many that touch no agent code.
- **Asymmetric error costs.** A **false positive** dispatches a specialist reviewer that
  finds nothing — extra scrutiny, benign. A **false negative** skips a checklist that
  should have run. The research rates FP risk LOW and FN risk MEDIUM, and accepts the
  trade because the FN case has a recovery path: the general reviewer can raise the
  signal itself and trigger a second round ([[Corrective Follow-Up Dispatch]]).

## Signals are guidance, not a gate

A raised signal says "dispatch this dimension"; it does not say "block if this
dimension is absent". Keeping signals advisory means a regex miss degrades the review
rather than failing it, and lets the operator override dispatch without editing the
pattern table. The same stance — deterministic input, advisory output — appears in
[[Cross-Sweep Finding Fingerprint]]'s promotion rules.

## Maintaining the pattern table

Patterns are derived from the corpus of past findings, not anticipated: a signal is
added when a class of change has repeatedly needed a specialist and the detector missed
it. This mirrors the n ≥ 3 rule for recurrence signatures in the
[[Falsifiable Hypothesis Gate]], and for the same reason — a pattern added on
speculation fires on nothing and erodes trust in the table.

## See Also
- [[Corrective Follow-Up Dispatch]] — extends (the recovery round when `detect-signals` misses)
- [[Parallel Dimension Scanner Architecture]] — prerequisite-for (which dimensions to run)
- [[Deterministic Review Substrate]] — extends (same determinism preference, applied before review rather than within it)
- [[Scope-Gated Reporter Dispatch]] — alternative-to (declared scope vs detected signals as the dispatch input)
- [[Agent Quality Review Checklist]] — extends
