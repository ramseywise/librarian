"""ScraperBase — shared ABC for all ETL scrapers in librarian.ingest.

Provides:
  - source_name / output_dir attributes
  - structlog setup (via librarian.log_config.configure_logging)
  - ManifestSession integration
  - dry-run guard
  - cli() classmethod: argparse boilerplate + instantiation + run

Subclass protocol:
    class MyScraper(ScraperBase):
        source_name = "my-source"
        output_dir = REPO_ROOT / "data" / "raw" / "my-source"

        def run(self, dry_run: bool = False) -> list[Path]:
            ...

        # Optional: add extra CLI arguments
        @classmethod
        def _add_args(cls, parser: argparse.ArgumentParser) -> None:
            parser.add_argument("--extra-flag", ...)

        # Optional: build instance from parsed args (override if constructor needs extra args)
        @classmethod
        def _from_args(cls, args: argparse.Namespace) -> "MyScraper":
            return cls(extra_flag=args.extra_flag)
"""

from __future__ import annotations

import argparse
import random
import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx
import structlog

from librarian.config import get_settings
from librarian.ingest.manifest import ManifestSession
from librarian.log_config import configure_logging

REPO_ROOT = get_settings().root
log = structlog.get_logger()

MAX_ATTEMPTS = 4
BACKOFF_BASE_S = 1.0
BACKOFF_CAP_S = 30.0
RETRY_AFTER_CAP_S = 60.0


def _retry_after(resp: httpx.Response) -> float | None:
    """Seconds named by a Retry-After header (delta-seconds or HTTP date), capped; None if absent."""
    value = resp.headers.get("retry-after")
    if not value:
        return None
    try:
        seconds = float(value)
    except ValueError:
        try:
            seconds = (parsedate_to_datetime(value) - datetime.now(UTC)).total_seconds()
        except (TypeError, ValueError):
            return None
    return min(max(seconds, 0.0), RETRY_AFTER_CAP_S)


def request_with_retry(
    client: httpx.Client,
    method: str,
    url: str,
    *,
    max_attempts: int = MAX_ATTEMPTS,
    **kwargs: object,
) -> httpx.Response:
    """Send a request, retrying transient failures with exponential backoff and jitter.

    Retries connect/read timeouts, connection errors, 429 (sleeping for Retry-After when given)
    and 5xx. Any other 4xx raises at once. Returns a response that passed raise_for_status();
    after the last attempt the final error is raised (an httpx.HTTPError).
    """
    for attempt in range(1, max_attempts + 1):
        delay = min(BACKOFF_CAP_S, BACKOFF_BASE_S * 2 ** (attempt - 1))
        delay += random.uniform(0, delay / 2)
        try:
            resp = client.request(method, url, **kwargs)  # pyright: ignore[reportArgumentType]
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if (status != 429 and status < 500) or attempt == max_attempts:
                raise
            retry_after = _retry_after(exc.response)
            if retry_after is not None:
                delay = retry_after
            reason = f"status_{status}"
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            if attempt == max_attempts:
                raise
            reason = type(exc).__name__
        log.warning(
            "ingest.http_retry", url=url, attempt=attempt, reason=reason, sleep_s=round(delay, 2)
        )
        time.sleep(delay)
    raise AssertionError("unreachable")  # pragma: no cover - loop always returns or raises


class ScraperBase(ABC):
    """Base class for all ETL scrapers."""

    source_name: str = ""  # override in subclass
    output_dir: Path = REPO_ROOT / "data" / "raw"  # override in subclass

    @abstractmethod
    def run(self, dry_run: bool = False) -> list[Path]:
        """Run the scraper. Returns list of paths written (or that would be written)."""

    def manifest_session(self) -> ManifestSession:
        """Return a fresh ManifestSession for batch ingest tracking."""
        return ManifestSession()

    # ------------------------------------------------------------------
    # CLI entry point
    # ------------------------------------------------------------------

    @classmethod
    def _add_args(cls, parser: argparse.ArgumentParser) -> None:
        """Hook: add scraper-specific arguments to the parser."""
        return  # default no-op; subclasses override to add CLI args

    @classmethod
    def _from_args(cls, args: argparse.Namespace) -> ScraperBase:
        """Hook: construct the scraper from parsed args. Override if needed."""
        return cls()

    @classmethod
    def cli(cls, description: str | None = None, argv: list[str] | None = None) -> None:
        """Parse args (argv, default sys.argv), configure logging, run the scraper."""
        configure_logging()
        parser = argparse.ArgumentParser(description=description or f"{cls.source_name} scraper")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be written, don't write",
        )
        cls._add_args(parser)
        args = parser.parse_args(argv)

        scraper = cls._from_args(args)
        written = scraper.run(dry_run=args.dry_run)

        prefix = "[dry-run] " if args.dry_run else ""
        source = cls.source_name or cls.__name__
        print(f"\n{prefix}{source}: {len(written)} file(s) → {scraper.output_dir}")
