"""presenter -> deck spec -> build_deck, with a fake Claude client and a fake image provider.

No network: the client and provider are injected, and `--dry-run` must not touch either.
Needs python-pptx and pillow (the `presenter` extra); skips without them.
"""

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

pytest.importorskip("pptx")
pytest.importorskip("PIL")

from pptx import Presentation

from librarian.tools.presenter import pipeline
from librarian.tools.presenter.models import (
    DeckIntake,
    DeckOutline,
    SlideContent,
    SlideOutline,
)
from librarian.tools.presenter.outline import OUTLINE_SYSTEM
from librarian.tools.presenter.slide_writer import SLIDE_SYSTEM
from librarian.tools.presenter.viz_classifier import PROMPT_SYSTEM, SCENE_SYSTEM
from librarian.tools.slides import build_deck as bd
from librarian.tools.slides import deck_stamp

TYPES = ["narrative", "concept", "architecture", "data", "code_demo", "team"]
BODIES = {
    "narrative": ["One sentence thesis"],
    "concept": ["First idea", "Second idea", "Third idea"],
    "architecture": ["Ingest", "Index", "Retrieve", "Answer"],
    "data": ["Latency: 40 ms", "Cost: 3 cents"],
    "code_demo": ["Create the client", "Send the brief", "Read the deck"],
    "team": ["Ada: owner", "Lin: reviewer"],
}


def outline() -> DeckOutline:
    return DeckOutline(
        title="Agent Design Review",
        slides=[
            SlideOutline(
                number=i + 1,
                title=f"Slide {i + 1}",
                type=t,
                talking_points=["a", "b"],
                speaker_note="intent",
            )
            for i, t in enumerate(TYPES)
        ],
    )


def contents(with_brief: bool = True) -> list[SlideContent]:
    return [
        SlideContent(
            slide_number=i + 1,
            slide_type=t,
            headline=f"Headline {i + 1}",
            body=BODIES[t],
            speaker_note=f"Say {i + 1}",
            image_brief="a diagram" if with_brief and t in ("concept", "narrative") else None,
        )
        for i, t in enumerate(TYPES)
    ]


INTAKE = DeckIntake(goal="Explain the design", audience="engineers", tone="plain")


class FakeClient:
    """Answers each presenter prompt by its system prompt; counts calls."""

    def __init__(self) -> None:
        self.calls = 0
        self.messages = self

    def create(self, **kw: Any) -> Any:
        self.calls += 1
        system, user = kw["system"], kw["messages"][0]["content"]
        if system == OUTLINE_SYSTEM:
            reply: Any = outline().model_dump()
        elif system == SLIDE_SYSTEM:
            n = int(user.split("Slide ", 1)[1].split(":", 1)[0])
            c = contents()[n - 1]
            reply = {
                "headline": c.headline,
                "body": c.body,
                "speaker_note": c.speaker_note,
                "image_brief": c.image_brief,
            }
        elif system == SCENE_SYSTEM:
            reply = {"scene": "s", "key_elements": ["k"], "mood": "m", "color_palette": ["blue"]}
        elif system == PROMPT_SYSTEM:
            reply = {}
        else:
            raise AssertionError("unexpected system prompt")
        block = type("B", (), {"text": json.dumps(reply)})()
        return type("R", (), {"content": [block]})()


class FakeProvider:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate_image(self, prompt: str, dest: Path, width: int, height: int) -> Path:
        from PIL import Image

        self.prompts.append(prompt)
        dest.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (160, 90), "navy").save(dest, "PNG")
        return dest


def layouts(spec: dict) -> dict[str, str]:
    return {s["title"]: s["layout"] for s in spec["parts"][0]["slides"]}


def test_compose_maps_every_slide_type() -> None:
    spec = pipeline.compose_spec(outline(), contents(), INTAKE)
    assert list(layouts(spec).values()) == [
        "statement",
        "bullets",
        "flow",
        "cards",
        "steps",
        "cards",
    ]
    slides = spec["parts"][0]["slides"]
    assert slides[5]["cards"] == [
        {"title": "Ada", "body": "owner"},
        {"title": "Lin", "body": "reviewer"},
    ]
    assert slides[0]["notes"] == "Say 1"
    assert spec["deck"]["output"] == "agent_design_review.pptx"


