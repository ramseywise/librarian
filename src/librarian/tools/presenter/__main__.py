from __future__ import annotations

import argparse
import sys

import structlog
from rich.console import Console
from rich.prompt import IntPrompt, Prompt

from librarian.log_config import configure_logging
from librarian.tools.presenter._settings import settings

console = Console()
log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Deck workflow
# ---------------------------------------------------------------------------


def run_deck(dry_run: bool = False) -> None:
    from librarian.tools.presenter import pipeline
    from librarian.tools.presenter.intake import collect_deck_intake
    from librarian.tools.presenter.outline import approval_checkpoint, generate_outline
    from librarian.tools.presenter.slide_writer import generate_slide_content

    model = settings.viz_model

    # 1. Intake
    intake = collect_deck_intake()

    # 2. Outline + approval checkpoint
    console.print("\n[bold yellow]Generating outline…[/bold yellow]")
    outline = generate_outline(intake, model)
    outline = approval_checkpoint(outline, model, intake)

    # 3. Slide content
    console.print("\n[bold yellow]Writing slide content…[/bold yellow]")
    slides = generate_slide_content(outline, intake, model)

    if dry_run:
        console.print("\n[bold cyan]Dry run — skipping image fetch and render.[/bold cyan]")
        for slide in slides:
            console.print(
                f"\n[bold]{slide.slide_number}. {slide.headline}[/bold] ({slide.slide_type})"
            )
            for bullet in slide.body:
                console.print(f"  • {bullet}")
        return

    # 4-6. Image prompts, image fetch, then the deck spec rendered by build_deck.
    out_dir = settings.viz_output_dir / pipeline.slugify(outline.title)
    console.print("\n[bold yellow]Building images and rendering deck…[/bold yellow]")
    spec_path, out_path = pipeline.build_media_and_deck(outline, slides, intake, out_dir)
    console.print(f"\n[bold green]Done![/bold green] Spec [cyan]{spec_path}[/cyan]")
    console.print(f"Deck saved to [cyan]{out_path}[/cyan]")


# ---------------------------------------------------------------------------
# Image-only workflow
# ---------------------------------------------------------------------------


def run_image() -> None:
    from librarian.tools.presenter.image_fetcher import fetch_single_image
    from librarian.tools.presenter.intake import collect_image_intake
    from librarian.tools.presenter.viz_classifier import propose_image_concepts

    model = settings.viz_model
    images_dir = settings.viz_output_dir / "images"
    img_w = settings.image_width
    img_h = settings.image_height

    # 1. Intake
    intake = collect_image_intake()

    # 2. Propose concepts
    console.print("\n[bold yellow]Generating image concepts…[/bold yellow]")
    concepts = propose_image_concepts(
        goal=intake.goal,
        description=intake.description,
        audience=intake.audience,
        tone=intake.tone,
        model=model,
        n=3,
        img_width=img_w,
        img_height=img_h,
    )

    # 3. Display concepts and let user pick
    console.print()
    for i, c in enumerate(concepts, 1):
        console.print(f"[bold cyan][{i}][/bold cyan] [bold]{c.label}[/bold] ({c.viz_type})")
        console.print(f"    {c.description}")
        console.print(f"    [dim]Why: {c.rationale}[/dim]")
        console.print()

    while True:
        choice = IntPrompt.ask(
            "Pick a concept", choices=[str(i) for i in range(1, len(concepts) + 1)]
        )
        selected = concepts[choice - 1]

        confirm = Prompt.ask(
            f"Generate [bold]{selected.label}[/bold]? Or [bold]revise[/bold] the prompt first",
            choices=["generate", "revise"],
            default="generate",
        )

        if confirm == "revise":
            revision = Prompt.ask("Describe what to change")
            # Re-propose with the revision appended to description
            updated_description = f"{intake.description}. Revision: {revision}"
            concepts = propose_image_concepts(
                goal=intake.goal,
                description=updated_description,
                audience=intake.audience,
                tone=intake.tone,
                model=model,
                n=3,
                img_width=img_w,
                img_height=img_h,
            )
            console.print()
            for i, c in enumerate(concepts, 1):
                console.print(f"[bold cyan][{i}][/bold cyan] [bold]{c.label}[/bold] ({c.viz_type})")
                console.print(f"    {c.description}")
                console.print(f"    [dim]Why: {c.rationale}[/dim]")
                console.print()
            continue

        break

    if not selected.filled_prompt:
        console.print(
            "[red]Selected concept has no image prompt — it may be a skip_image type.[/red]"
        )
        sys.exit(1)

    # 4. Fetch
    import re

    filename_slug = re.sub(r"[^\w]+", "_", selected.label.lower()).strip("_")[:40]
    filename = f"{filename_slug}.png"

    console.print("\n[bold yellow]Fetching image…[/bold yellow]")
    out_path = fetch_single_image(selected.filled_prompt, images_dir, filename)

    console.print(f"\n[bold green]Done![/bold green] Image saved to [cyan]{out_path}[/cyan]")

    # Revision loop — offer another round
    while True:
        again = Prompt.ask("Generate another variation?", choices=["yes", "no"], default="no")
        if again == "no":
            break

        revision = Prompt.ask("What should change?")
        updated_description = f"{intake.description}. Revision: {revision}"
        new_concepts = propose_image_concepts(
            goal=intake.goal,
            description=updated_description,
            audience=intake.audience,
            tone=intake.tone,
            model=model,
            n=1,
            img_width=img_w,
            img_height=img_h,
        )
        if new_concepts and new_concepts[0].filled_prompt:
            slug = re.sub(r"[^\w]+", "_", new_concepts[0].label.lower()).strip("_")[:40]
            out_path = fetch_single_image(
                new_concepts[0].filled_prompt, images_dir, f"{slug}_v2.png"
            )
            console.print(f"[bold green]Saved:[/bold green] [cyan]{out_path}[/cyan]")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    configure_logging()

    parser = argparse.ArgumentParser(description="Presentation authoring agent")
    parser.add_argument(
        "--image-only",
        action="store_true",
        help="Run in image-only mode (no deck generation)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate outline and slide content only — skip image fetch and render",
    )
    parser.add_argument(
        "--provider",
        choices=["pollinations", "replicate"],
        help="Override the image provider from settings",
    )
    args = parser.parse_args(argv)

    if args.provider:
        settings.image_provider = args.provider

    if args.image_only:
        run_image()
    else:
        run_deck(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
