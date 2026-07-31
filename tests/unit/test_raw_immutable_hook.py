"""Evidence for Buyi "raw/ is immutable once written".

Cures the BY-4 debt record: immutability had docs-only enforcement (CLAUDE.md)
with no deterministic guard. The guard must block mutation of EXISTING raw/
files while permitting creation — the nine etl/ ingest scripts create new files
under raw/ as intended behaviour, and a blanket write-block breaks all of them.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "raw-immutable.sh"

BLOCK = 2
ALLOW = 0


def run_hook(file_path: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["bash", str(HOOK)],
        cwd=REPO,
        env={"PATH": "/usr/bin:/bin:/usr/local/bin", "CLAUDE_TOOL_INPUT_FILE_PATH": file_path},
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stderr


@pytest.fixture()
def existing_raw_file() -> Path:
    """A real file under raw/, cleaned up afterwards."""
    target = REPO / "raw" / "web" / "_immutability-fixture.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("original content\n")
    yield target
    target.unlink(missing_ok=True)


def test_blocks_edit_of_existing_raw_file(existing_raw_file: Path) -> None:
    code, err = run_hook(str(existing_raw_file.relative_to(REPO)))
    assert code == BLOCK
    assert "BLOCKED" in err
    assert "immutable once written" in err


def test_blocks_via_absolute_path(existing_raw_file: Path) -> None:
    code, _ = run_hook(str(existing_raw_file))
    assert code == BLOCK


def test_blocks_via_traversal_path(existing_raw_file: Path) -> None:
    """A ../ path landing back inside raw/ is still a raw/ mutation."""
    code, _ = run_hook(f"data/wiki/../../raw/web/{existing_raw_file.name}")
    assert code == BLOCK


def test_permits_creating_new_raw_file() -> None:
    """The ingest path — etl/ scripts create new files under raw/."""
    code, err = run_hook("raw/web/_does-not-exist-a91f.md")
    assert code == ALLOW, f"creation must be permitted or ingest breaks: {err}"


def test_permits_creating_raw_file_in_new_subdir() -> None:
    """ingest_pdf.py and friends may create a source dir that doesn't exist yet."""
    code, err = run_hook("raw/brand-new-source-dir/first-file.md")
    assert code == ALLOW, err


def test_ignores_paths_outside_raw() -> None:
    for path in ("data/wiki/rag/chunking.md", "app/mcp_server/server.py", "CLAUDE.md"):
        code, err = run_hook(path)
        assert code == ALLOW, f"{path} must not be blocked: {err}"


def test_ignores_empty_path() -> None:
    code, _ = run_hook("")
    assert code == ALLOW


def test_every_etl_ingest_script_target_dir_stays_writable() -> None:
    """The nine etl/ writers all create into raw/ subdirs — none may be blocked."""
    for subdir in (
        "notion",
        "linear",
        "meetings",
        "playground-docs",
        "pdfs",
        "web",
        "repos",
        "books",
        "articles",
    ):
        code, err = run_hook(f"raw/{subdir}/2026-07-20-new-ingest.md")
        assert code == ALLOW, f"ingest into raw/{subdir}/ must be permitted: {err}"
