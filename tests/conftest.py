from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "e2e: end-to-end tests requiring live servers")
    config.addinivalue_line("markers", "unit: fast unit tests, no servers needed")
