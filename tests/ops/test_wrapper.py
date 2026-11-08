"""The ./librarian wrapper: syntax, argument handling and the commands it would run (dry run)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "librarian"


def _run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    import os

    return subprocess.run(
        ["bash", str(WRAPPER), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={**os.environ, "LIBRARIAN_IMAGE": "", **(env or {})},
        check=False,
    )


def test_wrapper_is_valid_bash_and_executable() -> None:
    assert subprocess.run(["bash", "-n", str(WRAPPER)], check=False).returncode == 0
    assert WRAPPER.stat().st_mode & 0o111


def test_no_command_and_unknown_command_exit_2() -> None:
    assert _run().returncode == 2
    r = _run("frobnicate")
    assert r.returncode == 2 and "unknown command" in r.stderr


def test_help_lists_every_verb() -> None:
    out = _run("help").stdout
    for verb in ("start", "stop", "status", "logs", "backup", "restore", "upgrade", "content push"):
        assert verb in out


def test_host_start_never_builds() -> None:
    out = _run("--dry-run", "start").stdout
    assert "up -d --no-build" in out and "--build " not in out
    assert "docker-compose.local.yml" not in out


def test_local_start_uses_the_local_file_and_builds() -> None:
    out = _run("--local", "--dry-run", "start").stdout
    assert "-f docker-compose.yml -f docker-compose.local.yml up -d --build librarian" in out


def test_backup_runs_in_the_backup_service() -> None:
    out = _run("--dry-run", "backup").stdout
    assert "run --rm backup librarian ops backup" in out


def test_restore_requires_object_and_identity() -> None:
    assert _run("--dry-run", "restore").returncode == 2
    r = _run("--dry-run", "restore", "latest")
    assert r.returncode == 2 and "--identity" in r.stderr
    assert _run("--dry-run", "restore", "latest", "--bogus").returncode == 2


def test_restore_fences_stops_api_first_and_passes_replace() -> None:
    out = _run("--dry-run", "restore", "latest", "--identity", "/tmp/k.txt", "--replace").stdout
    lines = [ln for ln in out.splitlines() if ln.startswith("+ docker")]
    assert lines[0].endswith("stop librarian")
    assert "ops restore latest --identity /run/age-identity --replace" in lines[1]
    assert lines[2].endswith("up -d --no-build librarian")


def test_upgrade_gates_on_a_backup_before_pulling_and_resolves_a_bare_tag() -> None:
    out = _run(
        "--dry-run", "upgrade", "sha-abc", env={"LIBRARIAN_IMAGE": "ghcr.io/me/librarian:sha-old"}
    ).stdout
    lines = [ln for ln in out.splitlines() if ln.startswith("+ docker")]
    assert "ops upgrade ghcr.io/me/librarian:sha-abc" in lines[0]
    assert lines[1].endswith("pull librarian")
    assert lines[2].endswith("up -d --no-build")


def test_upgrade_is_refused_locally_and_needs_a_tag() -> None:
    assert _run("--local", "--dry-run", "upgrade", "sha-1").returncode == 2
    assert _run("--dry-run", "upgrade").returncode == 2


def test_content_push_maps_to_the_guarded_script() -> None:
    out = _run("--dry-run", "content", "push").stdout
    assert "+ scripts/deploy-content.sh" in out
    assert _run("--dry-run", "content").returncode == 2
    script = (ROOT / "scripts" / "deploy-content.sh").read_text()
    assert "private/" in script  # the guard the wrapper relies on is still there


@pytest.mark.skipif(
    subprocess.run(["which", "shellcheck"], capture_output=True).returncode != 0,
    reason="no shellcheck",
)
def test_wrapper_passes_shellcheck() -> None:
    assert subprocess.run(["shellcheck", str(WRAPPER)], check=False).returncode == 0
