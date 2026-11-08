"""librarian.ingest.scrape_extractions — reading extractions become append-only raw sources."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from librarian.ingest import scrape_extractions as se


def _extraction(key: str, pdf: str, **extra: object) -> dict:
    return {
        "schema": 1,
        "key": key,
        "pdf": pdf,
        "bib": {"title": "A Paper", "authors": ["A", "B", "C", "D"], "year": 2024, "arxiv": key},
        "read": {"by": "source-reader", "at": "2026-11-08"},
        "type": "empirical",
        "question": "Does it work?",
        "results": [{"claim": "It scores 80%.", "kind": "measured", "setup": "on X"}],
        "terms": [{"term": "EGS", "definition": "gradient shrink"}],
        "lineage": [{"work": "GLM", "year": 2022, "arxiv": "2103.10360", "relation": "extends"}],
        **extra,
    }


def _sibling(tmp_path: Path, *extractions: dict) -> Path:
    folder = tmp_path / "lae" / se.EXTRACTIONS
    folder.mkdir(parents=True)
    for i, e in enumerate(extractions):
        (folder / f"{i}.json").write_text(json.dumps(e))
    return tmp_path / "lae"


def test_filename_uses_read_date_and_pdf() -> None:
    paper = _extraction("2210.02414", "generative-ai/01-x/sources/zeng-2022-glm-130b.pdf")
    assert se.filename(paper) == "2026-11-08-zeng-2022-glm-130b.md"
    chapter = _extraction("sha1:ab", "data-science/sources/islp/ch05-resampling.pdf")
    assert se.filename(chapter) == "2026-11-08-islp-ch05-resampling.md"


def test_render_has_frontmatter_and_sections() -> None:
    text = se.render(_extraction("2210.02414", "generative-ai/01-x/sources/zeng.pdf"))
    front = yaml.safe_load(text.split("---\n")[1])
    assert front["key"] == "2210.02414" and front["course_home"] == "generative-ai"
    assert front["extracted_from"] == "learn-ai-engineering/generative-ai/01-x/sources/zeng.pdf"
    assert "## Results\n\n- It scores 80%. Setup: on X" in text
    assert "**EGS**: gradient shrink" in text and "extends GLM, 2022 (arXiv:2103.10360)" in text
    assert "A, B, C et al." in text
    assert "## Limits" not in text  # empty fields leave no heading


def test_scrape_is_append_only_and_filters_by_home(tmp_path: Path) -> None:
    sibling = _sibling(
        tmp_path,
        _extraction("1", "generative-ai/01-x/sources/one.pdf"),
        _extraction("2", "data-science/sources/two.pdf"),
    )
    out = tmp_path / "raw"
    written = se.ExtractionsScraper(sibling, out, home="generative-ai").run()
    assert [p.name for p in written] == ["2026-11-08-one.md"]
    (out / "2026-11-08-one.md").write_text((out / "2026-11-08-one.md").read_text() + "kept\n")
    assert len(se.ExtractionsScraper(sibling, out).run()) == 1  # only the other home is new
    assert (out / "2026-11-08-one.md").read_text().endswith("kept\n")  # never rewritten


def test_same_pdf_name_in_two_homes_gets_two_files(tmp_path: Path) -> None:
    sibling = _sibling(
        tmp_path,
        _extraction("2305.13048", "generative-ai/01-x/sources/peng-2023-rwkv.pdf"),
        _extraction("https://doi.org/10.1/x", "ai-engineering/07-y/sources/peng-2023-rwkv.pdf"),
    )
    out = tmp_path / "raw"
    assert len(se.ExtractionsScraper(sibling, out).run()) == 2
    assert se.ExtractionsScraper(sibling, out).run() == []
