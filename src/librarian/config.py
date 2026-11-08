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
from typing import Any

from dotenv import dotenv_values
from pydantic import AliasChoices, Field
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

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


# Settings that hold a secret. Each can be given as `<NAME>` or `<NAME>_FILE` (a path to a file
# holding the value, as docker/compose `secrets:` mount them at /run/secrets/<name>), so the
# value need not sit in `.env` or in `docker inspect` output.
SECRET_FIELDS = (
    "database_url",
    "api_token",
    "session_secret",
    "google_client_secret",
    "github_client_secret",
    "resend_api_key",
    "anthropic_api_key",
    "remote_api_key",
    "release_webhook_secret",
    "metrics_token",
)


class SecretFileError(ValueError):
    """A `<NAME>_FILE` that cannot be read, or that is set together with `<NAME>`."""


class _SecretFileSource(PydanticBaseSettingsSource):
    """Fills `SECRET_FIELDS` from `<NAME>_FILE` in the environment or the `.env` file.

    Trailing newlines are stripped (secret files usually end in one). An unreadable file, or
    both `<NAME>` and `<NAME>_FILE` set to something, stops startup with a message naming the
    variable (never the value).
    """

    def __init__(self, settings_cls: type[BaseSettings], env_file: str | None) -> None:
        super().__init__(settings_cls)
        self._dotenv: dict[str, str | None] = dotenv_values(env_file) if env_file else {}

    def _lookup(self, name: str) -> str:
        return os.environ.get(name) or self._dotenv.get(name) or ""

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for name in SECRET_FIELDS:
            alias = self.settings_cls.model_fields[name].validation_alias
            names = alias.choices if isinstance(alias, AliasChoices) else (alias or name,)
            names = [str(n) for n in names]
            path = next((p for n in names if (p := self._lookup(f"{n}_FILE"))), "")
            if not path:
                continue
            if any(self._lookup(n) for n in names):
                raise SecretFileError(f"set {names[0]} or {names[0]}_FILE, not both")
            try:
                out[name] = Path(path).read_text(encoding="utf-8").rstrip("\r\n")
            except OSError as e:
                raise SecretFileError(
                    f"{names[0]}_FILE={path}: cannot read the file ({e.strerror or e})"
                ) from e
        return out


