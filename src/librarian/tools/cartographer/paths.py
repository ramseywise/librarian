"""Where the guard hooks write their telemetry.

The hook libraries (galactus `.claude/hooks/lib.sh`, `~/.claude/scripts/bash-nudge.sh`)
log to ``$CLAUDE_TELEMETRY_DIR``, defaulting to guacamayo's ``.sounding/telemetry/`` and
falling back to ``~/.claude`` only when that directory does not exist. Cartographer must
read from the same place, or the hook-activity card reports a dead log while the real one
fills up elsewhere (observed 2026-11-20: ~/.claude/.hook-log.jsonl frozen, guacamayo's
growing). This module is the single resolution of that path on the read side.
"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_TELEMETRY_DIR = Path.home() / "workspace" / "guacamayo" / ".sounding" / "telemetry"
FALLBACK_TELEMETRY_DIR = Path.home() / ".claude"

HOOK_LOG_NAME = ".hook-log.jsonl"
HOOK_PASS_LOG_NAME = ".hook-pass-log.jsonl"


def hook_telemetry_dir() -> Path:
    """Resolve the directory the hooks log into, mirroring lib.sh.

    Order: ``$CLAUDE_TELEMETRY_DIR`` if set, else the guacamayo default if it exists,
    else ``~/.claude``.
    """
    env = os.environ.get("CLAUDE_TELEMETRY_DIR")
    if env:
        return Path(env).expanduser()
    if DEFAULT_TELEMETRY_DIR.is_dir():
        return DEFAULT_TELEMETRY_DIR
    return FALLBACK_TELEMETRY_DIR


def hook_log_path() -> Path:
    """Blocks/warns log (`log_event` in lib.sh)."""
    return hook_telemetry_dir() / HOOK_LOG_NAME


def hook_pass_log_path() -> Path:
    """Silent-pass log (`log_pass` in lib.sh)."""
    return hook_telemetry_dir() / HOOK_PASS_LOG_NAME
