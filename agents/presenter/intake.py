from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt

from core.config.agent_settings import settings
from agents.presenter.models import DeckIntake, ImageIntake

console = Console()


def _summarize_codebase(path: Path) -> str:
    """Read top-level structure and any README from the given path."""
    lines: list[str] = []

    # Top-level entries
    entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
    lines.append(f"Root: {path.name}/")
    for entry in entries[:30]:  # cap to avoid prompt bloat
        prefix = "  " if entry.is_file() else "  [dir] "
        lines.append(f"{prefix}{entry.name}")

    # README content (first 100 lines)
    for readme_name in ("README.md", "README.rst", "README.txt", "README"):
        readme = path / readme_name
        if readme.exists():
            readme_lines = readme.read_text(errors="replace").splitlines()[:100]
            lines.append("\n--- README ---")
            lines.extend(readme_lines)
            break

    return "\n".join(lines)


def collect_deck_intake() -> DeckIntake:
    console.rule("[bold]Presentation Setup")

    goal = Prompt.ask("[bold]What is the goal of this presentation?")
    tone = Prompt.ask("Tone", default="professional but approachable")

    default_audience = settings.viz_audience
    use_default = Confirm.ask(
        f"Use default audience?\n  [dim]{default_audience}[/dim]", default=True
    )
    audience = default_audience if use_default else Prompt.ask("Audience")

    use_template = Confirm.ask("Use slide template?", default=True)

    codebase_summary: str | None = None
    has_codebase = Confirm.ask("Reference a codebase?", default=False)
    if has_codebase:
        raw = Prompt.ask("Path to codebase (or paste a short description)")
        path = Path(raw).expanduser()
        if path.exists() and path.is_dir():
            console.print(f"[dim]Reading {path}…[/dim]")
            codebase_summary = _summarize_codebase(path)
            console.print("[green]Codebase summarized.[/green]")
        else:
            codebase_summary = raw  # treat as freeform description

    return DeckIntake(
        goal=goal,
        audience=audience,
        tone=tone,
        codebase_summary=codebase_summary,
        use_template=use_template,
    )


def collect_image_intake() -> ImageIntake:
    console.rule("[bold]Image Generation Setup")

    goal = Prompt.ask("[bold]What is this image for?")
    description = Prompt.ask("Describe what you want to convey")
    tone = Prompt.ask("Tone / aesthetic", default="modern, clean, professional")

    default_audience = settings.viz_audience
    use_default = Confirm.ask(
        f"Use default audience?\n  [dim]{default_audience}[/dim]", default=True
    )
    audience = default_audience if use_default else Prompt.ask("Audience")

    return ImageIntake(
        goal=goal,
        description=description,
        audience=audience,
        tone=tone,
    )
