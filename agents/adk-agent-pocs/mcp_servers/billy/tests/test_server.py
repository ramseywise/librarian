"""End-to-end connectivity tests via FastMCP in-memory Client."""

from playground.agent_poc.mcp_servers.billy.app.main_noauth import mcp
from fastmcp import Client

ALL_TOOLS = {
    "list_customers",
    "edit_customer",
    "create_customer",
    "get_invoice",
    "list_invoices",
    "get_invoice_summary",
    "edit_invoice",
    "create_invoice",
    "list_products",
    "edit_product",
    "create_product",
    "send_invoice_by_email",
    "invite_user",
    "fetch_support_knowledge",
}


class TestServerConnectivity:
    async def test_ping(self):
        async with Client(mcp) as c:
            assert await c.ping() is True

    async def test_all_tools_registered(self):
        async with Client(mcp) as c:
            tools = await c.list_tools()
            names = {t.name for t in tools}
            assert ALL_TOOLS == names
