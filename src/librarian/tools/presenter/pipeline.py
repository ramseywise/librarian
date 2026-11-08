"""Presenter pipeline: Claude writes the content, `build_deck` renders it.

The Claude-calling stages (outline, slide writing, viz classification, image generation) are
unchanged. This module is what they feed: it composes a deck spec in the schema
`librarian.tools.slides.build_deck` reads, writes it beside its output, and renders it there, so a
presenter deck gets the house style, the overflow fixes, previews and `make deck-check`.

Output directory layout (images are relative to the spec, as build_deck expects):

    <out>/deck.yaml    the spec (edit it and rebuild: `python -m librarian.tools.slides.build_deck <out>/deck.yaml`)
    <out>/assets/      generated images
    <out>/<slug>.pptx  the deck
    <out>/outline.json, brief.json   the approved outline and the brief it answers (reused by --yes)

Slide type mapping (presenter `SlideContent.slide_type` -> deck spec `layout`):

    any, with a generated image   -> image (image left, bullets right)
    architecture                  -> flow when 3-5 short bullets, else bullets
    concept                       -> bullets
    narrative                     -> statement when one bullet, else bullets
    data                          -> cards when 2-4 bullets, else bullets   (no table: bullets are prose)
    code_demo                     -> steps, 2-6 bullets, else bullets       (no code: bullets are prose)
    team                          -> cards, "Name: role" bullets split into title and body, else bullets
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import structlog
import yaml

from librarian.tools.presenter._settings import settings
from librarian.tools.presenter.models import DeckIntake, DeckOutline, SlideContent

log = structlog.get_logger(__name__)

MAX_SIDE_BULLETS = 6
SHORT_STEP = 40  # chars: a flow box label stays readable below this


def slugify(text: str, limit: int = 40) -> str:
    return re.sub(r"[^\w]+", "_", text.lower()).strip("_")[:limit] or "deck"


# --- brief -----------------------------------------------------------------


_FIELD = re.compile(r"^\s*(audience|tone|codebase)\s*:\s*(.+?)\s*$", re.I)


def parse_brief(arg: str) -> DeckIntake:
    """A brief file or inline text -> intake. `Audience:`, `Tone:` and `Codebase:` lines are fields; the rest is the goal."""
    path = Path(arg).expanduser()
    text = path.read_text(encoding="utf-8") if len(arg) < 4096 and path.is_file() else arg
    fields: dict[str, str] = {}
    goal_lines: list[str] = []
    for line in text.splitlines():
        match = _FIELD.match(line)
        if match and match.group(1).lower() not in fields:
            fields[match.group(1).lower()] = match.group(2)
        else:
            goal_lines.append(line)
    goal = "\n".join(goal_lines).strip()
    if not goal:
        raise ValueError("the brief has no goal text")
    codebase: str | None = None
    if "codebase" in fields:
        from librarian.tools.presenter.intake import _summarize_codebase

        root = Path(fields["codebase"]).expanduser()
        codebase = _summarize_codebase(root) if root.is_dir() else fields["codebase"]
    return DeckIntake(
        goal=goal,
        audience=fields.get("audience", settings.viz_audience),
        tone=fields.get("tone", "professional but approachable"),
        codebase_summary=codebase,
        use_template=False,
    )


# --- spec composition ------------------------------------------------------


def _short(items: list[str]) -> bool:
    return all(len(i) <= SHORT_STEP for i in items)


def _split_card(item: str) -> dict[str, str]:
    for sep in (": ", " - ", " — "):
        head, found, tail = item.partition(sep)
        if found and head and tail:
            return {"title": head, "body": tail}
    return {"title": item}


def slide_spec(slide: SlideContent, image: str | None) -> dict[str, Any]:
    """One presenter slide -> one deck-spec slide (see the module docstring for the mapping)."""
    body = list(slide.body)
    spec: dict[str, Any] = {"title": slide.headline}
    if image:
        spec.update(layout="image", image=image, bullets=body[:MAX_SIDE_BULLETS])
    elif slide.slide_type == "architecture" and 3 <= len(body) <= 5 and _short(body):
        spec.update(layout="flow", steps=body)
    elif slide.slide_type == "narrative" and len(body) == 1:
        spec.update(layout="statement", statement=body[0])
    elif slide.slide_type in ("data", "team") and 2 <= len(body) <= 4:
        cards = [_split_card(b) for b in body] if slide.slide_type == "team" else None
        spec.update(layout="cards", cards=cards or [{"title": b} for b in body])
    elif slide.slide_type == "code_demo" and 2 <= len(body) <= 6:
        spec.update(layout="steps", steps=[{"title": b} for b in body])
    else:
        spec.update(layout="bullets", bullets=body[:MAX_SIDE_BULLETS])
    if slide.speaker_note:
        spec["notes"] = slide.speaker_note
    return spec


def compose_spec(
    outline: DeckOutline,
    slides: list[SlideContent],
    intake: DeckIntake,
    images: dict[int, str] | None = None,
    output: str | None = None,
) -> dict[str, Any]:
    """The deck spec build_deck reads. `images` maps slide number to a path relative to the spec.

    One closing-style part (`agenda: false, divider: false`) holds every slide: a talk has no
    lecture spine, so the per-part story rules (takeaway, code, flow) do not apply to it.
    """
    images = images or {}
    return {
        "deck": {
            "title": outline.title,
            "subtitle": intake.goal.splitlines()[0][:120],
            "tagline": f"{intake.audience} · {intake.tone}",
            "reference": "librarian present",
            "output": output or f"{slugify(outline.title)}.pptx",
            "notes": intake.goal,
        },
        "parts": [
            {
                "title": outline.title,
                "agenda": False,
                "divider": False,
                "slides": [slide_spec(s, images.get(s.slide_number)) for s in slides],
            }
        ],
    }


def write_spec(spec: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "deck.yaml"
    path.write_text(
        yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8"
    )
    return path


def render(spec_path: Path) -> Path:
    """Render the spec through build_deck (needs python-pptx and pillow: the `presenter` extra)."""
    from librarian.tools.slides import build_deck

    build_deck.WARNINGS.clear()
    out = build_deck.build(spec_path)
    for warning in build_deck.WARNINGS:
        print(f"WARN {warning}", file=sys.stderr)
    return out


def build_media_and_deck(
    outline: DeckOutline,
    slides: list[SlideContent],
    intake: DeckIntake,
    out_dir: Path,
    *,
    images: bool = True,
    client: Any = None,  # noqa: ANN401 - anthropic.Anthropic or a test double
    provider: Any = None,  # noqa: ANN401 - an ImageProvider or a test double
) -> tuple[Path, Path]:
    """Classify slides, generate images into <out>/assets, write the spec, render it. Returns (spec, pptx)."""
    image_rel: dict[int, str] = {}
    if images:
        from librarian.tools.presenter.image_fetcher import fetch_images_for_slides
        from librarian.tools.presenter.viz_classifier import classify_slides

        style = (
            f"Deck title: {outline.title}\nAudience: {intake.audience}\nTone: {intake.tone}\n"
            "Maintain visual coherence: use a consistent color palette, recurring "
            "visual motifs, and unified style across all slides."
        )
        prompts = classify_slides(
            slides,
            settings.viz_model,
            style,
            settings.image_width,
            settings.image_height,
            client=client,
        )
        found = fetch_images_for_slides(
            prompts, out_dir / "assets", slugify(outline.title), provider=provider
        )
        image_rel = {n: p.relative_to(out_dir).as_posix() for n, p in found.items()}
    spec_path = write_spec(compose_spec(outline, slides, intake, image_rel), out_dir)
    return spec_path, render(spec_path)


# --- non-interactive entry -------------------------------------------------


def _brief_hash(intake: DeckIntake) -> str:
    return hashlib.sha256(intake.model_dump_json().encode()).hexdigest()


def plan(intake: DeckIntake, out_dir: Path, images: bool) -> list[str]:
    """What a run would do. Pure: no client, no network, no files."""
    return [
        f"brief: {intake.goal.splitlines()[0][:100]}",
        f"audience: {intake.audience}; tone: {intake.tone}",
        f"model: {settings.viz_model}; image provider: {settings.image_provider if images else 'off (--no-images)'}",
        "claude calls: 1 outline, then 1 per slide"
        + (", then 2 per slide with an image (scene, prompt)" if images else ""),
        f"writes: {out_dir}/deck.yaml, {out_dir}/<slug>.pptx"
        + (f", {out_dir}/assets/" if images else ""),
    ]


def present(
    brief: str,
    out_dir: Path | None = None,
    *,
    dry_run: bool = False,
    images: bool = True,
    yes: bool = False,
    client: Any = None,  # noqa: ANN401
    provider: Any = None,  # noqa: ANN401
    interactive: bool | None = None,
) -> int:
    """Brief -> outline -> approval -> slides -> images -> spec -> deck. Exit code for the CLI."""
    from rich.console import Console

    console = Console()
    intake = parse_brief(brief)
    out_dir = out_dir or settings.viz_output_dir / slugify(intake.goal.splitlines()[0])
    if dry_run:
        for line in plan(intake, out_dir, images):
            console.print(line, markup=False)
        console.print("dry run: no API calls made, nothing written", markup=False)
        return 0

    from librarian.tools.presenter.outline import (
        _print_outline,
        approval_checkpoint,
        generate_outline,
    )
    from librarian.tools.presenter.slide_writer import generate_slide_content

    out_dir.mkdir(parents=True, exist_ok=True)
    model = settings.viz_model
    outline_file, brief_file = out_dir / "outline.json", out_dir / "brief.json"
    digest = _brief_hash(intake)
    outline: DeckOutline | None = None
    if (
        yes
        and outline_file.is_file()
        and brief_file.is_file()
        and json.loads(brief_file.read_text())["sha"] == digest
    ):
        outline = DeckOutline.model_validate_json(outline_file.read_text())
        console.print(f"reusing the approved outline in {outline_file}", markup=False)
    if outline is None:
        outline = generate_outline(intake, model, client=client)
        outline_file.write_text(outline.model_dump_json(indent=2), encoding="utf-8")
        brief_file.write_text(json.dumps({"sha": digest}), encoding="utf-8")
        tty = sys.stdin.isatty() if interactive is None else interactive
        if not yes:
            if not tty:
                _print_outline(outline)
                console.print(
                    f"outline saved to {outline_file}; edit it if needed, then re-run with --yes",
                    markup=False,
                )
                return 3
            outline = approval_checkpoint(outline, model, intake)
            outline_file.write_text(outline.model_dump_json(indent=2), encoding="utf-8")

    slides = generate_slide_content(outline, intake, model, client=client)
    spec_path, pptx = build_media_and_deck(
        outline, slides, intake, out_dir, images=images, client=client, provider=provider
    )
    console.print(f"spec: {spec_path}\ndeck: {pptx}", markup=False)
    return 0


def main(argv: list[str] | None = None) -> int:
    import argparse

    from librarian.log_config import configure_logging

    ap = argparse.ArgumentParser(
        prog="librarian present",
        description="Brief -> outline -> slides -> images -> deck.yaml -> .pptx through build_deck.",
    )
    ap.add_argument("brief", help="a brief file, or the brief as text")
    ap.add_argument("--out", type=Path, help="output dir (default output/presenter/<slug>)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan; no API calls, no files")
    ap.add_argument("--no-images", action="store_true", help="skip image prompts and generation")
    ap.add_argument(
        "--yes",
        action="store_true",
        help="approve the outline without asking (reuses outline.json when the brief is unchanged)",
    )
    args = ap.parse_args(argv)
    configure_logging()
    try:
        return present(
            args.brief,
            args.out,
            dry_run=args.dry_run,
            images=not args.no_images,
            yes=args.yes,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"librarian present: {exc}", file=sys.stderr)
        return 1
