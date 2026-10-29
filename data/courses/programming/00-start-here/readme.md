---
imported_hash: 3fe8f19bcce5560f
title: Drills — the gym
summary: Practice by language and topic, not a sequence.
order: 1
kind: reading
source: sisyphus/drills/README.md
---

# Drills — the gym

Practice by language and topic, not a sequence. Come in, pick a track, drill, log it.
Learning material (the curriculum) lives in the public
[learn-ai-engineering](https://github.com/ramseywise/learn-ai-engineering) repo; interview
format and round prep live in [`../interviewing/`](../interviewing/README.md). This folder is reps.

librarian imports `drills/` as its **programming** course (`make import-courses`): every
`.md` here becomes a lesson, each track folder a module. Notebooks, `.sql`, `.ts` and `.py`
files stay here and are linked, not imported.

## Tracks

| Track | Folder | What's there | Status |
|---|---|---|---|
| Python | [`python/`](../python/readme.md) | ~120 HackerRank solutions, LeetCode pattern notebooks | Solid |
| SQL | [`sql/`](../sql/readme.md) | 52 HackerRank solutions (select, join, aggregation); 1 window-functions drill | Solid on basics; CTEs and analytics patterns to add |
| TypeScript (+ HTML/CSS) | [`typescript/`](../typescript/readme.md) | HackerRank scaffold, ESLint reference, 1 types drill | Thin — biggest gap |
| Terraform | [`terraform/`](../terraform/readme.md) | Track plan, 1 review drill | Started |
| Tooling | [`tooling/`](../tooling/readme.md) | Git workflow reference | Bash and Docker to add |
| Coding rounds | [`coding/`](coding/) | Interview-format drills: prompts, seeded-bug problems, battleship pages, DSA reference | Active — driven by `/coding-drill` and `/env-drill` |
| MCQ | [`mcq/`](mcq/) | Multiple-choice quizzes (system design basics) | One quiz |

`coding/` keeps its existing layout: the `coding-drill` and `env-drill` skills and
`pyproject.toml` depend on its paths.

## Drill schema

New drills are one Markdown file per drill, `drills/<track>/<topic>/<slug>.md`, with
code alongside when the drill needs it (`<slug>.py`, `<slug>.sql`, `<slug>.ts`, `<slug>.tf`).

```yaml
---
title: Window functions — running total per user
track: sql                  # python | sql | typescript | terraform | tooling | coding
topic: window-functions     # folder name; free-form but reuse existing ones
difficulty: medium          # easy | medium | hard
timebox_min: 20
concepts: [window-functions, partitioning]   # learn-ai-engineering / librarian concept slugs
source: original            # original | hackerrank | leetcode | <upstream URL>
---
```

The title lives in frontmatter only — no `# H1` in the body (markdownlint MD025 counts both).
Body sections, in order:

1. **Prompt** — the task, inputs, constraints. Safe to read before attempting.
2. **Starter** — given code or schema (or a link to the sibling file).
3. **Tests** — how to check an answer: expected output, a test file, or a query result.
4. **Solution** — under a `<details>` block so it is not read by accident.
5. **Notes** — the pattern, common mistakes, follow-up variants.

Worked examples of the schema: [`sql/window-functions/top-orders-per-user.md`](../sql/window-functions/top-orders-per-user.md),
[`typescript/types/group-by.md`](../typescript/types/group-by.md),
[`terraform/review/web-stack.md`](../terraform/review/web-stack.md).

`concepts` is what links a drill to the curriculum: librarian's Practice mode uses it to
draw concept → drill edges in the graph. Existing HackerRank / LeetCode solutions keep their
upstream layout and are listed in each track README instead of being rewritten.

## Logging

`coding/drill-log.md` is the one append-only log (date, drill, stance, time, grade). The
`coding-drill` skill writes to it; log language-track drills there too so progress stays in
one place. Use the drill's file slug as the QID (`top-orders-per-user`) — librarian's Practice
mode reads the Date/QID/Score columns live (never the Note column, never copied into librarian)
to show attempt counts per drill.

## History

Moved from learn-ai-engineering `programming/` on 2026-10-28: `HackerRank/{python,sql,typescript}`
→ `{python,sql,typescript}/hackerrank/`, `Python Basics/` → `python/basics/` (moved back the same day to learn-ai-engineering
`data-analytics/python-basics/` — it is a tutorial, not drills, and the public curriculum starts there), `Leet-Code/` →
`python/leetcode/` (a nested git repo, gitignored), `git.md` → `tooling/`, `eslint.md` →
`typescript/`.
