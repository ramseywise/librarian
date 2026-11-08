"""Where backups live: a bucket through the `aws` CLI, or a directory (`file://`, tests and drills)."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse

from librarian.config import Settings
from librarian.ops import proc
from librarian.ops.proc import OpsError


class Storage(Protocol):
    def put(self, src: Path, name: str) -> None: ...
    def get(self, name: str, dest: Path) -> None: ...
    def names(self) -> list[str]: ...


class LocalStorage:
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def put(self, src: Path, name: str) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, self.directory / name)

    def get(self, name: str, dest: Path) -> None:
        source = self.directory / name
        if not source.is_file():
            raise OpsError(f"no such backup object: {name}")
        shutil.copyfile(source, dest)

    def names(self) -> list[str]:
        if not self.directory.is_dir():
            return []
        return sorted(p.name for p in self.directory.iterdir() if p.is_file())


class S3Storage:
    """`aws s3 cp` / `aws s3 ls`. Credentials come from AWS_* in the environment, not from argv."""

    def __init__(self, url: str, endpoint_url: str = "") -> None:
        self.url = url.rstrip("/")
        self.endpoint_url = endpoint_url

    def _cmd(self, *args: str) -> list[str]:
        cmd = ["aws", *args]
        if self.endpoint_url:
            cmd += ["--endpoint-url", self.endpoint_url]
        return cmd

    def put(self, src: Path, name: str) -> None:
        proc.run(self._cmd("s3", "cp", str(src), f"{self.url}/{name}", "--only-show-errors"))

    def get(self, name: str, dest: Path) -> None:
        proc.run(self._cmd("s3", "cp", f"{self.url}/{name}", str(dest), "--only-show-errors"))

    def names(self) -> list[str]:
        out = proc.run(self._cmd("s3", "ls", f"{self.url}/")).stdout
        # "2026-11-08 03:30:01     123456 librarian-....dump.age"; "PRE dir/" lines have no size.
        return sorted(parts[-1] for line in out.splitlines() if len(parts := line.split()) == 4)


def open_storage(settings: Settings) -> Storage:
    url = settings.backup_url
    if not url:
        raise OpsError("LIBRARIAN_BACKUP_URL is not set (s3://bucket/prefix or file:///dir)")
    parsed = urlparse(url)
    if parsed.scheme == "file":
        return LocalStorage(Path(parsed.path))
    if parsed.scheme == "s3" and parsed.netloc:
        return S3Storage(url, settings.backup_endpoint_url)
    raise OpsError("LIBRARIAN_BACKUP_URL must be s3://bucket/prefix or file:///dir")
