"""Extract text from research PDFs in Dropbox → raw/pdfs/

Usage:
    uv run python scripts/ingest_pdf.py                    # all PDFs in DROPBOX_PDF_PATH
    uv run python scripts/ingest_pdf.py path/to/file.pdf   # single PDF
"""

from __future__ import annotations

import sys
from pathlib import Path

import pdfplumber
import structlog
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()
log = structlog.get_logger()

RAW_PDFS = Path("raw/pdfs")


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


def main() -> None:
    settings = Settings()

    if len(sys.argv) > 1:
        pdfs = [Path(sys.argv[1])]
    else:
        pdfs = list(settings.dropbox_pdf_path.glob("**/*.pdf"))
        log.info("found_pdfs", count=len(pdfs), source=str(settings.dropbox_pdf_path))

    extracted = []
    for pdf in pdfs:
        try:
            out = extract_pdf(pdf, RAW_PDFS)
            extracted.append(out)
        except Exception:
            log.exception("pdf_extraction_failed", path=str(pdf))

    log.info("extraction_complete", count=len(extracted))
    print(f"\nExtracted {len(extracted)} PDFs to {RAW_PDFS}/")
    print("Run /ingest raw/pdfs/ in Claude Code to compile into wiki.")


if __name__ == "__main__":
    main()
