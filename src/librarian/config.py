"""One settings object: the repo root, every path derived from it, model names.

Every module that used to compute `Path(__file__).parent.parent...` reads its location
from `get_settings()` instead, so moving a file never changes where `data/` is.

The root is, in order: `$LIBRARIAN_ROOT`, else the nearest ancestor of this package that
holds a `pyproject.toml` (a source checkout or an editable install), else the nearest
ancestor of the working directory that does. An installed wheel run outside a checkout must
set `LIBRARIAN_ROOT`.

Existing environment variable names keep working (`WIKI_DIR`, `COURSES_DIR`, `WIKI_DB_PATH`,
`SISYPHUS_DIR`, `LIBRARIAN_EMBEDDING_MODEL`, `ANTHROPIC_MODEL`, ...). Defaults are the
locations the repo used before the move: index and cache files at the root, logs in `logs/`.
Tests that need other locations keep monkeypatching the module-level names each module
assigns from here; `get_settings.cache_clear()` rebuilds the object after an env change.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _walk_up_to_pyproject(start: Path) -> Path | None:
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    return None


def discover_root() -> Path:
    """The repo root: `$LIBRARIAN_ROOT`, else a pyproject.toml above the package, else above cwd."""
    env = os.environ.get("LIBRARIAN_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    found = _walk_up_to_pyproject(Path(__file__).resolve().parent) or _walk_up_to_pyproject(
        Path.cwd().resolve()
    )
    if found is None:
        raise RuntimeError(
            "Cannot locate the librarian repo: set LIBRARIAN_ROOT to the checkout "
            "(the directory holding pyproject.toml and data/)."
        )
    return found


def _env(*names: str) -> AliasChoices:
    return AliasChoices(*names)


class Settings(BaseSettings):
    """Paths, model names and endpoints. Paths default to locations under `root`."""

    model_config = SettingsConfigDict(
        env_file=str(discover_root() / ".env"),
        extra="ignore",
        populate_by_name=True,
    )

    root: Path = Field(default_factory=discover_root, validation_alias=_env("LIBRARIAN_ROOT"))

    # Content. WIKI_DIR / COURSES_DIR override the defaults, as they did for the MCP server.
    override_wiki_dir: Path | None = Field(default=None, validation_alias=_env("WIKI_DIR"))
    override_courses_dir: Path | None = Field(default=None, validation_alias=_env("COURSES_DIR"))
    # Index and caches. Still at the repo root; moving them under var/ is a later phase.
    override_wiki_db_path: Path | None = Field(default=None, validation_alias=_env("WIKI_DB_PATH"))
    override_embeddings_cache_path: Path | None = Field(
        default=None, validation_alias=_env("EMBEDDINGS_CACHE_PATH")
    )
    override_code_index_path: Path | None = Field(
        default=None, validation_alias=_env("CODE_INDEX_PATH")
    )
    override_logs_dir: Path | None = Field(
        default=None, validation_alias=_env("LIBRARIAN_LOGS_DIR")
    )
    # The private sisyphus checkout, read live for drill attempts.
    override_sisyphus_dir: Path | None = Field(default=None, validation_alias=_env("SISYPHUS_DIR"))

    # Models and endpoints.
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2", validation_alias=_env("LIBRARIAN_EMBEDDING_MODEL")
    )
    anthropic_model: str = Field(
        default="claude-opus-5-5", validation_alias=_env("ANTHROPIC_MODEL")
    )
    anthropic_api_key: str = Field(default="", validation_alias=_env("ANTHROPIC_API_KEY"))
    codemap_api_url: str = Field(
        default="http://localhost:8100", validation_alias=_env("CODEMAP_API_URL")
    )
    skip_warmup: bool = Field(default=False, validation_alias=_env("LIBRARIAN_SKIP_WARMUP"))

    # ── derived locations ────────────────────────────────────────────────────

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def wiki_dir(self) -> Path:
        return self.override_wiki_dir or self.data_dir / "wiki"

    @property
    def private_dir(self) -> Path:
        return self.wiki_dir / "private"

    @property
    def courses_dir(self) -> Path:
        return self.override_courses_dir or self.data_dir / "courses"

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def manifest_path(self) -> Path:
        return self.raw_dir / "manifest.jsonl"

    @property
    def telemetry_dir(self) -> Path:
        return self.data_dir / "telemetry"

    @property
    def metrics_file(self) -> Path:
        return self.telemetry_dir / "metrics.jsonl"

    @property
    def glossary_file(self) -> Path:
        return self.data_dir / "glossary.yaml"

    @property
    def logs_dir(self) -> Path:
        return self.override_logs_dir or self.root / "logs"

    @property
    def retrieval_log(self) -> Path:
        return self.logs_dir / "retrieval.jsonl"

    @property
    def flashcard_log(self) -> Path:
        return self.logs_dir / "flashcards.jsonl"

    @property
    def wiki_db_path(self) -> Path:
        return self.override_wiki_db_path or self.root / ".wiki_index.duckdb"

    @property
    def embeddings_cache_path(self) -> Path:
        return self.override_embeddings_cache_path or self.root / ".embeddings_cache.duckdb"

    @property
    def code_index_path(self) -> Path:
        return self.override_code_index_path or self.root / ".code_index.duckdb"

    @property
    def cache_dir(self) -> Path:
        return self.root / ".cache"

    @property
    def lesson_vec_cache(self) -> Path:
        return self.cache_dir / "lesson_embeddings.npz"

    @property
    def curriculum_snapshot(self) -> Path:
        return self.cache_dir / "curriculum.json"

    @property
    def sisyphus_dir(self) -> Path:
        return self.override_sisyphus_dir or self.root.parent / "sisyphus"

    @property
    def drill_log(self) -> Path:
        return self.sisyphus_dir / "drills" / "coding" / "drill-log.md"

    @property
    def dotenv_file(self) -> Path:
        return self.root / ".env"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
