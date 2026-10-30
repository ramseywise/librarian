---
title: Render-Scoped Component Types Remount Their Subtree
tags: [patterns, infra, pattern]
summary: A React markdown renderer that builds its components map (and heading component types) inside render gives every element a new type on each parent re-render, so React unmounts and remounts the whole subtree; anything holding DOM references, like a table-of-contents IntersectionObserver, ends up watching detached nodes after an unrelated click.
updated: 2026-10-30
sources:
  - data/raw/repos/librarian/.claude--docs--plans--2026-10-30-frontend-audit-fixes.md
---

# Render-Scoped Component Types Remount Their Subtree

Found in the 2026-10-30 audit of the librarian Courses tab (finding B1).

## Symptom

Clicking "Mark complete" on a lesson broke the on-page table of contents: it stopped
tracking the heading in view. The button only updates progress state in a parent, so
nothing about it should touch the lesson body.

## Mechanism

The markdown component built its `components` map, including the heading component
*types*, inside its render function. React decides whether to keep a subtree by comparing
element types. A function created during render is a new type on every render, so any
parent re-render (here, the progress update) made every heading a different component.
React unmounted the old heading DOM and mounted new nodes. The TOC's
IntersectionObserver still held the old nodes and was now watching elements no longer in
the document.

Nothing errors. The page renders correctly, and the defect shows only in behaviour that
depends on DOM identity.

## Fix

- Hoist heading components to module scope so their identity is stable.
- Memoise the `components` map on the inputs that actually change it (lesson id and the
  two link callbacks).
- Make those callbacks stable in the parent (`useCallback`), or the memo keys change on
  every render anyway.
- Write a repro test before the fix: re-render the parent and assert the heading nodes
  are the same DOM objects.

## See Also
- [[Librarian Graph Explorer]]
- [[Red-Then-Green Proof for Fix-Stage Tests]] — extends (the repro-first discipline the fix uses)
