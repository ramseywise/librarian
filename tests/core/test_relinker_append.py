from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from core.relinker import append_see_also


def test_appends_under_real_heading(tmp_path: Path) -> None:
    page = tmp_path / "page.md"
    page.write_text("# Title\n\nBody.\n\n## See Also\n- [[Existing]]\n")

    append_see_also(page, "New Page")

    lines = page.read_text().splitlines()
    heading = lines.index("## See Also")
    assert lines[heading + 1] == "- [[New Page]] <!-- auto-linked -->"


def test_ignores_quoted_heading_in_inline_code(tmp_path: Path) -> None:
    page = tmp_path / "page.md"
    page.write_text(
        "# Title\n\n"
        "- `POST /api/writeback` -> insert wikilink in `## See Also` (endpoint exists)\n\n"
        "## See Also\n- [[Existing]]\n"
    )

    append_see_also(page, "New Page")

    content = page.read_text()
    # the prose line that quotes the heading must be untouched
    assert "insert wikilink in `## See Also` (endpoint exists)" in content
    lines = content.splitlines()
    heading = lines.index("## See Also")
    assert lines[heading + 1] == "- [[New Page]] <!-- auto-linked -->"


def test_creates_section_when_absent(tmp_path: Path) -> None:
    page = tmp_path / "page.md"
    page.write_text("# Title\n\nBody only.\n")

    append_see_also(page, "New Page")

    assert page.read_text().endswith("## See Also\n- [[New Page]] <!-- auto-linked -->\n")
