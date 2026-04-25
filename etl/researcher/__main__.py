from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import date
from pathlib import Path

import structlog
from dotenv import load_dotenv

from core.config.agent_settings import settings

load_dotenv()

log = structlog.get_logger(__name__)

MANIFEST_PATH = settings.obsidian_vault / ".processed.json"


def _load_manifest() -> dict[str, dict[str, str]]:
    """Load the processed-files manifest. Returns empty dict if missing."""
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def _save_manifest(manifest: dict[str, dict[str, str]]) -> None:
    """Persist the processed-files manifest."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _pdf_hash(pdf_path: Path) -> str:
    """SHA-256 of first 64 KiB — fast enough for dedup, catches re-uploads."""
    hasher = hashlib.sha256()
    with pdf_path.open("rb") as f:
        hasher.update(f.read(65536))
    return hasher.hexdigest()


def _relative_key(pdf_path: Path) -> str:
    """Manifest key: relative path from readings_dir, or absolute as fallback."""
    try:
        return str(pdf_path.relative_to(settings.readings_dir))
    except ValueError:
        return str(pdf_path.resolve())


def _find_unprocessed(
    manifest: dict[str, dict[str, str]],
    force: bool = False,
) -> list[Path]:
    """Recursively find PDFs in readings_dir not yet in the manifest."""
    if not settings.readings_dir.exists():
        log.error("batch.readings_dir_missing", path=str(settings.readings_dir))
        return []

    pdfs: list[Path] = sorted(settings.readings_dir.rglob("*.pdf"))
    if force:
        return pdfs

    unprocessed: list[Path] = []
    for pdf in pdfs:
        key = _relative_key(pdf)
        entry = manifest.get(key)
        if entry is None:
            unprocessed.append(pdf)
        elif entry.get("hash") != _pdf_hash(pdf):
            # PDF was re-uploaded with different content
            log.info("batch.changed_pdf", key=key)
            unprocessed.append(pdf)

    return unprocessed


def _run_single(pdf_path: Path, dry_run: bool, topic: str | None) -> None:
    """Process a single PDF and write note."""
    from etl.researcher.agent import ResearchAgent
    from etl.researcher.writer import render_note, write_note

    log.info("cli.start", pdf=str(pdf_path), dry_run=dry_run, topic=topic)

    agent = ResearchAgent()
    note = agent.process_pdf(pdf_path, topic_override=topic)

    if dry_run:
        print(render_note(note))
        log.info("cli.dry_run_done")
    else:
        note_path = write_note(note, pdf_path, topic_override=topic)
        log.info("cli.done", output=str(note_path))
        print(f"Note written: {note_path}")


def _run_batch(dry_run: bool, force: bool, max_pdfs: int = 5) -> None:
    """Scan readings_dir for unprocessed PDFs and process each.

    Args:
        dry_run: List files without writing.
        force: Re-process all PDFs regardless of manifest.
        max_pdfs: Maximum number of PDFs to process in this run.
            Prevents runaway token spend when many PDFs accumulate.
            Each PDF costs ~2 API calls (chunks + merge).
    """
    from etl.researcher.agent import ResearchAgent
    from etl.researcher.models import resolve_topic
    from etl.researcher.writer import write_note

    manifest = _load_manifest()
    unprocessed = _find_unprocessed(manifest, force=force)

    if not unprocessed:
        print("No unprocessed PDFs found.")
        return

    # Apply PDF limit
    total_found = len(unprocessed)
    if len(unprocessed) > max_pdfs:
        unprocessed = unprocessed[:max_pdfs]
        print(
            f"Found {total_found} PDF(s), processing first {max_pdfs} (--max-pdfs limit):"
        )
    else:
        print(f"Found {total_found} PDF(s) to process:")

    for pdf in unprocessed:
        print(f"  {_relative_key(pdf)}")

    if total_found > max_pdfs:
        print(f"  ... and {total_found - max_pdfs} more (next run)")

    if dry_run:
        print("\n(dry-run — no files written)")
        return

    agent = ResearchAgent()
    processed = 0
    skipped = 0
    failed = 0

    for pdf in unprocessed:
        key = _relative_key(pdf)
        log.info("batch.processing", key=key)

        try:
            resolve_topic(pdf)
        except ValueError:
            log.warning("batch.unknown_topic", key=key)
            print(f"  SKIP (unknown topic folder): {key}")
            skipped += 1
            continue

        try:
            note = agent.process_pdf(pdf)
            write_note(note, pdf)

            manifest[key] = {
                "date": date.today().isoformat(),
                "hash": _pdf_hash(pdf),
                "note": note.metadata.title,
            }
            _save_manifest(manifest)

            processed += 1
            print(f"  OK: {key}")

        except FileExistsError:
            log.info("batch.already_exists", key=key)
            manifest[key] = {
                "date": date.today().isoformat(),
                "hash": _pdf_hash(pdf),
                "note": "(already existed)",
            }
            _save_manifest(manifest)
            skipped += 1
            print(f"  SKIP (note exists): {key}")

        except Exception as exc:
            log.error("batch.failed", key=key, error=str(exc))
            failed += 1
            print(f"  FAIL: {key} — {exc}")

    print(
        f"\nBatch complete: {processed} processed, {skipped} skipped, {failed} failed"
    )
    if total_found > max_pdfs:
        remaining = total_found - max_pdfs
        print(f"Remaining: {remaining} PDF(s) will be processed in the next run")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Obsidian notes from PDFs using Claude."
    )
    parser.add_argument(
        "pdf_path",
        type=Path,
        nargs="?",
        default=None,
        help="Path to a single PDF file (omit for --batch mode)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Scan readings_dir for unprocessed PDFs and process each",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print rendered notes to stdout (single) or list files (batch) without writing",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-process all PDFs regardless of manifest (batch mode only)",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        metavar="SLUG",
        help="Override the Obsidian topic folder slug (single file mode only)",
    )
    parser.add_argument(
        "--max-pdfs",
        type=int,
        default=int(os.environ.get("RESEARCH_CRON_MAX_PDFS", "5")),
        metavar="N",
        help="Max PDFs to process per batch run (default: 5, env: RESEARCH_CRON_MAX_PDFS). "
        "Each PDF costs ~2 API calls. Set to 0 for unlimited.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=int(os.environ.get("RESEARCH_CRON_MAX_TOKENS", "4096")),
        metavar="N",
        help="Max output tokens per API call (default: 4096, env: RESEARCH_CRON_MAX_TOKENS)",
    )
    args = parser.parse_args()

    # Validate argument combinations
    if args.batch and args.pdf_path:
        print("Error: --batch and pdf_path are mutually exclusive", file=sys.stderr)
        sys.exit(1)

    if not args.batch and not args.pdf_path:
        parser.print_help()
        sys.exit(1)

    # Expose max_tokens for agent to pick up
    if args.max_tokens != 4096:
        os.environ["RESEARCH_MAX_TOKENS"] = str(args.max_tokens)

    if args.batch:
        max_pdfs = args.max_pdfs if args.max_pdfs > 0 else sys.maxsize
        try:
            _run_batch(dry_run=args.dry_run, force=args.force, max_pdfs=max_pdfs)
        except KeyboardInterrupt:
            log.info("batch.interrupted")
            sys.exit(130)
        except Exception as exc:
            log.error("batch.fatal", error=str(exc))
            print(f"Fatal error: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        pdf_path = args.pdf_path
        if not pdf_path.exists():
            log.error("cli.pdf_not_found", path=str(pdf_path))
            print(f"Error: PDF not found: {pdf_path}", file=sys.stderr)
            sys.exit(1)

        if not pdf_path.suffix.lower() == ".pdf":
            log.error("cli.not_a_pdf", path=str(pdf_path))
            print(f"Error: file is not a PDF: {pdf_path}", file=sys.stderr)
            sys.exit(1)

        try:
            _run_single(pdf_path, dry_run=args.dry_run, topic=args.topic)
        except FileExistsError as exc:
            log.error("cli.note_exists", error=str(exc))
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            log.info("cli.interrupted")
            sys.exit(130)
        except Exception as exc:
            log.error("cli.error", error=str(exc))
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
