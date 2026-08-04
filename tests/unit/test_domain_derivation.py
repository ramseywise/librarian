"""Evidence for staff-review F4: the domain taxonomy is derived from disk, not a list.

The hardcoded DOMAINS list had drifted — 6 on-disk directories missing (context,
foundations, interview, prompting, ...) and DOMAIN_TAG_SET carried a phantom
deep-agents entry. Deriving from WIKI_DIR makes drift impossible: adding a
directory adds a domain.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.backend import wiki_parser
from app.mcp_server import server


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    wiki_dir = tmp_path / "wiki"
    for name in ("rag", "context", "private"):
        (wiki_dir / name).mkdir(parents=True)
    monkeypatch.setattr(server, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(wiki_parser, "WIKI_DIR", wiki_dir)
    return wiki_dir


def test_domains_match_on_disk_dirs(wiki: Path) -> None:
    assert server._domains() == ["context", "rag"]


def test_private_is_never_a_domain(wiki: Path) -> None:
    assert "private" not in server._domains()
    assert "private" not in wiki_parser._domain_tag_set()


def test_adding_a_directory_adds_a_domain(wiki: Path) -> None:
    (wiki / "interview").mkdir()
    assert server._domains() == ["context", "interview", "rag"]
    assert wiki_parser._domain_tag_set() == {"context", "interview", "rag"}


def test_missing_wiki_dir_yields_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    gone = tmp_path / "nope"
    monkeypatch.setattr(server, "WIKI_DIR", gone)
    monkeypatch.setattr(wiki_parser, "WIKI_DIR", gone)
    assert server._domains() == []
    assert wiki_parser._domain_tag_set() == set()


def test_real_wiki_dirs_are_all_domains() -> None:
    """Against the real repo: every on-disk domain dir is addressable (F4's bug was
    interview/context/etc. being unlisted)."""
    on_disk = sorted(
        d.name for d in server.WIKI_DIR.iterdir() if d.is_dir() and d.name != "private"
    )
    assert server._domains() == on_disk
    assert "interview" in on_disk  # the canonical missing-from-the-old-list example
