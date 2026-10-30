---
title: Execution-Made Decisions Leave Stale Invariants
tags: [patterns, pattern]
summary: "When execution quietly reverses a plan's resolved decision, the structure changes but the sentence stating the old invariant survives. The fix is reconciling docs, not migrating content again. The plan's own test-plan invariant is the cheapest detector, and a same-named file in two places is a different document until its content proves it is a copy."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/LAE-28-research.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--LAE-28-research.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/LAE-28-plan.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--LAE-28-plan.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-07-21-ai-engineering-foundations.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--2026-07-21-ai-engineering-foundations.md
---

# Execution-Made Decisions Leave Stale Invariants

Found in the learn-ai-engineering repo. An issue asked for "docs/ content" to be
integrated into the depth pillars. Research found that no `docs/` directory had ever
existed, that the integration had already happened, and that the work left was one false
sentence.

## The sequence

1. A plan **resolved** an architecture question: pillar READMEs would *point to* cleaned
   notes in a separate `interviewing/notes/` layer and never copy them. Its test plan
   encoded the invariant as a grep: `grep -rl 'origin:' ai-engineering/` must return
   nothing, meaning no note frontmatter inside pillar directories.
2. Execution **did the opposite**. The owner moved the note files physically into each
   pillar directory, which was a better fit for how the notes were used. No plan was
   updated, because nobody experienced it as a decision.
3. The crosswalk tables were updated to the new paths. But the root README kept the
   prose: *"No content is duplicated. READMEs link to `interviewing/notes/*.md` — they do
   not copy them."* That sentence now described an architecture the repo did not have.
4. A later issue saw the gap between the prose and the tree and asked for a content
   migration that had already been done.

The decision was real. It was simply made by execution instead of by the plan, and the
only trace it left was the invariant sentence that went false.

## What to do

- **Re-run the plan's invariant checks against the live tree.** The test-plan grep from
  step 1 returned a list of note files inside pillar directories. That one command proved
  the reversal. Test-plan invariants in old plans work as free drift detectors.
- **Scope the work as reconciliation, not migration.** Once the structure is confirmed as
  the intended one, the fix is to correct the stale sentence and record the decision that
  was actually made ("absorbed into pillars, not a separate layer") in every README that
  describes the architecture, in compatible wording. The plan came out as a single short
  session, much smaller than the issue implied.
- **Record the decision where the old one lived.** Otherwise the next reader of the
  original plan rebuilds the pointer model.

## Same filename is not duplication

Research also flagged two `observability.md` files, one in each pillar, as a diverged
duplicate: `diff -q` said they differed, and the diff ran to 254 lines. Planning read both
files. One was a 36-line generic note on trace and span concepts. The other was a 221-line
schema contract for a specific support-agent system, with its own title. They were **two
different documents that happened to share a filename**, not copies that had drifted. A
cross-reference elsewhere in the repo already described the second file correctly. Only its
own pillar README described it wrongly.

The resolution was a scope-explicit rename and a README correction, not a merge. A merge
would have mixed a concept note into a schema contract. The general rule: a large diff
between same-named files is evidence of two documents as often as of drift. Compare titles
and purpose before choosing between dedupe and rename.

The same research left "support-agents" content as an open unknown because nothing was
filed under that name. Planning found the content spread across eval and RAG notes under
system-specific names. **Searching by the issue's vocabulary misses content filed under
the system's own names.**

## See Also
- [[Stated Seams Drift, Enforced Seams Hold]] — extends (a stated invariant with no enforcing check goes false; here the check existed in a plan but was never re-run)
- [[Design Decisions Migrate Into Plans]] — alternative-to (decisions leaking downward into plans, versus decisions leaking out of plans into execution)
- [[AI Engineering Curriculum Structure]] — instance-of (the absorbed-into-pillars layout this reconciled)
- [[No-Placeholder Plan Discipline]] — related (verification steps that check structure when the deliverable is markdown)
