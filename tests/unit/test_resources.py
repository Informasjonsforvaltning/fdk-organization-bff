"""Unit test cases for resources module."""

import pytest

from fdk_organization_bff.resources.ping import Ping


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ping_get() -> None:
    """Test Ping.get."""
    result = await Ping.get()

    assert result.status == 200
    assert result.text == "OK"
