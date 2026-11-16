"""Running a lab's code: the `LabRunner` interface and the local backend behind it.

A run is one lab, a mode (`run` its entry script, or `check` its `verified_by`) and the files the
editor changed. The runner yields events as plain dicts, which the API streams as SSE:

    {"type": "start", "command": "uv run importance_noise.py"}
    {"type": "output", "stream": "stdout" | "stderr", "text": "..."}
    {"type": "image", "path": "figures/roc.png", "mime": "image/png", "data": "<base64>"}
    {"type": "done", "exit": 0, "seconds": 3.2, "timedOut": false, "truncated": false}
    {"type": "error", "message": "..."}

`LocalRunner` runs on this machine as this user. Each run gets its own copy of the lab's practice
folder, cloned (copy-on-write on APFS and reflink filesystems) from the course repo next to this one
(`settings.course_sources_dir`, where the datasets live) or from the mirror when that is missing.
The edits are written into the copy, never into either tree, and the copy is deleted afterwards.
The command is an argv (no shell) with a cleaned environment, in its own process group so a
timeout or a closed stream kills everything it started. It is no sandbox: the API only exposes it
when `dev_run_labs` is on and public mode is off. A container backend implements the same
interface.
"""

from __future__ import annotations

import asyncio
import base64
import codecs
import contextlib
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol

from librarian.config import get_settings
from librarian.courses.labs import COURSES_DIR, Lab
from librarian.log_config import get_logger

log = get_logger(__name__)

Mode = Literal["run", "check"]
Event = dict[str, object]

MAX_OUTPUT_BYTES = 400_000
MAX_IMAGES = 12
MAX_IMAGE_BYTES = 3_000_000
IMAGE_MIME = {
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}
CONCURRENT_RUNS = 2
# What a lab's process sees of this environment; provider keys only for labs that call one.
ENV_KEEP = ("PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE", "USER", "LOGNAME", "SHELL")
ENV_KEEP_PREFIXES = ("UV_",)
PROVIDER_KEYS = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY")
COPY_IGNORE = (".venv", "node_modules", "__pycache__", ".ipynb_checkpoints", ".pytest_cache")


@dataclass(frozen=True)
class RunRequest:
    lab: Lab
    mode: Mode = "run"
    files: dict[str, str] = field(default_factory=dict)  # practice-relative path → edited text


class LabRunner(Protocol):
    def run(self, request: RunRequest) -> AsyncIterator[Event]: ...


class LabRunError(ValueError):
    """The request cannot be run: no such command for this lab, or an edit outside its files."""


def source_practice_dir(lab: Lab, sources_root: Path | None = None) -> Path | None:
    """The lab's practice folder in the course repo, matching the module case-insensitively."""
    root = sources_root or get_settings().course_sources_dir
    course = root / lab.course
    if not course.is_dir():
        return None
    for module in course.iterdir():
        if module.name.lower() == lab.module.lower() and (module / "practice").is_dir():
            return module / "practice"
    return None


def _clone(src: Path, dest: Path) -> None:
    """Copy `src` to `dest`, copy-on-write where the filesystem can, plainly where it cannot."""
    flags = ["-cR"] if sys.platform == "darwin" else ["-R", "--reflink=auto"]
    try:
        subprocess.run(["cp", *flags, str(src), str(dest)], check=True, capture_output=True)
        return
    except (OSError, subprocess.CalledProcessError) as e:
        log.debug("lab_runner.clone_fallback", src=str(src), error=str(e))
        shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(src, dest, symlinks=True, ignore=shutil.ignore_patterns(*COPY_IGNORE))


def _images(root: Path) -> dict[Path, int]:
    out = {}
    for path in root.rglob("*"):
        if path.suffix.lower() in IMAGE_MIME and not set(path.relative_to(root).parts) & set(
            COPY_IGNORE
        ):
            with contextlib.suppress(OSError):
                out[path] = path.stat().st_mtime_ns
    return out


def _env(lab: Lab, tmp: Path) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k in ENV_KEEP or k.startswith(ENV_KEEP_PREFIXES)}
    if not lab.runs_offline:
        env.update({k: os.environ[k] for k in PROVIDER_KEYS if k in os.environ})
    env.update({"MPLBACKEND": "Agg", "PYTHONUNBUFFERED": "1", "TMPDIR": str(tmp), "NO_COLOR": "1"})
    return env


def _kill(proc: asyncio.subprocess.Process) -> None:
    if proc.returncode is None:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL)


def validate(request: RunRequest) -> None:
    """Raise LabRunError unless the lab has the requested command and every edit is one of its files."""
    lab = request.lab
    if (lab.run if request.mode == "run" else lab.check) is None:
        raise LabRunError(f"{lab.id} has no {request.mode} command")
    if stray := set(request.files) - set(lab.files):
        raise LabRunError(f"not files of this lab: {', '.join(sorted(stray))}")


