from __future__ import annotations

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from core.client import create_client, parse_json_response
from agents.presenter.models import DeckIntake, DeckOutline

console = Console()

OUTLINE_SYSTEM = """You are a presentation strategist. Given a goal, audience, and tone,
produce a concise narrative arc for a slide deck. Output a JSON object with:
- "title": deck title
- "slides": list of objects, each with:
  - "number": int
  - "title": slide title
  - "type": one of architecture|concept|narrative|data|code_demo|team
  - "talking_points": list of 2-3 short strings
  - "speaker_note": one sentence of intent

Keep decks to 8-12 slides. Lead with context, end with a clear call to action."""


def generate_outline(intake: DeckIntake, model: str) -> DeckOutline:
    client = create_client()

    context_block = ""
    if intake.codebase_summary:
        context_block = f"\n\nCodebase context:\n{intake.codebase_summary}"

    user_msg = (
        f"Goal: {intake.goal}\n"
        f"Audience: {intake.audience}\n"
        f"Tone: {intake.tone}"
        f"{context_block}"
    )

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=OUTLINE_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )

    data = parse_json_response(client, response.content[0].text, model, OUTLINE_SYSTEM)
    return DeckOutline(**data)


def _print_outline(outline: DeckOutline) -> None:
    console.print(f"\n[bold cyan]{outline.title}[/bold cyan]\n")
    table = Table(
        show_header=True, header_style="bold magenta", box=None, pad_edge=False
    )
    table.add_column("#", style="dim", width=3)
    table.add_column("Title", min_width=28)
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Key points", min_width=40)

    for slide in outline.slides:
        points = " · ".join(slide.talking_points)
        table.add_row(str(slide.number), slide.title, slide.type, points)

    console.print(table)
    console.print()


def approval_checkpoint(
    outline: DeckOutline, model: str, intake: DeckIntake
) -> DeckOutline:
    """Print outline and loop until user approves."""
    while True:
        _print_outline(outline)
        choice = Prompt.ask(
            "Review the outline above",
            choices=["approve", "edit", "restart"],
            default="approve",
        )

        if choice == "approve":
            return outline

        if choice == "restart":
            console.print("[yellow]Restarting outline generation…[/yellow]")
            outline = generate_outline(intake, model)
            continue

        # edit: ask for freeform instruction, regenerate with it
        instruction = Prompt.ask("What should change?")
        outline = _apply_edit(outline, instruction, model, intake)


def _apply_edit(
    outline: DeckOutline, instruction: str, model: str, intake: DeckIntake
) -> DeckOutline:
    client = create_client()

    user_msg = (
        f"Here is the current outline:\n{outline.model_dump_json(indent=2)}\n\n"
        f"Apply this change: {instruction}\n\n"
        f"Return the full updated outline as JSON matching the original schema."
    )

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=OUTLINE_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )

    data = parse_json_response(client, response.content[0].text, model, OUTLINE_SYSTEM)
    return DeckOutline(**data)
