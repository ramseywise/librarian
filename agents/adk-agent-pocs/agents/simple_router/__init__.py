import logging
import os

if os.getenv("SIMPLE_ROUTER_DEBUG", "0") == "1":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(name)s: %(message)s",
    )

from .agent import root_agent, router_agent

__all__ = ["root_agent", "router_agent"]
