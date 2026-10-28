---
title: Topic-Lifecycle Docs Layout
tags: [meta, decision]
summary: Grouping agent working docs by artifact type (research/, plans/, reviews/) quietly disconnects them; grouping by topic and lifecycle stage (scope/, build/, backlog/, reference/, archive/) with a cascade archive and a review-to-plan write-back keeps research, plan and review findings attached.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/archived/docs-restructure/research.md
---

# Topic-Lifecycle Docs Layout

A restructure of the `.claude/docs/` folder in the playground repo (2026-04), decided
after a full inventory of 32 docs and their cross-references.

## The three failures of type-grouping

The old layout sorted artifacts by kind: `research/`, `plans/`, `reviews/`. Each folder
was tidy. The relationships between them were not.

1. **Reviews didn't feed back into plans.** Two reviews returned "Needs changes" and
   neither set of findings ever reached its plan. The review skill was terminal: it wrote
   a file and stopped. The one review that did close the loop improvised a
   "post-review fixes applied" section inside the review itself.
2. **Research got orphaned.** Six research docs had no plan written against them, and
   one plan was filed under `research/` by mistake.
3. **The index couldn't keep up.** A hand-maintained INDEX.md had six broken paths and
   stale status markers. It was trying to track by hand relationships that the
   directory structure should have enforced.

Research, planning and execution all had iteration phases. Review was the only stage
with no way back. That gap is the real defect, and the layout made it invisible.

## The layout

```
scope/<topic>/research*.md     # what to build and why; stays live through review
build/<topic>/plan.md          # how; cites scope research by path
build/<topic>/review.md        # did we build it right
backlog/<topic>/plan.md        # blocked or deferred
reference/<name>.md            # evergreen: stack audits, tradeoff logs
archive/<topic>/{scope,build}/ # cascade-moved when the review resolves
```

## Key decisions

- **Topic is the grouping unit.** One topic's research, plan and review sit together,
  rather than being matched across three folders by filename convention.
- **Scope stays live until the review resolves, not until the plan is written.** Scope
  research is reference material during execution. It archives only in a single
  **cascade** with its build, triggered when the review is Approved or all blocking
  findings are resolved.
- **One scope feeds many builds.** Scope topics are deliberately broader than build
  topics: one infrastructure research doc fed both a restructure plan and a CI/CD plan.
  Don't force 1:1. Build plans cite the scope sections they use.
- **Reference is separate from scope.** Evergreen docs have no build target and never
  enter the lifecycle.
- **The review writes back to the plan.** When the verdict isn't approved, `/code-review`
  appends a `## Review Findings` section to `plan.md`, with a status per finding
  (open / addressed / deferred / won't-fix). Three options were weighed:
  - a convention in CLAUDE.md, rejected because two existing reviews had already shown
    it gets skipped;
  - a PostToolUse hook, rejected because it would fire on every write;
  - a skill enhancement, chosen because the skill already reads the plan during review,
    so writing back costs almost nothing.

The research's own verdict was that the write-back mattered more than the folders.
Without it, the new structure would just be a prettier version of the same
disconnection.

## See Also
- [[Claude Workflow System]] — extends (the research → plan → execute → review pipeline these folders hold)
- [[Plan-Doc Status Enum]] — related (status vocabulary inside the plan docs this layout files)
- [[Contract-Anchored Findings Get Fixed]] — related (what makes a review finding land once it reaches the plan)
