"""Every wiki page's frontmatter must be valid YAML that parses to a mapping.

`grep "^summary:"` (what wiki-lint.sh checks) passes a line like
`summary: Gate: run evals first` that YAML rejects ("mapping values are not allowed
here"). python-frontmatter then raises on that page and the graph builder, MCP index
and relinker drop it — or crash. Unquoted colons in summary/title are the usual cause.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
WIKI = REPO / "data" / "wiki"
FM = re.compile(r"\A---\n(.*?)\n---", re.S)
PAGES = sorted(p for p in WIKI.rglob("*.md") if not p.name.startswith("_"))


@pytest.mark.parametrize("page", PAGES, ids=lambda p: str(p.relative_to(WIKI)))
def test_frontmatter_is_valid_yaml_mapping(page: Path) -> None:
    m = FM.match(page.read_text())
    assert m, "missing --- frontmatter block"
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        pytest.fail(f"invalid YAML (quote values containing ': '): {exc}")
    assert isinstance(data, dict), "frontmatter is not a key: value mapping"
