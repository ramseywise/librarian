from __future__ import annotations

from pathlib import Path

import pytest

from librarian.wiki.source_links import COURSE_REPO_BLOB, OriginResolver, resolve_origin


def _raw(raw: Path, rel: str, header: str) -> None:
    f = raw / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(f"---\n{header}\n---\n\nBody text.\n")


@pytest.fixture()
def dirs(tmp_path: Path) -> tuple[Path, Path]:
    raw = tmp_path / "raw"
    course = tmp_path / "course"
    pdf = course / "ai-engineering/02-context/sources/zhang-2026.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-1.4")
    _raw(
        raw,
        "papers/2026-11-02-zhang.md",
        "title: 'AutoCompact'\narxiv: '2610.02163'\n"
        "extracted_from: learn-ai-engineering/ai-engineering/02-context/sources/zhang-2026.pdf",
    )
    _raw(raw, "articles/a.md", "title: An article\nurl: https://example.com/post")
    _raw(raw, "articles/bad.md", "title: Bad\nurl: javascript:alert(1)")
    _raw(
        raw,
        "papers/moved.md",
        "title: Moved\nextracted_from: learn-ai-engineering/x/sources/gone.pdf",
    )
    _raw(
        raw,
        "papers/escape.md",
        "title: Escape\nextracted_from: learn-ai-engineering/../secret/sources/x.pdf",
    )
    _raw(raw, "sessions/2026-04-24.md", "title: A session\nurl: https://example.com/session")
    _raw(raw, "meetings/m.md", "title: Client meeting\nurl: https://example.com/m")
    return raw, course


def test_paper_gets_arxiv_and_course_pdf(dirs: tuple[Path, Path]) -> None:
    raw, course = dirs
    origin = resolve_origin("data/raw/papers/2026-11-02-zhang.md", raw, course)
    assert origin == {
        "title": "AutoCompact",
        "links": [
            {"kind": "arxiv", "href": "https://arxiv.org/abs/2610.02163"},
            {
                "kind": "pdf",
                "href": f"{COURSE_REPO_BLOB}/ai-engineering/02-context/sources/zhang-2026.pdf",
            },
        ],
    }


def test_article_gets_its_url_and_only_http(dirs: tuple[Path, Path]) -> None:
    raw, course = dirs
    assert resolve_origin("data/raw/articles/a.md", raw, course)["links"] == [
        {"kind": "web", "href": "https://example.com/post"}
    ]
    assert resolve_origin("data/raw/articles/bad.md", raw, course) is None


@pytest.mark.parametrize(
    "source",
    [
        "data/raw/sessions/2026-04-24.md",
        "data/raw/meetings/m.md",
        "data/raw/papers/../sessions/2026-04-24.md",
        "data/raw/papers/private/x.md",
        "data/raw/papers/missing.md",
        "evals/golden_multihop.json",
        "/etc/passwd",
    ],
)
def test_never_opens_sessions_meetings_or_paths_outside(
    dirs: tuple[Path, Path], source: str
) -> None:
    raw, course = dirs
    assert resolve_origin(source, raw, course) is None


def test_pdf_dropped_when_moved_or_escaping(dirs: tuple[Path, Path]) -> None:
    raw, course = dirs
    assert resolve_origin("data/raw/papers/moved.md", raw, course) is None
    assert resolve_origin("data/raw/papers/escape.md", raw, course) is None
    # Without the course repo checked out, the PDF link is trusted as written.
    moved = resolve_origin("data/raw/papers/moved.md", raw, None)
    assert moved and moved["links"][0]["href"].endswith("/x/sources/gone.pdf")


def test_resolver_counts_every_source_and_dedupes(dirs: tuple[Path, Path]) -> None:
    raw, course = dirs
    resolve = OriginResolver(raw, course)
    origins, count = resolve(
        [
            "data/raw/papers/2026-11-02-zhang.md",
            "data/raw/papers/2026-11-02-zhang.md",
            "data/raw/sessions/2026-04-24.md",
            "data/raw/articles/a.md",
        ]
    )
    assert count == 4
    assert [o["title"] for o in origins] == ["AutoCompact", "An article"]
    assert resolve(None) == ([], 0)
