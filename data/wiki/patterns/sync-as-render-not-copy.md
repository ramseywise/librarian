---
title: Sync as Render, Not Copy
tags: [llm, patterns, pattern]
summary: When one canonical source ships into a second tree that addresses it differently, the sync must transform link targets and variable names rather than mirror bytes — a byte-for-byte copy cannot serve both contexts, and hand-copied files drift backwards.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-agents-skills-sync.md
---

# Sync as Render, Not Copy

Seven files in a template tree were byte-identical to their reservoir originals —
hand-copied, covered by no sync script. The sync script that existed had **zero
references** to that directory, so those files rotted exactly the way earlier
unsynced entries had.

## Drift runs backwards

The failure mode is not simply "the copy falls behind." Here it ran the other
direction: the *template's* `framework-selection` was **newer than the
reservoir** — it carried an entire third framework (Vercel AI SDK), a
runtime-first decision branch, and a 3-way comparison table that canon did not
have.

A hand-copied file is not a stale replica; it is an **unmanaged fork**. Someone
edits whichever copy they happen to be in, and after enough sessions neither tree
is authoritative. Resolving it required promoting the template version *to* canon
rather than overwriting it.

## The proof that it is a render

> **The sync is a RENDER, not a copy.** Proven by the promotion diff: the two
> contexts need different link targets. Global says "read `adk-scaffold.md`"; the
> template must say "invoke `.agents/skills/adk-scaffold/SKILL.md`". A
> byte-for-byte mirror cannot serve both.

Two real transforms, each verified against the hand-maintained copy:

1. **Link rewriting** — canon is a flat directory (`adk-scaffold.md`); the
   template nests skills (`.agents/skills/adk-scaffold/SKILL.md`). Applied to
   skills only; flat references stay flat in both trees, so their links already
   resolve.
2. **Copier variable substitution** — `source_root` → `py_project_root/ai_source_root`.

### The adjacent-forms bug

The variable transform carries a subtle defect worth recording. Canon writes the
variable **both braced** (inside an example path) **and bare** (in the prose
sentence right after it), on adjacent lines. The first implementation substituted
only the braced form — leaving a sentence that named a variable its own example
no longer used.

Order matters in the fix: **braced first**. The reverse order would nest
`{py_project_root}/{ai_source_root}` inside the outer braces.

## Two destinations, decided by what the directory promises

The 28 files did not all render the same way, and the deciding evidence was the
destination's own README, which declares it a curated *framework reference
library* — "durable framework knowledge that outlives any one tool":

| Source | Destination | Why |
|---|---|---|
| 7 framework/scaffold docs | `.agents/skills/<name>/SKILL.md` | Genuine skills; frontmatter already hand-authored in canon, **copied verbatim rather than synthesized** |
| 21 code-gen payload files | `.agents/references/<name>.md` | Flat, no frontmatter |

Rendering all 28 as skills would have meant **inventing 21 descriptions** and
diluting a directory whose README makes a specific promise. A hand-written
description beats a guessed one — and the Apache-2.0 attribution block on two
Google-derived skills must survive the render, which synthesis would silently
drop.

## Renderer conventions that make it safe

- **Hard-fail on missing names** — a renamed source breaks the sync loudly
  instead of silently shipping nothing.
- **Per-file diff before overwrite**, plus `--dry-run`.
- **Reverse check** (absent from the older script): a reservoir file listed in
  *neither* array warns loudly, since it would otherwise silently never ship.
  **Warn, not fail** — adding a reference upstream shouldn't break an unrelated
  sync.
- **Idempotent re-run**, verified.

Verification standard: 6 of 7 skills reproduced the hand-maintained files
byte-for-byte, and the seventh differed only by the intentional promotion edits.
Nothing needed deleting — the renderer produces a **superset** of what was there.

## Fix defects at canon, before mirroring

A full mirror stamps every canon defect into every scaffolded project, so the
security fixes landed *first*. See [[Payload Security Defects at Canon]].

## The accepted tradeoff, recorded

The mirror is **all 30 files, not a per-capability subset** — the simplest
script, shipping ~11k lines into every scaffolded project regardless of relevance.
The tradeoff was accepted deliberately, with an explicit instruction to **record
it in the script header so it doesn't read as an oversight later.** A deliberate
cost that looks identical to an accident unless someone writes down which it was.

## See Also
- [[Payload Security Defects at Canon]] — prerequisite-for (fix before mirroring)
- [[Capability Runtime-Coupling Tiers]] — extends (what gets rendered)
- [[Copier Upstream Update Workflow]] — alternative-to (pulling template changes downstream)
- [[Template Migrations for Structural Moves]] — complements
- [[AI Project Template Scaffold]] — instance-of
- [[Multi-Repo Claude Organization]] — prerequisite-for (the reservoir/template layering)
