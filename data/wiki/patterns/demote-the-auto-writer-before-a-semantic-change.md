---
title: Demote the Auto-Writer Before a Semantic Change
tags: [patterns, infra, pattern]
summary: "Before changing semantics that an automated writer depends on, take away the writer's ability to write into the corpus and route its output to a suggestions file. A resolution regression then lands somewhere it can be inspected and discarded, not baked into the data. Gate the change itself on a measured blast radius recorded as a number."
updated: 2026-10-17
sources:
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-04-LIB-110-restructure-shared-extraction.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-05-LIB-106-relinker-suggest-only.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-04-staff-review-fixes.md
---

# Demote the Auto-Writer Before a Semantic Change

From librarian's slugify unification (2026-08). Two slug functions resolved wikilinks
differently:

- **A** lower-cased and replaced spaces: `"RAG & Retrieval"` became `rag & retrieval`.
- **B** collapsed every non-alphanumeric run to a dash, giving `rag-retrieval`.

The refactor would make B the only function. At the time, the relinker **auto-appended
links directly into wiki pages** based on those slugs.

## The sequencing argument

The two changes touched different lines of the relinker, so textual conflict was minor.
The order mattered for another reason. If slug semantics changed while the relinker could
still write, any resolution regression would **write itself into the corpus**. Reverting
the code would not undo the links already written, so the change could not be cleanly
rolled back. Once the relinker became suggest-only, the same regression would land in
`_relink_suggestions.md`, where it could be inspected and discarded.

So the small change (remove both page-write paths) went first, and the risky semantic
change was gated on it. During execution the gate was re-checked at two review
boundaries. Both times the semantic step was correctly refused because the writer still
had write access. It ran only after the demotion merged.

**Rule:** a change that can corrupt data through a downstream writer is destructive. The
same change made after that writer is demoted to proposing is reversible. Demote first.

## Gate the change on a number

The plan had assumed existing tests "pin the behaviour, making extraction mechanical".
That turned out to be false. Every fixture title was clean alphanumeric text, which gives
identical output under both functions and cannot expose the difference (see
[[Characterization Pins Before Extraction]]). So the work ran in this order:

1. **Write characterization tests** asserting the current output of A and B on the inputs
   where they differ: punctuation, apostrophes, unicode, double spaces, leading or
   trailing punctuation.
2. **Measure the blast radius over the live corpus.** Over 284 pages and 2,948 links:
   24 titles slug differently, but each one's kebab-case file stem already equals its
   B-slug, so the stem fallback resolves it either way. **0** links resolve under A but
   not under B. **1** link resolved only under B, a stray trailing backslash that B strips.
   B was a strict improvement.
3. **Done-when is a number, not an estimate.** The plan's gate was "if that number is
   large, stop and reopen the choice." After unification the same script was re-run and
   reported 0 newly unresolvable links.

## Delete the fallback that papers over the divergence

The MCP server already chained B with an explicit A fallback
(`slug_to_path.get(slug) or slug_to_path.get(raw.lower().replace(" ", "-"))`). Someone had
hit the divergence in production and patched around it instead of fixing it. That fallback
is the bug's fingerprint. It was deleted as part of unification, because leaving it in
place makes the unification impossible to verify: the fallback quietly resolves exactly
the cases the change is supposed to prove.

## See Also
- [[Wiki Graph Engineering — Edge Quality Over Edge Count]] — extends (the relinker suggest-only decision this depends on)
- [[Characterization Pins Before Extraction]] — prerequisite-for (pin both variants before collapsing them)
- [[Arm Unattended Writers by Risk Type]] — extends (disarm by risk type; here, disarm by sequencing)
- [[Read-Only by Default with Explicit Authorization]] — extends (writers propose, humans apply)
- [[Fallback Mistaken for the Design]] — extends (a compatibility fallback hides the divergence it patches)
