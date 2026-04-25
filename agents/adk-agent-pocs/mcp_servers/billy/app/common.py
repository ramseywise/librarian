"""Common registration logic — register all tools exactly once.

Both main_noauth.py (and a future main.py with OAuth) call register_all(mcp)
so tool registration is never duplicated.
"""

import functools
import logging

from fastmcp import FastMCP

from playground.agent_poc.mcp_servers.billy.app.tools.customers import (
    create_customer,
    edit_customer,
    list_customers,
)
from playground.agent_poc.mcp_servers.billy.app.tools.emails import (
    send_invoice_by_email,
)
from playground.agent_poc.mcp_servers.billy.app.tools.invitations import invite_user
from playground.agent_poc.mcp_servers.billy.app.tools.invoices import (
    create_invoice,
    edit_invoice,
    get_insight_monthly_revenue,
    get_insight_top_customers,
    get_invoice,
    get_invoice_summary,
    list_invoices,
)
from playground.agent_poc.mcp_servers.billy.app.tools.products import (
    create_product,
    edit_product,
    list_products,
)
from playground.agent_poc.mcp_servers.billy.app.tools.support_knowledge import (
    fetch_support_knowledge,
)

_log = logging.getLogger("billy.tools")


def _logged(fn):
    """Wrap a tool function with entry/exit logging to stderr."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        _log.info("[MCP] ▶ %s  args=%s kwargs=%s", fn.__name__, args, kwargs)
        try:
            result = fn(*args, **kwargs)
            _log.info("[MCP] ◀ %s  result=%.300s", fn.__name__, str(result))
            return result
        except Exception:
            _log.exception("[MCP] ✗ %s raised", fn.__name__)
            raise

    return wrapper


def register_all(mcp: FastMCP) -> None:
    """Register every Billy stub tool on *mcp*."""

    # Customers
    mcp.tool()(_logged(list_customers))
    mcp.tool()(_logged(edit_customer))
    mcp.tool()(_logged(create_customer))

    # Invoices
    mcp.tool()(_logged(get_invoice))
    mcp.tool()(_logged(list_invoices))
    mcp.tool()(_logged(get_invoice_summary))
    mcp.tool()(_logged(edit_invoice))
    mcp.tool()(_logged(create_invoice))

    # Insights
    mcp.tool()(_logged(get_insight_monthly_revenue))
    mcp.tool()(_logged(get_insight_top_customers))

    # Products
    mcp.tool()(_logged(list_products))
    mcp.tool()(_logged(edit_product))
    mcp.tool()(_logged(create_product))

    # Emails
    mcp.tool()(_logged(send_invoice_by_email))

    # Invitations
    mcp.tool()(_logged(invite_user))

    # Support knowledge
    mcp.tool()(_logged(fetch_support_knowledge))
