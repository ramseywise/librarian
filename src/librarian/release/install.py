"""Pull a release, verify it, unpack it and swap it in; pin one for a rollback.

`pull()` is what the API runs on start, on a timer and on a signed POST /admin/reload, and what
`librarian release pull` runs. Every API worker may call it at once: a file lock lets one of
them do the work, and the others then find `current` already pointing at the release.

The order is chosen so a reader never sees a half-installed release:
  1. download to a temporary name and compare the sha256 with the published one;
  2. unpack into `releases/<name>.<pid>.tmp`, refusing a member outside it, a link or a device
     (tarfile's `data` filter) and any path under a `private/` directory, then rename;
  3. check the manifest: its name, and that its index was built for this state dir;
  4. copy the index into `index/` and repoint `index/current` (each IndexHandle follows it);
  5. repoint `content/current`. Then prune: the current release and the two before it stay.
"""

from __future__ import annotations

import contextlib
import fcntl
import json
import os
import shutil
import tarfile
import time
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path

import zstandard

from librarian.config import get_settings
from librarian.log_config import get_logger
from librarian.release import paths, store
from librarian.release.package import has_private_part, sha256_file
from librarian.retrieval import artifact, corpus

log = get_logger(__name__)

# Releases kept on disk besides the current one, so a rollback needs no download.
KEEP_PREVIOUS = 2


class ReleaseError(RuntimeError):
    """A release could not be installed; what is being served is unchanged."""


@dataclass(frozen=True)
class InstallResult:
    release: str | None
    changed: bool
    pinned: bool = False

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@contextlib.contextmanager
def _lock(root: Path) -> Iterator[None]:
    root.mkdir(parents=True, exist_ok=True)
    with (root / ".release.lock").open("w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def current_name(root: Path | None = None) -> str | None:
    return paths.read_current(root or paths.content_root())


def current_manifest(root: Path | None = None) -> dict[str, object] | None:
    """The served release's manifest, or None when no release is installed."""
    root = root or paths.content_root()
    name = paths.read_current(root)
    if name is None:
        return None
    try:
        return json.loads((root / paths.RELEASES / name / paths.MANIFEST).read_text())
    except (OSError, ValueError):
        return None


def pinned(root: Path | None = None) -> str | None:
    try:
        text = ((root or paths.content_root()) / paths.PIN).read_text().strip()
    except OSError:
        return None
    return text or None


def list_releases(root: Path | None = None) -> list[dict[str, object]]:
    """Releases on disk, newest first, each with `current` and `pinned` flags."""
    root = root or paths.content_root()
    live, pin_name = paths.read_current(root), pinned(root)
    out = []
    for d in _installed(root):
        out.append(
            {"name": d.name, "current": d.name == live, "pinned": d.name == pin_name}
            | _manifest_summary(d)
        )
    return out


def _manifest_summary(d: Path) -> dict[str, object]:
    try:
        m = json.loads((d / paths.MANIFEST).read_text())
    except (OSError, ValueError):
        return {}
    return {"created_at": m.get("created_at"), "git_sha": m.get("git_sha")}


def _installed(root: Path) -> list[Path]:
    """Complete releases (they have a manifest), newest unpack first."""
    rel = root / paths.RELEASES
    if not rel.is_dir():
        return []
    dirs = [d for d in rel.iterdir() if d.is_dir() and (d / paths.MANIFEST).is_file()]
    return sorted(dirs, key=lambda d: d.stat().st_mtime, reverse=True)


def _extract(archive: Path, name: str, releases: Path) -> Path:
    tmp = releases / f"{name}.{os.getpid()}.tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    try:
        dctx = zstandard.ZstdDecompressor()
        with (
            archive.open("rb") as raw,
            dctx.stream_reader(raw) as zfh,
            tarfile.open(fileobj=zfh, mode="r|") as tar,
        ):
            for member in tar:
                parts = Path(member.name).parts
                if not parts or parts[0] != name:
                    raise ReleaseError(f"member outside {name}/: {member.name}")
                if has_private_part(Path(*parts[1:]) if len(parts) > 1 else ""):
                    raise ReleaseError(f"private path in release: {member.name}")
                if not (member.isfile() or member.isdir()):
                    raise ReleaseError(f"not a file or directory: {member.name}")
                tar.extract(member, tmp, filter="data")
        final = releases / name
        if final.exists():
            shutil.rmtree(final)
        os.replace(tmp / name, final)
    except (tarfile.TarError, zstandard.ZstdError, OSError) as e:
        raise ReleaseError(f"cannot unpack {archive.name}: {e}") from e
    finally:
        if tmp.exists():
            shutil.rmtree(tmp)
    os.utime(final)  # mtime = when it was installed: prune keeps the newest
    return final


def _check_manifest(release_dir: Path, name: str) -> dict[str, object]:
    try:
        manifest = json.loads((release_dir / paths.MANIFEST).read_text())
    except (OSError, ValueError) as e:
        raise ReleaseError(f"{name}: no readable manifest") from e
    if manifest.get("name") != name:
        raise ReleaseError(f"{name}: manifest names {manifest.get('name')!r}")
    serve_root = str(get_settings().var_dir.resolve())
    if manifest.get("index") and manifest.get("serve_root") != serve_root:
        raise ReleaseError(
            f"{name}: index built for state dir {manifest.get('serve_root')}, this host uses"
            f" {serve_root}; build the release with LIBRARIAN_STATE_DIR={serve_root}"
        )
    return manifest


def _install_index(release_dir: Path, manifest: dict[str, object]) -> None:
    rel = manifest.get("index")
    if not rel:
        return
    src = release_dir / str(rel)
    if not src.is_file():
        raise ReleaseError(f"{release_dir.name}: manifest names a missing index {rel}")
    index_dir = corpus.INDEX_DIR
    index_dir.mkdir(parents=True, exist_ok=True)
    dest = index_dir / src.name
    if not dest.exists():
        tmp = dest.with_name(f"{dest.name}.{os.getpid()}.tmp")
        shutil.copyfile(src, tmp)
        os.replace(tmp, dest)
    os.utime(dest)
    artifact.repoint(index_dir, dest)


def _install_caches(release_dir: Path) -> None:
    target = get_settings().lesson_vec_cache
    src = release_dir / "cache" / target.name
    if src.is_file() and not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)


