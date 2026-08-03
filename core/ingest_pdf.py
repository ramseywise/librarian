"""Extract text from research PDFs in Dropbox → raw/pdfs/

Usage:
    uv run python core/ingest_pdf.py                    # all PDFs in DROPBOX_PDF_PATH
    uv run python core/ingest_pdf.py --pdf path/to/file.pdf  # single PDF
    uv run python core/ingest_pdf.py --dry-run
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pdfplumber
import structlog
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from core.base import REPO_ROOT, ScraperBase

load_dotenv()
log = structlog.get_logger()

RAW_PDFS = REPO_ROOT / "data" / "raw" / "pdfs"


class Settings(BaseSettings):
    dropbox_pdf_path: Path = Path("~/Dropbox/research-pdfs").expanduser()


def extract_pdf(pdf_path: Path, out_dir: Path) -> Path:
    """Extract text from a PDF and write to raw/pdfs/<stem>.md."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{pdf_path.stem}.md"

    log.info("extracting_pdf", source=str(pdf_path), dest=str(out_path))

    with pdfplumber.open(pdf_path) as pdf:
        pages = []
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"<!-- Page {i} -->\n{text}")

    content = f"# {pdf_path.stem}\n\n**Source:** {pdf_path}\n\n---\n\n" + "\n\n---\n\n".join(pages)
    out_path.write_text(content, encoding="utf-8")
    log.info("extracted_pdf", pages=len(pages), dest=str(out_path))
    return out_path


class PdfScraper(ScraperBase):
    source_name = "ingest-pdf"
    output_dir = RAW_PDFS

    def __init__(self, pdf: Path | None = None) -> None:
        self._pdf = pdf  # single-file override; None = scan all

    def run(self, dry_run: bool = False) -> list[Path]:
        settings = Settings()
        if self._pdf is not None:
            pdfs = [self._pdf]
        else:
            pdfs = list(settings.dropbox_pdf_path.glob("**/*.pdf"))
            log.info("found_pdfs", count=len(pdfs), source=str(settings.dropbox_pdf_path))

        written: list[Path] = []
        for pdf in pdfs:
            if dry_run:
                out_path = self.output_dir / f"{pdf.stem}.md"
                print(f"  [would extract] {pdf} → {out_path}")
                written.append(out_path)
                continue
            try:
                out = extract_pdf(pdf, self.output_dir)
                written.append(out)
            except Exception:
                log.exception("pdf_extraction_failed", path=str(pdf))

        log.info("extraction_complete", count=len(written))
        if not dry_run:
            print(f"\nExtracted {len(written)} PDFs to {self.output_dir}/")
            print("Run /ingest raw/pdfs/ in Claude Code to compile into wiki.")

        return written

    @classmethod
    def _add_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--pdf",
            type=Path,
            default=None,
            metavar="PATH",
            help="Single PDF to extract (default: all PDFs in DROPBOX_PDF_PATH)",
        )

    @classmethod
    def _from_args(cls, args: argparse.Namespace) -> PdfScraper:
        return cls(pdf=args.pdf)


if __name__ == "__main__":
    PdfScraper.cli(description="Extract text from research PDFs → raw/pdfs/")