class Settings(BaseSettings):
    """Paths, model names and endpoints. Paths default to locations under `root`."""

    model_config = SettingsConfigDict(
        env_file=str(discover_root() / ".env"),
        extra="ignore",
        populate_by_name=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        env_file = settings_cls.model_config.get("env_file")
        return (
            init_settings,
            _SecretFileSource(settings_cls, str(env_file) if env_file else None),
            env_settings,
            dotenv_settings,
            file_secret_settings,
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
    # The private sisyphus checkout; `librarian db import-drill-log` reads its drill log (local only).
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
    # Login (librarian.api.routers.auth). Each method is on when its settings are set; any of them
    # turns open mode off. The callback and email links are built on LIBRARIAN_PUBLIC_URL, e.g.
    # https://librarian.example.com; an https URL also makes the cookies Secure.
    public_url: str = Field(default="", validation_alias=_env("LIBRARIAN_PUBLIC_URL"))
    # Signs the short-lived OAuth state cookie. 32+ random bytes; changing it only breaks logins in flight.
    session_secret: str = Field(default="", validation_alias=_env("LIBRARIAN_SESSION_SECRET"))
    # Absolute lifetime (never extended) and idle timeout of a browser session. 0 idle = no timeout.
    session_days: int = Field(default=30, ge=1, validation_alias=_env("LIBRARIAN_SESSION_DAYS"))
    session_idle_days: int = Field(
        default=7, ge=0, validation_alias=_env("LIBRARIAN_SESSION_IDLE_DAYS")
    )
    google_client_id: str = Field(default="", validation_alias=_env("GOOGLE_CLIENT_ID"))
    google_client_secret: str = Field(default="", validation_alias=_env("GOOGLE_CLIENT_SECRET"))
    github_client_id: str = Field(default="", validation_alias=_env("GITHUB_CLIENT_ID"))
    github_client_secret: str = Field(default="", validation_alias=_env("GITHUB_CLIENT_SECRET"))
    # Email sign-in links, sent through Resend from a domain verified there (SPF and DKIM).
    resend_api_key: str = Field(default="", validation_alias=_env("RESEND_API_KEY"))
    email_from: str = Field(default="", validation_alias=_env("EMAIL_FROM"))
    # Requests per client address per window to /auth/* (shared by all workers), and links per email per hour.
    auth_rate_limit: int = Field(default=10, validation_alias=_env("LIBRARIAN_AUTH_RATE_LIMIT"))
    auth_rate_window_s: int = Field(
        default=60, validation_alias=_env("LIBRARIAN_AUTH_RATE_WINDOW_S")
    )
    email_links_per_hour: int = Field(
        default=5, validation_alias=_env("LIBRARIAN_EMAIL_LINKS_PER_HOUR")
    )
    # Reader feedback (librarian.feedback): rows written per user per window, and how long they
    # are kept (`librarian feedback prune`, run daily by the backup service).
    feedback_rate_limit: int = Field(
        default=30, validation_alias=_env("LIBRARIAN_FEEDBACK_RATE_LIMIT")
    )
    feedback_rate_window_s: int = Field(
        default=3600, validation_alias=_env("LIBRARIAN_FEEDBACK_RATE_WINDOW_S")
    )
    feedback_retention_days: int = Field(
        default=180, ge=1, validation_alias=_env("LIBRARIAN_FEEDBACK_RETENTION_DAYS")
    )
    # Experiments and their variants, e.g. `ranking=control,hybrid-union;prompt=v1,v2`
    # (librarian.experiments). Each user is assigned one variant per experiment, stably.
    experiments: str = Field(default="", validation_alias=_env("LIBRARIAN_EXPERIMENTS"))
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
    # Proxies whose X-Forwarded-For uvicorn believes (comma-separated, "*" for any). Behind Caddy
    # the per-address sign-in limit needs it, or every client is the proxy's one address.
    forwarded_allow_ips: str = Field(
        default="127.0.0.1", validation_alias=_env("LIBRARIAN_FORWARDED_ALLOW_IPS")
    )
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
    # `librarian mcp` remote mode: with a key (an `lk_` key from `librarian keys create` or the
    # account page) every wiki tool call goes to this API instead of the local index.
    remote_api_key: str = Field(default="", validation_alias=_env("LIBRARIAN_API_KEY"))
    remote_api_url: str = Field(
        default="http://localhost:8000", validation_alias=_env("LIBRARIAN_API_URL")
    )
    codemap_api_url: str = Field(
        default="http://localhost:8100", validation_alias=_env("CODEMAP_API_URL")
    )
    skip_warmup: bool = Field(default=False, validation_alias=_env("LIBRARIAN_SKIP_WARMUP"))
    # Dev convenience: with no built index, the API and the MCP server build one themselves
    # (in the background for the API) and rebuild it when the wiki changes. Production sets
    # this to 0 and runs `librarian index build` as a separate job.
    index_autobuild: bool = Field(default=True, validation_alias=_env("LIBRARIAN_INDEX_AUTOBUILD"))
    # Content releases (librarian.release). With a URL the API serves the release it pulls
    # (`<url>/latest` names it; https or file://), on start, every poll interval and on a signed
    # POST /admin/reload. Unset: content is read from data/ as on a dev checkout.
    release_url: str = Field(default="", validation_alias=_env("LIBRARIAN_RELEASE_URL"))
    release_poll_s: float = Field(
        default=60.0, ge=0, validation_alias=_env("LIBRARIAN_RELEASE_POLL_S")
    )
    # HMAC-SHA256 key for the release webhook (X-Librarian-Signature). Unset: admins only.
    release_webhook_secret: str = Field(
        default="", validation_alias=_env("LIBRARIAN_RELEASE_WEBHOOK_SECRET")
    )

    # GET /metrics (Prometheus). Unset: the route answers 404 and nothing is collected. Set: the
    # scraper sends it as `Authorization: Bearer <token>`. Caddy also refuses /metrics from outside.
    metrics_token: str = Field(default="", validation_alias=_env("LIBRARIAN_METRICS_TOKEN"))

    # Backups (librarian.ops). Where the encrypted dumps go: `s3://bucket/prefix` (needs the `aws`
    # CLI and AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY in the environment) or `file:///dir`.
    # Unset: `librarian ops backup` refuses to run.
    backup_url: str = Field(default="", validation_alias=_env("LIBRARIAN_BACKUP_URL"))
    # S3-compatible endpoint, e.g. https://<account>.r2.cloudflarestorage.com for Cloudflare R2.
    backup_endpoint_url: str = Field(
        default="", validation_alias=_env("LIBRARIAN_BACKUP_ENDPOINT_URL")
    )
    # age public key (age1...). The host holds only this; the private key stays off the host.
    backup_age_recipient: str = Field(
        default="", validation_alias=_env("LIBRARIAN_BACKUP_AGE_RECIPIENT")
    )
    # `ops upgrade` takes a new backup unless the newest one is younger than this many minutes.
    backup_max_age_min: int = Field(
        default=15, ge=0, validation_alias=_env("LIBRARIAN_BACKUP_MAX_AGE_MIN")
    )
    # Time of day (UTC, HH:MM) the compose `backup` service runs `ops backup`.
    backup_at: str = Field(
        default="03:30",
        pattern=r"^([01]\d|2[0-3]):[0-5]\d$",
        validation_alias=_env("LIBRARIAN_BACKUP_AT"),
    )

    # ── derived locations ────────────────────────────────────────────────────

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def wiki_dir(self) -> Path:
        if self.override_wiki_dir:
            return self.override_wiki_dir
        return self.content_dir / "wiki" if self.release_url else self.data_dir / "wiki"

    @property
    def private_dir(self) -> Path:
        return self.wiki_dir / "private"

    @property
    def courses_dir(self) -> Path:
        if self.override_courses_dir:
            return self.override_courses_dir
        return self.content_dir / "courses" if self.release_url else self.data_dir / "courses"

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
    def login_methods(self) -> list[str]:
        """The sign-in methods configured: "google", "github", "email"."""
        methods = [
            name
            for name, ident, secret in (
                ("google", self.google_client_id, self.google_client_secret),
                ("github", self.github_client_id, self.github_client_secret),
            )
            if ident and secret
        ]
        if self.resend_api_key and self.email_from:
            methods.append("email")
        return methods

    @property
    def open_mode(self) -> bool:
        """No token and no login configured: every request is the owner (local use)."""
        return not self.api_token and not self.login_methods

    @property
    def secure_cookies(self) -> bool:
        return self.public_url.startswith("https://")

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
