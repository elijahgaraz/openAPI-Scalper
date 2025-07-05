"""Compatibility wrapper for coverage.

This module simply re-exports all objects from :mod:`ctrader_open_api` so that
pytest coverage options referring to ``ctrader_openApiPy`` work correctly.
"""

from ctrader_open_api import *  # noqa: F401,F403
