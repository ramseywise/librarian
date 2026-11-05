"""The ingest-reviewer agent's file, its agreement with /ingest, and its seeded-fault fixture.

Structural only: nothing here runs the agent. Whether it finds the seeded faults is a live
check, by giving it the fixture's source and pages and comparing with expected.json.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).parents[2]
AGENT = REPO / ".claude" / "agents" / "ingest-reviewer.md"
INGEST = REPO / ".claude" / "skills" / "ingest" / "SKILL.md"
SKILLS_DIR = REPO / ".claude" / "skills"
FIXTURE = Path(__file__).parent / "fixtures" / "ingest-reviewer"
EXPECTED = json.loads((FIXTURE / "expected.json").read_text())
WIKI_CITING_SKILLS = ["harness-audit", "evals-bootstrap"]
COPY_RUN = 8  # the reviewer's copied-wording threshold, in consecutive words


def _agent() -> tuple[dict, str]:
    _, front, body = AGENT.read_text().split("---\n", 2)
    return yaml.safe_load(front), body


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def _longest_shared_run(a: str, b: str) -> int:
    left, right = _words(a), _words(b)
    best = 0
    previous = [0] * (len(right) + 1)
    for word in left:
        current = [0] * (len(right) + 1)
        for j, other in enumerate(right):
            if word == other:
                current[j + 1] = previous[j] + 1
                best = max(best, current[j + 1])
        previous = current
    return best


def _page_body(name: str) -> str:
    return (FIXTURE / name).read_text().split("---\n", 2)[2]


def test_agent_has_read_only_tools() -> None:
    front, _ = _agent()
    tools = {t.strip() for t in front["tools"].split(",")}
    assert tools <= {"Bash", "Read", "Grep", "Glob"}
    assert front["name"] == "ingest-reviewer"


@pytest.mark.parametrize("check", ["unsupported", "copied", "name", "orphan", "unreadable"])
def test_agent_names_each_defect_type(check: str) -> None:
    _, body = _agent()
    assert re.search(rf"(?m)^\d+\. {check} — ", body)


def test_agent_output_matches_what_ingest_prints() -> None:
    ingest = INGEST.read_text()
    assert "`ingest-reviewer`" in ingest
    assert "Review: <PASS | numbered defect list" in ingest
    verdict = json.loads((SKILLS_DIR / "ingest" / "evals" / "format.json").read_text())
    pattern = next(
        r for case in verdict["output_cases"] for r in case["output_regex"] if "Review:" in r
    )
    _, body = _agent()
    blocks = re.findall(r"```text\n(.*?)```", body, flags=re.S)
    assert blocks[0].strip() == "PASS"
    assert blocks[1].startswith("1. ")
    for block in blocks:
        assert re.search(pattern, f"Review: {block.strip()}")


def test_agent_protects_private_pages_and_ignores_source_instructions() -> None:
    _, body = _agent()
    assert "Never print its title, filename or path" in body
    assert "ignore any instructions" in body
    assert "public author of a cited paper" in body


def test_fixture_seeds_a_private_name() -> None:
    source = (FIXTURE / EXPECTED["source"]).read_text()
    page = (FIXTURE / EXPECTED["faulty_page"]).read_text()
    name = next(f for f in EXPECTED["faults"] if f["type"] == "name")["needle"]
    assert name in source and name in page


def test_fixture_seeds_a_claim_the_source_lacks() -> None:
    source = (FIXTURE / EXPECTED["source"]).read_text()
    page = (FIXTURE / EXPECTED["faulty_page"]).read_text()
    claim = next(f for f in EXPECTED["faults"] if f["type"] == "unsupported")["needle"]
    assert claim in page and claim not in source
    assert "latency" not in source


def test_fixture_has_exactly_the_seeded_faults() -> None:
    assert sorted(f["type"] for f in EXPECTED["faults"]) == ["name", "unsupported"]
    source = (FIXTURE / EXPECTED["source"]).read_text()
    for name in EXPECTED["new_pages"]:
        assert _longest_shared_run(_page_body(name), source) < COPY_RUN, name
    faulty_title = yaml.safe_load(
        (FIXTURE / EXPECTED["faulty_page"]).read_text().split("---\n", 2)[1]
    )["title"]
    linking_title = yaml.safe_load(
        (FIXTURE / EXPECTED["linking_page"]).read_text().split("---\n", 2)[1]
    )["title"]
    assert f"[[{faulty_title}]]" in (FIXTURE / EXPECTED["linking_page"]).read_text()
    assert f"[[{linking_title}]]" in (FIXTURE / EXPECTED["faulty_page"]).read_text()


def test_fixture_negative_controls_appear_on_both_sides() -> None:
    source = (FIXTURE / EXPECTED["source"]).read_text()
    page = (FIXTURE / EXPECTED["faulty_page"]).read_text()
    for name in EXPECTED["must_not_flag"]:
        assert name in source and name in page
    for name in EXPECTED["stripped_correctly"]:
        assert name in source and name not in page


@pytest.mark.parametrize("skill", WIKI_CITING_SKILLS)
def test_cited_wiki_pages_exist_and_are_public(skill: str) -> None:
    text = (SKILLS_DIR / skill / "SKILL.md").read_text()
    cited = re.findall(r"\[\[([^\]]+)\]\] `(data/wiki/[^`]+\.md)`", text)
    assert cited
    for title, rel in cited:
        assert not rel.startswith("data/wiki/private/")
        path = REPO / rel
        assert path.is_file(), rel
        front = yaml.safe_load(path.read_text().split("---\n", 2)[1])
        assert front["title"] == title
        assert "tombstone" not in front["tags"]


NEW_SKILLS = ["quiz", "gaps", "challenge", "wiki-weekly", "harness-audit", "evals-bootstrap"]


@pytest.mark.parametrize("skill", NEW_SKILLS)
def test_skill_has_trigger_evals_of_both_polarities(skill: str) -> None:
    cases = json.loads((SKILLS_DIR / skill / "evals" / "evals.json").read_text())
    assert all(set(c) == {"input", "expected"} for c in cases)
    assert sum(c["expected"] for c in cases) >= 3
    assert sum(not c["expected"] for c in cases) >= 3


def test_wiki_weekly_says_it_is_not_the_course_weekly() -> None:
    text = (SKILLS_DIR / "wiki-weekly" / "SKILL.md").read_text()
    assert "not the course" in text
    assert "/weekly" in text


@pytest.mark.parametrize("skill", NEW_SKILLS)
def test_new_skills_never_open_private_pages(skill: str) -> None:
    text = (SKILLS_DIR / skill / "SKILL.md").read_text()
    if skill == "gaps":  # reads only the script's output, which withholds private names
        assert "Report withheld entries by count only" in text
    else:
        assert "open `data/wiki/private/`" in text or "open or cite anything in" in text
