"""Lecture slides for the study UI: per-slide images, text and notes for one module's deck.

A module's deck is `data/courses/<course>/<module>/slides/deck.yaml` and its lectures are
`slides/lectures/<NN-slug>.yaml`. The tracked specs stay the source. The viewer needs per-slide
images, which `librarian.tools.slides.build_deck --preview` renders (courses may not import `librarian.tools.slides`, so
the build runs as a subprocess, exactly as `make slides` runs it). Output goes to the state dir,
`var/slides/<course>/<module>[/<lecture>]/`, never to a tracked path:

    slides.json    per-slide title, text and notes, read back from the built deck
    slide-NN.png   one image per slide
    built.json     which yaml (sha256, as `deck_stamp.py` computes it) the output came from

What a build needs: `uv` (it fetches python-pptx, pillow and resvg-py), and for the images macOS
Quick Look (`qlmanage`). Without Quick Look the text and notes still build and the viewer shows text
slides. Without `uv` the slides are read straight from the yaml (no generated title or divider
slides, no images). `status` says which one the caller got, and `needs` lists what is missing.

Production serves prebuilt files only. A deck's output is read from the content release,
`<content dir>/slides/<deck id>/` (`settings.content_slides_dir`, default `var/content/current/slides`),
when it holds a `built.json` for that deck, else from the state dir as above, so a dev checkout is
unchanged. The subprocess build runs only when `settings.dev_build_slides` is on
(`LIBRARIAN_DEV_BUILD_SLIDES`, set by `make api`). With it off, `deck` never builds and `build_deck`
only reads.

With the build on, a deck is rebuilt in a background thread when its stamp no longer matches the yaml;
the request that finds it stale answers at once with the yaml text and `status: "building"`.
`build_deck.py` also writes the .pptx beside the yaml (gitignored), as `make slides` does.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

import yaml

from librarian.config import get_settings
from librarian.log_config import get_logger

log = get_logger(__name__)

_settings = get_settings()
# Module-level so a test can point them at a temp dir, as the catalog's paths are.
ROOT = _settings.root
COURSES_DIR = _settings.courses_dir
BUILD_DIR = _settings.slides_build_dir
CONTENT_DIR = _settings.content_slides_dir  # prebuilt decks of the content release
DEV_BUILD = _settings.dev_build_slides  # may this process run a build at all

BUILD_TIMEOUT_S = 600
RETRY_FAILED_S = 600.0  # a failed build is retried after this, or at once when the yaml changes
_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_PNG = re.compile(r"^slide-(\d+)\.png$")
_MD_MARKS = re.compile(r"\*\*|__|`")
# Text-bearing keys of a yaml slide, in reading order.
_TEXT_KEYS = ("kicker", "statement", "attribution", "recall", "subtitle", "summary", "takeaway")

_LOCK = threading.Lock()
_RUNNING: dict[str, threading.Thread] = {}


# ── which deck ──────────────────────────────────────────────────────────────


def _split(deck_id: str) -> tuple[str, str, str | None] | None:
    parts = deck_id.strip("/").split("/")
    if len(parts) not in (2, 3) or not all(_SEGMENT.match(p) for p in parts):
        return None
    if parts[0] == "private":  # the public tree only: private lessons never reach the viewer
        return None
    return parts[0], parts[1], parts[2] if len(parts) == 3 else None


def _slides_dir(course: str, module: str) -> Path:
    return COURSES_DIR / course / module / "slides"


def lecture_ids(course: str, module: str) -> list[str]:
    folder = _slides_dir(course, module) / "lectures"
    return sorted(p.stem for p in folder.glob("*.yaml")) if folder.is_dir() else []


def resolve(deck_id: str) -> tuple[str, Path] | None:
    """(canonical deck id, spec path) of a deck, or None. A module with no deck.yaml of its own
    resolves to its first lecture."""
    split = _split(deck_id)
    if split is None:
        return None
    course, module, lecture = split
    base = _slides_dir(course, module)
    if lecture:
        spec = base / "lectures" / f"{lecture}.yaml"
        return (f"{course}/{module}/{lecture}", spec) if spec.is_file() else None
    if (base / "deck.yaml").is_file():
        return f"{course}/{module}", base / "deck.yaml"
    lectures = lecture_ids(course, module)
    if lectures:
        return f"{course}/{module}/{lectures[0]}", base / "lectures" / f"{lectures[0]}.yaml"
    return None


def module_decks(module_id: str) -> list[dict[str, str]]:
    """The decks of one module: its own deck first, then its lectures. [] when it has none."""
    split = _split(module_id)
    if split is None or split[2] is not None:
        return []
    course, module, _ = split
    out = []
    if (_slides_dir(course, module) / "deck.yaml").is_file():
        out.append(
            {
                "id": f"{course}/{module}",
                "title": _deck_title(_slides_dir(course, module) / "deck.yaml"),
            }
        )
    for lecture in lecture_ids(course, module):
        spec = _slides_dir(course, module) / "lectures" / f"{lecture}.yaml"
        out.append({"id": f"{course}/{module}/{lecture}", "title": _deck_title(spec) or lecture})
    return out


def _load_spec(spec: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(spec.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        log.warning("slides.spec_unreadable", spec=spec.name, error=str(e))
        return {}
    return data if isinstance(data, dict) else {}


def _deck_title(spec: Path) -> str:
    deck = _load_spec(spec).get("deck")
    return str(deck.get("title", "")) if isinstance(deck, dict) else ""


def stamp(spec: Path) -> str:
    """sha256 of the yaml bytes: the value `librarian/tools/slides/deck_stamp.py` writes into a built deck."""
    return hashlib.sha256(spec.read_bytes()).hexdigest()


# ── text straight from the yaml (the fallback) ─────────────────────────────


def _plain(value: object) -> str:
    return _MD_MARKS.sub("", str(value)).strip() if isinstance(value, str | int | float) else ""


def yaml_slides(spec: Path) -> list[dict[str, str]]:
    """Slides as the yaml states them, without the generated title, agenda and divider slides."""
    data = _load_spec(spec)
    out: list[dict[str, str]] = []
    for part in data.get("parts") or []:
        if not isinstance(part, dict):
            continue
        for sl in part.get("slides") or []:
            if not isinstance(sl, dict):
                continue
            lines = [_plain(sl.get("title"))]
            lines += [_plain(sl.get(k)) for k in _TEXT_KEYS]
            for key in ("bullets", "items", "points"):
                lines += [_plain(b) for b in sl.get(key) or [] if isinstance(b, str)]
            for step in sl.get("steps") or []:
                if isinstance(step, dict):
                    lines.append(
                        " - ".join(
                            x for x in (_plain(step.get("label")), _plain(step.get("sub"))) if x
                        )
                    )
            lines = [ln for ln in lines if ln]
            out.append(
                {
                    "title": lines[0] if lines else "",
                    "text": "\n".join(lines),
                    "notes": _plain(sl.get("notes")),
                }
            )
    return out


# ── the built output ───────────────────────────────────────────────────────


def build_enabled() -> bool:
    """True on a dev machine that may build decks on request; false when the API only serves files."""
    return DEV_BUILD


def _out_dir(deck_id: str) -> Path:
    """Where a deck's built output is read: the content release if it has the deck, else the state dir."""
    shipped = CONTENT_DIR / deck_id
    return shipped if (shipped / "built.json").is_file() else BUILD_DIR / deck_id


