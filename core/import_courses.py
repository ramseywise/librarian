"""Import learn-ai-engineering + sisyphus coursework → data/courses/

One course per subject directory (ai-engineering, generative-ai, data-* from
learn-ai-engineering; programming and interviewing from sisyphus — see SUBJECT_SOURCES).
Inside a subject, each top-level directory becomes a module and every
authored .md / .mdx / .ipynb file under it becomes a lesson. Files at the subject root
land in a synthetic `00-start-here` module. Subdirectories inside a module become
sidebar sections, so the source layout survives as-is.

Conversions:
- .mdx (Nextra pages, e.g. the DAIR.AI Prompt Engineering Guide) → plain markdown.
  <Tabs>/<Tab> become labelled blocks, <Screenshot>/<Callout>/<Cards> become images,
  blockquotes and link lists; course-promo components are dropped. Code fences are
  never touched.
- .ipynb → markdown cells + fenced code cells. Outputs are dropped.
- Relative images are copied into the module's `assets/`, and links to other imported
  files are rewritten to the lesson they became.

Vendored upstream snapshots (`*-main`, `*-master`, hash-suffixed, nested git repos — see
learn-ai-engineering/VENDORED.md) are NOT imported. They are listed on their module as
references. PDFs are listed as readings.

Re-runnable while learn-ai-engineering is mid-consolidation. Every generated file
carries `imported_hash`, a hash of the text the importer wrote:
- unchanged since import + source changed  → rewritten
- edited in librarian (hash mismatch)      → left alone, reported as `kept_local_edit`
- source deleted or moved                  → generated copy removed (unless edited)
Files without `imported_hash` are hand-authored lessons and are never touched.

Usage:
    uv run python core/import_courses.py
    uv run python core/import_courses.py --dry-run
    uv run python core/import_courses.py --subject ai-engineering
    uv run python core/import_courses.py --source ~/workspace/learn-ai-engineering
    uv run python core/import_courses.py --sisyphus ~/workspace/sisyphus
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import re
import shutil
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

import structlog
import yaml

from core.base import REPO_ROOT
from core.scrape_claude_docs import WORKSPACE_DIR
from core.wiki_common import slugify

log = structlog.get_logger()

LAE = "learn-ai-engineering"
SISYPHUS = "sisyphus"
DEFAULT_SOURCE = WORKSPACE_DIR / LAE
DEFAULT_SISYPHUS = WORKSPACE_DIR / SISYPHUS
COURSES_DIR = REPO_ROOT / "data" / "courses"

# Subjects that don't live at learn-ai-engineering/<slug>: slug → (repo, dir in that repo).
# Interview prep and the language drills moved to sisyphus on 2026-10-28; the course slugs
# stay the same so existing data/courses/ paths and local edits carry over.
SUBJECT_SOURCES: dict[str, tuple[str, str]] = {
    "programming": (SISYPHUS, "drills"),
    "interviewing": (SISYPHUS, "interviewing"),
}

# slug → (title, order, summary). Order follows CURRICULUM.md Path C (broad → deep), with
# interviewing last because it is the summary layer, not the depth layer. Summaries are
# fixed here because subject READMEs open with curriculum-ordering notes, not blurbs.
SUBJECTS: dict[str, tuple[str, int, str]] = {
    "programming": (
        "Programming",
        1,
        "Language drills (Python, SQL, TypeScript, Terraform) and interview-format coding rounds.",
    ),
    "data-analytics": (
        "Data Analytics",
        2,
        "Python fundamentals for working with data: core language features, then text analytics.",
    ),
    "data-science": (
        "Data Science",
        3,
        "Machine learning and deep learning fundamentals: course work, worked assignments "
        "and notebooks.",
    ),
    "data-engineering": (
        "Data Engineering",
        4,
        "Pipelines, warehouses, orchestration and streaming, via two DataTalksClub Zoomcamps.",
    ),
    "generative-ai": (
        "Generative AI",
        5,
        "LLM fundamentals, RAG, agentic foundations and frameworks, RL and alignment, "
        "observability and applications.",
    ),
    "ai-engineering": (
        "AI Engineering",
        6,
        "The engineering disciplines on top of models: prompt, context, harness, loop, graph "
        "and eval.",
    ),
    "interviewing": (
        "Interviewing",
        7,
        "Interview prep for AI, ML, data science and forward-deployed engineering roles.",
    ),
}

ROOT_MODULE = "00-start-here"
LESSON_EXTS = {".md", ".mdx", ".ipynb"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
MAX_ASSET_BYTES = 2 * 1024 * 1024
MAX_LESSON_CHARS = 400_000

_VENDORED_RE = re.compile(r"(-main|-master|-[0-9a-f]{7})$")
# Suffix rule exceptions. The Prompt Engineering Guide is imported on purpose so the
# Nextra copy can be deleted from learn-ai-engineering. (BayesianML-master was renamed
# to BayesianML on 2026-10-28 and no longer needs one.)
VENDORED_ALLOW = {"Prompt-Engineering-Guide-main"}
# Nested git repos are skipped unless they are your own work.
NESTED_GIT_ALLOW = {"Leet-Code", "leetcode"}
SKIP_DIRS = {"node_modules", ".next", ".ipynb_checkpoints", "__pycache__", "site-packages"}
# sisyphus drill progress history — not lesson content.
SKIP_FILES = {"drill-log.md"}
DRILL_FIELDS = ("title", "track", "topic", "difficulty", "timebox_min")

_HASH_LINE_RE = re.compile(r"^imported_hash: [0-9a-f]+\n", re.MULTILINE)
_TRAILING_WS_RE = re.compile(r"[ \t]+$", re.MULTILINE)
_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_H1_RE = re.compile(r"^#\s+(.+?)\s*#*\s*$", re.MULTILINE)
_NUM_PREFIX_RE = re.compile(r"^(\d+)[-_. ]+")
_MD_IMAGE_RE = re.compile(r"(!\[[^\]]*\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")
_MD_LINK_RE = re.compile(r"((?<!!)\[[^\]]*\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")
_HTML_IMG_RE = re.compile(r"(<img\b[^>]*?\bsrc=[\"'])([^\"']+)([\"'])", re.IGNORECASE)
# `STUDENT_TOKEN = 'abc123'` — coursework notebooks carry grader tokens and emails.
# `KEY` needs a prefix (api_key, SECRET_KEY): a bare `key='sentence'` is an ordinary kwarg.
# Values opening with `<` or `[` are special tokens (oov_token="<oov>", "[CLS]"), not secrets.
_CREDENTIAL_RE = re.compile(
    r"""(\b(?:\w*(?:TOKEN|SECRET|PASSWORD|EMAIL)|\w+KEY)\s*=\s*)(['"])[^'"\n<\[][^'"\n]*\2""",
    re.IGNORECASE,
)


# ── Naming ────────────────────────────────────────────────────────────────────


def _stem(name: str) -> str:
    """Filename without extension or Nextra's `.en` locale suffix."""
    stem = Path(name).stem
    return stem[:-3] if stem.endswith(".en") else stem


def prettify(name: str) -> str:
    """`01-prompt-engineering` → `Prompt Engineering`; leaves mixed-case names alone."""
    text = _NUM_PREFIX_RE.sub("", _stem(name)) or _stem(name)
    text = re.sub(r"[-_]+", " ", text).strip()
    return text[:1].upper() + text[1:] if text.islower() else text


def _order_of(name: str) -> int | None:
    m = _NUM_PREFIX_RE.match(name)
    return int(m.group(1)) if m else None


def _dest_segment(name: str) -> str:
    return slugify(_stem(name)) or "untitled"


# ── Discovery ─────────────────────────────────────────────────────────────────


@dataclass
class Lesson:
    src: Path
    module: str  # dest module dir name
    rel_dir: tuple[str, ...]  # source dirs between module and file
    dest: Path  # relative to COURSES_DIR
    title: str = ""
    order: int = 0


@dataclass
class Module:
    name: str  # dest dir name
    src_dir: Path | None
    title: str
    order: int
    lessons: list[Lesson] = field(default_factory=list)
    readings: list[dict[str, str]] = field(default_factory=list)
    references: list[dict[str, str]] = field(default_factory=list)


def _is_vendored(path: Path) -> bool:
    if path.name in VENDORED_ALLOW:
        return False
    if _VENDORED_RE.search(path.name):
        return True
    return (path / ".git").exists() and path.name not in NESTED_GIT_ALLOW


def _vendored_urls(source: Path) -> dict[str, str]:
    """Map `subject/.../dir` → upstream URL from VENDORED.md's table."""
    vendored_md = source / "VENDORED.md"
    if not vendored_md.exists():
        return {}
    urls: dict[str, str] = {}
    for m in re.finditer(r"^\|\s*`([^`]+)`\s*\|\s*(https?://\S+)", vendored_md.read_text(), re.M):
        urls[m.group(1)] = m.group(2)
    return urls


def _meta_order(directory: Path) -> dict[str, tuple[int, str]]:
    """Nextra `_meta*.json` → {stem: (index, title)} for ordering and titles."""
    for meta in sorted(directory.glob("_meta*.json")):
        try:
            data = json.loads(meta.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        out: dict[str, tuple[int, str]] = {}
        for i, (key, val) in enumerate(data.items()):
            title = val if isinstance(val, str) else (val or {}).get("title", "")
            out[key] = (i, title)
        return out
    return {}


def _file_rank(path: Path, meta: dict[str, tuple[int, str]]) -> tuple[int, int, str]:
    name = path.name.lower()
    if name == "readme.md":
        return (0, 0, name)
    if name == "curriculum.md":
        return (1, 0, name)
    if (n := _order_of(path.name)) is not None:
        return (2, n, name)
    if _stem(path.name) in meta:
        return (3, meta[_stem(path.name)][0], name)
    return (4, 0, name)


def _walk(
    directory: Path, rel: tuple[str, ...]
) -> Iterator[tuple[Path, tuple[str, ...], dict[str, tuple[int, str]]]]:
    """Yield (file, rel_dirs, meta) for lesson files, depth-first, in display order."""
    try:
        entries = list(directory.iterdir())
    except OSError:
        return
    meta = _meta_order(directory)
    files = [
        p
        for p in entries
        if p.is_file() and p.suffix.lower() in LESSON_EXTS and p.name not in SKIP_FILES
    ]
    for f in sorted(files, key=lambda p: _file_rank(p, meta)):
        yield f, rel, meta
    dirs = [
        p
        for p in entries
        if p.is_dir()
        and not p.name.startswith(".")
        and not p.name.endswith("_files")
        and p.name not in SKIP_DIRS
        and not _is_vendored(p)
    ]
    for d in sorted(
        dirs, key=lambda p: (_order_of(p.name) is None, _order_of(p.name) or 0, p.name.lower())
    ):
        yield from _walk(d, (*rel, d.name))


def _collect_extras(directory: Path, source: Path, urls: dict[str, str], module: Module) -> None:
    """PDFs → readings, vendored snapshot dirs → references (recursive, skip vendored)."""
    for dp, dns, fns in os.walk(directory):
        here = Path(dp)
        keep = []
        for d in dns:
            p = here / d
            if d.startswith(".") or d in SKIP_DIRS:
                continue
            if _is_vendored(p):
                rel = str(p.relative_to(source))
                module.references.append(
                    {"title": d, "source": rel, **({"url": urls[rel]} if rel in urls else {})}
                )
                continue
            keep.append(d)
        dns[:] = sorted(keep)
        for f in sorted(fns):
            if f.lower().endswith(".pdf"):
                module.readings.append(
                    {"title": prettify(f), "source": str((here / f).relative_to(source))}
                )


def discover(source: Path, subject: str, subject_dir: Path | None = None) -> list[Module]:
    """`source` is the repo root (paths in metadata are relative to it); `subject_dir`
    defaults to `source / subject` and differs only for SUBJECT_SOURCES entries."""
    subject_dir = subject_dir or source / subject
    urls = _vendored_urls(source)
    modules: dict[str, Module] = {}

    root = Module(ROOT_MODULE, None, "Start Here", 0)
    modules[ROOT_MODULE] = root
    root_meta = _meta_order(subject_dir)
    for f in sorted(
        (
            p
            for p in subject_dir.iterdir()
            if p.is_file() and p.suffix.lower() in LESSON_EXTS and p.name not in SKIP_FILES
        ),
        key=lambda p: _file_rank(p, root_meta),
    ):
        root.lessons.append(Lesson(f, ROOT_MODULE, (), Path()))
    for f in sorted(subject_dir.glob("*.pdf")):
        root.readings.append({"title": prettify(f.name), "source": str(f.relative_to(source))})

    children = [
        p
        for p in subject_dir.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p.name not in SKIP_DIRS
    ]
    for i, d in enumerate(
        sorted(
            children,
            key=lambda p: (_order_of(p.name) is None, _order_of(p.name) or 0, p.name.lower()),
        )
    ):
        if _is_vendored(d):
            rel = str(d.relative_to(source))
            root.references.append(
                {"title": d.name, "source": rel, **({"url": urls[rel]} if rel in urls else {})}
            )
            continue
        name = _dest_segment(d.name)
        mod = Module(name, d, prettify(d.name), _order_of(d.name) or 100 + i)
        for f, rel, _ in _walk(d, ()):
            mod.lessons.append(Lesson(f, name, rel, Path()))
        _collect_extras(d, source, urls, mod)
        if mod.lessons or mod.readings or mod.references:
            modules[name] = mod

    for mod in modules.values():
        for i, lesson in enumerate(mod.lessons):
            lesson.order = i + 1
            segs = [_dest_segment(s) for s in lesson.rel_dir]
            lesson.dest = Path(subject, mod.name, *segs, f"{_dest_segment(lesson.src.name)}.md")
        _dedupe_dests(mod.lessons)
    return [m for m in modules.values() if m.lessons or m.readings or m.references]


def _dedupe_dests(lessons: list[Lesson]) -> None:
    """`intro.md` + `intro.ipynb` in one dir would collide after slugging — suffix the later."""
    seen: set[Path] = set()
    for lesson in lessons:
        dest, n = lesson.dest, 2
        while dest in seen:
            dest = lesson.dest.with_name(f"{lesson.dest.stem}-{n}.md")
            n += 1
        lesson.dest = dest
        seen.add(dest)


# ── Conversion ────────────────────────────────────────────────────────────────


def _outside_fences(text: str) -> Iterator[tuple[str, bool]]:
    """Yield (line, in_fence) so transforms can skip code blocks."""
    in_fence = False
    for line in text.split("\n"):
        if _FENCE_RE.match(line):
            yield line, True
            in_fence = not in_fence
            continue
        yield line, in_fence


def _jsx_attr(tag: str, attr: str) -> str:
    m = re.search(rf"\b{attr}\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|\{{([^}}]*)\}})", tag)
    if not m:
        return ""
    return next(g for g in m.groups() if g is not None).strip()


def _dedent(lines: list[str]) -> list[str]:
    widths = [len(ln) - len(ln.lstrip()) for ln in lines if ln.strip()]
    cut = min(widths) if widths else 0
    return [ln[cut:] for ln in lines]


_DROP_BLOCKS = ("CoursesSection", "CoursePromo", "CourseCard", "AnnouncementBar")


def mdx_to_markdown(text: str) -> tuple[str, dict[str, str]]:
    """Convert a Nextra MDX page to plain markdown.

    Returns (markdown, image_imports) where image_imports maps an `import X from 'p'`
    binding to its path — <Screenshot src={X}> becomes `![alt](p)`.
    """
    imports: dict[str, str] = {}
    out: list[str] = []
    tabs: list[str] = []  # labels of the open <Tabs items=[...]>
    tab_idx = 0
    tab_buf: list[str] | None = None
    drop_depth = 0
    tag_buf: str | None = None  # accumulates a multi-line JSX tag

    def emit(line: str) -> None:
        (tab_buf if tab_buf is not None else out).append(line)

    text = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.S)
    for line, in_fence in _outside_fences(text):
        if in_fence:
            if drop_depth == 0:
                emit(line)
            continue
        stripped = line.strip()

        if tag_buf is not None:
            tag_buf += " " + stripped
            if not stripped.endswith(">"):
                continue
            stripped, tag_buf = tag_buf, None
        elif re.match(r"^<[A-Z][A-Za-z]*\b", stripped) and not stripped.endswith(">"):
            tag_buf = stripped
            continue

        if m := re.match(r"^import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"];?$", stripped):
            imports[m.group(1)] = m.group(2)
            continue
        if re.match(r"^(import|export)\s", stripped):
            continue

        if any(stripped.startswith(f"<{c}") for c in _DROP_BLOCKS):
            if not stripped.endswith("/>"):
                drop_depth += 1
            continue
        if any(stripped.startswith(f"</{c}") for c in _DROP_BLOCKS):
            drop_depth = max(0, drop_depth - 1)
            continue
        if drop_depth:
            continue

        # <Tab> (Nextra 2) and <Tabs.Tab> (Nextra 3) are the same thing.
        if re.match(r"^<(Tabs\.)?Tab\b", stripped):
            tab_buf = []
            continue
        if re.match(r"^</(Tabs\.)?Tab>", stripped) and tab_buf is not None:
            label = tabs[tab_idx] if tab_idx < len(tabs) else f"Option {tab_idx + 1}"
            body, tab_buf = _dedent(tab_buf), None
            out.extend([f"**{label}**", "", *body, ""])
            tab_idx += 1
            continue
        if re.match(r"^<Tabs\b", stripped):
            items = re.findall(r"['\"]([^'\"]+)['\"]", _jsx_attr(stripped, "items"))
            tabs, tab_idx = items, 0
            continue
        if re.match(r"^</Tabs>", stripped):
            tabs = []
            continue

        if stripped.startswith("<Screenshot"):
            src = _jsx_attr(stripped, "src")
            alt = _jsx_attr(stripped, "alt") or src
            path = imports.get(src, src)
            emit(f"![{alt}]({path})")
            continue
        if stripped.startswith("<Callout"):
            kind = _jsx_attr(stripped, "type") or "info"
            label = {"warning": "Warning", "error": "Caution"}.get(kind, "Note")
            emit(f"<!--callout:{label}-->")
            continue
        if stripped.startswith("</Callout"):
            _close_callout(tab_buf if tab_buf is not None else out)
            continue
        if stripped.startswith("<Card") and not stripped.startswith("<Cards"):
            title = _jsx_attr(stripped, "title") or "Link"
            href = _jsx_attr(stripped, "href")
            emit(f"- [{title}]({href})" if href else f"- {title}")
            continue
        if stripped.startswith("<iframe"):
            src = _jsx_attr(stripped, "src")
            if src:
                emit(f"▶ Video: <{src}>")
            continue
        if re.match(r"^</?[A-Z][A-Za-z]*\b[^>]*/?>$", stripped):
            continue  # any other component wrapper: keep its children, drop the tag
        emit(line)

    md = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n", imports


def _close_callout(buf: list[str]) -> None:
    """Prefix the lines since the callout marker with `> ` and drop promo callouts."""
    idx = next((i for i in range(len(buf) - 1, -1, -1) if buf[i].startswith("<!--callout:")), None)
    if idx is None:
        return
    label = buf[idx][len("<!--callout:") : -len("-->")]
    body = buf[idx + 1 :]
    del buf[idx:]
    if re.search(r"PROMPTING20|% off|\bpromo code\b", "\n".join(body), re.I):
        return
    buf.append(f"> **{label}:**")
    buf.extend(f"> {ln}".rstrip() for ln in body if ln.strip())
    buf.append("")


def notebook_to_markdown(raw: str) -> str:
    nb = json.loads(raw)
    lang = (
        nb.get("metadata", {}).get("language_info", {}).get("name")
        or nb.get("metadata", {}).get("kernelspec", {}).get("language")
        or "python"
    )
    parts: list[str] = []
    for cell in nb.get("cells", []):
        src = cell.get("source", "")
        src = "".join(src) if isinstance(src, list) else src
        if not src.strip():
            continue
        if cell.get("cell_type") == "markdown":
            parts.append(src.strip())
        elif cell.get("cell_type") == "code":
            parts.append(f"```{lang}\n{src.rstrip()}\n```")
    return "\n\n".join(parts) + "\n"


def _title_from(body: str, fallback: str) -> str:
    m = _H1_RE.search(body)
    if m:
        title = re.sub(r"[*_`]|<[^>]+>", "", m.group(1)).strip()
        if 0 < len(title) <= 120:
            return title
    return fallback


def _summary_from(body: str) -> str:
    for para in re.split(r"\n\s*\n", body):
        p = para.strip()
        if not p or p.startswith(("#", "```", "|", "!", ">", "-", "*", "<", "[")) or len(p) < 40:
            continue
        # Bare links, numbered lists, and "…as follows:" lead-ins make useless summaries.
        if re.match(r"^(\S+://\S+|\d+[.)]\s)", p) or p.rstrip().endswith(":"):
            continue
        p = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", p)
        p = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", p)
        # Code spans keep their text verbatim (`order_id` stays order_id); only
        # emphasis markers outside them are dropped.
        spans = re.split(r"(`[^`]*`)", " ".join(p.split()))
        p = "".join(
            s.strip("`") if s.startswith("`") else re.sub(r"\*+|(?<!\w)_+|_+(?!\w)", "", s)
            for s in spans
        )
        m = re.match(r"(.{40,240}?[.!?])(\s|$)", p)
        return m.group(1) if m else p[:240].rstrip() + ("…" if len(p) > 240 else "")
    return ""


# ── Link + asset rewriting ────────────────────────────────────────────────────


def _is_relative(url: str) -> bool:
    return not re.match(r"^([a-z][a-z0-9+.-]*:|#|/|<)", url, re.I)


@functools.cache
def _image_index(root: Path) -> dict[str, list[Path]]:
    """basename → image files under a module dir (vendored dirs excluded)."""
    index: dict[str, list[Path]] = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not _is_vendored(Path(dp) / d)]
        for f in fns:
            if Path(f).suffix.lower() in IMAGE_EXTS:
                index.setdefault(f, []).append(Path(dp) / f)
    return index


