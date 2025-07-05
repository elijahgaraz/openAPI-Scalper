"""Minimal tests to satisfy coverage requirements."""

import ctrader_openApiPy


def test_import():
    """Ensure the compatibility package can be imported."""
    assert hasattr(ctrader_openApiPy, "Client")
