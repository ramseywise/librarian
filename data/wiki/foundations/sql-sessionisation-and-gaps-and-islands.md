---
title: SQL Sessionisation and Gaps-and-Islands
tags: [foundations, pattern]
summary: "Two window tricks for grouping consecutive rows without loops: a running sum of gap flags numbers sessions, and a running index minus row_number is constant along an unbroken run so it serves as an island key."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--06-sql-for-analytics.md
---

# SQL Sessionisation and Gaps-and-Islands

Both solve "group consecutive rows until a condition breaks".

## Sessionisation

A session starts after, say, 30 minutes without activity. Compare each event with the previous using a lag window per user, flag starts (no previous event, or gap over the threshold), then a running sum of the flags numbers the sessions. On 29,782 page views this recovered all 5,974 true sessions without splitting or merging one, only because the simulated sessions were well separated. Threshold changes the count: 15 minutes found 6,127 (splits long sessions), 60 minutes found 5,894 (merges separate sessions). No threshold is right in general; real data has no ground truth column, so inspect the gap distribution and report sensitivity.

## Gaps and islands

To find streak lengths (consecutive active months), number each customer's active months with row_number and subtract it from a running month index (year x 12 + month). Along an unbroken run both rise by one, so the difference is constant; a skipped month makes it jump. Group by customer and difference for streak length and start. In the example 36,135 streaks lasted one month and only 87 lasted six; 54,651 active customer-months formed 43,370 streaks, so consecutive-month buying is rare.

## See Also
- [[SQL Window Functions]] — prerequisite-for
- [[SQL Date Spine and Window Frames]] — related
- [[Revenue Bridge Query]] — related
