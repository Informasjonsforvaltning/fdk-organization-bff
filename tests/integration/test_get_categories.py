"""Integration test cases for organization categories."""

from typing import Any

import pytest


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_state_categories(client: Any, docker_service: str) -> None:
    """Should return the state categories response without empty orgs."""
    response = await client.get("/organizationcategories/state?includeEmpty=false")
    response_json = await response.json()

    assert response.status == 200
    assert len(response_json["categories"]) == 19
    assert response_json["categories"][1]["category"]["id"] == "972417793"
    assert len(response_json["categories"][1]["organizations"]) == 0


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_state_categories_include_empty(client: Any, docker_service: str) -> None:
    """Should return the state categories response with empty orgs."""
    response = await client.get("/organizationcategories/state?includeEmpty=true")
    response_json = await response.json()

    assert response.status == 200
    assert len(response_json["categories"]) == 19
    assert response_json["categories"][1]["category"]["id"] == "972417793"
    assert len(response_json["categories"][1]["organizations"]) == 7


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_municipality_categories(client: Any, docker_service: str) -> None:
    """Should return the municipality categories response without empty orgs."""
    response = await client.get(
        "/organizationcategories/municipality?includeEmpty=false"
    )
    response_json = await response.json()

    assert response.status == 200
    assert len(response_json["categories"]) == 11
    assert response_json["categories"][3]["category"]["id"] == "964982953"
    assert len(response_json["categories"][3]["organizations"]) == 0


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_municipality_categories_include_empty(
    client: Any, docker_service: str
) -> None:
    """Should return the municipality categories response with empty orgs."""
    response = await client.get(
        "/organizationcategories/municipality?includeEmpty=true"
    )
    response_json = await response.json()

    assert response.status == 200
    assert len(response_json["categories"]) == 11
    assert response_json["categories"][3]["category"]["id"] == "964982953"
    assert len(response_json["categories"][3]["organizations"]) == 2
