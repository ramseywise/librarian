#!/usr/bin/env python3
"""Keep the skills shared by this repo and learn-ai-engineering ("lae") one maintained thing.

    uv run python -m librarian.tools.skillsync check      exit 1 if a copy differs from its render
    uv run python -m librarian.tools.skillsync sync       write both copies from the templates

The templates are `.claude/skills/_shared/<skill>.md` (Claude Code only loads `<name>/SKILL.md`,
so the `_shared` folder is invisible to it). Each is rendered once per repo:

* `{{NAME}}` is replaced from the `VARS` table below, the one place the repos differ.
* A block between `{{#librarian}}` (or `{{#lae}}`) and `{{/}}` is kept for that repo only.

The rendered `SKILL.md` carries a "generated" line. Edit the template, never a copy.

The sibling checkout is optional: `--sibling`, else `COURSE_SOURCES_DIR`, else
`../learn-ai-engineering`. When it is missing `check` reports the skip and checks this repo only;
that is the CI case. `sync` refuses a sibling skill that has uncommitted hand edits (no "Generated from" stamp yet)
and never runs git write commands. Standard library only.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHARED = ".claude/skills/_shared"
SKILLS = ("chapter", "papers", "readings", "curriculum")
REPOS = ("librarian", "lae")
SIBLING_NAME = "learn-ai-engineering"

_BLOCK_OPEN = re.compile(r"^\{\{#(\w+)\}\}$")
_BLOCK_CLOSE = "{{/}}"
_VAR = re.compile(r"\{\{([A-Z_]+)\}\}")

# Where the two repos really differ. Everything else in a skill is shared text.
_WHERE_LIBRARIAN = """\
## Where commands run

This skill spans two checkouts. The reading pipeline exists only in the sibling `learn-ai-engineering` repo
(`../learn-ai-engineering`, the same checkout as `COURSE_SOURCES_DIR`): `scripts/papers/` (`potw.py`, the ledger,
`extract.py`, `figures.py`, `citegraph.py`), the PDFs under `<home>/sources/` and the extractions. The notes are
authored here. Paths below are written as the ledger gives them, relative to the sibling.

- **In the sibling** (`cd ../learn-ai-engineering` first): every `scripts/papers/` command, every `make papers*`,
  `ledger-check` and `extract-*` target, and every `sources/` path.
- **In this repo:** the notes. A ledger `note` such as `ai-engineering/02-context-engineering/notes/05-x.md` is
  `data/courses/ai-engineering/02-context-engineering/notes/05-x.md` here, and so are the home's `references.md`
  and `README.md`. Lessons are authored in `data/courses/` only (the importer is retired): never edit the sibling's
  copy of a note. `make chapter-check`, `make link-check` and `/curriculum` run here.
- **`mark integrated`** runs in the sibling and looks for the citation in the sibling's copy of the note and
  `references.md`, which edits made here do not change. If it refuses for that reason, check that the citation is in
  the `data/courses/` note and `references.md`, then rerun with `--no-citation "authored in librarian data/courses"`.
  The user sees every such exception.
- **The `source-reader` agent** in this repo is read-only and writes no extraction. The reader that writes
  `scripts/papers/extractions/<key>.json` is the sibling's (it has the Write tool). Where a step below says the reader
  writes or checks an extraction, run that step in a session started in the sibling, or note in the report that the
  extraction is missing and the key needs `/extract <key>` there.
"""

_WHERE_LAE = """\
## Where commands run

Run from the repo root: the pipeline (`scripts/papers/`), the PDFs under `<home>/sources/` and the notes this skill
edits are all here. Lessons are also authored in the sibling librarian repo (`../librarian/data/courses/`). Whether
an edit made here has to be mirrored there is the user's call: ask once per session rather than assuming, and list
the edit in the report.
"""

_WHERE_READINGS_LIBRARIAN = """\
## Where commands run

Every command in this skill is the reading pipeline, and the pipeline exists only in the sibling
`learn-ai-engineering` repo (`../learn-ai-engineering`): `cd ../learn-ai-engineering` before running any of them.
`/papers` and `/chapter` then write the findings into the notes in this repo's `data/courses/`.
"""

_WHERE_READINGS_LAE = """\
## Where commands run

