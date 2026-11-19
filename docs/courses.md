# Courses (`data/courses/`) internals

Moved from CLAUDE.md. Contract summary stays in CLAUDE.md: courses are authored and editable, `private/` is the publication gate, the drill log never enters `data/`.


- Learning content served by the Courses tab of the graph UI (`src/librarian/courses/catalog.py`).
  It is **not** raw input and **not** compiled wiki: edit it directly, add lessons freely.
- Layout: `<course>/<module>/[section dirs/]<lesson>.md`; `_course.md` and `_module.md`
  hold `title` / `summary` / `order` frontmatter. Lesson frontmatter: `title`, `summary`,
  `order`, optional `section`, `kind` (`reading` | `notebook`), and `wiki: [page-id, …]`
  to link concepts explicitly. Inline `[[Wiki Page]]` links work too. Images go in the
  module's `assets/` and are referenced relatively.
- **Tier and depth:** content is classified on two axes (`src/librarian/courses/depth.py`; rubric:
  `.claude/skills/pillar/references/depth-rubric.md`). A lesson may carry `tier` (`foundations` |
  `practitioner` | `specialist`) for the note as a whole, set by `/curriculum tier`, and
  `depth_sections: {<exact heading text>: <depth>}` (`intro` | `core` | `deep`) for its sections, where
  a section's depth covers its subsections unless one has its own entry. `depth` is only the default
  for the sections not listed; a note has no depth of its own. All three are authored in the source
  repo and kept by the importer, which drops and logs an illegal value; the lesson routes return them
  as `tier`, `depth` and `depthSections` only when set. `librarian courses check curriculum` reports,
  as information, a lesson with no tier in a module where another has one (`no_tier`) and the sections
  of a tagged lesson that step back down in depth (`depth_order`). A `_quiz.md` question may carry `depth`, `subject` (the course it
  tests, when not the one its file is in) and `topic`; none is sent to the client. `librarian courses
  check chapters` and `check quiz` fail illegal values, and `check curriculum` reports, as information,
  a module with tagged lessons and nothing at one depth (`no_unit_at_depth`). Depth is not a level:
  "level" means the three study formats below. Lesson depth is not read yet (the syllabus will:
  `.claude/docs/plans/2026-11-17-intake-placement-syllabus.md`).
- **Intake and placement:** `src/librarian/courses/placement.py` holds the rule and
  `src/librarian/courses/intake.py` the store (`intakes`, `intake_responses`, `placements`; migration
  `0009_intake`). A learner gives a profile, then per chosen subject answers two blocks of
  `LIBRARIAN_INTAKE_BLOCK_SIZE` questions: the first at `core` (`intro` if they have never used the
  subject), the second set by how the first went. The result is a tier per subject (`foundations`,
  `practitioner`, `specialist`); a tier describes a learner, a depth describes content. The pool is
  every multiple-choice question with a `depth` in the public tree, keyed `placement:<question id>`;
  the private overlay is never read. A subject without a full block at every depth, or one the learner
  skips, is placed from their goal. Answers are graded on the server and no key or explanation is sent
  until the sitting is complete. Routes: `GET /api/intake`, `POST /api/intake/profile`,
  `POST /api/intake/answers`, `GET /api/placement`, `PUT /api/placement/{subject}`; `/api/me` carries
  `intake` (`none` | `in_progress` | `done`). The two free-text answers are stored with the profile,
  never logged, and removed with the account; one model call maps them to public modules and falls back
  to "not interpreted" when it cannot run. There is no page for any of this yet.
