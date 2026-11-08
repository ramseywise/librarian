"""Fail when the Python or Node version differs between the image and CI.

Compared: the Dockerfile base images (`python:X.Y`, `node:N`), `.python-version`, the floor in
pyproject's `requires-python`, and every `python-version:` / `node-version:` in
`.github/workflows/*.yml`. Run from CI (`versions` job) and by `tests/core/test_check_versions.py`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _first(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text, re.MULTILINE)
    return m.group(1) if m else None


def python_versions(root: Path) -> dict[str, set[str]]:
    """Every place that names a Python minor version, as `X.Y`."""
    found: dict[str, set[str]] = {}
    docker = _first(r"^FROM\s+python:(\d+\.\d+)", (root / "Dockerfile").read_text())
    if docker:
        found["Dockerfile"] = {docker}
    pv = root / ".python-version"
    if pv.exists():
        found[".python-version"] = {".".join(pv.read_text().strip().split(".")[:2])}
    floor = _first(
        r'^requires-python\s*=\s*"[>=~^ ]*(\d+\.\d+)', (root / "pyproject.toml").read_text()
    )
    if floor:
        found["pyproject requires-python (floor)"] = {floor}
    for wf in sorted((root / ".github" / "workflows").glob("*.yml")):
        vals = re.findall(r"^\s*python-version:\s*[\"']?(\d+\.\d+)", wf.read_text(), re.MULTILINE)
        if vals:
            found[f"workflows/{wf.name}"] = set(vals)
    return found


def node_versions(root: Path) -> dict[str, set[str]]:
    """Every place that names a Node major version."""
    found: dict[str, set[str]] = {}
    docker = _first(r"^FROM\s+node:(\d+)", (root / "Dockerfile").read_text())
    if docker:
        found["Dockerfile"] = {docker}
    for wf in sorted((root / ".github" / "workflows").glob("*.yml")):
        vals = re.findall(r"^\s*node-version:\s*[\"']?(\d+)", wf.read_text(), re.MULTILINE)
        if vals:
            found[f"workflows/{wf.name}"] = set(vals)
    return found


def check(root: Path = ROOT) -> list[str]:
    """Return one message per disagreement; empty when everything agrees."""
    problems: list[str] = []
    for name, found in (("Python", python_versions(root)), ("Node", node_versions(root))):
        if "Dockerfile" not in found:
            problems.append(f"{name}: no version found in the Dockerfile")
            continue
        if not any(k.startswith("workflows/") for k in found):
            problems.append(f"{name}: CI does not pin a version (set it explicitly in a workflow)")
        values = set().union(*found.values())
        if len(values) > 1:
            detail = ", ".join(f"{k}={'/'.join(sorted(v))}" for k, v in found.items())
            problems.append(f"{name} versions disagree: {detail}")
    return problems


def main() -> int:
    problems = check()
    for p in problems:
        print(f"ERROR {p}", file=sys.stderr)
    if not problems:
        print("ok: Python and Node versions agree across the Dockerfile, .python-version and CI")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
