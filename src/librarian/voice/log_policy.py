"""Keep what is said out of every log (D10). Call `pin_logging` before importing Pipecat.

Pipecat's default loguru sink is stderr at DEBUG, and it logs transcripts and spoken text there
(`Transcription: [...]`, `Generating TTS [...]`). One TTS message carrying text is a WARNING, so
a level alone would not be the guard: the sink lets only ERROR and above through, and even then
prints the level, module and line with no message, as an exception's text can quote its input.

Three settings would send content somewhere else and are forced off too: the smart-turn model's
audio dump, the Anthropic SDK's request log, and Hugging Face telemetry during a model download.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

CHATTY_STDLIB_LOGGERS = (
    "aioice",
    "aiortc",
    "anthropic",
    "faster_whisper",
    "httpcore",
    "httpx",
    "huggingface_hub",
    "openai",
    "phonemizer",
)
FORBIDDEN_ENV = ("PIPECAT_SMART_TURN_LOG_DATA", "ANTHROPIC_LOG")
PIPECAT_MIN_LEVEL = "ERROR"


def content_free_format(record: Any) -> str:
    """Where it happened and how bad, never the message or the traceback text."""
    exception = record["exception"]
    kind = exception.type.__name__ if exception and exception.type else "-"
    return "{time:HH:mm:ss} {level} {name}:{line} " + f"exception={kind}\n"


def pin_logging(sink: Any = None) -> None:
    """Replace every loguru sink with a content-free one. Safe to call more than once.

    `sink` is for tests; the default is stderr. Without the `voice` extra there is no loguru and
    no Pipecat to quieten, so the rest still applies.
    """
    for key in FORBIDDEN_ENV:
        os.environ.pop(key, None)
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    for name in CHATTY_STDLIB_LOGGERS:
        logging.getLogger(name).setLevel(logging.ERROR)
    try:
        from loguru import logger
    except ImportError:
        return
    logger.remove()
    logger.add(
        sink if sink is not None else sys.stderr,
        level=PIPECAT_MIN_LEVEL,
        format=content_free_format,
        backtrace=False,
        diagnose=False,
    )
