"""The stdlib course checks (`librarian courses check ...`): tmp_path fixtures plus one real-tree smoke each.

The real-tree tests assert only that a check completes and prints a summary, never how many findings
there are: content findings are the course's business, not this suite's.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from librarian.cli import main as cli
from librarian.courses.checks import (
    check_chapters,
    check_drills,
    check_manifest,
    common,
    crosswalk,
    curriculum_map,
    link_check,
    smoke_labs,
)

PRIVATE_NAME = "zq-secret-solution"


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def note(body: str = "Body.\n", **meta: str) -> str:
    front = "".join(f"{k}: {v}\n" for k, v in meta.items())
    return f"---\ntitle: T\n{front}---\n{body}"


@pytest.fixture
def courses(tmp_path: Path) -> Path:
    return tmp_path / "courses"


# --- common ---------------------------------------------------------------------------------------


def test_public_files_skip_private(courses: Path) -> None:
    write(courses / "a" / "b" / "one.md", note())
    write(courses / "private" / "a" / f"{PRIVATE_NAME}.md", note())
    assert common.public_files(courses) == ["a/b/one.md"]
    assert common.is_private(courses / "private" / "x.md", courses)
    assert not common.is_private(courses / "a" / "x.md", courses)


def test_resolve_arg_strips_data_courses(courses: Path) -> None:
    assert common.resolve_arg("data/courses/a/b", courses) == courses / "a" / "b"


# --- check_chapters -------------------------------------------------------------------------------


def test_origin_is_optional_until_required(courses: Path) -> None:
    lesson = write(courses / "c" / "m" / "01-a.md", note())
    assert check_chapters.metadata_problems(lesson.read_text(), lesson, courses) == []
    problems = check_chapters.metadata_problems(
        lesson.read_text(), lesson, courses, require_origin=True
    )
    assert any("origin" in p for p in problems)


def test_illegal_origin_fails(courses: Path) -> None:
    lesson = write(courses / "c" / "m" / "01-a.md", note(origin="notes"))
    problems = check_chapters.metadata_problems(lesson.read_text(), lesson, courses)
    assert any("origin 'notes'" in p for p in problems)


def test_language_subset_sections() -> None:
    assert check_chapters.in_language_subset(Path("programming/typescript/notes/04-generics.md"))
    assert not check_chapters.in_language_subset(Path("programming/python/notes/x.md"))
    assert check_chapters.language_subset_problems("# T\n\nShort.\n")


def test_run_counts_a_short_lesson_and_hides_private(
    courses: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write(courses / "c" / "m" / "notes" / "01-a.md", note("Too short.\n"))
    write(courses / "private" / "c" / "m" / "notes" / f"{PRIVATE_NAME}.md", note("Too short.\n"))
    count, bad, lines = check_chapters.run([courses / "c" / "m"], courses)
    assert (count, bad) == (1, 1)
    assert PRIVATE_NAME not in "\n".join(lines)
    assert check_chapters.main(["--root", str(courses), "c/m", "--strict"]) == 1
    assert PRIVATE_NAME not in capsys.readouterr().out


def test_chapters_real_tree_completes(capsys: pytest.CaptureFixture[str]) -> None:
    check_chapters.main(["--all"])
    assert "notes meet" in capsys.readouterr().out


# --- link_check -----------------------------------------------------------------------------------


def test_broken_link_found_and_fence_ignored(courses: Path) -> None:
    write(courses / "c" / "m" / "02-b.md", note())
    lesson = write(
        courses / "c" / "m" / "01-a.md",
        note("[ok](02-b.md) [bad](03-missing.md) [web](https://x.io/a)\n```\n[no](nope.md)\n```\n"),
    )
    assert link_check.broken_links(lesson, lesson.read_text(), courses) == ["03-missing.md"]


def test_link_into_private_is_skipped_and_never_named(
    courses: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write(courses / "private" / "c" / "m" / f"{PRIVATE_NAME}.md", note())
    write(
        courses / "c" / "m" / "01-a.md",
        note(f"[x](../../private/c/m/{PRIVATE_NAME}.md) [y](missing.md)\n"),
    )
    assert link_check.main(["--root", str(courses)]) == 1
    out = capsys.readouterr().out
    assert "missing.md" in out
    assert PRIVATE_NAME not in out


def test_sources_link_is_no_error_without_a_library(
    courses: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(link_check.sources, "sources_root", lambda: None)
    lesson = write(courses / "c" / "m" / "01-a.md", note("[p](sources/paper.pdf)\n"))
    assert link_check.broken_links(lesson, lesson.read_text(), courses) == []


def test_links_real_tree_completes(capsys: pytest.CaptureFixture[str]) -> None:
    link_check.main([])
    out = capsys.readouterr().out
    assert "broken links found" in out or "All links OK" in out


# --- curriculum_map -------------------------------------------------------------------------------


def test_curriculum_build_and_cli(
    courses: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write(courses / "ai" / "01-a" / "readme.md", note("Start: [one](notes/01-one.md)\n"))
    write(courses / "ai" / "01-a" / "notes" / "01-one.md", note("[two](02-two.md)\n"))
    write(courses / "ai" / "01-a" / "notes" / "02-two.md", note("End.\n"))
    out = tmp_path / "map.json"
    assert curriculum_map.main(["--root", str(courses), "--out", str(out), "build"]) == 0
    data = json.loads(out.read_text())
    assert data
    assert curriculum_map.main(["--root", str(courses), "--out", str(out), "issues"]) in (0, 1)
    assert "wrote" in capsys.readouterr().out or out.exists()


def test_curriculum_never_lists_private(courses: Path, tmp_path: Path) -> None:
    write(courses / "ai" / "01-a" / "notes" / "01-one.md", note())
    write(courses / "private" / "ai" / "01-a" / "notes" / f"{PRIVATE_NAME}.md", note())
    out = tmp_path / "map.json"
    curriculum_map.main(["--root", str(courses), "--out", str(out), "build"])
    assert PRIVATE_NAME not in out.read_text()


def test_curriculum_real_tree_completes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "map.json"
    assert curriculum_map.main(["--out", str(out), "build"]) == 0
    assert out.exists()
    curriculum_map.main(["--out", str(out), "issues"])
    assert "issue" in capsys.readouterr().out


# --- check_drills ---------------------------------------------------------------------------------

DRILL = (
    "---\ntitle: D\ntrack: python\ntopic: t\ndifficulty: easy\ntimebox_min: 5\nsource: own\n---\n"
    "## Prompt\n\nx\n\n## Starter\n\ny\n\n## Tests\n\nz\n"
)


def test_drill_schema(courses: Path) -> None:
    write(courses / "programming" / "drills" / "python" / "ok.md", DRILL)
    write(
        courses / "programming" / "drills" / "python" / "bad.md",
        DRILL.replace("difficulty: easy\n", "difficulty: brutal\n"),
    )
    write(courses / "private" / "programming" / "drills" / f"{PRIVATE_NAME}.md", "---\n---\n")
    files, lines = check_drills.run(courses, ["programming/drills"])
    assert files == 2
    assert any("bad.md: unknown difficulty" in line for line in lines)
    assert PRIVATE_NAME not in "\n".join(lines)


def test_drills_real_tree_completes(capsys: pytest.CaptureFixture[str]) -> None:
    check_drills.main([])
    assert "files" in capsys.readouterr().out


# --- check_manifest -------------------------------------------------------------------------------


def test_manifest_optional_by_default_required_on_request(courses: Path) -> None:
    write(courses / "data-science" / "01-m" / "practice" / "lab.py", "print(1)\n")
    assert check_manifest.run(courses)[1] == []
    assert check_manifest.run(courses, require_manifest=True)[1]


def test_manifest_entry_must_exist(courses: Path) -> None:
    base = courses / "data-science" / "01-m" / "practice"
    write(base / "lab.py", "print(1)\n")
    write(
        base / "manifest.yaml",
        'examples:\n  - path: "practice/gone.py"\n    purpose: "x"\n    licence: "course"\n',
    )
    _, problems = check_manifest.run(courses)
    assert any("does not exist" in p for p in problems)


def test_manifest_real_tree_completes(capsys: pytest.CaptureFixture[str]) -> None:
    check_manifest.main([])
    assert "manifest-check" in capsys.readouterr().out


# --- crosswalk ------------------------------------------------------------------------------------


def test_crosswalk_unit_must_exist_and_output_is_stable(courses: Path, tmp_path: Path) -> None:
    write(courses / "programming" / "sql" / "01.md", note())
    write(
        courses / "programming" / "drills" / "sql" / "q.md",
        note(units="[programming/sql, programming/nope]"),
    )
    out = tmp_path / "cw.md"
    code, lines = crosswalk.run(courses, out)
    assert code == 1 and any("programming/nope" in line for line in lines)
    write(courses / "programming" / "drills" / "sql" / "q.md", note(units="[programming/sql]"))
    assert crosswalk.run(courses, out)[0] == 0
    assert "programming/sql" in out.read_text()
    assert crosswalk.run(courses, out, check=True)[0] == 0
    out.write_text("stale")
    assert crosswalk.run(courses, out, check=True)[0] == 1


def test_crosswalk_skips_private_links_silently(courses: Path, tmp_path: Path) -> None:
    write(courses / "private" / "x" / f"{PRIVATE_NAME}.md", note())
    write(
        courses / "interviewing" / "r.md",
        note(f"[a](../private/x/{PRIVATE_NAME}.md)\n"),
    )
    code, lines = crosswalk.run(courses, tmp_path / "cw.md")
    assert code == 0
    assert PRIVATE_NAME not in "\n".join(lines)


def test_crosswalk_real_tree_completes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    crosswalk.main(["--out", str(tmp_path / "cw.md")])
    assert "crosswalk:" in capsys.readouterr().out


# --- smoke_labs -----------------------------------------------------------------------------------


def test_find_folder_refuses_private(courses: Path, tmp_path: Path) -> None:
    (courses / "c" / "practice").mkdir(parents=True)
    (courses / "private" / "c").mkdir(parents=True)
    sources = tmp_path / "src"
    assert smoke_labs.find_folder("c/practice", courses, sources) == courses / "c" / "practice"
    assert smoke_labs.find_folder("private/c", courses, sources) is None


def test_smoke_labs_runs_and_reports(courses: Path, capsys: pytest.CaptureFixture[str]) -> None:
    folder = courses / "c" / "m" / "practice"
    write(folder / "ok.py", "print('hi')\n")
    write(folder / "boom.py", "raise SystemExit(3)\n")
    assert smoke_labs.main([str(folder), "--timeout", "20"]) == 1
    assert "boom" in capsys.readouterr().out


def test_smoke_labs_real_tree_completes() -> None:
    assert smoke_labs.main(["no-such-folder"]) == 2


# --- cli ------------------------------------------------------------------------------------------


def test_cli_dispatch(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli(["courses", "check"]) == 0
    assert "smoke-labs" in capsys.readouterr().out
    assert cli(["courses", "check", "nope"]) == 2
    assert cli(["courses", "review", "nope"]) == 2


# --- concept homes --------------------------------------------------------------------------------


def _concept_registry(tmp_path: Path) -> Path:
    registry = {
        "concepts": {
            "softmax": {
                "pattern": "\\bsoftmax\\b",
                "homes": [
                    "generative-ai/01-a/notes/01-home.md#softmax",
                    "data-science/01-b/notes/09-deep.md",
                ],
            }
        }
    }
    return write(tmp_path / "concept_homes.json", json.dumps(registry))


def _concept_issues(courses: Path, registry: Path) -> list[dict]:
    issues = curriculum_map.build(courses, None, registry)["issues"]
    return [i for i in issues if i["kind"] == "concept_unlinked"]


def test_concept_homes_report_only_the_unlinked_use(courses: Path, tmp_path: Path) -> None:
    write(
        courses / "generative-ai/01-a/notes/01-home.md",
        note("# Home\n\n## Softmax\n\nSoftmax lives here.\n"),
    )
    write(
        courses / "generative-ai/01-a/notes/02-linked.md",
        note("A [softmax](01-home.md#softmax) again.\n"),
    )
    write(
        courses / "generative-ai/01-a/notes/03-unlinked.md",
        note("intro\n\nThe Softmax of the scores.\n"),
    )
    write(courses / "generative-ai/01-a/notes/04-fenced.md", note("```\nsoftmax(x)\n```\n"))
    write(
        courses / "generative-ai/01-a/notes/05-deeper.md",
        note("softmax, see [deep](../../../data-science/01-b/notes/09-deep.md).\n"),
    )
    write(courses / "data-science/01-b/notes/09-deep.md", note("softmax in depth\n"))
    found = _concept_issues(courses, _concept_registry(tmp_path))
    assert [i["path"] for i in found] == ["generative-ai/01-a/notes/03-unlinked.md"]
    assert "line 6" in found[0]["detail"]
    assert "generative-ai/01-a/notes/01-home.md#softmax" in found[0]["detail"]
    assert "concept_unlinked" in curriculum_map.INFO_KINDS


def test_concept_homes_without_a_registry_report_nothing(courses: Path, tmp_path: Path) -> None:
    write(courses / "generative-ai/01-a/notes/03-unlinked.md", note("The softmax.\n"))
    assert _concept_issues(courses, tmp_path / "missing.json") == []
