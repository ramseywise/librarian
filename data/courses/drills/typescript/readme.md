---
imported_hash: 4ccfa7823b126bcc
title: TypeScript (with HTML/CSS)
summary: 'HTML/CSS is folded into this track: it only comes up next to TypeScript (the librarian UI, kiez front end), so drills for it sit here as a web/ topic.'
order: 1
kind: reading
source: sisyphus/drills/typescript/README.md
---

# TypeScript (with HTML/CSS)

| Path | What |
|---|---|
| [`hackerrank/`](hackerrank/) | Scaffold: `tsconfig.json`, `package.json`, one solved problem (`solutions/example-plus-minus.ts`) |
| [`eslint.md`](eslint.md) | ESLint configuration reference |
| [`types/`](types/) | Schema drills: [typed `groupBy`](types/group-by.md). Tests run with `node --test` (Node 22.18+ runs `.ts` directly) |

HTML/CSS is folded into this track: it only comes up next to TypeScript (the librarian UI,
kiez front end), so drills for it sit here as a `web/` topic.

## Gaps

Compared with the Python track this is a scaffold, not a track:

| Area | Python coverage | TypeScript gap |
|---|---|---|
| HackerRank problems | ~120 solved across 18 categories | 1 example; strings, collections, classes all missing |
| LeetCode / DS&A | Pattern notebooks (arrays, two pointers, sliding window, linked lists) | No TS solutions |
| Language idioms | — | Types and generics, narrowing, `async`/`await`, modules |
| Web (HTML/CSS) | — | Semantic markup, flexbox/grid layout, DOM events, fetch + render |

**Order to build**: HackerRank TS first (fixed problem set, scaffold already exists), then
`types/` and `async/` schema drills, then `web/`. LeetCode in TS is lowest priority — the
Python notebooks are the canonical algorithm reference.
