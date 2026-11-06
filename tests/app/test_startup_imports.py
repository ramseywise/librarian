"""The API must open its port before torch loads: that import was most of a restart."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_importing_the_api_loads_no_heavy_ml_libraries() -> None:
    code = (
        "import sys; import apps.api.main; "
        "print([m for m in ('torch', 'sentence_transformers', 'sklearn', 'umap', 'numba') "
        "if m in sys.modules])"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True
    )
    assert out.stdout.strip().splitlines()[-1] == "[]"
