"""Labs: the manifest loader, the `verified_by` parser, the note ↔ lab joins, the local runner and
the lab routes.

Everything runs against a tmp courses tree (module constants monkeypatched, caches cleared). The
runner tests put a fake `uv` on the path that runs the script with this Python, so no lab
dependencies are installed and no network is touched.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from librarian.api.routers import courses as courses_routes
from librarian.api.security import require_user
from librarian.courses import catalog as courses
from librarian.courses import importer as ic
from librarian.courses import lab_runner, labs
from librarian.courses.lab_runner import LabRunError, LocalRunner, RunRequest

MOD = "data-science/01-classical-ml"

MANIFEST = """examples:
  - path: practice/importance_noise.py
    purpose: Permutation importance against noise features.
    demonstrates: []
    pattern: evaluation
    language: python
    runs_offline: true
    verified_by: uv run importance_noise.py
    licence: course
  - path: practice/credit-default-lab
    purpose: A full pipeline.
    demonstrates: [notes/Pipelines.md]
    pattern: pipeline
    language: python
    runs_offline: false
    verified_by: cd credit-default-lab && uv run --no-project pytest_runner.py
    licence: course
  - path: practice/chartstyle.py
    purpose: Shared chart style.
    demonstrates: []
    pattern: other
    language: python
    verified_by: none
    licence: course
  - path: practice/not_mirrored.py
    purpose: Licence unrecorded, so not here.
    demonstrates: [notes/pipelines.md]
    language: python
    licence: unrecorded
  - path: practice/widget.ts
    purpose: TypeScript, listed for reading.
    demonstrates: [notes/pipelines.md]
    language: typescript
    verified_by: npx tsx widget.ts
    licence: course
"""

SCRIPT = """import sys
from pathlib import Path
print("hello from", Path(__file__).name)
print("to stderr", file=sys.stderr)
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture()
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    root = tmp_path / "courses"
    pillar = root / MOD
    _write(root / "data-science" / "_course.md", "---\ntitle: Data Science\norder: 1\n---\n")
    _write(pillar / "_module.md", "---\ntitle: Classical ML\norder: 1\n---\n")
    _write(
        pillar / "notes" / "pipelines.md",
        "---\ntitle: Pipelines\nsummary: Fit transforms inside the split.\n---\n\nBuild one.\n",
    )
    _write(
        pillar / "notes" / "importance.md",
        "---\ntitle: Feature Importance\nsummary: Which features matter.\n---\n\n"
        "Run `importance_noise.py` to see noise features rank.\n",
    )
    _write(pillar / "practice" / "manifest.yaml", MANIFEST)
    _write(pillar / "practice" / "importance_noise.py", SCRIPT)
    _write(pillar / "practice" / "chartstyle.py", "STYLE = 1\n")
    _write(pillar / "practice" / "widget.ts", "export {}\n")
    _write(pillar / "practice" / "credit-default-lab" / "run.py", "print('pipeline')\n")
    _write(pillar / "practice" / "credit-default-lab" / "features.py", "X = 1\n")
    _write(pillar / "practice" / "credit-default-lab" / "config.yaml", "k: 1\n")
    _write(pillar / "practice" / "credit-default-lab" / "data" / "big.json", "{}\n")
    # A private lesson in the same module that names the file: never linked from a lab.
    _write(
        root / "private" / MOD / "notes" / "client.md",
        "---\ntitle: Client Notes\n---\n\nWe ran importance_noise.py on client data.\n",
    )

    monkeypatch.setattr(labs, "COURSES_DIR", root)
    monkeypatch.setattr(courses, "COURSES_DIR", root)
    monkeypatch.setattr(courses, "WIKI_DIR", tmp_path / "wiki")
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "lessons.npz")
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
    labs._load.cache_clear()
    courses._load.cache_clear()
    yield root
    labs._load.cache_clear()
    courses._load.cache_clear()


# ---- verified_by → Command ----


@pytest.mark.parametrize(
    ("text", "argv", "cwd"),
    [
        ("uv run lab.py", ("uv", "run", "lab.py"), "."),
        ("uv run python lab.py --rows 10", ("uv", "run", "python", "lab.py", "--rows", "10"), "."),
        (
            "uv run --no-project --with 'psycopg[binary]' lab.py",
            ("uv", "run", "--no-project", "--with", "psycopg[binary]", "lab.py"),
            ".",
        ),
        ("uv run -m pytest -q", ("uv", "run", "-m", "pytest", "-q"), "."),
        ("cd folder && uv run main.py", ("uv", "run", "main.py"), "folder"),
    ],
)
def test_parse_check_accepts_plain_uv_runs(text: str, argv: tuple[str, ...], cwd: str) -> None:
    assert labs.parse_check(text, Path("folder")) == labs.Command(argv, cwd)


