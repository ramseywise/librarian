# Curriculum and wiki: one map

How the course, the wiki and the glossary relate, on one page. Detail stays in the docs linked at the
end; where this page and one of them disagree, that doc and the code are right and this page needs
fixing.

## Three bodies of content

| | Lives in | Written by | Made from |
|---|---|---|---|
| **Course** | `data/courses/`, a mirror of `../learn-ai-engineering` | authored in the source repo, brought in by `librarian courses import` | books, papers, labs |
| **Wiki** | `data/wiki/` | Claude only, by the ingest protocol | `data/raw/` (append-only) |
| **Glossary** | `data/glossary.yaml` | by hand | each definition paraphrases one public wiki page |

`private/` under either tree is the publication gate: it stays on this machine and nothing public
links into it.

## The course, top down

| Unit | Also called | File that defines it |
|---|---|---|
| Program | | `CURRICULUM.md` (source repo): outcomes, role map, learning paths |
| Course | subject | `<course>/README.md`: the syllabus |
| Module | pillar, unit | `<course>/<module>/README.md`: reading order, builds on, feeds into |
| Note | lesson, chapter | `notes/NN-slug.md` |
| Section | | a heading inside a note |

Around a module's notes: `_quiz.md` (questions), `_flashcards.md` (generated from decks and interview
checklists), `slides/` (deck specs), `practice/` (labs), and drills under `programming/drills`.

Notes connect to each other by the README reading order, each note's `## Next`, and the README's
"builds on" and "feeds into" tables. `librarian courses check curriculum` builds the map of all of it
and reports the problems.

## The wiki

| Thing | What it is | Rule |
|---|---|---|
| **Domain** | the page's top-level directory (`rag/`, `data-science/`, ...) | the primary retrieval axis; derived from disk, never from a list |
| **Tags** | frontmatter | one domain tag, exactly one type tag (`concept`, `pattern`, `decision`, ...), any topic tags (`adk`, `voice`, ...) |
| **Links** | `[[Page Title]]` | in `## See Also`, typed (`extends`, `prerequisite-for`, `alternative-to`, `instance-of`, `contradicts`, `supersedes`, `related`); the type describes the linked page |

## How the three connect

| From | To | How | Code |
|---|---|---|---|
| Note | wiki pages | `wiki:` in frontmatter, inline `[[links]]`, wiki pages whose `sources:` list the note's raw copy, title mentions in prose, then nearest pages by embedding | `courses/linker.py` |
| Wiki directory | course | a fixed table groups directories into one area per course, for the map only | `wiki/areas.py` |
| Course and module | wiki pages | the curriculum facet: the pages each module's notes link, and per course the pages no note links ("Not yet in a lesson") | `courses/curriculum.py` |
| Course | wiki page | derived placement: the lowest tier among the notes linking the page ("introduced at") and their modules; on the map as `pageTier`, at the end of MCP `read_page`; never written to wiki frontmatter. `librarian courses check tiers` flags a `prerequisite-for` link whose prerequisite is tiered above its page | `courses/curriculum.py`, `courses/checks/tier_order.py` |
| Glossary term | wiki pages | `page:` names the page it paraphrases; mentions are word matches in public page bodies | `courses/glossary.py` |
| Glossary term | notes | hover definitions in lessons | `courses/glossary.py` |
| Maths concept | the notes that teach it | `data/concept_homes.json`; a note that uses the concept without linking its home is reported | `courses/checks/curriculum_map.py` |

None of these changes a wiki page's domain. The course is an overlay on the wiki: directories stay the
domains for tags, search and lint.

## How course content is classified

| Word | Applies to | Values | Status |
|---|---|---|---|
| **Tier** | a note; a flashcard takes its note's | foundations, practitioner, specialist | field and `/curriculum tier` built; notes not yet tiered |
| **Depth** | a section of a note; a quiz question; a flashcard | intro, core, deep | fields built; notes and cards not yet tagged |
| **Tier** (placement) | a learner, per subject | the same three | built: intake and placement |
| **Level** | a study format | 1 multiple choice, 2 flashcards, 3 worked problems | built |
| **Difficulty** | a drill | easy, medium, hard | built |

Rubric for tier and depth: `.claude/skills/pillar/references/depth-rubric.md`.

## Who keeps it together

| Job | Tool |
|---|---|
| Where a topic belongs, what it overlaps, a note's tier | `/curriculum`, with the read-only `curriculum-steward` agent |
| Module layout and the chapter standard | `/pillar`, `.claude/skills/pillar/references/pillar-layout.md` |
| Wiki health, taxonomy drift | `/lint`, `/wiki-sync` |
| What the wiki lacks for the course | `/gaps` |

## Where the detail is

- The whole syllabus, every module's objectives and every note with its wiki pages:
  [syllabus.md](syllabus.md) (generated: `uv run librarian courses syllabus`)
- Course internals, mirror, quizzes, labs, private overlay: [courses.md](courses.md)
- Wiki directories and tags: [wiki-schema.md](wiki-schema.md)
- Map panel, atlas, glossary on the map: [feature-notes.md](feature-notes.md)
- Page format, link types, ingest: `CLAUDE.md`
- Lint checks and health numbers: [wiki-health.md](wiki-health.md)
