# Wiki Templates

Templates and tables moved out of `CLAUDE.md`. The rules that point here live in `CLAUDE.md`.

## Source Confidence

All raw sources may include an optional `confidence` field in frontmatter:

| Level | Sources | Treatment during ingest |
|-------|---------|------------------------|
| `high` | Own design docs, CLAUDE.md, verified decisions | Claims become wiki assertions |
| `medium` | Documentation, articles, meeting notes | Claims added with attribution (default if omitted) |
| `low` | Web scrapes, unverified transcripts | Claims marked provisional |

When a `low` confidence source contradicts a `high` confidence wiki claim, flag the conflict but note the disparity. When a `high` confidence source contradicts `medium`, update the wiki and note both sources. Default to `medium` if the field is absent.

**Self-reported claims:** when a source makes a claim about itself (a vendor about its product, an author about their own tool) and nothing independent confirms it, name the source and write "(self-reported)" inline straight after the claim. This holds whatever the source's confidence level.

## Tombstone Page

A page removed by compaction is never deleted — it becomes a **tombstone**: same
filename (inbound wikilinks stay valid), `tombstone` added to tags, body reduced to one
line pointing at its successor:

```markdown
---
title: Old Page Title
tags: [rag, tombstone]
summary: Retired — superseded by Successor Page.
updated: YYYY-MM-DD
sources: [...unchanged...]
---

# Old Page Title

Retired YYYY-MM-DD. See [[Successor Page]] — supersedes.
```

Tombstones are excluded from the search index (MCP server skips `tombstone`-tagged
pages at build time) but remain readable via `read_page`. They are exempt from orphan
rules. Only `/compact-wiki` creates tombstones.

## Conflict Entry (`data/wiki/_conflicts.md`)

When a new source contradicts an existing wiki claim:

1. **Do not silently overwrite** the existing claim.
2. Add an entry to `data/wiki/_conflicts.md`:

```markdown
## Conflict: [Topic] — [YYYY-MM-DD]

**Claim A** (from `[[Existing Page]]`, sourced from `data/raw/...`):
> Exact quote or paraphrase of claim A

**Claim B** (from new source `data/raw/...`):
> Exact quote or paraphrase of claim B

**Status:** Unresolved — needs human review
**Impact:** [which projects or decisions does this affect?]
**Would settle it:** [the source, measurement or test that would decide between the claims]
```

3. Tag the affected page with `conflict` in frontmatter.
4. During lint, surface all unresolved conflicts.

## Conflict Resolution (human review step)

To resolve a conflict in `data/wiki/_conflicts.md`:

1. Read both claims and their source files.
2. Determine which is correct — or synthesise both if both are partially right.
3. Update the affected wiki page with the correct/synthesised claim; cite both sources.
4. Mark the conflict entry resolved:

```markdown
**Status:** Resolved — [YYYY-MM-DD]
**Resolution:** Claim A was correct; Claim B referred to a different threshold (chunk-level vs. reranker-level). Updated [[Affected Page]] to distinguish both contexts.
```

5. Remove the `conflict` tag from the page frontmatter.
6. Run `/lint` to confirm no remaining unresolved conflicts.

## Ingest Examples

Things that get their own page (ingest step 3): `semantic caching`, `RRF fusion`, `inter-annotator agreement`, `prefix caching`, `CRAG retry loop`, `HistoryCondenser`. Rule of thumb: if it has a name and a non-obvious mechanism, it gets a page. Do NOT bury these as bullets inside a coarser page — they become nodes in the graph only if they are pages.

Typed relink candidates are added manually in this shape: `- [[Page]] — extends`. Adding untyped links is what the graph already has too many of (see `data/wiki/meta/wiki-graph-engineering.md`).

Decision file name example: `2026-04-24-adk-vs-langgraph.md`. File name example: `langgraph-vs-adk-comparison.md`.

## Typed Link Examples

```markdown
## See Also
- [[CRAG Retry Logic]] — extends
- [[RAG Evaluation]] — prerequisite-for
- [[LangGraph vs ADK]] — alternative-to
```

Use `related` rather than inventing a type (`part-of`, `depends-on`, `complements`, …); put the nuance in a parenthetical note: `- [[X]] — related (part of; the eval stage)`.