def _find_moved_image(url: str, root: Path) -> Path | None:
    """Relocate an image whose relative path broke because its page or folder moved.

    Consolidation moves pages (and their `img/` dirs) around, so `../../img/x/sky.png`
    stops resolving. Match on the longest shared path tail among same-named files.
    """
    tail = [p for p in Path(url.split("#")[0].replace("%20", " ")).parts if p not in ("..", ".")]
    if not tail:
        return None
    candidates = _image_index(root.resolve()).get(tail[-1], [])

    def shared(c: Path) -> int:
        n = 0
        for a, b in zip(reversed(c.parts), reversed(tail), strict=False):
            if a != b:
                break
            n += 1
        return n

    best = max(candidates, key=shared, default=None)
    return best if best and shared(best) >= min(2, len(tail)) else None


def _rewrite_body(
    body: str,
    lesson: Lesson,
    image_imports: dict[str, str],
    src_to_dest: dict[Path, Path],
    module_src: Path,
    plan: Plan,
) -> str:
    lesson_dir = (COURSES_DIR / lesson.dest).parent
    module_dest = COURSES_DIR / lesson.dest.parts[0] / lesson.dest.parts[1]
    asset_root = module_src if module_src else lesson.src.parent

    def resolve(url: str) -> Path | None:
        path = url.split("#")[0].split("?")[0]
        if not path:
            return None
        try:
            target = (lesson.src.parent / path.replace("%20", " ")).resolve()
        except (OSError, ValueError):
            return None
        return target if target.exists() else None

    def image(url: str) -> str:
        url = image_imports.get(url, url)
        if not _is_relative(url):
            return url
        target = resolve(url) or _find_moved_image(url, asset_root)
        if not target or target.suffix.lower() not in IMAGE_EXTS or not target.is_file():
            return url
        if target.stat().st_size > MAX_ASSET_BYTES:
            return url
        try:
            rel = target.relative_to(asset_root)
        except ValueError:
            rel = Path(target.name)
        dest = (
            module_dest
            / "assets"
            / Path(*[_dest_segment(p) for p in rel.parent.parts], target.name)
        )
        plan.assets[dest] = target
        return os.path.relpath(dest, lesson_dir).replace(" ", "%20")

    def link(url: str) -> str:
        if not _is_relative(url):
            return url
        target = resolve(url)
        if target and target in src_to_dest:
            anchor = "#" + url.split("#", 1)[1] if "#" in url else ""
            return os.path.relpath(COURSES_DIR / src_to_dest[target], lesson_dir) + anchor
        return url

    out: list[str] = []
    for line, in_fence in _outside_fences(body):
        if not in_fence:
            line = _MD_IMAGE_RE.sub(lambda m: m.group(1) + image(m.group(2)) + m.group(3), line)
            line = _HTML_IMG_RE.sub(lambda m: m.group(1) + image(m.group(2)) + m.group(3), line)
            line = _MD_LINK_RE.sub(lambda m: m.group(1) + link(m.group(2)) + m.group(3), line)
        out.append(line)
    return "\n".join(out)


