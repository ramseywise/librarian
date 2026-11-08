---
name: slides
description: "Build a lecture deck (.pptx) for any module of any course (ai-engineering, generative-ai, data-analytics, data-science, data-engineering, programming, interviewing) from its notes, in the course's house style (the LangGraph deck look). Writes data/courses/<pillar>/slides/deck.yaml, renders it with src/librarian/tools/slides/build_deck.py, previews every slide and fixes overflow. Usage: /slides 02-context-engineering, /slides generative-ai/02-rag-retrieval, /slides data-analytics/06-applied-analyses, /slides programming/python/01-foundations. Run from the librarian repo: media is built here, not in learn-ai-engineering."
---

You are turning one pillar's notes into a lecture deck. The notes are the source of truth.
The deck is a talk built on them: one idea per slide, with the evidence kept in. It is not
the notes reflowed onto slides.

A deck whose first line is `# imported_hash:` is mirrored from `../learn-ai-engineering`: edit the sibling's
`slides/` spec, run `uv run librarian courses import --subject <course>`, then build here. A deck written here with
no hash is this repo's own, and the import leaves it alone.

The rendering is deterministic. You write a YAML spec, and `src/librarian/tools/slides/build_deck.py`
draws it. Never hand-edit the `.pptx`. Edit the YAML and rebuild.

Read `references/deck-spec.md` before writing the spec. It has the schema, the layout
catalogue, the palette and the writing rules. The worked example is
`data/courses/ai-engineering/01-prompt-engineering/slides/deck.yaml`.

---

**Lecture series.** To teach a pillar as one full lecture per note, write `slides/lectures/NN-slug.yaml` instead of `slides/deck.yaml`, one note at a time. The steps below still apply, with `LECTURE=NN-slug` on the build. See "Lecture series" in `references/deck-spec.md`, and run `make deck-graph` after adding a lecture.

## Step 1 — Pick the pillar

Below, paths are relative to `data/courses/`, and a pillar is a course's module directory.
`$ARGUMENTS` names a pillar directory under `ai-engineering/` (`02-context-engineering`, or
just `02`), a path such as `data-science/03-nlp`, or a programming module such as
`programming/sql/01-select`. Below, `<pillar>` means that full path, and `make slides PILLAR=`
takes any of these forms. A pillar that does not yet match `.claude/skills/pillar/references/pillar-layout.md` should go through `/pillar` first. If it is empty, list the pillars that have `notes/` but no `slides/deck.yaml`,
and pick the first. If `slides/deck.yaml` already exists, you are **revising** it. Read it
first and keep what still matches the notes. A deck inherits its notes' errors, so if the pillar has not been through
`/review`, say so in your report. It does not block the deck.

## Step 2 — Read the pillar

- `README.md`. Its groupings of the notes (Foundations / Techniques / …) become the deck's
  **parts**. Its rules of thumb become the wrap-up slide.
- Every file in `notes/`, in order. For each note, write down:
  - the claim it makes
  - the numbers that back the claim
  - any contrast, table, pipeline or ladder it contains
- `assets/` (if present). Figures from the papers can go on `image` slides. Images
  sit in that folder, named `<first-author-lastname>-<short-title>-fig<N>.<ext>` (e.g.
  `li-ai-agents-in-depth-fig5-4.svg`). A figure the notes don't show yet goes into the note
  first, then onto a slide: the notes are the source of truth.

## Step 3 — Plan

- **Parts.** Mirror the README groupings, usually 3–5 parts. Add a closing part with
  `agenda: false, divider: false` containing a rules-of-thumb `cards` slide and a
  where-next `bullets` slide.
- **Slides.** Plan about 2–4 slides per note, within the size rule in deck-spec.md. Follow its story rules: each part opens by posing the problem and every content slide has a `takeaway`. Choose
  each slide's layout from the content's shape (see the writing rules in deck-spec.md).
  Avoid long runs of the same layout.
