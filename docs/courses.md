# Courses (`data/courses/`) internals

Moved from CLAUDE.md. Contract summary stays in CLAUDE.md: courses are authored and editable, `private/` is the publication gate, the drill log never enters `data/`.


- Learning content served by the Courses tab of the graph UI (`src/librarian/courses/catalog.py`).
  It is **not** raw input and **not** compiled wiki: edit it directly, add lessons freely.
- Layout: `<course>/<module>/[section dirs/]<lesson>.md`; `_course.md` and `_module.md`
  hold `title` / `summary` / `order` frontmatter. Lesson frontmatter: `title`, `summary`,
  `order`, optional `section`, `kind` (`reading` | `notebook`), and `wiki: [page-id, …]`
  to link concepts explicitly. Inline `[[Wiki Page]]` links work too. Images go in the
  module's `assets/` and are referenced relatively.
- `../learn-ai-engineering` is the source and `data/courses/` its mirror: notes, `slides/` deck specs
  and practice code are authored there and brought in with `uv run librarian courses import [--subject X]
  [--dry-run]` (`make import-courses`; `src/librarian/courses/importer.py`). Generated lessons and decks carry an
  `imported_hash` line; a file edited here (hash mismatch) or written here with no hash is never overwritten
  and is reported as `kept_local_edit`. Practice code comes by sibling git history: files committed since the
  commit recorded in `_mirror.json` are copied when their lab folder is already mirrored (a new lab folder is
  logged as `practice_folder_not_mirrored` and stays a decision), and each `practice/manifest.yaml` is
  rewritten to the mirror's file names. Book and paper figures, including a subject home's `sources/images/`,
  go to the private mirror only. `--adopt REV` takes back hashless files unchanged since librarian commit
  REV (used once, after the 2026-11-06 import stripped the hashes). Drills are the `drills` module of the
  Programming course (`programming/drills`); the root `.gitignore` keeps local files out of it. Never copy
  from sisyphus (private; `jobs/` is personal PII).
  Drill files (frontmatter with a `track`, schema in `programming/drills/README.md`) are
  `kind: drill` with `track`/`topic`/`difficulty`/`timebox_min`/`units`, and their `concepts` become
  `wiki` links. They feed Practice mode: `GET /api/courses/practice` and the `#/practice` tab.
  Concepts with no wiki page show as plain `drill.tags`. Attempt counts come from the caller's
  drill attempts in the database only. The owner brings the sisyphus `drills/coding/drill-log.md`
  in locally with `librarian db import-drill-log [--user EMAIL]` (Date, QID, Aid and Score only, never
  the Note; idempotent); the server never reads it, and it is never written into `data/`: this
  repo is public and the log is personal history.
  `make flashcards` (`src/librarian/tools/slides/flashcards.py`) turns the local `slides/deck.yaml` and
  `slides/lectures/*.yaml` of each module into its `_flashcards.md`. The tool only deletes files carrying its own `generated_by` line. Frontmatter
  `cards: [{front, back, lesson?}, ...]`, served by `GET /api/courses/flashcards/<module or
  lesson id>`, studied at `#/flashcards/<id>`; self-grades go via `POST /api/courses/flashcard-results` to the attempts store, and `src/librarian/courses/leitner.py` computes due dates from it; it stores no schedule of its own.
  **Attempts store:** the `attempts` table of the database (`librarian.db`; `src/librarian/courses/attempts.py`) holds every graded event, each owned by one user: flashcards, quiz answers and drill runs (`POST /api/courses/drill-results`). Every study route reads and writes only the caller's rows, and Leitner days are the user's calendar days (`users.timezone`). An old `var/attempts.sqlite3` comes in with `librarian db import-attempts`; an old `logs/flashcards.jsonl` is imported once into the owner's history and left alone. **Progress:** `GET`/`POST /api/courses/progress` (`src/librarian/courses/progress.py`) stores each lesson as `opened` or `done` per user (done is never downgraded); `/api/me` carries the summary. **Quizzes:** `<module>/_quiz.md` (frontmatter `questions: [{prompt, options, answer, explanation?, lesson?, id?}]`), checked by `librarian courses check quiz`, served without answers by `GET /api/courses/quiz/<id>` and graded by `POST /api/courses/quiz-results`; a wrong answer is due tomorrow like a missed card. Never seed one from `private/`. **Slides viewer:** `#/slides/<module>[/<lecture>]`; `GET /api/courses/slides/<id>` rebuilds a stale deck in the background into `var/slides/` (images need `uv` and macOS Quick Look; without them the viewer shows the slide text). **Study home:** `#/study`, from `GET /api/courses/study`: cards and questions due, the next drill for the weakest track, the module's lecture.
- Private and tombstoned wiki pages are never linked from lessons.
- **`data/courses/private/`** (gitignored, mirrors the layout: `private/<course>/<module>/...`) holds
  what must not be public: solutions to site problems (`leetcode/`, `hackerrank/`), `coding/scratch/`,
  interview prep. It is the publication gate: anything there stays on this machine. The catalog serves
  it to the local UI as part of its course with `private: true`, but it never reaches the search index,
  MCP, the curriculum snapshot, the gap list or a public lesson's prev/next. Nothing public links into it.
  Two kinds of file live only in the mirror, written by the importer (or by hand), with the public lessons unchanged
  (`librarian.courses.overlay`): book and paper figures with no licence to share (all of `<module>/assets/sources/...`
  and named figures elsewhere in `assets/`; the asset route and deck builder fall back to the mirror, the UI hides a figure that is in neither tree) and each module's
  `readings:` list (`private/<course>/<module>/_module.md`, merged by the catalog; the public
  `_module.md` keeps `readings_count`). Lessons' `sources/` links
  are resolved at render time through `COURSE_SOURCES_DIR` (default `../learn-ai-engineering`) and
  served by `GET /api/courses/sources/<path>`, local only (`SERVE_COURSE_SOURCES=false` turns it off).
  PDFs are never copied: a cited reading is a link into the sibling.
  `data/concept_homes.json` (hand-edited) lists the maths concepts and the lessons that teach them, for `courses check curriculum`.
- **Media is built here, for every course.** Deck specs are `<course>/<module>/slides/deck.yaml`
  or `slides/lectures/NN-slug.yaml`, images are in the module's `assets/`, and `src/librarian/tools/slides/`
  renders them: `make slides PILLAR=<course>/<module> [PREVIEW=1] [PDF=1]`, `make slides-all`,
  `make deck-check`, `make deck-graph`. Authoring steps are in the `/slides` skill. Built `.pptx`
  and `.pdf` files are gitignored. `src/librarian/tools/presenter/` is a
  separate LLM-driven tool for one-off talks, not course media.

---