# ── Writing ───────────────────────────────────────────────────────────────────


@dataclass
class Plan:
    files: dict[Path, str] = field(default_factory=dict)  # dest (abs) → text
    assets: dict[Path, Path] = field(default_factory=dict)  # dest (abs) → source


def _hash(text: str) -> str:
    return hashlib.sha256(_HASH_LINE_RE.sub("", text).encode()).hexdigest()[:16]


def _normalize_ws(text: str) -> str:
    """What the trailing-whitespace and end-of-file-fixer pre-commit hooks leave behind."""
    return _TRAILING_WS_RE.sub("", text).rstrip("\n") + "\n"


def render(meta: dict, body: str = "") -> str:
    """Frontmatter + body, with `imported_hash` covering everything else in the file."""
    head = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000)
    # Pre-normalized so the commit hooks leave the file (and its hash) untouched.
    text = _normalize_ws(f"---\n{head}---\n\n{body}" if body else f"---\n{head}---\n")
    digest = _hash(text)
    return text.replace("---\n", f"---\nimported_hash: {digest}\n", 1)


def _recorded_hash(text: str) -> str | None:
    m = re.search(r"^imported_hash: ([0-9a-f]+)$", text, re.M)
    return m.group(1) if m else None


def build_plan(source: Path, subjects: list[str], sisyphus: Path = DEFAULT_SISYPHUS) -> Plan:
    plan = Plan()
    roots = {LAE: source, SISYPHUS: sisyphus}
    for subject in subjects:
        repo, rel = SUBJECT_SOURCES.get(subject, (LAE, subject))
        root = roots[repo]
        subject_dir = root / rel
        if not subject_dir.is_dir():
            log.warning("subject_missing", subject=subject, path=str(subject_dir))
            continue
        modules = discover(root, subject, subject_dir)
        src_to_dest = {
            lesson.src.resolve(): lesson.dest for mod in modules for lesson in mod.lessons
        }
        title, order, summary = SUBJECTS[subject]
        plan.files[COURSES_DIR / subject / "_course.md"] = render(
            {
                "title": title,
                "summary": summary,
                "order": order,
                "source": f"{repo}/{rel}",
            }
        )
        for mod in modules:
            mod_summary = ""
            if mod.src_dir and (mod.src_dir / "README.md").exists():
                mod_readme = (mod.src_dir / "README.md").read_text(errors="replace")
                mod_summary = _summary_from(mod_readme)
                mod.title = (
                    _title_from(mod_readme, mod.title)
                    if len(_title_from(mod_readme, "")) < 60
                    else mod.title
                )
            meta: dict = {"title": mod.title, "summary": mod_summary, "order": mod.order}
            if mod.src_dir:
                meta["source"] = f"{repo}/{mod.src_dir.relative_to(root)}"
            if mod.readings:
                meta["readings"] = mod.readings
            if mod.references:
                meta["references"] = mod.references
            plan.files[COURSES_DIR / subject / mod.name / "_module.md"] = render(meta)
            for lesson in mod.lessons:
                _plan_lesson(plan, lesson, mod, root, src_to_dest, repo)
    return plan


