"""Presenter settings — replaces the missing core.config.agent_settings module.

Same reason as etl/researcher/_settings.py: tools/presenter/ was copied in from
another repo (commit 7a3a174) that had a core/ package; core/ has never existed
here, so every presenter entry point died at import. Defaults below are taken
from the call sites, which read these attributes and nothing else.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PresenterSettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    viz_model: str = Field(default="claude-opus-4-8")
    viz_audience: str = Field(default="engineering")
    viz_output_dir: Path = Field(default=Path("output") / "presenter")

    image_provider: str = Field(default="pollinations")
    image_width: int = Field(default=1280)
    image_height: int = Field(default=720)

    # Pollinations is the default provider: no credential required.
    pollinations_model: str = Field(default="flux")
    pollinations_seed: int | None = Field(default=None)
    pollinations_enhance: bool = Field(default=True)

    # Only needed when image_provider="replicate"; providers.py raises if unset.
    replicate_api_token: str | None = Field(default=None)


settings = PresenterSettings()
