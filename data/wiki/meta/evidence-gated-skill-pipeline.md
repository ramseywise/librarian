---
title: Evidence-Gated Skill Pipeline
tags: [meta, llm, pattern]
summary: A chain of single-purpose Claude Code skills (scan → capture → research → match-gap → rank → tailor → review → convert) over one evidence store, where every downstream skill refuses to run without the upstream analysis section, a `[VERIFY]` tag travels with unconfirmed claims, and the honest gap list is treated as the point of the pipeline rather than a defect to soften.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/job-system/skills/capture-job/SKILL.md
  - data/raw/claude-docs/job-system/skills/convert-cv/SKILL.md
  - data/raw/claude-docs/job-system/skills/interview-prep/SKILL.md
  - data/raw/claude-docs/job-system/skills/match-gap/SKILL.md
  - data/raw/claude-docs/job-system/skills/rank-preferences/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/rank-preferences/SKILL.md
  - data/raw/claude-docs/job-system/skills/refresh-jobs/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/refresh-jobs/SKILL.md
  - data/raw/claude-docs/job-system/skills/research-company/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/research-company/SKILL.md
  - data/raw/claude-docs/job-system/skills/review-materials/SKILL.md
  - data/raw/claude-docs/job-system/skills/scan-sources/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/scan-sources/SKILL.md
  - data/raw/claude-docs/job-system/skills/tailor/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/capture-job/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/convert-cv/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/interview-prep/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/match-gap/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/review-materials/SKILL.md
  - data/raw/claude-docs/sisyphus/skills/tailor/SKILL.md
  - data/raw/claude-docs/job-system/docs/plans/2026-07-23-job-system-enhancement.md
  - data/raw/claude-docs/sisyphus/docs/plans/2026-07-23-job-system-enhancement.md
  - data/raw/repos/sisyphus/.claude--docs--plans--2026-07-23-job-system-enhancement.md
  - data/raw/claude-docs/job-system/docs/plans/2026-07-25-JOB-15-19-pipeline-work.md
  - data/raw/claude-docs/sisyphus/docs/plans/2026-07-25-JOB-15-19-pipeline-work.md
  - data/raw/repos/sisyphus/.claude--docs--plans--2026-07-25-JOB-15-19-pipeline-work.md
  - data/raw/repos/sisyphus/CLAUDE.md
---

# Evidence-Gated Skill Pipeline

The job-system repo (also vendored as `sisyphus`) is a chain of ten small skills that turn
a list of postings into tailored application documents. Its subject is incidental; the
design is a reusable way to build a document-generation pipeline that cannot fabricate.

## One evidence store, many readers

Every claim any skill may make about the author lives in a single `evidence-store.md`,
alongside a numbered `guardrails.md` that the skills cite by rule number. No skill creates
evidence; if the user discovers uncaptured experience, they edit the store directly and
re-run. Skills that *write* (tailor, interview-prep, review) are told to use evidence-store
claims only — no invented metrics, no upgraded titles, no merged roles across employers.

## The `[VERIFY]` tag travels

A claim in the store that is real but unconfirmed in exact wording carries `[VERIFY]`.
Each stage has an explicit policy for it:

| Stage | `[VERIFY]` claims |
|---|---|
| match-gap (scoring) | may count toward fit, but are marked in the output |
| tailor (CV / letter) | **excluded entirely** |
| interview-prep | usable in a scaffold, tag carried forward so the user confirms before saying it aloud |
| review | gaps discovered get flagged as `[VERIFY]` additions, not silently fixed |

The tag is how uncertainty crosses skill boundaries without being laundered into fact.

## Downstream skills refuse without upstream sections

`tailor`, `rank-preferences` and `interview-prep` all begin with the same precondition: if
the brief has no `## Match / Gap analysis` section, **stop** and tell the user to run
`match-gap`. Rationale per skill: "never tailor blind"; "preference ranking without a fit
score has no anchor"; "no prep without analysis". Analysis is appended to the *same* brief
file so brief and analysis travel together, and the presence of the section is the gate.