def _plan_lesson(
    plan: Plan,
    lesson: Lesson,
    mod: Module,
    source: Path,
    src_to_dest: dict,
    repo: str = LAE,
) -> None:
    try:
        raw = lesson.src.read_text(errors="replace")
    except OSError as e:
        log.warning("lesson_unreadable", path=str(lesson.src), error=str(e))
        return
    ext = lesson.src.suffix.lower()
    imports: dict[str, str] = {}
    kind = "reading"
    drill: dict = {}
    if ext == ".mdx":
        body, imports = mdx_to_markdown(raw)
    elif ext == ".ipynb":
        try:
            body = notebook_to_markdown(raw)
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            log.warning("notebook_unparseable", path=str(lesson.src), error=str(e))
            return
        kind = "notebook"
    else:
        body = raw
        if body.startswith("---\n"):  # source frontmatter is not ours to keep…
            end = body.find("\n---", 4)
            if end != -1:
                drill = _drill_meta(body[4:end])  # …except the sisyphus drill schema
                body = body[end + 4 :].lstrip()
        if drill:
            kind = "drill"
    if len(body) > MAX_LESSON_CHARS:
        log.warning("lesson_too_large", path=str(lesson.src), chars=len(body))
        return
    body = _CREDENTIAL_RE.sub(r'\1"<redacted>"', body)

    meta_titles = _meta_order(lesson.src.parent)
    meta_title = meta_titles.get(_stem(lesson.src.name), (0, ""))[1]
    fallback = prettify(lesson.src.name)
    if lesson.src.name.lower() == "readme.md":
        fallback = "Overview"
    title = drill.pop("title", "") or meta_title or _title_from(body, fallback)
    body = _rewrite_body(body, lesson, imports, src_to_dest, mod.src_dir or lesson.src.parent, plan)

    meta: dict = {
        "title": title,
        "summary": _summary_from(body),
        "order": lesson.order,
        "kind": kind,
    }
    if lesson.rel_dir:
        meta["section"] = " / ".join(prettify(s) for s in lesson.rel_dir)
    meta.update(drill)
    meta["source"] = f"{repo}/{lesson.src.relative_to(source)}"
    plan.files[COURSES_DIR / lesson.dest] = render(meta, body)