- The course README in the source repo also sets what the course page shows, read by
  `course_outline` in `src/librarian/courses/importer.py`: the numbered list under `## Course outcomes`
  becomes `outcomes` in `_course.md`; module links under `## Core…` and `## Advanced…` headings set each
  module's `group` and its `order` (folders are not renamed); the numbered list after "Learning
  objectives" in a `### [Title](<module>/README.md)` section becomes the module's `objectives`. A
  leading folder number is dropped from a module title. The course's own pages (`00-start-here`, and
  a `sources` folder with no lessons) are not modules: the catalog serves them as the course's
  `guide`, `readings` and `references`, shown at the end of the course page.
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
  `slides/lectures/*.yaml` of each module into its `_flashcards.md` (front: `recall`, else `title`; back: `answer`, else `takeaway`). A card can also carry `more` (the in-depth answer behind the short one), `depth` (its own) and `sources` (references): from the slide keys `more`, `depth` and `refs`, or from checklist columns after the answer headed `More` or `In depth`, `Depth` and `Sources` (`;` between references). None of them changes a front, so schedules are kept. A card's `tier` is its lesson's and is added when the catalog loads. After the deck cards it adds one card per row of each lesson's `## Interview checklist` table (front: the question, back: the answer, links reduced to their text), attached to that lesson; a row whose question is already a card's front is dropped. The tool only deletes files carrying its own `generated_by` line. Frontmatter
  `cards: [{front, back, more?, depth?, sources?, lesson?}, ...]`, served by `GET /api/courses/flashcards/<module or
  lesson id>`, studied at `#/flashcards/<id>`; self-grades go via `POST /api/courses/flashcard-results` to the attempts store, and `src/librarian/courses/leitner.py` computes due dates from it; it stores no schedule of its own.
  **Attempts store:** the `attempts` table of the database (`librarian.db`; `src/librarian/courses/attempts.py`) holds every graded event, each owned by one user: flashcards, quiz answers and drill runs (`POST /api/courses/drill-results`). Every study route reads and writes only the caller's rows, and Leitner days are the user's calendar days (`users.timezone`). An old `var/attempts.sqlite3` comes in with `librarian db import-attempts`; an old `logs/flashcards.jsonl` is imported once into the owner's history and left alone. **Progress:** `GET`/`POST /api/courses/progress` (`src/librarian/courses/progress.py`) stores each lesson as `opened` or `done` per user (done is never downgraded); `/api/me` carries the summary. **Quizzes:** `<module>/_quiz.md` (frontmatter `questions: [{prompt, options, answer, explanation?, lesson?, id?}]`), checked by `librarian courses check quiz`, served without answers by `GET /api/courses/quiz/<id>` and graded by `POST /api/courses/quiz-results`; a wrong answer is due tomorrow like a missed card. A question with no `options` is a worked problem: `answer` is a number, the learner types one, and it is right within `tolerance` (default: half a unit of the answer's last decimal place). **Levels:** the three formats test one topic three ways, and a module or lesson page lists those it has in order: level 1 multiple choice (`#/quiz/<id>?choice`), level 2 flashcards (`#/flashcards/<id>`), level 3 worked problems (`#/quiz/<id>?worked`). Never seed one from `private/`. **Slides viewer:** `#/slides/<module>[/<lecture>]`; `GET /api/courses/slides/<id>` rebuilds a stale deck in the background into `var/slides/` (images need `uv` and macOS Quick Look; without them the viewer shows the slide text). **Sidebar and topic page:** the sidebar (240px) shows Graph, Courses, Study and Labs, then each course as an uppercase label over its modules, each with its lesson count; the current module is filled and lessons are never listed there. A module page (`#/courses/<course>/<module>`) runs in order: Test yourself (the three levels, each with a meter and "20 of 32 right · 4 to redo" once signed in), Learn (decks with a Play link to `#/slides/<deck>?play=1`, then notes in reading order), Hands-on (labs and drills), Wiki and References. A module carries `wiki: [{id, title, summary}]` (the 12 public, non-tombstoned pages its lessons cite most, ties by title) and `wikiCount` (all of them); the Wiki section links "Show on the graph" to `#/map/all?tags=module%3A<course>%2F<module>`. Per-user level progress is not in the cached catalog: `GET /api/courses/study-progress` (signed in) returns `{<course>/<module>: {choice|cards|worked: {total, right, redo}}}` from the latest attempt per item. **Study home:** `#/study`, from `GET /api/courses/study`: cards and questions due, the next drill for the weakest track, the module's lecture.
- **Labs** (`#/labs`, `src/librarian/courses/labs.py`): every entry of a pillar's
  `practice/manifest.yaml` whose path is in the mirror. The importer (`plan_labs`) adopts every
  committed file of a lab whose `licence` is not `unrecorded`; an `unrecorded` one is logged as
  `lab_not_cleared` and stays out. Helpers (`pattern: other`, no `demonstrates`) are not labs. A lab's
  notes are its `demonstrates` plus any public note in its module that names the lab's file; a note
  lists its labs (`labs` on the lesson) and links each to its workspace. `GET /api/courses/labs[/<id>]`
  serves the list and one lab with its editable files. Two commands come from an entry: `run`, its
  entry script (the file, or a folder's `run.py`/`main.py`/... or its only script), and `check`, its
  `verified_by` when that is a plain `uv run` of a file or module (optionally after one `cd <lab
  folder> &&`); anything else stays text on the page. Only Python labs run; notebooks and TypeScript
  are read-only. **Running** (`POST /api/courses/lab-runs`, SSE; `src/librarian/courses/lab_runner.py`)
  is local only: the route is a 404 unless `LIBRARIAN_DEV_RUN_LABS=1` (`make api` sets it) and public
  mode is off. `LocalRunner` clones the lab's practice folder from `COURSE_SOURCES_DIR` (falling back to
  the mirror) into a temp dir, writes the editor's edits into the copy, runs the argv without a shell in
  its own process group with an allowlisted environment (provider keys only for `runs_offline: false`),
  kills it after `LAB_RUN_TIMEOUT_S` (300), streams the output and returns the figures the run
  wrote. It is no sandbox; a container backend implements the same `LabRunner` interface later. The
  chat gets the open lab as `lab` on `POST /api/chat`: the server builds a brief (purpose, notes, the
  edit as a diff, the output tail) and sends it as an uncached system block framed as data.
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

## Not verified

- The lab runner. `docs/status.md` records one hand run on 2026-11-10 on the development Mac, with the real `uv`, and
  no green continuous-integration run. It is not a sandbox, has not been run in a container, and has not been run
  with more than one worker.
- The lab brief sent to the chat (the "lab" field on `POST /api/chat`) was tested with a fake client, not a real model.