@pytest.mark.parametrize(
    "text",
    [
        "",
        "none",
        "npx tsx widget.ts",
        "uv run lab.py | head",
        "uv run lab.py > out.txt",
        "uv run $HOME/lab.py",
        "uv run ../other/lab.py",
        "uv run /abs/lab.py",
        "uv run notes.txt",
        "uv run --unknown-flag lab.py",
        "uv run -m",
        "cd elsewhere && uv run lab.py",
        "cd folder && uv run a.py && uv run b.py",
        "uv run 'unterminated",
    ],
)
def test_parse_check_refuses_anything_else(text: str) -> None:
    assert labs.parse_check(text, Path("folder")) is None


# ---- manifest loader ----


def test_loader_keeps_mirrored_labs_and_skips_helpers(tree: Path) -> None:
    found = labs.all_labs()
    assert sorted(found) == [
        f"{MOD}/practice/credit-default-lab",
        f"{MOD}/practice/importance_noise.py",
        f"{MOD}/practice/widget.ts",
    ]
    noise = found[f"{MOD}/practice/importance_noise.py"]
    assert noise.title == "Importance noise"
    assert noise.files == ("importance_noise.py",)
    assert noise.run == labs.Command(("uv", "run", "importance_noise.py"))
    assert noise.check == labs.Command(("uv", "run", "importance_noise.py"))


def test_folder_lab_finds_its_entry_and_editable_files(tree: Path) -> None:
    lab = labs.get(f"{MOD}/practice/credit-default-lab")
    assert lab is not None and lab.is_folder
    assert lab.run == labs.Command(("uv", "run", "run.py"), cwd="credit-default-lab")
    assert lab.check is not None and lab.check.cwd == "credit-default-lab"
    # Scripts first; the data/ folder is never offered for editing.
    assert lab.files == (
        "credit-default-lab/features.py",
        "credit-default-lab/run.py",
        "credit-default-lab/config.yaml",
    )
    assert lab.notes == (f"{MOD}/notes/Pipelines",)
    assert lab.runs_offline is False


def test_non_python_labs_are_listed_but_never_runnable(tree: Path) -> None:
    lab = labs.get(f"{MOD}/practice/widget.ts")
    assert lab is not None and lab.run is None and lab.check is None
    assert lab.verified_by == "npx tsx widget.ts"


def test_private_manifests_are_not_read(tree: Path) -> None:
    _write(tree / "private" / MOD / "practice" / "manifest.yaml", MANIFEST)
    _write(tree / "private" / MOD / "practice" / "importance_noise.py", SCRIPT)
    labs._load.cache_clear()
    assert not [i for i in labs.all_labs() if i.startswith("private/")]


def test_lab_file_only_serves_the_labs_own_files(tree: Path) -> None:
    lab = labs.get(f"{MOD}/practice/importance_noise.py")
    assert lab is not None
    assert (
        labs.lab_file(lab, "importance_noise.py") == tree / MOD / "practice" / "importance_noise.py"
    )
    assert labs.lab_file(lab, "chartstyle.py") is None
    assert labs.lab_file(lab, "../notes/pipelines.md") is None


# ---- note ↔ lab joins ----


def test_labs_join_notes_by_manifest_and_by_filename(tree: Path) -> None:
    rows = {r["id"]: r for r in courses.list_labs()}
    noise = rows[f"{MOD}/practice/importance_noise.py"]
    # `demonstrates: []`, so the note that names the file links it; the private one never does.
    assert [n["id"] for n in noise["notes"]] == [f"{MOD}/notes/importance"]
    # The manifest's `Pipelines.md` resolves to the mirror's lower-cased note.
    folder = rows[f"{MOD}/practice/credit-default-lab"]
    assert [n["id"] for n in folder["notes"]] == [f"{MOD}/notes/pipelines"]
    assert folder["hasRun"] and folder["hasCheck"] and not folder["runsOffline"]
    assert [r["id"] for r in courses.list_labs(language="typescript")] == [
        f"{MOD}/practice/widget.ts"
    ]
    assert courses.list_labs(course="nope") == []


def test_lesson_lists_its_labs(tree: Path) -> None:
    lesson = courses.lesson_detail(f"{MOD}/notes/pipelines")
    assert lesson is not None
    assert {lab["id"] for lab in lesson["labs"]} == {
        f"{MOD}/practice/credit-default-lab",
        f"{MOD}/practice/widget.ts",
    }


