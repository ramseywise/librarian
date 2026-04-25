---
name: sprint-balancing
description: >
  Use this skill to review and rebalance sprint milestone assignments in a Linear project.
  Triggers include: "review my sprint balance", "check if my sprints are overloaded",
  "which issues should be stretch goals", "are my sprint assignments realistic given dependencies",
  "check my dependency order", "are cross-track sync points correct", or any request to
  sanity-check a milestone plan against team capacity, dependency order, and sprint dates.
  The skill checks story point totals per sprint, flags sequential dependency chains that
  exceed sprint capacity, maps dependency order within and across tracks, identifies
  cross-track sync points, and verifies milestone target dates align with the sprint calendar.
---

# Sprint Balance & Dependency Review

## Overview

This skill reviews sprint milestone assignments in a Linear project across three dimensions:

1. **SP load** — is each sprint within the team's capacity target?
2. **Dependency order** — are issues sequenced correctly within each track, and are cross-track sync points identified?
3. **Date alignment** — do milestone target dates align with the sprint calendar?

## Inputs to gather

Before starting, confirm:

- **Team structure** — how many people, and how are they split across tracks? (e.g. "2 juniors on separate tracks, 1 senior floating")
- **Sprint length** — how many working days per sprint? (default: 10)
- **Sprint start date** — when does the first sprint begin?
- **Capacity target** — total SP per sprint. If tracks are owned by individuals, capacity = SP per track per person. If shared, capacity = team_size × days × ~1 SP/day.
- **SP-to-days conversion:**
  - 1 SP = 0.5 day (XS)
  - 3 SP = 1.5 days (S)
  - 5 SP = 3.5 days (M)
  - 8 SP = 6 days (L — flag and suggest splitting)

---

## Part 1 — SP Load Check

### Step 1: Read milestones

Use `Linear:get_project` with `includeMilestones: true` to read all milestones. For each:
- List all issues assigned to the milestone, noting main vs stretch
- Fetch SP estimate for each issue
- Note which track each issue belongs to (if tracks are documented)

### Step 2: Sum SP per sprint per track

For each sprint, sum main SP per track and compare to per-person capacity.

| Status | Condition |
|--------|-----------|
| ✅ On target | Track SP within ±20% of per-person capacity |
| ⚠️ Over | Track SP > per-person capacity + 20% |
| ⚠️ Under | Track SP < per-person capacity - 30% (check for carry-overs from prior sprint stretch) |

**Note on carry-overs:** If a prior sprint has stretch goals, assume they carry into the next
sprint when assessing load. A sprint that looks under-loaded may be absorbing stretch carry-over.

### Step 3: Flag sequential chain overflows

Within each track, identify chains of issues where each depends on the previous (A→B→C→D).
For each chain:
1. Sum the chain SP
2. Convert to days
3. **Flag if chain days > sprint days** — issues at the tail of the chain cannot realistically complete

Issues at the end of chains longer than the sprint window are **stretch candidates**.

---

## Part 2 — Dependency Order Check

### Step 4: Build the dependency map

For each issue in the sprint, fetch its `blockedBy` relationships using `Linear:get_issue`
with `includeRelations: true`. Build a dependency map across all tracks in the sprint.

### Step 5: Check ordering within each track

For each track, verify that issues are listed in dependency order — no issue appears before
its blocker. If ordering is wrong, flag it and suggest the corrected sequence.

**Common pattern to catch:** An issue that depends on a cross-track item being listed
too early. Example: VIR-108 (depends on VIR-114 from Track 1) listed first in Track 2 —
it should be last.

### Step 6: Identify cross-track sync points

Cross-track sync points are places where one track must wait for the other before proceeding.
For each one, document:
- Which issue in Track A unblocks which issue in Track B
- Roughly when in the sprint this handoff happens (early / mid / late)

Format sync points clearly in the milestone description so the team can coordinate:
```
⏳ wait for VIR-111 (Track 2) before starting VIR-112
```

**Zigzag pattern** (common in parallel tracks): Track A unblocks Track B, then Track B
unblocks Track A again. Name these explicitly — they are coordination risk points.

### Step 7: Check stretch-blocks-main across sprints

