"""scripts/deploy-content.sh: private/ never reaches the destination (rsync to a local dir)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "deploy-content.sh"

pytestmark = pytest.mark.skipif(shutil.which("rsync") is None, reason="rsync not installed")


def _write(path: Path, text: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture()
def src(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    _write(root / "data" / "wiki" / "rag" / "page.md")
    _write(root / "data" / "wiki" / "private" / "secret.md", "SECRET")
    _write(root / "data" / "courses" / "c" / "m" / "lesson.md")
    _write(root / "data" / "courses" / "private" / "c" / "solution.md", "SECRET")
    return root


def _run(src: Path, dest: Path, **env: str) -> subprocess.CompletedProcess[str]:
    full = {
        **os.environ,
        "DEPLOY_HOST": "unused",
        "DEPLOY_PATH": str(dest),
        "DEPLOY_SRC": str(src),
        "DEPLOY_LOCAL": "1",
        **env,
    }
    return subprocess.run(
        ["bash", str(SCRIPT)], env=full, capture_output=True, text=True, check=False
    )


def _all_files(dest: Path) -> list[str]:
    return sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file())


def test_private_is_excluded_and_deploy_succeeds(src: Path, tmp_path: Path) -> None:
    dest = tmp_path / "remote"
    res = _run(src, dest)
    assert res.returncode == 0, res.stderr
    assert _all_files(dest) == ["data/courses/c/m/lesson.md", "data/wiki/rag/page.md"]


def test_refuses_without_deploy_host(src: Path, tmp_path: Path) -> None:
    env = {k: v for k, v in os.environ.items() if k != "DEPLOY_HOST"}
    res = subprocess.run(
        ["bash", str(SCRIPT)],
        env={**env, "DEPLOY_PATH": str(tmp_path / "r")},
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode != 0
    assert "DEPLOY_HOST" in res.stderr
    assert not (tmp_path / "r").exists()


def test_dry_run_aborts_before_any_transfer_when_exclude_is_broken(
    src: Path, tmp_path: Path
) -> None:
    dest = tmp_path / "remote"
    res = _run(src, dest, DEPLOY_EXCLUDE="nothing-matches-this/")
    assert res.returncode == 1
    assert "private/" in res.stderr
    assert _all_files(dest) == []  # nothing was copied, not even the public files


def test_post_check_fails_on_a_private_file_already_at_the_destination(
    src: Path, tmp_path: Path
) -> None:
    dest = tmp_path / "remote"
    _write(dest / "data" / "wiki" / "private" / "old.md", "SECRET")
    res = _run(src, dest)
    assert res.returncode == 1
    assert "private files exist at the destination" in res.stderr
    assert "old.md" in res.stderr


def test_empty_private_mountpoints_at_the_destination_are_fine(src: Path, tmp_path: Path) -> None:
    dest = tmp_path / "remote"
    (dest / "data" / "wiki" / "private").mkdir(parents=True)
    (dest / "data" / "courses" / "private").mkdir(parents=True)
    assert _run(src, dest).returncode == 0


def test_built_slides_are_shipped_without_private(src: Path, tmp_path: Path) -> None:
    slides = tmp_path / "built"
    _write(slides / "c" / "m" / "slide-01.png", "png")
    _write(slides / "c" / "m" / "built.json", "{}")
    _write(slides / "private" / "c" / "slide-01.png", "SECRET")
    dest = tmp_path / "remote"
    res = _run(src, dest, DEPLOY_SLIDES_SRC=str(slides))
    assert res.returncode == 0, res.stderr
    files = _all_files(dest)
    assert "content/slides/c/m/slide-01.png" in files
    assert "content/slides/c/m/built.json" in files
    assert not any("private" in f for f in files)


def test_missing_built_slides_do_not_fail_the_deploy(src: Path, tmp_path: Path) -> None:
    res = _run(src, tmp_path / "remote", DEPLOY_SLIDES_SRC=str(tmp_path / "nope"))
    assert res.returncode == 0, res.stderr
    assert "skipping slides" in res.stderr
