"""data/courses/private/: the gitignored home of course files that must not be public.

Covers the tracked-file guard, the lesson leak check in `librarian wiki check`, how the
catalog marks and excludes private lessons, and that nothing derived from them reaches an
index, a snapshot or the gap list.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from librarian.courses import catalog as courses
from librarian.courses import curriculum
from librarian.retrieval import corpus
from librarian.wiki.telemetry import main

REPO = Path(__file__).resolve().parents[2]
SECRET_MODULE = "zq-hackerrank-solutions"
SECRET_LESSON = "zq-two-sum-solution"

PAGE = "---\ntitle: {title}\ntags: [rag, concept]\nsummary: s\nupdated: 2026-11-01\n---\n\n{body}\n"


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def lesson(title: str, body: str = "Body.", **meta: str) -> str:
    extra = "".join(f"{k}: {v}\n" for k, v in meta.items())
    return f"---\ntitle: {title}\n{extra}---\n\n{body}\n"


@pytest.fixture
def wiki(tmp_path: Path) -> Path:
    root = tmp_path / "wiki"
    write(root / "rag" / "hybrid-search.md", PAGE.format(title="Hybrid Search", body="Public."))
    write(root / "private" / "acme-notes.md", PAGE.format(title="Acme Notes", body="Private."))
    return root


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """Courses tree: one public course and one private module, in the mirrored layout."""
    r = tmp_path / "courses"
    write(r / "prog" / "_course.md", "---\ntitle: Programming\norder: 1\n---\n")
    write(r / "prog" / "01-basics" / "_module.md", "---\ntitle: Basics\norder: 1\n---\n")
    write(r / "prog" / "01-basics" / "intro.md", lesson("Intro", order="1"))
    write(r / "prog" / "01-basics" / "next.md", lesson("Next", order="2"))
    write(r / "private" / "prog" / "01-basics" / "mine.md", lesson("Mine", order="3"))
    write(
        r / "private" / "prog" / SECRET_MODULE / "_module.md",
        "---\ntitle: Secret Solutions\norder: 9\n---\n",
    )
    write(r / "private" / "prog" / SECRET_MODULE / f"{SECRET_LESSON}.md", lesson("Two Sum"))
    return r


def run_check(wiki: Path, tmp_path: Path, root: Path, *extra: str, repo: Path | None = None) -> int:
    return main(
        [
            "check",
            "--wiki-dir",
            str(wiki),
            "--telemetry-dir",
            str(tmp_path / "telemetry"),
            "--courses-dir",
            str(root),
            "--repo-root",
            str(repo or tmp_path / "not-a-repo"),
            *extra,
        ]
    )


# ── Ignore rule and the tracked-file guard ──────────────────────────────────


def test_repo_gitignores_the_private_course_tree() -> None:
    out = subprocess.run(
        ["git", "check-ignore", "-q", "data/courses/private/leetcode/x.md"],
        cwd=REPO,
        check=False,
    )
    assert out.returncode == 0


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    git(r, "init", "-q")
    write(r / ".gitignore", "data/courses/private/\ndata/wiki/private/\n")
    write(r / "data" / "courses" / "prog" / "a.md", "public\n")
    git(r, "add", ".gitignore", "data/courses/prog/a.md")
    return r


@pytest.mark.parametrize("tree", ["data/courses/private", "data/wiki/private"])
def test_force_added_private_file_fails_the_guard(
    tree: str,
    repo: Path,
    wiki: Path,
    root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert run_check(wiki, tmp_path, root, "--tracked-only", repo=repo) == 0
    leaked = write(repo / tree / "leetcode" / "zq-secret-solution.md", "x\n")
    git(repo, "add", "-f", str(leaked))
    capsys.readouterr()
    assert run_check(wiki, tmp_path, root, "--tracked-only", repo=repo) == 1
    out = capsys.readouterr().out
    assert f"1 tracked file(s) under {tree}/" in out
    assert "zq-secret-solution" not in out  # counted, never named
    # The full check fails the same way.
    assert run_check(wiki, tmp_path, root, repo=repo) == 1


def test_guard_passes_outside_a_git_checkout(wiki: Path, root: Path, tmp_path: Path) -> None:
    assert run_check(wiki, tmp_path, root, "--tracked-only") == 0


def test_precommit_runs_the_guard() -> None:
    config = (REPO / ".pre-commit-config.yaml").read_text()
    assert "librarian wiki check --tracked-only" in config


# ── Leak check: public lessons into data/courses/private/ ────────────────────

PRIVATE_LINKS = {
    "relative markdown link": "See [mine](../../private/prog/01-basics/mine.md).",
    "lesson-id style link": "See [mine](private/prog/01-basics/mine).",
    "image": "![fig](../../private/prog/01-basics/assets/fig.png)",
    "html src": '<img src="../../private/prog/01-basics/assets/fig.png">',
    "reference-style link": "[mine]: ../../private/prog/01-basics/mine.md",
    "anchor and query": "[mine](../../private/prog/01-basics/mine.md#top)",
    "path mention": "Stored in data/courses/private/prog.",
}


@pytest.mark.parametrize("body", PRIVATE_LINKS.values(), ids=PRIVATE_LINKS.keys())
def test_public_lesson_linking_into_private_blocks(
    body: str,
    wiki: Path,
    root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    write(root / "prog" / "01-basics" / "leak.md", lesson("Leak", f"line one\n{body}"))
    assert run_check(wiki, tmp_path, root) == 1
    out = capsys.readouterr().out
    assert "leak.md:6 links into data/courses/private/" in out
    assert "mine" not in out  # the target is never named
    assert SECRET_MODULE not in out and SECRET_LESSON not in out


FRONTMATTER_FORMS = {
    "lesson id field": "see: private/prog/01-basics/mine",
    "relative path field": "source: ../../private/prog/01-basics/mine.md",
}


@pytest.mark.parametrize("field", FRONTMATTER_FORMS.values(), ids=FRONTMATTER_FORMS.keys())
def test_frontmatter_reference_into_private_blocks(
    field: str, wiki: Path, root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    key, _, value = field.partition(": ")
    write(root / "prog" / "01-basics" / "leak.md", lesson("Leak", **{key: value}))
    assert run_check(wiki, tmp_path, root) == 1
    assert "leak.md:3 links into data/courses/private/" in capsys.readouterr().out


def test_flashcard_deck_naming_a_private_lesson_blocks(
    wiki: Path, root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write(
        root / "prog" / "01-basics" / "_flashcards.md",
        "---\ncards:\n  - front: q\n    back: a\n    lesson: private/prog/01-basics/mine\n---\n",
    )
    assert run_check(wiki, tmp_path, root) == 1
    assert "_flashcards.md:5 links into data/courses/private/" in capsys.readouterr().out


def test_clean_public_lessons_and_private_to_private_links_pass(
    wiki: Path, root: Path, tmp_path: Path
) -> None:
    write(
        root / "prog" / "01-basics" / "ok.md",
        lesson(
            "Ok",
            "[next](next.md) [web](https://example.com/private/x) ![i](assets/a.png) [t](#top)\n"
            "A private key is not a private course, and private/public keys are fine in prose.",
            see="prog/01-basics/next",
        ),
    )
    write(
        root / "private" / "prog" / "01-basics" / "links.md",
        lesson(
            "Links", "[mine](mine.md) [[Acme Notes]] and [intro](../../../prog/01-basics/intro.md)"
        ),
    )
    assert run_check(wiki, tmp_path, root) == 0


def test_a_look_alike_directory_is_not_private(wiki: Path, root: Path, tmp_path: Path) -> None:
    write(root / "prog" / "01-basics" / "ok.md", lesson("Ok", "[x](../privateer/notes.md)"))
    assert run_check(wiki, tmp_path, root) == 0


def test_link_check_runs_without_any_private_tree(tmp_path: Path) -> None:
    """CI has neither private tree; a link into one is still a leak."""
    bare_wiki = tmp_path / "wiki"
    write(bare_wiki / "rag" / "p.md", PAGE.format(title="P", body="x"))
    r = tmp_path / "courses"
    write(r / "prog" / "m" / "leak.md", lesson("Leak", "[x](../../private/prog/m/x.md)"))
    assert run_check(bare_wiki, tmp_path, r) == 1
    (r / "prog" / "m" / "leak.md").write_text(lesson("Leak", "fine"))
    assert run_check(bare_wiki, tmp_path, r) == 0


# ── Leak check: public lessons naming a private wiki page ────────────────────


def test_wikilink_to_private_wiki_page_from_a_lesson_blocks(
    wiki: Path, root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write(root / "prog" / "01-basics" / "leak.md", lesson("Leak", "see [[Acme Notes]] here"))
    assert run_check(wiki, tmp_path, root) == 1
    out = capsys.readouterr().out
    assert "leak.md:5 wikilink resolves to a private page" in out
    assert "Acme" not in out


@pytest.mark.parametrize("key", ["wiki", "concepts"])
def test_frontmatter_wiki_entry_naming_a_private_page_blocks(
    key: str, wiki: Path, root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write(
        root / "prog" / "01-basics" / "leak.md",
        f"---\ntitle: Leak\n{key}:\n  - hybrid-search\n  - acme-notes\n---\n\nbody\n",
    )
    assert run_check(wiki, tmp_path, root) == 1
    out = capsys.readouterr().out
    assert "leak.md:5 frontmatter wiki entry names a private page" in out
    assert "acme" not in out.lower()


def test_wiki_entries_for_public_pages_pass(wiki: Path, root: Path, tmp_path: Path) -> None:
    write(
        root / "prog" / "01-basics" / "ok.md",
        lesson("Ok", "[[Hybrid Search]]", wiki="[hybrid-search]"),
    )
    assert run_check(wiki, tmp_path, root) == 0


def test_public_page_of_the_same_name_wins(wiki: Path, root: Path, tmp_path: Path) -> None:
    write(wiki / "rag" / "acme-notes.md", PAGE.format(title="Acme Notes", body="Public twin."))
    write(root / "prog" / "01-basics" / "ok.md", lesson("Ok", "[[Acme Notes]]"))
    assert run_check(wiki, tmp_path, root) == 0


# ── Catalog ──────────────────────────────────────────────────────────────────


@pytest.fixture
def cat(root: Path, wiki: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> courses.Catalog:
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "v.npz")
    courses._load.cache_clear()
    sig = courses._signature(root, wiki)
    built = courses._load(root, wiki, sig)
    courses._load.cache_clear()
    return built


def test_catalog_marks_private_lessons_and_merges_them_into_their_course(
    cat: courses.Catalog,
) -> None:
    assert [c["id"] for c in cat.courses] == ["prog"]  # private/ is not a course
    prog = cat.courses[0]
    assert "private" not in prog  # it has public modules
    modules = {m["id"]: m for m in prog["modules"]}
    basics = modules["01-basics"]
    assert "private" not in basics  # mixed
    marked = {x["id"]: x.get("private", False) for x in basics["lessons"]}
    assert marked == {
        "prog/01-basics/intro": False,
        "prog/01-basics/next": False,
        "private/prog/01-basics/mine": True,
    }
    assert modules[SECRET_MODULE]["private"] is True  # only private lessons make it up
    assert cat.lessons["private/prog/01-basics/mine"].private is True
    assert cat.lessons["prog/01-basics/intro"].private is False


def test_private_only_course_is_marked(
    root: Path, wiki: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(root / "private" / "leetcode" / "arrays" / "p1.md", lesson("P1"))
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "v.npz")
    courses._load.cache_clear()
    built = courses._load(root, wiki, courses._signature(root, wiki))
    courses._load.cache_clear()
    leet = next(c for c in built.courses if c["id"] == "leetcode")
    assert leet["private"] is True


def test_public_lessons_never_neighbour_private_ones(
    cat: courses.Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(courses, "catalog", lambda: cat)
    nxt = courses.lesson_detail("prog/01-basics/next")
    assert nxt is not None and nxt["next"] is None
    mine = courses.lesson_detail("private/prog/01-basics/mine")
    assert mine is not None and mine["private"] is True
    assert mine["prev"]["id"] == "prog/01-basics/next"
    intro = courses.lesson_detail("prog/01-basics/intro")
    assert intro is not None and "private" not in intro


def test_curriculum_snapshot_leaves_private_lessons_out(
    cat: courses.Catalog, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for rec in cat.lessons.values():
        rec.concepts = ["hybrid-search"] if rec.private else []
    cat.wiki["hybrid-search"] = courses.WikiRef("hybrid-search", "Hybrid Search", "", "rag")
    built = curriculum._build(cat, [0, 0])
    text = str(built)
    assert SECRET_MODULE not in text and SECRET_LESSON not in text and "private" not in text
    assert built["primaryCourse"] == {}  # only a private lesson linked the page


def test_gap_list_names_nothing_private(
    wiki: Path, root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(
        root / "private" / "prog" / SECRET_MODULE / f"{SECRET_LESSON}.md",
        lesson("Two Sum", "[[Zq Missing Topic]]"),
    )
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "v.npz")
    courses._load.cache_clear()
    telemetry = tmp_path / "telemetry"
    rc = main(
        [
            "gaps",
            "--wiki-dir",
            str(wiki),
            "--telemetry-dir",
            str(telemetry),
            "--retrieval-log",
            str(tmp_path / "none.jsonl"),
            "--courses-dir",
            str(root),
            "--today",
            "2026-11-06",
        ]
    )
    courses._load.cache_clear()
    assert rc == 0
    text = (telemetry / "gaps.md").read_text().lower()
    assert "zq" not in text and "secret" not in text


# ── Retrieval corpus (MCP): same rule as the wiki ────────────────────────────


def test_corpus_never_indexes_or_serves_private_lessons(
    root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(corpus, "COURSES_DIR", root)
    names = {p.name for p in corpus.course_pages()}
    assert "intro.md" in names and "mine.md" not in names
    assert f"{SECRET_LESSON}.md" not in names
    assert corpus.course_pages(root / "private") == []
    assert corpus.is_private(root / "private" / "prog" / "01-basics" / "mine.md")
    assert not corpus.is_private(root / "prog" / "01-basics" / "intro.md")
    assert "course/private" not in corpus.course_domains()
    assert corpus.resolve_course_dir("course/private") is None


def test_read_page_treats_a_private_lesson_as_missing(
    root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from librarian.retrieval import pages

    monkeypatch.setattr(corpus, "COURSES_DIR", root)
    monkeypatch.setattr(corpus, "WIKI_DIR", root.parent / "wiki")
    assert "Page not found" in pages.read_page("course/private/prog/01-basics/mine")
    assert "Body." in pages.read_page("course/prog/01-basics/intro")
