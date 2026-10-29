---
imported_hash: cc72adff216a4fe0
title: FRONTEND.md
summary: This file defines stable frontend expectations so agents do not invent UI patterns unpredictably.
order: 33
kind: reading
section: Templates / Openai repo template / Docs
source: learn-ai-engineering/ai-engineering/03-harness-engineering/templates/openai-repo-template/docs/FRONTEND.md
---

# FRONTEND.md

This file defines stable frontend expectations so agents do not invent UI
patterns unpredictably.

## UI Principles

- Optimize for clarity before novelty.
- Keep interaction flows discoverable and restartable.
- Prefer a small number of reusable components over one-off variants.
- Accessibility checks are part of normal verification, not polish work.

## Guardrails

- Document the design system or component library in `docs/references/`.
- Record key user-facing states: empty, loading, success, error, retry.
- Keep copy, keyboard behavior, and visual hierarchy consistent across flows.
- When a UI bug is fixed, add or update the matching validation step.

## Verification Expectations

- Capture evidence for critical user journeys.
- Record browser or runtime validation steps in the relevant plan.
- If visual regressions are common, standardize screenshot or DOM checks.
