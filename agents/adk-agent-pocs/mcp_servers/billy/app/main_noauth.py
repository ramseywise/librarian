"""Billy stub MCP server — no-auth entry point.

Run in STDIO mode (default, for Claude Desktop / ADK MCPToolset):
    python -m app.main_noauth

Run in HTTP mode (for remote agents or browser testing):
    python -m app.main_noauth --http
"""

import logging
import sys

from dotenv import load_dotenv

load_dotenv()  # loads mcp_servers/billy/.env

from fastmcp import FastMCP

# In stdio mode stdout is the MCP protocol pipe — all logging must go to stderr.
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

from playground.agent_poc.mcp_servers.billy.app.common import register_all
from playground.agent_poc.mcp_servers.billy.app.config import Config

mcp = FastMCP(name=Config.SERVER_NAME)
register_all(mcp)


def run_server() -> None:
    if "--http" in sys.argv:
        print(
            f"Billy MCP server (SSE) listening on http://{Config.HOST}:{Config.PORT}/sse"
        )
        mcp.run(transport="sse", host=Config.HOST, port=Config.PORT)
    else:
        mcp.run()


if __name__ == "__main__":
    run_server()
