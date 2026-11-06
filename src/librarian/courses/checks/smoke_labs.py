#!/usr/bin/env python3
"""Run a practice folder's labs headless, each with a time limit, and report which ones fail.

Each lab runs with `uv run --script` in a temporary copy of the folder, so charts and other output files never touch
the working tree. MPLBACKEND=Agg stops matplotlib opening windows.

    librarian courses check smoke-labs data-analytics/06-applied-analyses/practice --pattern 'ch[0-9]*.py' --timeout 600

The labs themselves are not imported into data/courses/ (only their readmes are), so a folder that is not on disk
under data/courses/ is looked up in the course sources checkout (COURSE_SOURCES_DIR, the sibling
learn-ai-engineering by default). Folders under data/courses/private/ are refused.
"""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from librarian.config import get_settings
from librarian.courses.checks.common import default_root, is_private, resolve_arg


@dataclass
class Result:
    lab: str
    status: str  # ok, FAILED or TIMEOUT
    seconds: float
    tail: str = ""


def run_lab(lab: str, cmd: list[str], cwd: Path, timeout: float) -> Result:
    """Run one command in its own process group, so a timeout also kills anything it started."""
    env = {**os.environ, "MPLBACKEND": "Agg", "PYTHONUNBUFFERED": "1"}
    start = time.monotonic()
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, _ = proc.communicate()
        return Result(
            lab, "TIMEOUT", time.monotonic() - start, "\n".join((out or "").splitlines()[-8:])
        )
    status = "ok" if proc.returncode == 0 else "FAILED"
    tail = "" if status == "ok" else "\n".join(out.splitlines()[-8:])
    return Result(lab, status, time.monotonic() - start, tail)


def find_folder(arg: str, root: Path, sources: Path) -> Path | None:
    """`arg` as given, else under the courses dir, else under the course sources checkout."""
    for candidate in (resolve_arg(arg, root), sources / arg):
        if candidate.is_dir() and not is_private(candidate, root):
            return candidate
    return None


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="librarian courses check smoke-labs", description=(__doc__ or "").splitlines()[0]
    )
    ap.add_argument(
        "folder", help="a practice folder, e.g. data-analytics/06-applied-analyses/practice"
    )
    ap.add_argument("--pattern", default="*.py")
    ap.add_argument("--timeout", type=float, default=600, help="seconds allowed for each lab")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument(
        "--offline", action="store_true", help="use only packages already in uv's cache"
    )
    args = ap.parse_args(argv)

    folder = find_folder(args.folder, default_root(), get_settings().course_sources_dir)
    if folder is None:
        print(f"no such practice folder: {args.folder}")
        return 2
    labs = sorted(p.name for p in folder.glob(args.pattern))
    if not labs:
        print(f"no labs match {args.pattern} in {args.folder}")
        return 2
    uv = ["uv", "run", *(["--offline"] if args.offline else []), "--script"]
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "labs"
        shutil.copytree(folder, work, ignore=shutil.ignore_patterns("__pycache__"))
        with ThreadPoolExecutor(args.jobs) as pool:
            results = list(pool.map(lambda lab: run_lab(lab, [*uv, lab], work, args.timeout), labs))

    for r in results:
        print(f"{r.status:8} {r.seconds:7.1f}s  {r.lab}")
        if r.tail:
            print("\n".join("    " + line for line in r.tail.splitlines()))
    failed = [r for r in results if r.status != "ok"]
    print(
        f"{len(results) - len(failed)} of {len(results)} labs passed, limit {args.timeout:.0f}s each"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