Run from the repo root: the ledger, the inbox and the PDFs are all here.
"""

VARS: dict[str, dict[str, str]] = {
    "librarian": {
        "LAYOUT": ".claude/skills/pillar/references/pillar-layout.md",
        "RUN_FROM": (
            "Run from the librarian repo; its pipeline commands run in `../learn-ai-engineering`."
        ),
        "WHERE": _WHERE_LIBRARIAN,
        "WHERE_READINGS": _WHERE_READINGS_LIBRARIAN,
        "GREP_DIRS": "data/courses",
        "LINK_CHECK_NOTE": "run here: checks data/courses/ (the sibling's own script checks only the sibling)",
        "CHAPTER_CHECK_NOTE": " (here it checks `data/courses/`; edit lessons there)",
        "EXTRACT_NOTE": " (run it in the sibling: `/extract` is not in this repo)",
        "CURR_INTRO": (
            "Paths are relative to `data/courses/` in this repo. Lessons are authored and edited there "
            "directly (the importer is retired). PDF, paper and ledger steps stay in the sibling "
            "(`cd ../learn-ai-engineering`). "
        ),
        "CURR_MAP": "`librarian courses check curriculum`, over `data/courses/`",
        "CURR_CMD": "uv run librarian courses check curriculum",
        "CONCEPT_HOMES": "data/concept_homes.json",
        "PRACTICE_DIR": "interviewing/",
    },
    "lae": {
        "LAYOUT": "../librarian/.claude/skills/pillar/references/pillar-layout.md",
        "RUN_FROM": "Run from the learn-ai-engineering repo.",
        "WHERE": _WHERE_LAE,
        "WHERE_READINGS": _WHERE_READINGS_LAE,
        "GREP_DIRS": (
            "ai-engineering generative-ai data-analytics data-science data-engineering programming"
        ),
        "LINK_CHECK_NOTE": "checks this repo only",
        "CHAPTER_CHECK_NOTE": "",
        "EXTRACT_NOTE": "",
        "CURR_INTRO": "Paths are relative to the repo root. ",
        "CURR_MAP": "`scripts/curriculum_map.py`",
        "CURR_CMD": "python3 scripts/curriculum_map.py",
        "CONCEPT_HOMES": "scripts/concept_homes.json",
        "PRACTICE_DIR": "practice/",
    },
}


def render(template: str, repo: str, skill: str) -> str:
    """Render a template for one repo: keep its blocks, fill its variables, stamp the header."""
    out: list[str] = []
    keep = True
    block: str | None = None
    for line in template.splitlines():
        opened = _BLOCK_OPEN.match(line)
        if opened:
            if block is not None:
                raise ValueError(f"{skill}: nested block {line!r}")
            if opened.group(1) not in REPOS:
                raise ValueError(f"{skill}: unknown repo in {line!r}")
            block, keep = opened.group(1), opened.group(1) == repo
        elif line == _BLOCK_CLOSE:
            if block is None:
                raise ValueError(f"{skill}: {_BLOCK_CLOSE} without an open block")
            block, keep = None, True
        elif keep:
            out.append(line)
    if block is not None:
        raise ValueError(f"{skill}: block {block!r} never closed")
    text = "\n".join(out) + "\n"

    def fill(m: re.Match[str]) -> str:
        try:
            return VARS[repo][m.group(1)].rstrip("\n")
        except KeyError:
            raise ValueError(f"{skill}: no value for {{{{{m.group(1)}}}}}") from None

    text = _VAR.sub(fill, text)
    _, front, body = text.split("---\n", 2)
    stamp = (
        f"<!-- Generated from {SHARED}/{skill}.md in the librarian repo "
        "(uv run python -m librarian.tools.skillsync sync). Edit the template, not this file. -->\n"
    )
    return f"---\n{front}---\n{stamp}{body}"


def sibling_dir(explicit: str | None) -> Path:
    chosen = explicit or os.environ.get("COURSE_SOURCES_DIR")
    return Path(chosen).expanduser() if chosen else ROOT.parent / SIBLING_NAME


def _repo_roots(sibling: Path) -> dict[str, Path | None]:
    has_skills = (sibling / ".claude" / "skills").is_dir()
    return {"librarian": ROOT, "lae": sibling if has_skills else None}


def _dirty(repo_root: Path, skill: str) -> bool:
    """True when git reports uncommitted changes under a skill dir (or git cannot say)."""
    path = f".claude/skills/{skill}"
    try:
        done = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain", "--", path],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return True
    return done.returncode != 0 or bool(done.stdout.strip())


def expected(repo: str, skill: str) -> str:
    template = (ROOT / SHARED / f"{skill}.md").read_text()
    return render(template, repo, skill)


def check(sibling: Path, *, quiet: bool = False) -> int:
    roots = _repo_roots(sibling)
    bad = 0
    for repo, root in roots.items():
        if root is None:
            print(f"SKIP {repo}: no checkout with .claude/skills at {sibling}; not compared")
            continue
        for skill in SKILLS:
            path = root / ".claude" / "skills" / skill / "SKILL.md"
            want = expected(repo, skill)
            have = path.read_text() if path.exists() else ""
            if have == want:
                continue
            bad += 1
            print(f"DRIFT {repo}: {path} differs from {SHARED}/{skill}.md")
            if not quiet:
                diff = difflib.unified_diff(
                    have.splitlines(), want.splitlines(), "on disk", "rendered", lineterm="", n=1
                )
                print("\n".join(list(diff)[:40]))
    if bad:
        print("Edit the template, then run: make skills-sync")
    else:
        print(f"OK {len(SKILLS)} shared skills match their templates")
    return 1 if bad else 0


def sync(sibling: Path) -> int:
    roots = _repo_roots(sibling)
    status = 0
    for repo, root in roots.items():
        if root is None:
            print(f"SKIP {repo}: no checkout with .claude/skills at {sibling}")
            continue
        for skill in SKILLS:
            path = root / ".claude" / "skills" / skill / "SKILL.md"
            want = expected(repo, skill)
            if path.exists() and path.read_text() == want:
                continue
            hand_kept = path.exists() and "Generated from" not in path.read_text()
            if repo != "librarian" and hand_kept and _dirty(root, skill):
                print(
                    f"REFUSE {repo}: {path.parent} has uncommitted changes; commit or discard them first"
                )
                status = 1
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(want)
            print(f"WROTE {repo}: {path}")
    return status


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("command", choices=["check", "sync"])
    ap.add_argument(
        "--sibling", help="learn-ai-engineering checkout (default: COURSE_SOURCES_DIR or ../)"
    )
    ap.add_argument("--quiet", action="store_true", help="check: list drifted files without diffs")
    args = ap.parse_args(argv)
    sibling = sibling_dir(args.sibling)
    if args.command == "check":
        return check(sibling, quiet=args.quiet)
    return sync(sibling)


if __name__ == "__main__":
    sys.exit(main())
