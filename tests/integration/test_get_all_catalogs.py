"""Integration test cases for all organization catalogs."""

import json
from typing import Any


import pytest


from tests import responses


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_all_catalogs(client: Any, docker_service: str) -> None:
    """Should return the all_catalogs response."""
    response = await client.get("/organizationcatalogs")
    response_json = await response.json()

    assert response.status == 200
    assert response_json == json.loads(responses.all_catalogs)


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_all_include_empty(client: Any, docker_service: str) -> None:
    """Should return the all_catalogs response."""
    response = await client.get("/organizationcatalogs?includeEmpty=true")
    response_json = await response.json()

    assert response.status == 200
    assert len(response_json["organizations"]) == 135


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_all_nap_catalogs(client: Any, docker_service: str) -> None:
    """Should return the all_nap response."""
    response = await client.get("/organizationcatalogs?filter=transportportal")
    response_json = await response.json()

    assert response.status == 200
    assert response_json == json.loads(responses.all_nap)


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_invalid_filter(client: Any, docker_service: str) -> None:
    """Should return 400."""
    response = await client.get("/organizationcatalogs?filter=invalid")

    assert response.status == 400
