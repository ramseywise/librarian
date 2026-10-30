---
title: Issues Live in the Repo They Change
tags: [llm, pattern]
summary: File each issue in the repo whose code it changes, not in a central "board" repo where the idea came up. When moving a misfiled issue, fully qualify its cross-repo references first, because bare #N refs silently rebind to the destination repo.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/_user/CLAUDE.md
---

# Issues Live in the Repo They Change

**Rule:** an issue is filed in the repo whose code it changes, even when the idea surfaced
in a session working on a different repo. Only issues that change the coordinating repo
itself belong there.

## The failure it replaced

For a while, a meta/orchestration repo doubled as a cross-repo board: any idea raised in
its sessions was filed there, tagged with the target repo's prefix. After several weeks
about half of its backlog had foreign prefixes. The repos that had to do the work never saw
those issues in their own trackers, branch names, or PR auto-linking. The board looked
complete, but the work was invisible where it would actually be done.

A side effect: once the issue lives in the repo it changes, the repo prefix in the issue
title adds nothing and can be dropped. It stays in branch and PR names, where it still
tells checkouts apart.

## Transfer gotcha: bare refs rebind

`gh issue transfer <n> <owner>/<target>` moves a misfiled issue, but **bare `#N`
references in the body silently re-resolve against the destination repo** and point at
the wrong issue there, with no warning. Before transferring, rewrite every cross-repo
reference in fully qualified form (`owner/repo#65`, not `#65`).

This is the same failure class as renumbering IDs that other documents already cite: a
reference that was valid in one namespace binds silently to a different object in another.

## See Also
- [[Decision-ID Reservation Across Concurrent Plans]] — related (references that silently rebind when their namespace changes)
- [[Branch Naming Convention Pattern]] — related (prefix conventions in branch and PR names)
- [[Claude Workflow System]] — related (part of)
