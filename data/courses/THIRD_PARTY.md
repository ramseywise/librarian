# Third-party material

What this tree copied from other people, recorded so its origin and licence are not lost. Lesson text cites its own
sources in frontmatter or in a module's `references`. This file covers only lab and practice material that was
**copied in**, and it does not grant any rights in that material. Each licensed folder keeps its own `LICENSE`.

## Licensed labs and data

| Path | Upstream | Licence | What's here |
|---|---|---|---|
| `programming/typescript/practice/typescript-exercises/` | https://github.com/typescript-exercises/typescript-exercises | MIT | 15 exercises with solutions. Patches for TypeScript 7 are listed in its `NOTICE.md` |
| `programming/typescript/practice/type-challenges/` | https://github.com/type-challenges/type-challenges | MIT | 26 easy and medium challenges with their test cases. The solutions are written here |
| `programming/sql/practice/data/survey.db` | https://github.com/swcarpentry/sql-novice-survey | CC-BY 4.0 | The Antarctic survey database (8 KB) |
| `programming/sql/practice/data/clubdata.sql` | https://pgexercises.com/ | CC BY-SA 3.0 | PGExercises club data converted from Postgres to SQLite. `clubdata.db` is built from it and gitignored |
| `programming/drills/coding/dsa/` | https://github.com/dileeppandey/hello-interview | MIT, (c) 2019 Dileep Pandey | "Hello, Interview!" data structures and algorithms material, with its `LICENSE` kept alongside. Its problem statements derive from LeetCode, which the licence does not cover |
| `data-analytics/01-python-for-data-analysis/practice/mckinney/` | https://github.com/wesm/pydata-book (`2nd-edition`) | MIT (code) | Chapter lessons from the book's notebooks. The datasets (~240 MB) are not copied |
| `generative-ai/09-llms-from-scratch/practice/nn-zero-to-hero/` | https://github.com/karpathy/nn-zero-to-hero | MIT, (c) 2022 Andrej Karpathy | Lecture code (micrograd, makemore, nanoGPT). The 1.1 MB `input.txt` files are not copied, see `README-data.txt` there |
| `generative-ai/07-agentic-applications/practice/deep-research-bot/` | https://github.com/morganmcg1/deep-research-bot | Apache-2.0 | Deep research agent lab, with its `LICENSE` |
| `generative-ai/07-agentic-applications/practice/deep-research-bench/` | https://github.com/Ayanami0730/deep-research-bench | Apache-2.0 | DeepResearch Bench evaluation code, with its `LICENSE`. A contact address in its README was removed |
| `generative-ai/05-rl/practice/01-q-learning-treasure-hunt/` | https://github.com/bojieli/ai-agent-book (Bojie Li, *AI Agents in Depth*, Experiment 7-1) | Apache-2.0 | Game environment, tabular Q-learning agent and training script, trimmed and edited. `LICENSE` is the standard Apache-2.0 text and `NOTICE` records the attribution |

**Paraphrased, not vendored:** Charles Severance's *Python for Everybody* (CC BY-NC-SA 3.0) and the TypeScript Handbook
(CC-BY 4.0). No book text, slides or `mbox` data files are copied. The sample e-mail addresses in the regex exercises
are made up.

## Practice material: upstreams with no licence

Coding drills were condensed from the repository below. **It carries no licence**, and a repository with no licence
grants no right to copy or redistribute it. This table records where the material came from. It is not permission to
reuse it, and clearing it is still open.

| Upstream | Licence | Condensed into |
|---|---|---|
| https://github.com/alexeygrigorev/ai-engineering-gym | None | Coding drills in `programming/drills/coding/` (`algorithms/`, `implementation/`). 87 of the 89 `algorithms/` drills name a LeetCode problem as their `source:`; no licence here covers those problem statements |