def test_image_slides_use_the_image_layout() -> None:
    spec = pipeline.compose_spec(outline(), contents(), INTAKE, {2: "assets/x.png"})
    slide = spec["parts"][0]["slides"][1]
    assert slide["layout"] == "image" and slide["image"] == "assets/x.png"
    assert slide["bullets"] == BODIES["concept"]


def test_spec_builds_and_passes_deck_checks(tmp_path: Path) -> None:
    client, provider = FakeClient(), FakeProvider()
    spec_path, pptx = pipeline.build_media_and_deck(
        outline(), contents(), INTAKE, tmp_path, client=client, provider=provider
    )
    spec = yaml.safe_load(spec_path.read_text())
    bd.check_keys(spec["parts"])
    assert set(layouts(spec).values()) <= set(bd.LAYOUTS)
    assert spec_path == tmp_path / "deck.yaml"
    assert pptx == deck_stamp.pptx_for(spec_path)
    assert deck_stamp.state(spec_path) == "current"
    assert len(Presentation(str(pptx)).slides) == 1 + len(TYPES)
    # images were generated into the spec's own assets dir and resolve from it
    images = [s["image"] for s in spec["parts"][0]["slides"] if s["layout"] == "image"]
    assert len(images) == 2 and len(provider.prompts) == 2
    assert all((tmp_path / i).is_file() for i in images)
    assert not [w for w in bd.WARNINGS if "image not found" in w or "overflow" in w]


def test_no_images_skips_the_viz_calls(tmp_path: Path) -> None:
    client, provider = FakeClient(), FakeProvider()
    spec_path, _ = pipeline.build_media_and_deck(
        outline(), contents(), INTAKE, tmp_path, images=False, client=client, provider=provider
    )
    assert client.calls == 0 and provider.prompts == []
    assert "image" not in {
        s["layout"] for s in yaml.safe_load(spec_path.read_text())["parts"][0]["slides"]
    }


def test_present_end_to_end_with_fakes(tmp_path: Path) -> None:
    client, provider = FakeClient(), FakeProvider()
    code = pipeline.present(
        "Explain the design\nAudience: engineers",
        tmp_path,
        yes=True,
        client=client,
        provider=provider,
    )
    assert code == 0
    assert (tmp_path / "deck.yaml").is_file() and (tmp_path / "outline.json").is_file()
    assert client.calls == 1 + len(TYPES) + 2 * 2  # outline, slides, scene+prompt for 2 images


def test_without_yes_and_no_tty_it_stops_after_the_outline(tmp_path: Path) -> None:
    client = FakeClient()
    code = pipeline.present("Explain", tmp_path, client=client, interactive=False)
    assert code == 3 and client.calls == 1
    assert not (tmp_path / "deck.yaml").exists()


def test_dry_run_makes_no_client_calls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*a: object, **k: object) -> None:
        raise AssertionError("dry run reached the API")

    monkeypatch.setattr("librarian.tools.presenter._client.create_client", boom)
    monkeypatch.setattr("librarian.tools.presenter.providers.get_provider", boom)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    out = tmp_path / "deck"
    assert pipeline.main(["Explain the design", "--dry-run", "--out", str(out)]) == 0
    assert not out.exists()


def test_brief_file_fields(tmp_path: Path) -> None:
    brief = tmp_path / "brief.md"
    brief.write_text("Pitch the harness\nmore detail\nAudience: leads\nTone: blunt\n")
    intake = pipeline.parse_brief(str(brief))
    assert (intake.audience, intake.tone) == ("leads", "blunt")
    assert intake.goal == "Pitch the harness\nmore detail"
    with pytest.raises(ValueError):
        pipeline.parse_brief("Audience: x")


def test_cli_routes_present() -> None:
    from librarian import cli

    assert cli.main(["present", "Explain", "--dry-run"]) == 0