def _build_out_dir(deck_id: str) -> Path:
    """Where a build writes: always the state dir, never the content release."""
    return BUILD_DIR / deck_id


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def needs() -> list[str]:
    """What this machine lacks for image slides. Empty when it has everything."""
    missing = []
    if not shutil.which("uv"):
        missing.append("uv (fetches python-pptx, pillow and resvg-py to build the deck)")
    if not shutil.which("qlmanage"):
        missing.append("macOS Quick Look (qlmanage) to render slide images")
    return missing


def _build_command(spec: Path, out: Path) -> list[str]:
    return [
        "uv", "run", "-q", "--with", "python-pptx", "--with", "pillow", "--with", "resvg-py",
        "python", "-m", "librarian.tools.slides.build_deck", str(spec),
        "--preview", str(out), "--outline", str(out / "slides.json"),
    ]  # fmt: skip


def _run_build(spec: Path, out: Path) -> tuple[bool, str]:
    """Run build_deck.py as `make slides PREVIEW=1` does. (ok, error text)."""
    out.mkdir(parents=True, exist_ok=True)
    try:
        done = subprocess.run(
            _build_command(spec, out),
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=BUILD_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)
    if done.returncode != 0:
        return False, (done.stderr or done.stdout).strip()[-500:]
    return True, ""


def _build(deck_id: str, spec: Path) -> None:
    """Thread body: build, then record what came of it in built.json."""
    out = _build_out_dir(deck_id)
    try:
        digest = stamp(spec)
        ok, error = _run_build(spec, out)
        pngs = len(list(out.glob("slide-*.png"))) if out.is_dir() else 0
        record = {
            "stamp": digest,
            "ok": ok,
            "error": error,
            "pngs": pngs,
            "renderer": not needs(),
            "at": time.time(),
        }
        out.mkdir(parents=True, exist_ok=True)
        (out / "built.json").write_text(json.dumps(record), encoding="utf-8")
        log.info("slides.built", deck=deck_id, ok=ok, pngs=pngs)
    except Exception as e:  # a background thread must not die silently
        log.exception("slides.build_crashed", deck=deck_id, error=str(e))
    finally:
        with _LOCK:
            _RUNNING.pop(deck_id, None)


