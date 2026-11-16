"""Labs: the runnable practice examples each pillar lists in `practice/manifest.yaml`.

A lab is one manifest entry, a file or a folder under `<course>/<module>/practice/`, with what it is
for (`purpose`), the notes it backs (`demonstrates`) and, when one was run and passed, the command
that checks it (`verified_by`, relative to the practice folder). Its id is its path under the
courses dir: `data-science/01-classical-ml/practice/importance_noise.py`.

Two commands come out of an entry. `run` is the lab's entry script (`uv run <file>`): the file
itself, or a folder's `run.py` (or its only script). `check` is `verified_by`, held to the forms
that are a `uv run` of a file or module, optionally after one `cd <lab folder> &&`; anything else
(npx, npm, a shell pipeline) stays text on the page and is never run. Only Python labs are
runnable; notebooks and TypeScript are listed for reading.

The manifests are read from the courses dir (the importer mirrors every cleared lab), cached on
their mtimes, and joined to the catalog's lessons at query time, so a note lists its labs and a
lab its notes. Entries whose path is not in the mirror (licence `unrecorded`) are left out.
"""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from librarian.config import get_settings
from librarian.log_config import get_logger

log = get_logger(__name__)

COURSES_DIR = get_settings().courses_dir
MANIFEST_GLOB = "*/*/practice/manifest.yaml"
PRIVATE_COURSES = "private"

# Files the editor opens for a lab: its own text files, small enough to edit in a browser.
EDITABLE_EXTS = {".py", ".sql", ".toml", ".yaml", ".yml", ".json", ".txt", ".cfg", ".ini"}
MAX_EDITABLE_BYTES = 200_000
MAX_EDITABLE_FILES = 30
SKIP_DIRS = {"__pycache__", ".venv", "node_modules", ".ipynb_checkpoints", "data"}
# A folder lab's entry script, in this order of preference.
ENTRY_NAMES = ("run.py", "main.py", "lab.py", "demo.py", "app.py")

_UV_FLAGS_WITH_VALUE = {"--with", "--python", "-p", "--extra", "--group"}
_UV_FLAGS = {"--no-project", "--isolated", "--quiet", "-q"}
# Argv never reaches a shell; this keeps out what would only mean something to one ($, *, ;, |, >).
_SAFE_ARG_RE = re.compile(r"^[A-Za-z0-9_.,=:/@+\[\]-]+$")


@dataclass(frozen=True)
class Command:
    """An argv to run, from `cwd` (relative to the practice folder): never through a shell."""

    argv: tuple[str, ...]
    cwd: str = "."

    def display(self) -> str:
        line = shlex.join(self.argv)
        return line if self.cwd == "." else f"cd {self.cwd} && {line}"


@dataclass(frozen=True)
class Lab:
    id: str  # path under the courses dir
    course: str
    module: str
    path: str  # relative to the pillar, starts with practice/
    title: str
    purpose: str
    pattern: str
    language: str
    runs_offline: bool
    verified_by: str  # as written; "" for none
    licence: str
    notes: tuple[str, ...]  # lesson ids, as the manifest names them (resolved at query time)
    files: tuple[str, ...]  # editable files, relative to the practice folder
    run: Command | None = None
    check: Command | None = None
    is_folder: bool = False

    @property
    def practice_dir(self) -> str:
        """The practice folder, relative to the courses dir."""
        return f"{self.course}/{self.module}/practice"


def _title(name: str) -> str:
    """`importance_noise.py` → `Importance noise`; `credit-default-lab` → `Credit default lab`."""
    stem = Path(name).stem if "." in name else name
    words = re.sub(r"[_-]+", " ", stem).strip()
    return words[:1].upper() + words[1:] if words else name


def _editable(practice: Path, rel: Path) -> tuple[str, ...]:
    target = practice / rel
    if target.is_file():
        candidates = [target]
    elif target.is_dir():
        candidates = sorted(
            p
            for p in target.rglob("*")
            if p.is_file() and not set(p.relative_to(target).parts[:-1]) & SKIP_DIRS
        )
    else:
        return ()
    out = [
        p.relative_to(practice).as_posix()
        for p in candidates
        if p.suffix.lower() in EDITABLE_EXTS and p.stat().st_size <= MAX_EDITABLE_BYTES
    ]
    # Scripts first, then the rest, each in path order.
    out.sort(key=lambda f: (not f.endswith(".py"), f.count("/"), f))
    return tuple(out[:MAX_EDITABLE_FILES])


def _run_command(practice: Path, rel: Path, language: str) -> Command | None:
    if language != "python":
        return None
    target = practice / rel
    if target.is_file():
        return Command(("uv", "run", rel.as_posix())) if rel.suffix == ".py" else None
    if not target.is_dir():
        return None
    scripts = sorted(p.name for p in target.glob("*.py") if not p.name.startswith(("test", "_")))
    entry = next((n for n in ENTRY_NAMES if n in scripts), None)
    if entry is None and len(scripts) == 1:
        entry = scripts[0]
    if entry is None:
        return None
    return Command(("uv", "run", entry), cwd=rel.as_posix())


