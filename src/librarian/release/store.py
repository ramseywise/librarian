"""Read releases from object storage: `<base>/latest`, `<base>/<name>.tar.zst` and its `.sha256`.

`<base>` is LIBRARIAN_RELEASE_URL: an https prefix of a public-read bucket (a release holds only
public content, the same as the site serves) or `file:///dir` for tests and a local drill.
CI uploads with the bucket's own CLI; the server only ever reads.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit

import httpx

from librarian.log_config import get_logger
from librarian.release import paths

log = get_logger(__name__)

TIMEOUT = httpx.Timeout(30.0, read=120.0)
# Tests swap this for an httpx.MockTransport.
transport: httpx.BaseTransport | None = None


class StoreError(RuntimeError):
    """The store could not be read, or answered with something that is not a release."""


def _join(base: str, name: str) -> str:
    return base.rstrip("/") + "/" + name


def _local(url: str) -> Path | None:
    parts = urlsplit(url)
    return Path(unquote(parts.path)) if parts.scheme == "file" else None


def _client() -> httpx.Client:
    return httpx.Client(timeout=TIMEOUT, transport=transport, follow_redirects=True)


def read_text(base: str, name: str) -> str:
    url = _join(base, name)
    local = _local(url)
    try:
        if local is not None:
            return local.read_text()
        with _client() as client:
            resp = client.get(url, headers={"Cache-Control": "no-cache"})
            resp.raise_for_status()
            return resp.text
    except (OSError, httpx.HTTPError) as e:
        raise StoreError(f"cannot read {url}: {e}") from e


def latest(base: str) -> str:
    """The release name `<base>/latest` holds."""
    return paths.check_name(read_text(base, paths.LATEST).strip())


def expected_sha256(base: str, name: str) -> str:
    text = read_text(base, f"{name}{paths.ARCHIVE_SUFFIX}.sha256").split()
    if not text or len(text[0]) != 64:
        raise StoreError(f"no checksum in {name}{paths.ARCHIVE_SUFFIX}.sha256")
    return text[0].lower()


def download(base: str, name: str, dest: Path) -> Path:
    """Stream `<name>.tar.zst` to `dest` (written to a temporary name, then renamed)."""
    url = _join(base, f"{name}{paths.ARCHIVE_SUFFIX}")
    tmp = dest.with_name(f"{dest.name}.{os.getpid()}.part")
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        local = _local(url)
        if local is not None:
            shutil.copyfile(local, tmp)
        else:
            with _client() as client, client.stream("GET", url) as resp:
                resp.raise_for_status()
                with tmp.open("wb") as fh:
                    for chunk in resp.iter_bytes(1 << 20):
                        fh.write(chunk)
    except (OSError, httpx.HTTPError) as e:
        tmp.unlink(missing_ok=True)
        raise StoreError(f"cannot download {url}: {e}") from e
    os.replace(tmp, dest)
    return dest
