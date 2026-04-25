from __future__ import annotations

import subprocess
from pathlib import Path

from core.config.agent_settings import settings


def get_page_count(pdf_path: Path) -> int:
    """Return total page count for a PDF using pdfinfo."""
    result = subprocess.run(
        [str(settings.pdfinfo_bin), str(pdf_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":")[1].strip())
    raise ValueError(f"Could not parse page count from pdfinfo output for: {pdf_path}")


def extract_pages(pdf_path: Path, start: int, end: int) -> str:
    """Extract text from a page range (inclusive) using pdftotext."""
    result = subprocess.run(
        [
            str(settings.pdftotext_bin),
            "-f",
            str(start),
            "-l",
            str(end),
            str(pdf_path),
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def extract_toc(pdf_path: Path, toc_pages: int = 10) -> str:
    """Extract the first N pages as text for TOC/section detection."""
    return extract_pages(pdf_path, 1, toc_pages)
