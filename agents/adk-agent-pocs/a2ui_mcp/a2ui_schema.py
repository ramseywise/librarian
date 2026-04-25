"""Loads the A2UI v0.8 JSON schema from the repo root.

Used by agent_gateway/a2ui_parser.py for server-side validation.
"""

import json
import pathlib

_REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
A2UI_SCHEMA = json.loads((_REPO_ROOT / "a2ui_schema.json").read_text(encoding="utf-8"))