def _needs_build(built: object, digest: str) -> bool:
    if not isinstance(built, dict) or built.get("stamp") != digest:
        return True
    if not built.get("ok"):
        return time.time() - float(built.get("at", 0)) > RETRY_FAILED_S
    # Built without images: try again only if a renderer has appeared since.
    return not built.get("pngs") and not built.get("renderer") and not needs()


def _start(deck_id: str, spec: Path) -> bool:
    """Start a background build unless one is running. True when one is now running."""
    if not DEV_BUILD:
        return False
    with _LOCK:
        if deck_id in _RUNNING:
            return True
        if not shutil.which("uv"):
            return False
        thread = threading.Thread(
            target=_build, args=(deck_id, spec), daemon=True, name=f"slides-{deck_id}"
        )
        _RUNNING[deck_id] = thread
        thread.start()
        return True


def wait(deck_id: str, timeout: float | None = None) -> None:
    """Block until this deck's background build ends. For tests and scripts."""
    with _LOCK:
        thread = _RUNNING.get(deck_id)
    if thread:
        thread.join(timeout)


def image_url(deck_id: str, n: int) -> str:
    return f"/api/courses/slide-image/{deck_id}/{n}"


def build_deck(deck_id: str) -> dict[str, Any] | None:
    """Start a rebuild when the deck's output is missing or stale, then answer as `deck` does.
    Does nothing but read when `build_enabled()` is false."""
    return deck(deck_id, start=True)


def deck(deck_id: str, *, start: bool = False) -> dict[str, Any] | None:
    """One deck for the viewer. Read-only unless `start`, which begins a rebuild when needed.

    `stale` is true when a build is needed, none is running and one could start: the client
    then asks for it with `build_deck`.

    status: "ready" (images and text from the built deck), "building" (a build is running; the
    slides are the yaml's text), "text" (built, but this machine cannot render images) or
    "failed" (the last build failed; `error` says why, the slides are the yaml's text).
    """
    found = resolve(deck_id)
    if found is None:
        return None
    canonical, spec = found
    split = _split(canonical)
    assert split is not None  # resolve() returned it
    course, module, _ = split
    digest = stamp(spec)
    out = _out_dir(canonical)
    built = _read_json(out / "built.json")
    outline = _read_json(out / "slides.json")
    fresh = isinstance(built, dict) and built.get("stamp") == digest

    running = canonical in _RUNNING
    stale = False
    if _needs_build(built, digest) and not running:
        if start:
            running = _start(canonical, spec)
        else:
            stale = DEV_BUILD and bool(shutil.which("uv"))

    error = ""
    if fresh and isinstance(built, dict) and built.get("ok") and isinstance(outline, list):
        slides = [s for s in outline if isinstance(s, dict)]
        pngs = {int(m.group(1)) for p in out.glob("slide-*.png") if (m := _PNG.match(p.name))}
        has_images = bool(pngs)
        status = "ready" if has_images else "text"
    else:
        slides = yaml_slides(spec)
        pngs, has_images = set(), False
        if running:
            status = "building"
        elif isinstance(built, dict) and built.get("stamp") == digest and not built.get("ok"):
            status, error = "failed", str(built.get("error", ""))
        else:
            status = "text"  # no uv to build with, or output that cannot be read
    return {
        "id": canonical,
        "title": _deck_title(spec),
        "course": course,
        "module": f"{course}/{module}",
        "status": status,
        "images": has_images,
        "stale": stale,
        "needs": needs() if DEV_BUILD and status in ("text", "failed") else [],
        "error": error,
        "decks": module_decks(f"{course}/{module}"),
        "slides": [
            {
                "n": i,
                "title": str(s.get("title", "")),
                "text": str(s.get("text", "")),
                "notes": str(s.get("notes", "")),
                "image": image_url(canonical, i) if i in pngs else None,
            }
            for i, s in enumerate(slides, 1)
        ],
    }


def image_path(deck_id: str, n: int) -> Path | None:
    """The built PNG of slide `n` (1-based) of a deck, or None."""
    found = resolve(deck_id)
    if found is None or n < 1:
        return None
    base = _out_dir(found[0])
    path = base / f"slide-{n:02d}.png"
    if not path.is_file() or not path.resolve().is_relative_to(base.resolve()):
        return None  # missing, or a symlink pointing out of the deck's folder
    return path