- **Order.** Follow the notes. Put a pillar's thesis first, as a `statement`.
- **Syllabus, beats and levels.** If the README has a Syllabus section, plan the parts from it. Open with an
  `overview: true` part, and give each slide a `beat` and, where it is not `core`, a `level` (see deck-spec.md).

## Step 4 — Write `<pillar>/slides/deck.yaml`

- Put a header comment naming the notes the deck covers and the build command.
- Give every content slide `source:` (the note path) and `notes:` (what the speaker says,
  plus the context you cut from the slide).
- Set `output:` to `<topic>.pptx`, e.g. `context-engineering.pptx`.
- Watch the YAML traps listed in deck-spec.md. Quote cells that contain commas. Quote
  strings that start with `*` or `` ` ``.

## Step 5 — Build and look

```bash
make slides PILLAR=<pillar> PREVIEW=1
```

This writes the `.pptx` next to the YAML. With `PREVIEW=1` it also renders every slide to
PNG (macOS Quick Look, a few seconds for the whole deck) plus `sheet-NN.png` contact sheets, 6 slides
per sheet, in `<pillar>/slides/.preview/`. That folder is gitignored.

1. Fix every `WARN slide N …` line. Each one means text didn't fit even at the minimum size.
   Cut words; don't fight the layout.
2. **Dispatch `deck-reviewer`** with the pillar path. It reads every contact sheet and returns problems with the smallest
   YAML fix, so the images stay out of this session. Check that `SHEETS READ` covers them all. If the agent is unavailable,
   read every contact sheet yourself with the Read tool. A run with no warnings is not proof the
   slides look right. Check for:
   - text crowding a card edge
   - an orphaned word on its own line
   - a table that is too tall
   - an image that is too small
   - two adjacent slides that look identical
3. Rebuild until the deck is clean. `--strict` (`make slides … STRICT=1`) exits non-zero if
   any warning is left.
4. Add `PDF=1` on the final build. It writes `slides/<topic>.pdf`, one page per slide, which
   opens in a VS Code tab. The pages are images (1600 px, JPEG), with no speaker notes. The
   PDF and the `.pptx` are gitignored: this repo is public, and the YAML and `assets/`
   rebuild them. `make slides-all PDF=1` rebuilds every deck.
5. Check the size: `ls -la data/courses/<pillar>/slides/*.pptx`. **Keep the `.pptx` under
   1000 KB**, so a deck stays easy to send. The decks so far are 270–860 KB. The builder already shrinks every image to
   about 220 dpi at its size on the slide, and stores it as JPEG when that is smaller, so
   the original images can stay as they are. If a deck still goes over, the cause is too
   many image slides. Cut the weakest ones, or split the pillar into two decks.

## Step 6 — Wire it in

- In the pillar README, add a line pointing to `slides/<topic>.pptx` and `slides/deck.yaml`
  in the Layout or Start-here section.
- Run `make deck-graph-check`.
- Run `make flashcards`. It rewrites the module's `_flashcards.md` from every local `slides/deck.yaml` and `slides/lectures/*.yaml`, so a changed takeaway or `source:` reaches the study view. Run it again after any later deck edit.

## Step 7 — Stage, don't commit

`git add` the YAML, any new image in `assets/`, the readme change and the module's `_flashcards.md`. The `.pptx`, the `.pdf` and
`.preview/` are gitignored. Show
`git status` and `git diff --staged --stat`, and suggest a commit message such as
`docs(<pillar>): lecture deck from notes`. Don't commit.

## When the builder is the problem

If a layout can't express the content, or renders it badly, fix `src/librarian/tools/slides/build_deck.py`.
Don't contort the content to fit. Keep layouts generic, since every pillar uses them.
Document any new layout or key in `references/deck-spec.md`. Rebuild
`01-prompt-engineering` afterwards to check that the change didn't break the existing deck.
