"""scripts/check_versions.py: the image and CI agree on Python and Node."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_versions", ROOT / "scripts" / "check_versions.py"
)
assert _spec and _spec.loader
cv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cv)


def _repo(
    tmp_path: Path,
    *,
    docker_py: str = "3.12",
    docker_node: str = "22",
    ci_py: str = "3.12",
    ci_node: str = "22",
    pv: str = "3.12",
) -> Path:
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / "Dockerfile").write_text(
        f"FROM node:{docker_node}-slim AS web\nFROM python:{docker_py}-slim AS api\n"
    )
    (tmp_path / ".python-version").write_text(pv + "\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nrequires-python = ">=3.12"\n')
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text(
        f'with:\n  python-version: "{ci_py}"\n  node-version: {ci_node}\n'
    )
    return tmp_path


def test_agreeing_versions_pass(tmp_path: Path) -> None:
    assert cv.check(_repo(tmp_path)) == []


def test_python_mismatch_is_reported(tmp_path: Path) -> None:
    problems = cv.check(_repo(tmp_path, docker_py="3.13"))
    assert len(problems) == 1 and "Python versions disagree" in problems[0]


def test_node_mismatch_is_reported(tmp_path: Path) -> None:
    problems = cv.check(_repo(tmp_path, ci_node="20"))
    assert len(problems) == 1 and "Node versions disagree" in problems[0]


def test_ci_without_a_pinned_version_is_reported(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / ".github" / "workflows" / "ci.yml").write_text("name: CI\n")
    assert any("CI does not pin" in p for p in cv.check(repo))


def test_this_repo_agrees() -> None:
    assert cv.check(ROOT) == []