## Capture and scoring stay separated

`capture-job` and `refresh-jobs` extract and normalize only — "no fit scoring, no
tailoring". `scan-sources` populates an inbox and nothing more. `research-company` reports
facts and is told not to editorialize fit ("let the pipeline score"). Each skill ends with
an **"Explicitly out of scope"** section naming the sibling skill that owns the excluded
concern, which is how the chain stays composable.

## The gap list is the product

`match-gap` requires matches to be real correspondences, not stretches — the same
technology name matches, two different technical job titles do not — and puts unmatched
requirements in a Gaps list that must not be softened or omitted: "the gap list is the
point"; "never let a 'close enough' match slide into Matched to make the tier look
better." The fit tier is a ratio of matched must-haves, not a fabricated percentage.
`tailor` may address one obvious gap honestly rather than ignore it, and never spins a gap
as a strength.

## Smaller mechanics worth reusing

- **Source-specific intake**: known ATS platforms are fetched directly; a platform that
  blocks scraping triggers "ask the user to paste the text" rather than a failed fetch.
- **Dedup on identity, not URL**: same company + role collapses even when URLs differ,
  with a flag that it may be a repost.
- **Sensitive-data stripping at capture** (tracking params, accidentally pasted contact
  details) so nothing downstream has to.
- **Two-lens review** (domain specialist, then editor), each dimension scored separately,
  with fixes applied only on approval and the voice preserved — "improve clarity, not
  rewrite personality."
- **Rendering is its own skill** (`convert-cv`) that never modifies the source document
  and fails with a clear error when the renderer is missing.

## Later additions in the sisyphus copy

- **Question ids survive regeneration.** The interview-prep generator must carry each
  question's stable qid (an HTML comment stamped by the drill skills) through rewrites:
  same test reworded keeps it; a question rewritten to test something else loses it and
  the old id is retired, so the drill history log never points at a different question.
  See [[Graded Rehearsal Drill Harness]].
- **The convert step verifies its own render.** A fixed-A4 template clips silently, so a
  one-page PDF is not proof of success; fill is measured from text extents and end-of-column
  keywords. See [[Verify a Render by Text Extents, Not Pixels]].

## Lessons from the pipeline-enhancement plans

- **A `[VERIFY]` item should resolve to "confirm or omit", not block.** Open items on the
  master profile (a profile URL, unverified metrics) were closed by the owner either
  supplying the fact or writing "omit until available" — so tailoring can skip the claim
  rather than stall on it.
- **Fit and preference are separate axes.** The gap analysis scores evidence alignment
  (Strong/Moderate/Weak); a role can be a strong fit and still unattractive, so a
  lightweight preference-ranking step was added beside it instead of folded into the score.
- **A fetch error is not an expiration.** On a refresh pass, 10 of 13 non-live postings were
  ERRORs, mostly ATS boards that render via JavaScript (Ashby, Lever) plus timeouts and rate
  limits; only 3 were genuinely expired. JS-rendered boards need browser capture, and the
  status vocabulary keeps ERROR distinct from EXPIRED.

## See Also
- [[Claude Workflow System]] — instance-of (a project-local skill family)
- [[Puffin Consciousness Development Skills]] — alternative-to (another chained skill family, with a different gating mechanism)
- [[Agent Scaffolding Skill Layers]] — related (skill layering)
- [[Evidence Classification Model]] — related (verified / supported / hypothesis as a finer-grained version of `[VERIFY]`)
- [[Grounding Claim Methodology]] — related (claims traced to evidence)
- [[Design Decisions Migrate Into Plans]] — extends
- [[Graded Rehearsal Drill Harness]] — extends (the rehearsal skills that drill this pipeline's interview-prep output)
- [[Verify a Render by Text Extents, Not Pixels]] — extends (how the convert step's silent-clipping failures were caught)
- [[Skill Admission Test: Workflow With a Gate]] — instance-of