def test_lab_detail_carries_files_and_commands(tree: Path) -> None:
    detail = courses.lab_detail(f"{MOD}/practice/credit-default-lab")
    assert detail is not None
    assert [f["path"] for f in detail["files"]][:2] == [
        "credit-default-lab/features.py",
        "credit-default-lab/run.py",
    ]
    assert detail["run"] == "cd credit-default-lab && uv run run.py"
    assert detail["check"] == "cd credit-default-lab && uv run --no-project pytest_runner.py"
    assert detail["licence"] == "course"
    assert courses.lab_detail("nope") is None


def test_lab_brief_shows_the_edit_as_a_diff_and_the_output_tail(tree: Path) -> None:
    lab_id = f"{MOD}/practice/importance_noise.py"
    edited = SCRIPT.replace("hello from", "edited by me")
    brief = courses.lab_brief(lab_id, {"importance_noise.py": edited}, "x" * 20_000 + "END", 1)
    assert brief is not None
    assert "Purpose: Permutation importance against noise features." in brief
    assert "- Feature Importance: Which features matter." in brief
    assert '-print("hello from"' in brief and '+print("edited by me"' in brief
    assert brief.rstrip().endswith("END") or "END" in brief
    assert "x" * 9_000 not in brief  # the output is capped, keeping its end

    unchanged = courses.lab_brief(lab_id, {"importance_noise.py": SCRIPT})
    assert unchanged is not None and "unified diff" not in unchanged and "hello from" in unchanged
    assert courses.lab_brief("nope", {}) is None


# ---- the importer ----


def test_plan_labs_mirrors_cleared_labs_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "lae"
    pillar = source / "data-science" / "01-Classical-ML"
    _write(pillar / "practice" / "manifest.yaml", MANIFEST)
    for rel in (
        "importance_noise.py",
        "not_mirrored.py",
        "credit-default-lab/run.py",
        "credit-default-lab/notes.md",
    ):
        _write(pillar / "practice" / rel, "x = 1\n")
    dest = tmp_path / "courses"
    monkeypatch.setattr(ic, "COURSES_DIR", dest)
    plan = ic.Plan()
    plan.tracked = {p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file()}

    ic.plan_labs(plan, source, ["data-science"])

    got = sorted(p.relative_to(dest).as_posix() for p in plan.copies)
    assert got == [
        "data-science/01-classical-ml/practice/credit-default-lab/run.py",
        "data-science/01-classical-ml/practice/importance_noise.py",
        "data-science/01-classical-ml/practice/manifest.yaml",
    ]


# ---- the local runner ----


