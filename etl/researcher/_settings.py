"""Researcher settings — replaces the missing core.config.agent_settings module."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ResearcherSettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    obsidian_vault: Path = Field(default=Path.home() / "Obsidian")
    dropbox_pdf_path: Path = Field(default=Path.home() / "Dropbox" / "research-pdfs")
    gemini_model: str = Field(default="gemini-2.0-flash")


settings = ResearcherSettings()


def load_project_context() -> str:
    """Return project context markdown if .claude/docs/context.md exists."""
    context_path = (
        Path(__file__).resolve().parent.parent.parent / ".claude" / "docs" / "context.md"
    )
    if context_path.exists():
        return context_path.read_text(encoding="utf-8")
    return ""