For each issue marked **stretch** in sprint N:
1. Check if any issue in sprint N+1 **main** depends on it
2. If so, flag the sprint N+1 main issue as at-risk — it should either be moved to stretch,
   or the sprint N stretch should be promoted to main

---

## Part 3 — Date Alignment

### Step 8: Build the sprint calendar

From the sprint start date and sprint length, compute the end date for each sprint:
- Sprint 1: start → start + sprint_days
- Sprint 2: Sprint 1 end + 1 → Sprint 1 end + sprint_days
- etc.

### Step 9: Check milestone target dates

For each milestone, compare its `targetDate` to the corresponding sprint end date.

| Status | Condition |
|--------|-----------|
| ✅ Aligned | Milestone date = sprint end date (±3 days) |
| ✅ Acceptable | Milestone date is after sprint end (milestone can close after sprint ends) |
| ⚠️ Early | Milestone date is before sprint end — team won't have finished the sprint yet |
| ⚠️ Misaligned | Milestone date falls mid-sprint of the wrong sprint number |

If dates are misaligned, suggest updated target dates using `Linear:save_milestone`.

---

## Step 10 — Produce recommendations

Output a sprint-by-sprint summary:

```
Sprint N [dates] — Track 1: X SP | Track 2: Y SP | Capacity: Z SP/person
Milestone: [name] target [date] — ✅ aligned / ⚠️ [issue]

SP issues:       [none / list overloaded or under-loaded tracks]
Order issues:    [none / list misordered issues with correction]
Sync points:     [list cross-track handoffs with timing]
Stretch risks:   [list stretch goals that block next sprint's main work]
```

Then ask: **"Apply these changes? (yes / no / edit first)"**

If yes:
- Update milestone descriptions with corrected track ordering and sync point annotations
  using `Linear:save_milestone`
- Update milestone target dates where misaligned

---

## Worked example (HC/VA Eval & Improvement workstream)

**Team:** 2 juniors on separate tracks, 1 senior floating. 10-day sprints, ~30 SP/sprint.

**Sprint 2 — SP flag:**
Track 1 chain: VIR-102(5)→103(3)→104(3)→106(5)→107(3) = 19 SP = ~13 days.
Tail issues VIR-106 and VIR-107 can't complete in a 10-day sprint. Moved to Sprint 3 stretch.
Sprint 2 main dropped to 20 SP; with Sprint 1 carry-overs (VIR-98+101 = 10 SP) → 30 SP total.

**Sprint 3 — dependency order flag:**
Track 2 was listed as: VIR-108, VIR-125, VIR-111, VIR-116, VIR-113.
VIR-111 should be first (it unblocks Track 1's VIR-112). VIR-108 should be last
(it waits for Track 1's VIR-114). Corrected order: VIR-111→116→113→125→108.

Cross-track sync points identified:
1. Track 2 does VIR-111 first → unblocks Track 1 VIR-112 (early sprint)
2. Track 1 finishes VIR-112 → unblocks Track 2 VIR-113 (mid sprint)
3. Track 1 finishes VIR-114 → unblocks Track 2 VIR-108 (late sprint)

**Date alignment:**
Sprint 1 end: May 8 → Milestone 1 target: May 8 ✅
Sprint 2 end: May 22 → Milestone 2 target: May 22 ✅
Sprint 3 end: Jun 5 → Milestone 3 target: Jun 5 ✅
Sprint 4 end: Jun 19 → Milestone 4 target: Jun 12 ⚠️ (early — milestone falls mid-sprint)
                      → Milestone 5 target: Jun 26 ✅ (acceptable post-sprint close)

---

## Notes on this workstream

- Sprint capacity = 30 SP total (2 juniors × ~15 SP/track + senior float)
- Story points: 1 SP = XS, 3 SP = S, 5 SP = M
- External dependencies (legal sign-off, domain expert availability) should be kicked off
  on day 1 of their sprint — never leave external blockers for mid-sprint
- Annotation guidelines and masking sign-off are examples: both should be Sprint-start tasks
- Cross-track sync points are highest coordination risk — senior float should actively
  manage handoffs at each sync point
- Milestone dates can be after sprint end — allow 1–3 days for milestone closeout tasks