"""Wiki skills follow the output contract: section order, description, literal templates.

Runs offline against SKILL.md and each skill's evals/format.json. Whether a model's real
output matches is a live check: feed it to the same `output_regex` list.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

SKILLS_DIR = Path(__file__).parents[2] / ".claude" / "skills"
CONTRACT_SKILLS = [
    "ingest",
    "query",
    "lint",
    "compact-wiki",
    "learn",
    "quiz",
    "gaps",
    "challenge",
    "wiki-weekly",
    "harness-audit",
    "evals-bootstrap",
    "wiki-graph",
    "write",
    "wiki-rename",
]
SECTIONS = ["Core rule", "Workflow", "Output format", "Calibration"]
FORMAT_FILES = sorted(SKILLS_DIR.glob("*/evals/format.json"))


def _split(skill: str) -> tuple[dict, str]:
    text = (SKILLS_DIR / skill / "SKILL.md").read_text()
    _, front, body = text.split("---\n", 2)
    return yaml.safe_load(front), body


def _h2_headings(body: str) -> list[str]:
    """Level-2 headings outside code fences; templates contain `##` lines of their own."""
    headings, fenced = [], False
    for line in body.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("## "):
            headings.append(line[3:].strip())
    return headings


@pytest.mark.parametrize("skill", CONTRACT_SKILLS)
def test_sections_in_contract_order(skill: str) -> None:
    _, body = _split(skill)
    assert _h2_headings(body) == SECTIONS


@pytest.mark.parametrize("skill", CONTRACT_SKILLS)
def test_description_ends_with_use_when_and_do_not_use(skill: str) -> None:
    front, _ = _split(skill)
    assert re.search(r"Use when .+ Do NOT use for [^.]+\.$", front["description"])
    assert len(front["description"]) <= 1024


@pytest.mark.parametrize("skill", CONTRACT_SKILLS)
def test_core_rule_is_one_sentence(skill: str) -> None:
    _, body = _split(skill)
    rule = body.split("## Core rule\n", 1)[1].split("\n## ", 1)[0].strip()
    assert "\n" not in rule
    assert len(re.findall(r"[.!?](?:\s|$)", rule)) == 1


@pytest.mark.parametrize("skill", CONTRACT_SKILLS)
def test_output_format_has_a_literal_template(skill: str) -> None:
    _, body = _split(skill)
    section = body.split("## Output format\n", 1)[1].split("\n## Calibration", 1)[0]
    assert "```" in section


def test_every_contract_skill_with_evals_has_format_cases() -> None:
    expected = {s for s in CONTRACT_SKILLS if (SKILLS_DIR / s / "evals").is_dir()}
    assert {p.parents[1].name for p in FORMAT_FILES} >= expected


@pytest.mark.parametrize("path", FORMAT_FILES, ids=lambda p: p.parents[1].name)
def test_skill_text_satisfies_format_file(path: Path) -> None:
    spec = json.loads(path.read_text())
    text = (path.parents[1] / "SKILL.md").read_text()
    for literal in spec["template_literals"] + spec["must_mention"]:
        assert literal in text, literal
    for absent in spec["must_not_mention"]:
        assert absent not in text, absent


@pytest.mark.parametrize("path", FORMAT_FILES, ids=lambda p: p.parents[1].name)
def test_output_regexes_tell_good_from_bad(path: Path) -> None:
    for case in json.loads(path.read_text())["output_cases"]:
        for pattern in case["output_regex"]:
            assert re.search(pattern, case["good"]), pattern
        assert not all(re.search(p, case["bad"]) for p in case["output_regex"])
