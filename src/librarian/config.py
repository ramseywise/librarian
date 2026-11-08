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

from librarian.pricing import DEFAULT_CHAT_MODEL


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
    # One directory for everything the app writes (indexes, caches, logs, flashcard results).
    # Unset: the old locations (index files at the root, `logs/`, `.cache/`). A deployment sets
    # it to a volume so `data/` can be mounted read-only.
    override_state_dir: Path | None = Field(
        default=None, validation_alias=_env("LIBRARIAN_STATE_DIR")
    )
    # Index and caches. Each override below beats the state dir.
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
    # User state (attempts, chat spend): SQLAlchemy URL, e.g. postgresql://user:pw@host/db.
    # Unset: a SQLite file in the state dir (see `database_url_or_default`).
    database_url: str = Field(default="", validation_alias=_env("DATABASE_URL"))
    # The private sisyphus checkout, read live for drill attempts.
    override_sisyphus_dir: Path | None = Field(default=None, validation_alias=_env("SISYPHUS_DIR"))

    # The course sources repo (PDFs and book folders), read through the sources route and never
    # copied into data/. Default: the sibling learn-ai-engineering checkout.
    override_course_sources_dir: Path | None = Field(
        default=None, validation_alias=_env("COURSE_SOURCES_DIR")
    )
    # Local only: a deployment sets SERVE_COURSE_SOURCES=false and the route 404s.
    serve_course_sources: bool = Field(default=True, validation_alias=_env("SERVE_COURSE_SOURCES"))

    # Slides: the API serves prebuilt decks. Only a dev machine builds them on request
    # (`make api` turns this on); a deployment leaves it off and ships the built decks.
    dev_build_slides: bool = Field(
        default=False, validation_alias=_env("LIBRARIAN_DEV_BUILD_SLIDES")
    )
    # Dev only (`make api` turns it on): watch data/wiki, push graph updates over /ws and rebuild
    # the course catalog after an edit. Per process, so a deployment leaves it off.
    dev_watch: bool = Field(default=False, validation_alias=_env("LIBRARIAN_DEV_WATCH"))
    # Where a deployment's prebuilt content lives (`<dir>/slides/<module>/...`). Default: var/content/current.
    override_content_dir: Path | None = Field(
        default=None, validation_alias=_env("LIBRARIAN_CONTENT_DIR")
    )

    # Public mode (the deployed container): private/ trees are never read, indexed or served,
    # whatever is on disk. Local use leaves it off. The compose tmpfs masks are the second lock.
    public_mode: bool = Field(default=False, validation_alias=_env("LIBRARIAN_PUBLIC"))

    # API access. With no token the API is open (local dev); with one, every /api route and the
    # websocket require `Authorization: Bearer <token>`. /healthz and /readyz are always open.
    api_token: str = Field(default="", validation_alias=_env("LIBRARIAN_API_TOKEN"))
    # The admin that the bootstrap token and open mode act as (librarian.accounts). Other users
    # sign in with an `lk_` key from `librarian keys create`.
    owner_email: str = Field(
        default="owner@localhost", validation_alias=_env("LIBRARIAN_OWNER_EMAIL")
    )
    # Serve /docs, /redoc and /openapi.json (still behind the token when one is set).
    expose_docs: bool = Field(default=False, validation_alias=_env("LIBRARIAN_EXPOSE_DOCS"))
    # Comma-separated browser origins allowed by CORS. The Vite dev server by default.
    cors_origins: str = Field(
        default="http://localhost:5173", validation_alias=_env("LIBRARIAN_CORS_ORIGINS")
    )
    # The built web UI (`npm run build` in app), served by the API at "/" when it exists.
    override_web_dir: Path | None = Field(default=None, validation_alias=_env("LIBRARIAN_WEB_DIR"))
    # uvicorn worker processes for `librarian api` (the --workers default). Shared state is in
    # the database and the index file, so any number serve the same answers.
    api_workers: int = Field(default=1, ge=1, validation_alias=_env("LIBRARIAN_API_WORKERS"))
    # POST /api/chat/stream limits. The burst limit is per process (N workers allow N times as
    # many); the daily budget is read from the database, so it holds across workers. 0 turns a limit off.
    chat_rate_limit: int = Field(default=20, validation_alias=_env("LIBRARIAN_CHAT_RATE_LIMIT"))
    chat_rate_window_s: int = Field(
        default=60, validation_alias=_env("LIBRARIAN_CHAT_RATE_WINDOW_S")
    )
    # Off: the chat route answers 404 and the API key is not required at startup.
    chat_enabled: bool = Field(default=True, validation_alias=_env("LIBRARIAN_CHAT_ENABLED"))
    # Two daily caps: all users together, and each member (admins have only the global one).
    chat_daily_budget_usd: float = Field(
        default=5.0, validation_alias=_env("LIBRARIAN_CHAT_DAILY_BUDGET_USD")
    )
    chat_user_daily_budget_usd: float = Field(
        default=1.0, validation_alias=_env("LIBRARIAN_CHAT_USER_DAILY_BUDGET_USD")
    )
    # The daily spend is estimated from the price table in librarian.pricing, keyed by model id.

    # Models and endpoints.
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2", validation_alias=_env("LIBRARIAN_EMBEDDING_MODEL")
    )
    anthropic_model: str = Field(
        default=DEFAULT_CHAT_MODEL, validation_alias=_env("ANTHROPIC_MODEL")
    )
    anthropic_api_key: str = Field(default="", validation_alias=_env("ANTHROPIC_API_KEY"))
    codemap_api_url: str = Field(
        default="http://localhost:8100", validation_alias=_env("CODEMAP_API_URL")
    )
    skip_warmup: bool = Field(default=False, validation_alias=_env("LIBRARIAN_SKIP_WARMUP"))
    # Dev convenience: with no built index, the API and the MCP server build one themselves
    # (in the background for the API) and rebuild it when the wiki changes. Production sets
    # this to 0 and runs `librarian index build` as a separate job.
    index_autobuild: bool = Field(default=True, validation_alias=_env("LIBRARIAN_INDEX_AUTOBUILD"))

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
    def courses_private_dir(self) -> Path:
        return self.courses_dir / "private"

    @property
    def course_sources_dir(self) -> Path:
        return (
            self.override_course_sources_dir or self.root.parent / "learn-ai-engineering"
        ).expanduser()

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
    def concept_homes_file(self) -> Path:
        """Maths concepts and the lessons that teach them, read by `courses check curriculum`."""
        return self.data_dir / "concept_homes.json"

    @property
    def web_dir(self) -> Path:
        return self.override_web_dir or self.root / "app" / "dist"

    @property
    def state_dir(self) -> Path | None:
        return self.override_state_dir.expanduser() if self.override_state_dir else None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def logs_dir(self) -> Path:
        if self.override_logs_dir:
            return self.override_logs_dir
        return self.state_dir / "logs" if self.state_dir else self.root / "logs"

    @property
    def retrieval_log(self) -> Path:
        return self.logs_dir / "retrieval.jsonl"

    @property
    def flashcard_log(self) -> Path:
        return self.logs_dir / "flashcards.jsonl"

    @property
    def var_dir(self) -> Path:
        """Where per-learner state lives: the state dir, else `var/` (gitignored)."""
        return self.state_dir or self.root / "var"

    @property
    def attempts_db(self) -> Path:
        """Every graded study event (cards, questions, drill runs). Personal history: never tracked."""
        return self.var_dir / "attempts.sqlite3"

    @property
    def database_url_or_default(self) -> str:
        """`DATABASE_URL`, else SQLite at `var/librarian.sqlite3` (the state dir when set)."""
        return self.database_url or f"sqlite:///{self.var_dir / 'librarian.sqlite3'}"

    @property
    def slides_build_dir(self) -> Path:
        """Per-slide images and text built for the lecture viewer (not tracked)."""
        return self.var_dir / "slides"

    @property
    def content_dir(self) -> Path:
        """The prebuilt content release the API serves from; absent on a plain dev checkout."""
        return (self.override_content_dir or self.var_dir / "content" / "current").expanduser()

    @property
    def content_slides_dir(self) -> Path:
        """Prebuilt decks: `<module>/` trees shaped like `slides_build_dir`."""
        return self.content_dir / "slides"

    @property
    def index_dir(self) -> Path:
        """Built search indexes (`<id>.duckdb`) and the `current` pointer to the live one."""
        return self.var_dir / "index"

    @property
    def wiki_db_path(self) -> Path:
        return self.override_wiki_db_path or (self.state_dir or self.root) / ".wiki_index.duckdb"

    @property
    def embeddings_cache_path(self) -> Path:
        return (
            self.override_embeddings_cache_path
            or (self.state_dir or self.root) / ".embeddings_cache.duckdb"
        )

    @property
    def code_index_path(self) -> Path:
        return self.override_code_index_path or (self.state_dir or self.root) / ".code_index.duckdb"

    @property
    def cache_dir(self) -> Path:
        return self.state_dir / "cache" if self.state_dir else self.root / ".cache"

    @property
    def lesson_vec_cache(self) -> Path:
        return self.cache_dir / "lesson_embeddings.npz"

    @property
    def curriculum_snapshot(self) -> Path:
        return self.cache_dir / "curriculum.json"

    @property
    def curriculum_map_file(self) -> Path:
        """Output of `librarian courses check curriculum` (gitignored with .cache/)."""
        return self.cache_dir / "curriculum-map.json"

    @property
    def review_dir(self) -> Path:
        """Working data of the course reviewers: findings log, eval results. Gitignored (logs/)."""
        return self.logs_dir / "review"

    @property
    def review_findings_log(self) -> Path:
        return self.review_dir / "findings.jsonl"

    @property
    def signals_dir(self) -> Path:
        """Where `librarian courses review signals --write` puts its report. Gitignored (logs/)."""
        return self.logs_dir / "signals"

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


@lru_cache(maxsize=1)
def get_release() -> str:
    """The build identifier: `$LIBRARIAN_RELEASE`, else the git short sha, else `dev`.

    The Docker image has no `.git`, so it takes the value as the `LIBRARIAN_RELEASE` build arg.
    Logs, traces and Sentry all read this one value.
    """
    env = os.environ.get("LIBRARIAN_RELEASE", "").strip()
    if env:
        return env
    import subprocess

    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=discover_root(),
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "dev"
    sha = out.stdout.strip()
    return sha if out.returncode == 0 and sha else "dev"
