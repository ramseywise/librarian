---
name: present
description: "Turn a brief into a one-off talk deck: gathers the goal, audience and tone in the session, runs `librarian present` (Claude writes the outline, slides and image prompts; the deck spec is rendered by build_deck in the house style), then previews the result. Use when asked to make a presentation, pitch or talk from an idea or a codebase, or to rebuild a presenter deck after editing its outline or spec. Do NOT use for a course lecture built from notes (/slides), a cited outline for an article or talk from the wiki (/write), or a single image (run the interactive `presenter --image-only`)."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(uv run librarian present *)
  - Bash(uv run --with python-pptx --with pillow --with resvg-py python -m librarian.tools.slides.build_deck *)
---

You are making a one-off talk deck. The pipeline is a tool that calls Claude: it writes the content, and `build_deck` draws it. You gather the brief, run the tool, check the result and report. Never edit the `.pptx`.

## Core rule

The outline is approved by the user before any slide is written. Never pass `--yes` on the first real run.

## Workflow

`$ARGUMENTS` is the brief, or a path to a brief file. If it is empty, ask for the goal.

1. **Gather the brief.** Ask only for what is missing: the goal (what the talk must achieve), the audience, the tone and, if the talk is about code, the codebase path. Write it to `output/presenter/<slug>/brief.md`: the goal as free text, then `Audience: ...`, `Tone: ...` and `Codebase: ...` lines. Private wiki pages and `data/courses/private/` never go into a brief.

2. **Dry run.**
   ```bash
   uv run librarian present output/presenter/<slug>/brief.md --out output/presenter/<slug> --dry-run
   ```
   It makes no API calls and writes nothing. It prints the model, the image provider and how many Claude calls the run costs. Pass `--no-images` to the later runs if the user does not want generated images (they cost 2 Claude calls per image slide plus the image provider).

3. **Outline, then approval.** Run the same command without `--dry-run`. With no terminal it stops after the outline (exit 3) and saves `outline.json`. Show the user the printed outline and ask: approve, or what to change. To change it, edit `outline.json` (titles, types, points) or ask for a re-run with a sharper brief. Slide types: architecture, concept, narrative, data, code_demo, team.

4. **Build.** On approval, run again with `--yes`. It reuses `outline.json` if the brief is unchanged, writes the slides and images, then `deck.yaml` and the `.pptx` next to it. Print the `WARN` lines it reports.

5. **Preview and fix.**
   ```bash
   uv run --with python-pptx --with pillow --with resvg-py python -m librarian.tools.slides.build_deck output/presenter/<slug>/deck.yaml --preview output/presenter/<slug>/.preview
   ```
   Read the contact sheets (`sheet-NN.png`) and fix overflow or crowding in `deck.yaml` (cut words, change a layout), then rebuild with the same command. Layouts and keys are in `.claude/skills/slides/references/deck-spec.md`. Presenter maps its slide types onto `image`, `flow`, `statement`, `cards`, `steps` and `bullets`; `data` and `code_demo` slides have no table or code layout, because their text is prose.

6. **Report.** The deck path, the spec path, the slide count, the warnings left and the Claude calls made. Nothing here is staged or committed.

## Notes

- The interactive intake is still there: `uv run presenter` (needs `make install-presenter`).
- Tests: `uv run pytest -q tests -k present`.
