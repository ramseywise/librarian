"""Shared pytest fixtures for the Billy MCP server tests."""

import pytest
from playground.agent_poc.mcp_servers.billy.app.main_noauth import mcp


@pytest.fixture
def client():
    """Return the FastMCP in-memory client (sync helper for async tests)."""
    return mcp


@pytest.fixture(autouse=True)
def fresh_db(monkeypatch, tmp_path):
    """Give each test a clean, fully-seeded SQLite database."""
    from playground.agent_poc.mcp_servers.billy.app import db

    db_file = str(tmp_path / "test_billy.db")
    monkeypatch.setenv("BILLY_DB", db_file)
    db.init_db()
