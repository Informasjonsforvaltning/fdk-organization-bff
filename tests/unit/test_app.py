"""Unit test cases for app module."""

import os
from unittest.mock import patch

from aiohttp import web
import pytest

from fdk_organization_bff.app import create_app, setup_routes


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_app_default_cors() -> None:
    """Test create_app with default CORS settings."""
    with patch.dict(os.environ, {}, clear=True):
        app = await create_app()

        assert isinstance(app, web.Application)
        assert len(app.middlewares) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_app_custom_cors() -> None:
    """Test create_app with custom CORS settings."""
    with patch.dict(
        os.environ,
        {"CORS_ORIGIN_PATTERNS": "http://localhost:3000,https://example.com"},
        clear=True,
    ):
        app = await create_app()

        assert isinstance(app, web.Application)
        assert len(app.middlewares) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_app_cors_with_spaces() -> None:
    """Test create_app with CORS settings containing spaces."""
    with patch.dict(
        os.environ,
        {"CORS_ORIGIN_PATTERNS": "http://localhost:3000 , https://example.com"},
        clear=True,
    ):
        app = await create_app()

        assert isinstance(app, web.Application)
        assert len(app.middlewares) > 0


@pytest.mark.unit
def test_setup_routes() -> None:
    """Test setup_routes function."""
    app = web.Application()

    setup_routes(app)

    # Check that routes are added
    assert len(app.router.routes()) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_app_with_routes() -> None:
    """Test create_app includes all expected routes."""
    with patch.dict(os.environ, {}, clear=True):
        app = await create_app()

        # Check that routes are configured
        routes = [route.resource.canonical for route in app.router.routes()]

        # Should have routes for ping, ready, org catalog, etc.
        assert len(routes) > 0