def parse_check(verified_by: str, rel: Path) -> Command | None:
    """`verified_by` as a Command, or None for anything but a plain `uv run` of a file or module.

    `[cd <the lab's own folder> &&] uv run [--no-project | --with PKG | --python V ...] [python] (FILE | -m MOD) ARGS`.
    Every token must be a plain word (no globs, redirects, variables or quotes that hide them).
    """
    text = verified_by.strip()
    if not text or text == "none":
        return None
    cwd = "."
    if text.startswith("cd "):
        head, sep, rest = text.partition("&&")
        folder = head[3:].strip()
        if not sep or folder != rel.as_posix() or "&&" in rest:
            return None
        cwd, text = folder, rest.strip()
    try:
        argv = shlex.split(text)
    except ValueError:
        return None
    if argv[:2] != ["uv", "run"] or not all(_SAFE_ARG_RE.match(a) for a in argv):
        return None
    i = 2
    while i < len(argv) and argv[i].startswith("-") and argv[i] != "-m":
        if argv[i] in _UV_FLAGS:
            i += 1
        elif argv[i] in _UV_FLAGS_WITH_VALUE and i + 1 < len(argv):
            i += 2
        else:
            return None
    if i < len(argv) and argv[i] == "python":
        i += 1
    if i >= len(argv):
        return None
    target = argv[i]
    if target == "-m":
        if i + 1 >= len(argv):
            return None
    elif not target.endswith(".py") or ".." in Path(target).parts or target.startswith("/"):
        return None
    return Command(tuple(argv), cwd=cwd)


def _note_ids(course: str, module: str, demonstrates: Any) -> tuple[str, ...]:  # noqa: ANN401 - raw YAML
    out = []
    for note in demonstrates if isinstance(demonstrates, list) else []:
        if isinstance(note, str) and note.endswith((".md", ".ipynb")) and ".." not in note:
            out.append(f"{course}/{module}/{Path(note).with_suffix('').as_posix()}")
    return tuple(out)


def _load_manifest(manifest: Path, courses_dir: Path) -> list[Lab]:
    pillar = manifest.parent.parent
    course, module = pillar.parent.name, pillar.name
    try:
        data = yaml.safe_load(manifest.read_text())
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
        log.warning(
            "labs.manifest_skipped", path=str(manifest), error=str(e).splitlines()[0] or repr(e)
        )
        return []
    labs: list[Lab] = []
    practice = pillar / "practice"
    entries = data.get("examples") if isinstance(data, dict) else None
    for entry in entries or []:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        rel_pillar = Path(entry["path"])
        if rel_pillar.parts[:1] != ("practice",) or ".." in rel_pillar.parts:
            continue
        if not (pillar / rel_pillar).exists():
            continue  # not mirrored: licence unrecorded
        if entry.get("pattern") == "other" and not entry.get("demonstrates"):
            continue  # a helper module like chartstyle.py, not a lab
        rel = Path(*rel_pillar.parts[1:])
        language = str(entry.get("language") or "")
        verified_by = str(entry.get("verified_by") or "")
        labs.append(
            Lab(
                id=(pillar / rel_pillar).relative_to(courses_dir).as_posix(),
                course=course,
                module=module,
                path=rel_pillar.as_posix(),
                title=_title(rel.name),
                purpose=str(entry.get("purpose") or ""),
                pattern=str(entry.get("pattern") or "other"),
                language=language,
                runs_offline=bool(entry.get("runs_offline", True)),
                verified_by="" if verified_by == "none" else verified_by,
                licence=str(entry.get("licence") or ""),
                notes=_note_ids(course, module, entry.get("demonstrates")),
                files=_editable(practice, rel),
                run=_run_command(practice, rel, language),
                check=parse_check(verified_by, rel) if language == "python" else None,
                is_folder=(practice / rel).is_dir(),
            )
        )
    return labs


def _manifests(courses_dir: Path) -> list[Path]:
    return sorted(p for p in courses_dir.glob(MANIFEST_GLOB) if p.parts[-4] != PRIVATE_COURSES)


def _signature(paths: list[Path]) -> tuple[tuple[str, int], ...]:
    return tuple((str(p), p.stat().st_mtime_ns) for p in paths)


@lru_cache(maxsize=2)
def _load(courses_dir: Path, _sig: tuple[tuple[str, int], ...]) -> dict[str, Lab]:
    labs: dict[str, Lab] = {}
    for manifest in _manifests(courses_dir):
        for lab in _load_manifest(manifest, courses_dir):
            labs[lab.id] = lab
    log.debug("labs.loaded", labs=len(labs))
    return labs


def all_labs() -> dict[str, Lab]:
    """Lab id → Lab, in course and module order. Rebuilt when a manifest changes."""
    manifests = _manifests(COURSES_DIR)
    return _load(COURSES_DIR, _signature(manifests))


def get(lab_id: str) -> Lab | None:
    return all_labs().get(lab_id)


def lab_file(lab: Lab, rel: str) -> Path | None:
    """One of the lab's editable files in the mirror, or None when `rel` is not one of them."""
    if rel not in lab.files:
        return None
    target = COURSES_DIR / lab.practice_dir / rel
    return target if target.is_file() else None
