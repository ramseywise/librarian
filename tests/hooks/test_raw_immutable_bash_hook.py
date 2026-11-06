"""The Bash PreToolUse hook keeps data/raw/ append-only against shell commands.

Pure string input plus a tmp repo root (RAW_GUARD_ROOT): nothing under the real data/raw/
is touched. Existing raw files are created in the tmp tree only.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "raw_immutable_bash.py"
BLOCK, ALLOW = 2, 0


@pytest.fixture()
def root(tmp_path: Path) -> Path:
    web = tmp_path / "data" / "raw" / "web"
    web.mkdir(parents=True)
    (web / "a.md").write_text("original\n")
    (tmp_path / "data" / "wiki").mkdir(parents=True)
    (tmp_path / "scratch.md").write_text("x\n")
    return tmp_path


def run(root: Path, command: str, tool: str = "Bash") -> tuple[int, str]:
    payload = {"tool_name": tool, "cwd": str(root), "tool_input": {"command": command}}
    proc = subprocess.run(
        ["python3", str(HOOK)],
        input=json.dumps(payload),
        env={"PATH": "/usr/bin:/bin:/usr/local/bin", "RAW_GUARD_ROOT": str(root)},
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stderr


BLOCKED = [
    "rm data/raw/web/a.md",
    "rm -rf data/raw",
    "rm -rf data",
    "mv data/raw/web/a.md /tmp/elsewhere.md",
    "mv scratch.md data/raw/web/a.md",
    "sed -i 's/orig/new/' data/raw/web/a.md",
    "sed -i.bak -e 's/a/b/' data/raw/web/*.md",
    "perl -pi -e 's/a/b/' data/raw/web/a.md",
    "truncate -s 0 data/raw/web/a.md",
    "echo hi > data/raw/web/a.md",
    "echo hi >> data/raw/web/a.md",
    "cat scratch.md | tee data/raw/web/a.md",
    "cp scratch.md data/raw/web/a.md",
    "rsync -a --delete scratch/ data/raw/web/",
    "chmod 000 data/raw/web/a.md",
    "git rm data/raw/web/a.md",
    "git checkout -- data/raw/web/a.md",
    "git restore data/raw",
    "find data/raw -name '*.md' -delete",
    "find data/raw -type f -exec rm {} +",
    "ls data/raw/web | xargs rm",
    "cd data/raw/web && rm a.md",
    "bash -c 'rm data/raw/web/a.md'",
    "python3 -c \"from pathlib import Path; Path('data/raw/web/a.md').write_text('x')\"",
    "uv run pytest && rm data/raw/web/a.md",
    "rm {root}/data/raw/web/a.md",
    "rm data/wiki/../raw/web/a.md",
]

ALLOWED = [
    "cat data/raw/web/a.md",
    "grep -rn foo data/raw",
    "ls -la data/raw/web",
    "head -5 data/raw/web/a.md",
    "wc -l data/raw/web/a.md",
    "find data/raw -name '*.md'",
    "uv run librarian scrape repos",
    "echo hi > data/raw/web/brand-new.md",
    "cp scratch.md data/raw/web/brand-new.md",
    "cp data/raw/web/a.md scratch-copy.md",
    "mv scratch.md data/raw/web/moved-in.md",
    "rm scratch.md",
    "rm data/wiki/old.md",
    "sed -i 's/a/b/' data/wiki/page.md",
    "sed -n '1,5p' data/raw/web/a.md",
    "git status --short data/raw",
    "git diff data/raw",
    "diff data/raw/web/a.md scratch.md 2>/dev/null",
    "touch data/raw/web/a.md",
    "uv run pytest tests/hooks -q",
]


@pytest.mark.parametrize("command", BLOCKED)
def test_blocks_mutation(root: Path, command: str) -> None:
    code, err = run(root, command.replace("{root}", str(root)))
    assert code == BLOCK, f"should block: {command}"
    assert "BLOCKED" in err and "append-only" in err


@pytest.mark.parametrize("command", ALLOWED)
def test_allows_read_only_and_creation(root: Path, command: str) -> None:
    code, err = run(root, command)
    assert code == ALLOW, f"should allow: {command}\n{err}"


def test_ignores_other_tools_and_bad_input(root: Path) -> None:
    assert run(root, "rm data/raw/web/a.md", tool="Read")[0] == ALLOW
    proc = subprocess.run(["python3", str(HOOK)], input="not json", capture_output=True, text=True)
    assert proc.returncode == ALLOW


def test_blocks_via_symlink(root: Path) -> None:
    (root / "link").symlink_to(root / "data" / "raw")
    assert run(root, "rm link/web/a.md")[0] == BLOCK


def test_never_modifies_files(root: Path) -> None:
    run(root, "rm data/raw/web/a.md")
    assert (root / "data/raw/web/a.md").read_text() == "original\n"


def test_wired_in_settings() -> None:
    settings = json.loads((REPO / ".claude" / "settings.json").read_text())
    bash = [e for e in settings["hooks"]["PreToolUse"] if e["matcher"] == "Bash"]
    assert bash and "raw_immutable_bash.py" in bash[0]["hooks"][0]["command"]
    allow = settings["permissions"]["allow"]
    for dropped in ("Bash(rm:*)", "Bash(mv:*)", "Bash(sed:*)"):
        assert dropped not in allow
