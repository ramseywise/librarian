"""Configuration for the Billy MCP server."""

import os


class Config:
    SERVER_NAME = "billy-stub"
    HOST = os.getenv("MCP_HOST", "127.0.0.1")
    PORT = int(os.getenv("MCP_PORT", "8765"))
    BASE_URL = os.getenv("MCP_BASE_URL", "http://127.0.0.1:8765")