@dataclass
class LocalRunner:
    """Runs labs on this machine; see the module docstring for what that does and does not keep out."""

    timeout_s: float = 300
    sources_root: Path | None = None
    courses_dir: Path = COURSES_DIR
    _slots: asyncio.Semaphore = field(default_factory=lambda: asyncio.Semaphore(CONCURRENT_RUNS))

    async def run(self, request: RunRequest) -> AsyncIterator[Event]:
        validate(request)
        lab = request.lab
        command = lab.run if request.mode == "run" else lab.check
        assert command is not None  # validate
        uv = shutil.which("uv")
        if uv is None:
            yield {"type": "error", "message": "uv is not on PATH, so no lab can run here."}
            return
        async with self._slots:
            work = Path(tempfile.mkdtemp(prefix="lab-"))
            try:
                async for event in self._run_in(
                    work, request, (uv, *command.argv[1:]), command.cwd
                ):
                    yield event
            finally:
                await asyncio.to_thread(shutil.rmtree, work, True)

    async def _run_in(
        self, work: Path, request: RunRequest, argv: tuple[str, ...], cwd_rel: str
    ) -> AsyncIterator[Event]:
        lab = request.lab
        src = source_practice_dir(lab, self.sources_root) or self.courses_dir / lab.practice_dir
        # The course and module folders are kept so a lab's `Path(__file__).parents[2] / ...`
        # (the shared chart helper writes there) lands inside this run, not beside it.
        tree, tmp = work / "tree", work / "tmp"
        practice = tree / lab.practice_dir
        practice.parent.mkdir(parents=True)
        tmp.mkdir()
        await asyncio.to_thread(_clone, src, practice)
        for rel, text in request.files.items():
            (practice / rel).parent.mkdir(parents=True, exist_ok=True)
            (practice / rel).write_text(text)
        cwd = (practice / cwd_rel).resolve()
        if not cwd.is_relative_to(practice.resolve()) or not cwd.is_dir():
            yield {"type": "error", "message": f"no folder {cwd_rel} in this lab"}
            return
        before = await asyncio.to_thread(_images, tree)

        display = " ".join(("uv", *argv[1:]))
        yield {
            "type": "start",
            "command": display if cwd_rel == "." else f"cd {cwd_rel} && {display}",
        }
        log.info("lab_runner.start", lab=lab.id, mode=request.mode, edited=len(request.files))
        started = time.monotonic()
        proc = await asyncio.create_subprocess_exec(
            *argv,
            cwd=cwd,
            env=_env(lab, tmp),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )
        queue: asyncio.Queue[tuple[str, str] | None] = asyncio.Queue()

        async def pump(stream: asyncio.StreamReader, name: str) -> None:
            decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
            while chunk := await stream.read(4096):
                await queue.put((name, decoder.decode(chunk)))
            if tail := decoder.decode(b"", final=True):
                await queue.put((name, tail))
            await queue.put(None)

        assert proc.stdout is not None and proc.stderr is not None
        pumps = [
            asyncio.create_task(pump(proc.stdout, "stdout")),
            asyncio.create_task(pump(proc.stderr, "stderr")),
        ]
        sent, truncated, timed_out, open_streams = 0, False, False, 2
        deadline = started + self.timeout_s
        try:
            while open_streams:
                try:
                    item = await asyncio.wait_for(
                        queue.get(), max(0.0, deadline - time.monotonic())
                    )
                except TimeoutError:
                    timed_out = True
                    _kill(proc)
                    break
                if item is None:
                    open_streams -= 1
                    continue
                stream, text = item
                if sent >= MAX_OUTPUT_BYTES:
                    truncated = True
                    continue
                text = text[: MAX_OUTPUT_BYTES - sent]
                sent += len(text)
                yield {"type": "output", "stream": stream, "text": text}
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(proc.wait(), 5)
        finally:
            _kill(proc)  # a closed stream or a timeout: the whole process group goes
            for task in pumps:
                task.cancel()
        seconds = round(time.monotonic() - started, 2)

        after = await asyncio.to_thread(_images, tree)
        changed = [p for p, mtime in sorted(after.items()) if before.get(p) != mtime]
        for path in changed[:MAX_IMAGES]:
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if len(data) <= MAX_IMAGE_BYTES:
                yield {
                    "type": "image",
                    "path": path.relative_to(tree / lab.course).as_posix(),
                    "mime": IMAGE_MIME[path.suffix.lower()],
                    "data": base64.b64encode(data).decode(),
                }
        exit_code = proc.returncode if proc.returncode is not None else -1
        log.info(
            "lab_runner.done",
            lab=lab.id,
            mode=request.mode,
            exit=exit_code,
            seconds=seconds,
            timed_out=timed_out,
            images=len(changed),
        )
        yield {
            "type": "done",
            "exit": exit_code,
            "seconds": seconds,
            "timedOut": timed_out,
            "truncated": truncated,
        }


def runs_enabled() -> bool:
    """True on a dev machine that runs labs on request (`make api`); never in public mode."""
    settings = get_settings()
    return settings.dev_run_labs and not settings.public_mode


_runner: LabRunner | None = None


def get_runner() -> LabRunner:
    """The process's runner: local today, the place a container backend is chosen later."""
    global _runner
    if _runner is None:
        _runner = LocalRunner(timeout_s=get_settings().lab_run_timeout_s)
    return _runner