@pytest.fixture()
def fake_uv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A `uv` that drops `run` and any uv flags and runs the rest with this Python."""
    shim = tmp_path / "bin" / "uv"
    _write(
        shim,
        f'#!/bin/sh\nshift\nwhile [ "${{1#-}}" != "$1" ]; do shift; done\n'
        f'exec {sys.executable} "$@"\n',
    )
    shim.chmod(0o755)
    monkeypatch.setattr(
        lab_runner.shutil, "which", lambda name: str(shim) if name == "uv" else None
    )
    return shim


def _runner(tree: Path, tmp_path: Path, timeout_s: float = 30) -> LocalRunner:
    return LocalRunner(timeout_s=timeout_s, sources_root=tmp_path / "no-sources", courses_dir=tree)


async def _events(runner: LocalRunner, request: RunRequest) -> list[dict]:
    return [e async for e in runner.run(request)]


def _lab(lab_id: str) -> labs.Lab:
    lab = labs.get(lab_id)
    assert lab is not None
    return lab


@pytest.mark.unit
async def test_runner_streams_output_and_exit(tree: Path, tmp_path: Path, fake_uv: Path) -> None:
    lab = _lab(f"{MOD}/practice/importance_noise.py")
    events = await _events(_runner(tree, tmp_path), RunRequest(lab))
    assert events[0] == {"type": "start", "command": "uv run importance_noise.py"}
    out = "".join(str(e["text"]) for e in events if e.get("stream") == "stdout")
    err = "".join(str(e["text"]) for e in events if e.get("stream") == "stderr")
    assert "hello from importance_noise.py" in out and "to stderr" in err
    done = events[-1]
    assert done["type"] == "done" and done["exit"] == 0 and done["timedOut"] is False


@pytest.mark.unit
async def test_runner_uses_edits_in_a_copy_and_returns_figures(
    tree: Path, tmp_path: Path, fake_uv: Path
) -> None:
    lab = _lab(f"{MOD}/practice/importance_noise.py")
    source = tree / MOD / "practice" / "importance_noise.py"
    edited = (
        "from pathlib import Path\n"
        "out = Path(__file__).resolve().parents[2] / 'sources' / 'images'\n"
        "out.mkdir(parents=True, exist_ok=True)\n"
        "(out / 'fig.png').write_bytes(b'png')\n"
        "print('edited')\n"
        "raise SystemExit(3)\n"
    )
    events = await _events(
        _runner(tree, tmp_path), RunRequest(lab, files={"importance_noise.py": edited})
    )
    assert any(e.get("text") == "edited\n" for e in events)
    images = [e for e in events if e["type"] == "image"]
    assert [(i["path"], i["mime"], i["data"]) for i in images] == [
        ("sources/images/fig.png", "image/png", "cG5n")
    ]
    assert events[-1]["exit"] == 3
    assert source.read_text() == SCRIPT
    assert not (tree / "data-science" / "sources").exists()


@pytest.mark.unit
async def test_runner_kills_on_timeout(tree: Path, tmp_path: Path, fake_uv: Path) -> None:
    lab = _lab(f"{MOD}/practice/importance_noise.py")
    slow = "import time\nprint('start', flush=True)\ntime.sleep(30)\n"
    events = await _events(
        _runner(tree, tmp_path, timeout_s=1), RunRequest(lab, files={"importance_noise.py": slow})
    )
    done = events[-1]
    assert done["timedOut"] is True and done["exit"] != 0 and done["seconds"] < 10


@pytest.mark.unit
async def test_runner_env_holds_provider_keys_only_for_online_labs(
    tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setenv("LIBRARIAN_SECRET", "nope")
    offline = lab_runner._env(_lab(f"{MOD}/practice/importance_noise.py"), Path("/t"))
    online = lab_runner._env(_lab(f"{MOD}/practice/credit-default-lab"), Path("/t"))
    assert "ANTHROPIC_API_KEY" not in offline and online["ANTHROPIC_API_KEY"] == "sk-test"
    assert "LIBRARIAN_SECRET" not in offline and "LIBRARIAN_SECRET" not in online
    assert offline["MPLBACKEND"] == "Agg" and offline["TMPDIR"] == "/t"


def test_validate_refuses_missing_commands_and_stray_files(tree: Path) -> None:
    with pytest.raises(LabRunError, match="no run command"):
        lab_runner.validate(RunRequest(_lab(f"{MOD}/practice/widget.ts")))
    with pytest.raises(LabRunError, match=r"chartstyle\.py"):
        lab_runner.validate(
            RunRequest(_lab(f"{MOD}/practice/importance_noise.py"), files={"chartstyle.py": ""})
        )


# ---- routes ----


@pytest.fixture()
def client(tree: Path) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(courses_routes.router)
    app.dependency_overrides[require_user] = lambda: object()
    with TestClient(app) as c:
        yield c


def test_lab_list_and_detail_routes(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(lab_runner, "runs_enabled", lambda: False)
    body = client.get("/api/courses/labs").json()
    assert body["canRun"] is False and len(body["labs"]) == 3
    detail = client.get(f"/api/courses/labs/{MOD}/practice/importance_noise.py").json()
    assert detail["files"][0]["text"] == SCRIPT and detail["canRun"] is False
    assert client.get("/api/courses/labs/nope").status_code == 404


def test_run_route_is_404_unless_enabled(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(lab_runner, "runs_enabled", lambda: False)
    resp = client.post("/api/courses/lab-runs", json={"lab": f"{MOD}/practice/importance_noise.py"})
    assert resp.status_code == 404


def test_run_route_streams_and_refuses_stray_files(
    client: TestClient, tree: Path, tmp_path: Path, fake_uv: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(lab_runner, "runs_enabled", lambda: True)
    monkeypatch.setattr(lab_runner, "_runner", _runner(tree, tmp_path))
    lab_id = f"{MOD}/practice/importance_noise.py"

    resp = client.post("/api/courses/lab-runs", json={"lab": lab_id, "mode": "run"})
    assert resp.status_code == 200
    events = [
        json.loads(line[len("data: ") :])
        for line in resp.text.splitlines()
        if line.startswith("data: ")
    ]
    assert events[0]["type"] == "start" and events[-1]["type"] == "done"

    stray = client.post(
        "/api/courses/lab-runs", json={"lab": lab_id, "files": {"chartstyle.py": "x"}}
    )
    assert stray.status_code == 422
    assert client.post("/api/courses/lab-runs", json={"lab": "nope"}).status_code == 404
