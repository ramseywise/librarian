"""Shared fixtures — resets all mutable mock state before each test."""

import copy

import pytest

import playground.agent_poc.agents.billy_assistant.tools.customers as customers_mod
import playground.agent_poc.agents.billy_assistant.tools.invitations as invitations_mod
import playground.agent_poc.agents.billy_assistant.tools.invoices as invoices_mod
import playground.agent_poc.agents.billy_assistant.tools.products as products_mod

# Snapshot the initial state at import time (before any test mutates it).
_ORIG_CUSTOMERS = copy.deepcopy(customers_mod._MOCK_CUSTOMERS)
_ORIG_INVOICES = copy.deepcopy(invoices_mod._MOCK_INVOICES)
_ORIG_PRODUCTS = copy.deepcopy(products_mod._MOCK_PRODUCTS)


@pytest.fixture(autouse=True)
def reset_mock_state():
    """Restore all mock stores and counters to their initial state."""
    customers_mod._MOCK_CUSTOMERS[:] = copy.deepcopy(_ORIG_CUSTOMERS)
    customers_mod._next_id_counter = 4

    invoices_mod._MOCK_INVOICES[:] = copy.deepcopy(_ORIG_INVOICES)
    invoices_mod._next_invoice_counter = 4

    products_mod._MOCK_PRODUCTS[:] = copy.deepcopy(_ORIG_PRODUCTS)
    products_mod._next_product_counter = 6

    invitations_mod._MOCK_INVITATIONS.clear()

    yield
