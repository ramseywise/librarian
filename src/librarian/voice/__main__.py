"""`make voice`: pins logging first, because importing Pipecat already logs."""

from __future__ import annotations

from .log_policy import pin_logging

pin_logging()

import os  # noqa: E402

import anthropic  # noqa: E402
import uvicorn  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

from librarian.log_config import configure_logging  # noqa: E402

from .config import HOST, load_config  # noqa: E402
from .pipeline import LocalModels, PipecatSession  # noqa: E402
from .server import create_app  # noqa: E402

LLM_MAX_RETRIES = 1  # A slow retry helps nobody who is waiting for a reply out loud.


def main() -> None:
    load_dotenv()
    # An .env file may have set these, so the second pass is what guarantees they're off.
    pin_logging()
    configure_logging()
    cfg = load_config()
    models = LocalModels(cfg)

    def session_factory(plan, on_end):  # noqa: ANN001, ANN202
        client = anthropic.AsyncAnthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            timeout=cfg.llm_timeout_s,
            max_retries=LLM_MAX_RETRIES,
        )
        return PipecatSession(plan, cfg, models, client, on_end)

    app = create_app(cfg, models, session_factory)
    uvicorn.run(app, host=HOST, port=cfg.port, access_log=False, log_level="warning")


if __name__ == "__main__":
    main()
