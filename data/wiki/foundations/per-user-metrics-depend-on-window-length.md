---
title: Per-User Metrics Depend on Window Length
tags: [foundations, pattern]
summary: Any metric with the user as its unit grows with the observation window because users get more chances to return, so comparing periods of unequal length manufactures a change; match windows or use sessions.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--04-funnel-and-conversion.md
---

# Per-User Metrics Depend on Window Length

A per-user conversion appeared to fall from 11.34% to 9.94% while per-session conversion rose (7.48% to 7.60%). The two periods ran 198 and 108 days: the longer window gave each user more chances to return and buy, inflating the per-user rate (sessions per user 1.57 vs 1.34).

Over equal 108-day windows either side of the change, per-user conversion was 9.43% before and 9.94% after, moving the same way as per-session. A tool's default "users" report has the same flaw.

Rules:
- Compare equal windows, ideally same weekdays and season.
- Sessions suit steps within a visit (the unit does not grow with the window); per-user rates suit decisions about people.
- Sessions of one user are correlated, so session-level intervals are too narrow; with a large effect (13x the interval half-width) it does not matter, with a small one analyse by user.

## See Also
- [[Funnel Step Diagnosis]] — related
- [[Clustered Standard Errors]] — related
- [[Inspection Paradox in Metrics]] — related
