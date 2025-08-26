"""Integration test cases for specific organizations."""

import json
from typing import Any
from unittest.mock import Mock


import pytest


from tests import responses


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_ramsund(client: Any, docker_service: str) -> None:
    """Should return the ramsund response."""
    response = await client.get("/organizationcatalogs/910244132")
    response_json = await response.json()

    assert response.status == 200
    assert response_json == json.loads(responses.ramsund)


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_liland(client: Any, docker_service: str) -> None:
    """Should return the liland response."""
    response = await client.get("/organizationcatalogs/910258028")
    response_json = await response.json()

    assert response.status == 200
    assert response_json == json.loads(responses.liland)


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_fiskeri_direktoratet(client: Any, docker_service: str) -> None:
    """Should return the fiskeri response."""
    response = await client.get("/organizationcatalogs/971203420")
    response_json = await response.json()

    assert response.status == 200
    assert response_json == json.loads(responses.fiskeri)


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_karmsund_with_no_catalog_data(client: Any, docker_service: str) -> None:
    """Should return the karmsund response."""
    response = await client.get("/organizationcatalogs/910298062")
    response_json = await response.json()

    assert response.status == 200
    assert response_json == json.loads(responses.karmsund)


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_not_found(client: Any, docker_service: str) -> None:
    """Should return 404."""
    response = await client.get("/organizationcatalogs/123")

    assert response.status == 404


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_nap_ramsund(client: Any, docker_service: str) -> None:
    """Should return the ramsund_nap response."""
    response = await client.get(
        "/organizationcatalogs/910244132?filter=transportportal"
    )
    response_json = await response.json()

    assert response.status == 200
    assert response_json == json.loads(responses.ramsund_nap)


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_invalid_filter(client: Any, docker_service: str) -> None:
    """Should return 400."""
    response = await client.get("/organizationcatalogs/910244132?filter=invalid")

    assert response.status == 400


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_ntnu_remote_services_fail(client: Any, docker_service: str) -> None:
    """Should return 200."""
    response = await client.get("/organizationcatalogs/974767880")
    response_json = await response.json()

    assert response.status == 200
    assert response_json == json.loads(responses.ntnu)


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.asyncio
async def test_get_organization_catalog_with_failing_quality(
    client: Any,
    docker_service: str,
    mock_fetch_org_dataset_catalog_scores: Mock,
) -> None:
    """Mock closed session and get organization catalogs."""
    # Mock the function to raise an exception, which will result in empty scores
    mock_fetch_org_dataset_catalog_scores.side_effect = Exception("Mock failure")

    """Should return the ramsund response."""
    response = await client.get("/organizationcatalogs/910244132")
    response_json = await response.json()

    assert response.status == 200
    assert response_json == json.loads(responses.ramsund)