def _drill_meta(head: str) -> dict:
    """Fields of a sisyphus drill's frontmatter (drills/README.md) worth keeping.

    A drill is any file whose frontmatter names a `track`. Its `concepts` become `wiki`,
    the explicit concept links the courses API ranks first.
    """
    try:
        fm = yaml.safe_load(head)
    except yaml.YAMLError:
        return {}
    if not isinstance(fm, dict) or not fm.get("track"):
        return {}
    out: dict = {k: fm[k] for k in DRILL_FIELDS if fm.get(k) not in (None, "")}
    if isinstance(fm.get("concepts"), list):
        out["wiki"] = [str(c) for c in fm["concepts"]]
    return out


def apply(plan: Plan, subjects: list[str], dry_run: bool) -> dict[str, int]:
    stats = dict.fromkeys(
        ("created", "updated", "unchanged", "kept_local_edit", "removed", "assets"), 0
    )
    for dest, text in plan.files.items():
        if not dest.exists():
            stats["created"] += 1
        else:
            current = dest.read_text()
            recorded = _recorded_hash(current)
            hook_rewritten = _normalize_ws(_HASH_LINE_RE.sub("", current)) == _HASH_LINE_RE.sub(
                "", text
            )
            if (recorded is None or _hash(current) != recorded) and not hook_rewritten:
                stats["kept_local_edit"] += 1
                log.info("kept_local_edit", path=str(dest.relative_to(COURSES_DIR)))
                continue
            if current == text:
                stats["unchanged"] += 1
                continue
            stats["updated"] += 1
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text)

    for dest, src in plan.assets.items():
        if dest.exists() and dest.stat().st_size == src.stat().st_size:
            continue
        stats["assets"] += 1
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    # Generated files whose source vanished (moved or deleted during consolidation).
    for subject in subjects:
        subject_dir = COURSES_DIR / subject
        if not subject_dir.is_dir():
            continue
        for path in subject_dir.rglob("*.md"):
            if path in plan.files:
                continue
            current = path.read_text()
            recorded = _recorded_hash(current)
            if recorded is None or _hash(current) != recorded:
                continue  # hand-authored or locally edited — never delete
            stats["removed"] += 1
            log.info("removed_stale", path=str(path.relative_to(COURSES_DIR)))
            if not dry_run:
                path.unlink()
        if not dry_run:
            for d in sorted(subject_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if d.is_dir() and d.name != "assets" and not any(d.iterdir()):
                    d.rmdir()
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--sisyphus", type=Path, default=DEFAULT_SISYPHUS)
    parser.add_argument("--subject", action="append", choices=sorted(SUBJECTS))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    sisyphus = args.sisyphus.expanduser().resolve()
    subjects = args.subject or list(SUBJECTS)
    # Only require the repos the selected subjects actually read from.
    needed = {SUBJECT_SOURCES.get(s, (LAE, s))[0] for s in subjects}
    for repo, path in ((LAE, source), (SISYPHUS, sisyphus)):
        if repo in needed and not path.is_dir():
            parser.error(f"source not found: {path}")
    plan = build_plan(source, subjects, sisyphus)
    stats = apply(plan, subjects, args.dry_run)
    log.info("import_courses_done", dry_run=args.dry_run, subjects=len(subjects), **stats)


if __name__ == "__main__":
    main()