def _prune(root: Path, keep_names: set[str]) -> None:
    for d in _installed(root)[KEEP_PREVIOUS + 1 :]:
        if d.name not in keep_names:
            shutil.rmtree(d, ignore_errors=True)
            log.info("release.pruned", release=d.name)
    downloads = root / "downloads"
    if downloads.is_dir():
        for f in downloads.iterdir():
            f.unlink(missing_ok=True)
    if corpus.INDEX_DIR.is_dir():  # absent until the first release with an index
        artifact.prune(corpus.INDEX_DIR, keep=KEEP_PREVIOUS + 1)


def _fetch(base: str, name: str, root: Path) -> Path:
    archive = store.download(base, name, root / "downloads" / f"{name}{paths.ARCHIVE_SUFFIX}")
    want, got = store.expected_sha256(base, name), sha256_file(archive)
    if want != got:
        archive.unlink(missing_ok=True)
        raise ReleaseError(f"{name}: checksum mismatch (published {want[:12]}, got {got[:12]})")
    return _extract(archive, name, root / paths.RELEASES)


def _activate(name: str, base: str | None, root: Path) -> bool:
    """Make `name` current, fetching it when it is not on disk. True if anything changed."""
    if paths.read_current(root) == name:
        return False
    release_dir = root / paths.RELEASES / name
    if not (release_dir / paths.MANIFEST).is_file():
        if not base:
            raise ReleaseError(f"{name} is not on disk and LIBRARIAN_RELEASE_URL is not set")
        release_dir = _fetch(base, name, root)
    manifest = _check_manifest(release_dir, name)
    _install_index(release_dir, manifest)
    _install_caches(release_dir)
    previous = paths.read_current(root)
    paths.repoint(root, release_dir)
    os.utime(release_dir)
    _prune(root, {name, *(p for p in [previous, pinned(root)] if p)})
    log.info("release.installed", release=name, previous=previous)
    return True


def pull(base: str | None = None, *, root: Path | None = None) -> InstallResult:
    """Install the pinned release if there is one, else the one `<base>/latest` names."""
    root = root or paths.content_root()
    base = base if base is not None else get_settings().release_url
    t0 = time.perf_counter()
    with _lock(root):
        pin_name = pinned(root)
        if pin_name:
            name = pin_name
        elif base:
            try:
                name = store.latest(base)
            except (store.StoreError, ValueError) as e:
                raise ReleaseError(str(e)) from e
        else:
            raise ReleaseError("LIBRARIAN_RELEASE_URL is not set")
        try:
            changed = _activate(name, base, root)
        except store.StoreError as e:
            raise ReleaseError(str(e)) from e
    if changed:
        log.info("release.pull", release=name, seconds=round(time.perf_counter() - t0, 2))
    return InstallResult(name, changed, pinned=bool(pin_name))


def pin(ref: str, base: str | None = None, *, root: Path | None = None) -> InstallResult:
    """Serve `ref` (a release name, or a git sha prefix of one on disk) and stop following latest."""
    root = root or paths.content_root()
    base = base if base is not None else get_settings().release_url
    with _lock(root):
        name = _resolve_ref(ref, root)
        changed = _activate(name, base, root)
        (root / paths.PIN).write_text(name + "\n")
    log.info("release.pinned", release=name)
    return InstallResult(name, changed, pinned=True)


def unpin(*, root: Path | None = None) -> None:
    ((root or paths.content_root()) / paths.PIN).unlink(missing_ok=True)


def _resolve_ref(ref: str, root: Path) -> str:
    names = [d.name for d in _installed(root)]
    if ref in names:
        return ref
    matches = [
        n
        for n in names
        if n.removeprefix("content-").startswith(ref) or ref in (n, f"content-{ref}")
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ReleaseError(f"{ref!r} matches several releases: {', '.join(matches)}")
    return paths.check_name(ref if ref.startswith("content-") else f"content-{ref}")
