"""Integration test cases for ping & ready routes."""

from typing import Any

import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ping(client: Any) -> None:
    """Should return OK."""
    response = await client.get("/ping")
    response_content = await response.content.read()

    assert response.status == 200
    assert response_content.decode() == "OK"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ready(client: Any) -> None:
    """Should return OK."""
    response = await client.get("/ready")
    response_content = await response.content.read()

    assert response.status == 200
    assert response_content.decode() == "OK"
