"""The Python port of `drillPromptSpeech`, on invented drills and on the real catalog if present."""

from __future__ import annotations

import pytest
from voice_fakes import DRILL_BODY, REFERENCE_QUOTE

from librarian.courses import catalog as courses
from librarian.voice.drill_prompt import drill_prompt, to_speech, visible_text

SOLUTION = "\n\n## Solution\n\nThe answer.\n"


def test_a_recognised_drill_gives_up_its_prompt_only() -> None:
    result = drill_prompt(DRILL_BODY)
    assert result.ok
    assert "row of lanterns" in result.text
    assert "tally" not in result.text
    assert "Walk the row" not in result.text
    assert REFERENCE_QUOTE in result.withheld


@pytest.mark.parametrize(
    "body, reason",
    [
        ("# Title\n\nJust text.\n", "no Prompt section"),
        (f"## Prompt\n\nA.\n\n## Prompt\n\nB.{SOLUTION}", "more than one Prompt"),
        ("## Prompt\n\nNothing after this.\n", "where its Prompt section ends"),
        (
            f"<details><summary>Early</summary>x</details>\n\n## Prompt\n\nA.{SOLUTION}",
            "collapsed block before",
        ),
        (f"## Prompt\n\nA.\n\n<details>x</details>{SOLUTION}", "collapsed or marked"),
        (f"## Prompt\n\nAnswer: forty two.{SOLUTION}", "contain an answer"),
        (f"## Prompt\n\nHint: try a loop.{SOLUTION}", "contain an answer"),
        ("## Prompt\n\nA.\n\n## Afterwards\n\nIt is 42.\n", "not marked"),
        ("## Prompt\n\nA.\n\n## Hints\n\nOnly hints here.\n", "not marked"),
        (f"## Prompt\n\n```python\nx = 1\n```\n\n```text\ny\n```\n{SOLUTION}", None),
    ],
)
def test_anything_not_understood_is_refused_with_its_reason(body: str, reason: str | None) -> None:
    result = drill_prompt(body)
    if reason is None:
        assert result.ok
        assert "x = 1" not in result.text
    else:
        assert not result.ok
        assert not result.text
        assert reason in result.reason


def test_a_heading_inside_a_code_fence_is_not_structure() -> None:
    body = f"## Prompt\n\nA.\n\n```md\n## Prompt\n```\n{SOLUTION}"
    assert drill_prompt(body).ok


def test_speech_has_no_markup_left() -> None:
    spoken = to_speech("# Head\n\n**Bold** and `code_name` and [a link](http://x.test).\n\n- item")
    assert "*" not in spoken
    assert "http" not in spoken
    assert "code name" in spoken


def test_visible_text_drops_collapsed_blocks_and_answer_sections() -> None:
    body = "Intro line.\n\n<details>hidden</details>\n\n## Answer\n\nSecret.\n\n## Next\n\nShown.\n"
    seen = visible_text(body)
    assert "Intro line" in seen
    assert "Shown" in seen
    assert "hidden" not in seen
    assert "Secret" not in seen


def test_every_real_drill_passes_or_says_why() -> None:
    """Skips without a learn-ai-engineering checkout. Coverage is 102 of 102 at the time of writing,
    and a new drill in a new shape refuses the mode: it must not leak, so no count is pinned."""
    drills = [r for r in courses.catalog().lessons.values() if r.kind == "drill"]
    if not drills:
        pytest.skip("no course catalog on this machine")
    for rec in drills:
        result = drill_prompt(rec.body)
        assert result.ok or result.reason, rec.id
        assert "<details" not in result.text, rec.id
        assert "```" not in result.text, rec.id
        assert not result.ok or result.withheld, rec.id
