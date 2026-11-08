"""Build a content release: `content-<sha>.tar.zst`, its `.sha256` and a `latest` file.

The release is staged where the server will unpack it (`<state>/content/releases/<name>/`) and
`content/current` is pointed at it while the index is built, because the index stores every
page's absolute path and the server reads pages through `content/current`. The manifest records
that state dir as `serve_root`; a host with another one refuses the release instead of serving
an index whose paths lead nowhere. CI therefore builds inside the image (state dir `/app/var`).

No file under a `private/` directory gets in: both trees are copied without it, and the staged
tree and the archive member list are each checked again before anything is written.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import zstandard

from librarian.config import discover_root, get_release, get_settings
from librarian.log_config import get_logger
from librarian.release import paths

log = get_logger(__name__)

PRIVATE = "private"
# Not content: editor and OS droppings, local tool state.
_SKIP_NAMES = {".DS_Store", ".obsidian", "__pycache__", ".ipynb_checkpoints"}


class PrivatePathError(RuntimeError):
    """A path under a `private/` directory was about to enter a release."""


@dataclass(frozen=True)
class BuiltRelease:
    name: str
    archive: Path
    checksum: Path
    manifest: dict[str, object]


def has_private_part(rel: Path | str) -> bool:
    return PRIVATE in Path(rel).parts


def _ignore(dirpath: str, names: list[str]) -> set[str]:
    return {n for n in names if n == PRIVATE or n in _SKIP_NAMES}


def _copy_tree(src: Path, dest: Path) -> int:
    """Copy `src` without any `private/` directory. Symlinks are refused, not followed."""
    if not src.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
        return 0
    for p in src.rglob("*"):
        if p.is_symlink():
            raise RuntimeError(f"refusing a symlink in the content tree: {p.relative_to(src)}")
    shutil.copytree(src, dest, ignore=_ignore, dirs_exist_ok=True)
    return sum(1 for p in dest.rglob("*") if p.is_file())


def assert_no_private(root: Path) -> None:
    """Raise PrivatePathError if any file or directory under `root` sits in a `private/` dir."""
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if has_private_part(rel):
            raise PrivatePathError(f"private path in release: {rel}")


def _git_sha() -> str:
    if sha := os.environ.get("GITHUB_SHA"):  # CI builds inside the image, which has no .git
        return sha
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=discover_root(),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip()


def default_name() -> str:
    sha = _git_sha()
    return f"content-{sha[:12]}" if sha else f"content-{get_release()}"


def _build_index(stage: Path, content_root: Path) -> Path:
    """Build the index in a child process that reads the corpus through `content/current`."""
    env = {
        **os.environ,
        "WIKI_DIR": str(content_root / paths.CURRENT / "wiki"),
        "COURSES_DIR": str(content_root / paths.CURRENT / "courses"),
        "LIBRARIAN_PUBLIC": "true",
    }
    out_dir = stage / "index"
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, "-m", "librarian.release.package", "_index", str(out_dir)],
        env=env,
        check=True,
    )
    built = [p for p in out_dir.iterdir() if p.suffix == ".duckdb"]
    if len(built) != 1:
        raise RuntimeError(f"expected one index file in {out_dir}, found {len(built)}")
    # `build_artifact` leaves its pointer and lock beside the file; the host makes its own.
    for extra in out_dir.iterdir():
        if extra != built[0]:
            extra.unlink()
    return built[0]


def _index_child(out_dir: Path) -> int:
    """`_index <dir>`: runs in the child, after WIKI_DIR/COURSES_DIR are set."""
    from librarian.retrieval import artifact

    artifact.build_artifact(out_dir / f"{artifact.corpus_id()}.duckdb", keep=1)
    return 0


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_archive(stage: Path, name: str, archive: Path) -> None:
    """`stage` as `<name>/...` in a zstd tar; regular files and directories only."""
    tmp = archive.with_name(archive.name + ".tmp")
    cctx = zstandard.ZstdCompressor(level=10, threads=-1)
    with (
        tmp.open("wb") as raw,
        cctx.stream_writer(raw) as zfh,
        tarfile.open(fileobj=zfh, mode="w|") as tar,
    ):
        for p in sorted(stage.rglob("*")):
            rel = p.relative_to(stage)
            if has_private_part(rel):  # checked already; a second lock costs nothing
                raise PrivatePathError(f"private path in release: {rel}")
            if not (p.is_file() or p.is_dir()) or p.is_symlink():
                continue
            tar.add(p, arcname=f"{name}/{rel.as_posix()}", recursive=False)
    os.replace(tmp, archive)


def build(
    out_dir: Path,
    *,
    name: str | None = None,
    slides_dir: Path | None = None,
    build_index: bool = True,
) -> BuiltRelease:
    """Stage, index and pack a release into `out_dir`. Returns what was written."""
    settings = get_settings()
    name = name or default_name()
    paths.check_name(name)
    content_root = paths.content_root()
    releases = content_root / paths.RELEASES
    stage = releases / name
    if paths.read_current(content_root) == name:
        raise RuntimeError(f"{name} is the release being served; build under another name")
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    # Read from the checkout's data/, never from a release: the build is the source of one.
    wiki_src = settings.override_wiki_dir or settings.data_dir / "wiki"
    courses_src = settings.override_courses_dir or settings.data_dir / "courses"
    counts = {
        "wiki": _copy_tree(wiki_src, stage / "wiki"),
        "courses": _copy_tree(courses_src, stage / "courses"),
        "slides": _copy_tree(slides_dir, stage / "slides") if slides_dir else 0,
    }
    assert_no_private(stage)

    previous = paths.read_current(content_root)
    index_file: str | None = None
    try:
        if build_index:
            paths.repoint(content_root, stage)
            index_file = _build_index(stage, content_root).name
    finally:
        if previous is not None:
            paths.repoint(content_root, releases / previous)
        else:
            (content_root / paths.CURRENT).unlink(missing_ok=True)

    lesson_vecs = settings.lesson_vec_cache
    if lesson_vecs.is_file():  # vectors keyed by content hash: saves the host re-embedding
        (stage / "cache").mkdir()
        shutil.copy2(lesson_vecs, stage / "cache" / lesson_vecs.name)

    manifest: dict[str, object] = {
        "name": name,
        "git_sha": _git_sha(),
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "serve_root": str(settings.var_dir.resolve()),
        "index": f"index/{index_file}" if index_file else None,
        "files": counts,
    }
    (stage / paths.MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n")
    assert_no_private(stage)

    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / f"{name}{paths.ARCHIVE_SUFFIX}"
    _write_archive(stage, name, archive)
    checksum = archive.with_name(archive.name + ".sha256")
    checksum.write_text(f"{sha256_file(archive)}  {archive.name}\n")
    (out_dir / paths.LATEST).write_text(name + "\n")
    log.info("release.built", name=name, archive=str(archive), **counts)
    return BuiltRelease(name, archive, checksum, manifest)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "_index":
        raise SystemExit(_index_child(Path(sys.argv[2])))
    raise SystemExit("usage: python -m librarian.release.package _index <dir>")
