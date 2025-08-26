"""Unit test cases for adapter module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fdk_organization_bff.classes import FilterEnum
from fdk_organization_bff.service.adapter import (
    fetch_brreg_data,
    fetch_json_data,
    fetch_json_data_with_post,
    fetch_org_cat_data,
    fetch_org_dataset_catalog_scores,
    fetch_organizations_from_organization_catalog,
    fetch_reference_data,
    query_all_concepts_ordered_by_publisher,
    query_all_dataservices_ordered_by_publisher,
    query_all_datasets_ordered_by_publisher,
    query_all_informationmodels_ordered_by_publisher,
    query_publisher_concepts,
    query_publisher_dataservices,
    query_publisher_datasets,
    query_publisher_informationmodels,
    query_sparql_service,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_json_data_success() -> None:
    """Test fetch_json_data with successful response."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"data": "test"})

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response

    result = await fetch_json_data("http://test.com", None, mock_session)

    assert result == {"data": "test"}
    mock_session.get.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_json_data_with_params() -> None:
    """Test fetch_json_data with parameters."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"data": "test"})

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response

    params = {"key": "value"}
    result = await fetch_json_data("http://test.com", params, mock_session)

    assert result == {"data": "test"}
    mock_session.get.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_json_data_non_200_status() -> None:
    """Test fetch_json_data with non-200 status."""
    mock_response = MagicMock()
    mock_response.status = 404

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response

    result = await fetch_json_data("http://test.com", None, mock_session)

    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_json_data_with_post_success() -> None:
    """Test fetch_json_data_with_post with successful response."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"data": "test"})

    mock_session = MagicMock()
    mock_session.post.return_value.__aenter__.return_value = mock_response

    data = {"key": "value"}
    result = await fetch_json_data_with_post("http://test.com", data, mock_session)

    assert result == {"data": "test"}
    mock_session.post.assert_called_once_with(
        "http://test.com", json=data, headers={"Accept": "application/json"}
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_json_data_with_post_non_200_status() -> None:
    """Test fetch_json_data_with_post with non-200 status."""
    mock_response = MagicMock()
    mock_response.status = 500

    mock_session = MagicMock()
    mock_session.post.return_value.__aenter__.return_value = mock_response

    data = {"key": "value"}
    result = await fetch_json_data_with_post("http://test.com", data, mock_session)

    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_org_cat_data_success() -> None:
    """Test fetch_org_cat_data with successful response."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = {"organizationId": "12345678", "name": "Test Org"}

        mock_session = MagicMock()
        result = await fetch_org_cat_data("12345678", mock_session)

        assert result == {"organizationId": "12345678", "name": "Test Org"}
        mock_fetch.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_org_cat_data_none_response() -> None:
    """Test fetch_org_cat_data with None response."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = None

        mock_session = MagicMock()
        result = await fetch_org_cat_data("12345678", mock_session)

        assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_org_cat_data_list_response() -> None:
    """Test fetch_org_cat_data with list response (should return empty dict)."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = ["item1", "item2"]

        mock_session = MagicMock()
        result = await fetch_org_cat_data("12345678", mock_session)

        assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_organizations_from_organization_catalog_success() -> None:
    """Test fetch_organizations_from_organization_catalog with successful response."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = [
            {"organizationId": "12345678", "name": "Org 1"},
            {"organizationId": "87654321", "name": "Org 2"},
        ]

        mock_session = MagicMock()
        result = await fetch_organizations_from_organization_catalog(mock_session, None)

        expected = {
            "12345678": {"organizationId": "12345678", "name": "Org 1"},
            "87654321": {"organizationId": "87654321", "name": "Org 2"},
        }
        assert result == expected


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_organizations_from_organization_catalog_with_org_path() -> None:
    """Test fetch_organizations_from_organization_catalog with org_path parameter."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = [{"organizationId": "12345678", "name": "Org 1"}]

        mock_session = MagicMock()
        result = await fetch_organizations_from_organization_catalog(
            mock_session, "/test/path"
        )

        expected = {"12345678": {"organizationId": "12345678", "name": "Org 1"}}
        assert result == expected


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_organizations_from_organization_catalog_none_response() -> None:
    """Test fetch_organizations_from_organization_catalog with None response."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = None

        mock_session = MagicMock()
        result = await fetch_organizations_from_organization_catalog(mock_session, None)

        assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_brreg_data_success() -> None:
    """Test fetch_brreg_data with successful response."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = {
            "organisasjonsnummer": "12345678",
            "navn": "Test Org",
        }

        mock_session = MagicMock()
        result = await fetch_brreg_data("12345678", mock_session)

        assert result == {"organisasjonsnummer": "12345678", "navn": "Test Org"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_brreg_data_none_response() -> None:
    """Test fetch_brreg_data with None response."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = None

        mock_session = MagicMock()
        result = await fetch_brreg_data("12345678", mock_session)

        assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_brreg_data_list_response() -> None:
    """Test fetch_brreg_data with list response (should return empty dict)."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = ["item1", "item2"]

        mock_session = MagicMock()
        result = await fetch_brreg_data("12345678", mock_session)

        assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_reference_data_success() -> None:
    """Test fetch_reference_data with successful response."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = {"data": "reference"}

        mock_session = MagicMock()
        result = await fetch_reference_data("/test/path", mock_session)

        assert result == {"data": "reference"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_reference_data_none_response() -> None:
    """Test fetch_reference_data with None response."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = None

        mock_session = MagicMock()
        result = await fetch_reference_data("/test/path", mock_session)

        assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_reference_data_list_response() -> None:
    """Test fetch_reference_data with list response (should return empty dict)."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = ["item1", "item2"]

        mock_session = MagicMock()
        result = await fetch_reference_data("/test/path", mock_session)

        assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_sparql_service_success() -> None:
    """Test query_sparql_service with successful response."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = {"results": {"bindings": []}}

        mock_session = MagicMock()
        result = await query_sparql_service("SELECT * WHERE { ?s ?p ?o }", mock_session)

        assert result == {"results": {"bindings": []}}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_sparql_service_none_response() -> None:
    """Test query_sparql_service with None response."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = None

        mock_session = MagicMock()
        result = await query_sparql_service("SELECT * WHERE { ?s ?p ?o }", mock_session)

        assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_sparql_service_list_response() -> None:
    """Test query_sparql_service with list response (should return empty dict)."""
    with patch("fdk_organization_bff.service.adapter.fetch_json_data") as mock_fetch:
        mock_fetch.return_value = ["item1", "item2"]

        mock_session = MagicMock()
        result = await query_sparql_service("SELECT * WHERE { ?s ?p ?o }", mock_session)

        assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_org_dataset_catalog_scores_success() -> None:
    """Test fetch_org_dataset_catalog_scores with successful response."""
    with patch(
        "fdk_organization_bff.service.adapter.fetch_json_data_with_post"
    ) as mock_fetch:
        mock_fetch.return_value = {
            "aggregations": [{"score": "80", "max_score": "100"}]
        }

        mock_session = MagicMock()
        dataset_uris = ["http://example.com/dataset1", "http://example.com/dataset2"]
        result = await fetch_org_dataset_catalog_scores(dataset_uris, mock_session)

        assert result == {"aggregations": [{"score": "80", "max_score": "100"}]}
        mock_fetch.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_org_dataset_catalog_scores_none_response() -> None:
    """Test fetch_org_dataset_catalog_scores with None response."""
    with patch(
        "fdk_organization_bff.service.adapter.fetch_json_data_with_post"
    ) as mock_fetch:
        mock_fetch.return_value = None

        mock_session = MagicMock()
        dataset_uris = ["http://example.com/dataset1"]
        result = await fetch_org_dataset_catalog_scores(dataset_uris, mock_session)

        assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_publisher_datasets_success() -> None:
    """Test query_publisher_datasets with successful response."""
    with patch(
        "fdk_organization_bff.service.adapter.query_sparql_service"
    ) as mock_query:
        mock_query.return_value = {
            "results": {
                "bindings": [{"dataset": {"value": "http://example.com/dataset"}}]
            }
        }

        mock_session = MagicMock()
        result = await query_publisher_datasets(
            "12345678", FilterEnum.NONE, mock_session
        )

        assert result == [{"dataset": {"value": "http://example.com/dataset"}}]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_publisher_dataservices_success() -> None:
    """Test query_publisher_dataservices with successful response."""
    with patch(
        "fdk_organization_bff.service.adapter.query_sparql_service"
    ) as mock_query:
        mock_query.return_value = {
            "results": {
                "bindings": [{"service": {"value": "http://example.com/service"}}]
            }
        }

        mock_session = MagicMock()
        result = await query_publisher_dataservices(
            "12345678", FilterEnum.NONE, mock_session
        )

        assert result == [{"service": {"value": "http://example.com/service"}}]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_publisher_concepts_success() -> None:
    """Test query_publisher_concepts with successful response."""
    with patch(
        "fdk_organization_bff.service.adapter.query_sparql_service"
    ) as mock_query:
        mock_query.return_value = {
            "results": {
                "bindings": [{"concept": {"value": "http://example.com/concept"}}]
            }
        }

        mock_session = MagicMock()
        result = await query_publisher_concepts(
            "12345678", FilterEnum.NONE, mock_session
        )

        assert result == [{"concept": {"value": "http://example.com/concept"}}]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_publisher_informationmodels_success() -> None:
    """Test query_publisher_informationmodels with successful response."""
    with patch(
        "fdk_organization_bff.service.adapter.query_sparql_service"
    ) as mock_query:
        mock_query.return_value = {
            "results": {
                "bindings": [
                    {"informationmodel": {"value": "http://example.com/model"}}
                ]
            }
        }

        mock_session = MagicMock()
        result = await query_publisher_informationmodels(
            "12345678", FilterEnum.NONE, mock_session
        )

        assert result == [{"informationmodel": {"value": "http://example.com/model"}}]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_all_datasets_ordered_by_publisher_success() -> None:
    """Test query_all_datasets_ordered_by_publisher with successful response."""
    with patch(
        "fdk_organization_bff.service.adapter.query_sparql_service"
    ) as mock_query:
        mock_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "organizationNumber": {"value": "12345678"},
                        "count": {"value": "5"},
                    }
                ]
            }
        }

        mock_session = MagicMock()
        result = await query_all_datasets_ordered_by_publisher(
            FilterEnum.NONE, mock_session
        )

        assert result == [{"org": "12345678", "count": "5"}]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_all_dataservices_ordered_by_publisher_success() -> None:
    """Test query_all_dataservices_ordered_by_publisher with successful response."""
    with patch(
        "fdk_organization_bff.service.adapter.query_sparql_service"
    ) as mock_query:
        mock_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "organizationNumber": {"value": "12345678"},
                        "count": {"value": "3"},
                    }
                ]
            }
        }

        mock_session = MagicMock()
        result = await query_all_dataservices_ordered_by_publisher(
            FilterEnum.NONE, mock_session
        )

        assert result == [{"org": "12345678", "count": "3"}]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_all_concepts_ordered_by_publisher_success() -> None:
    """Test query_all_concepts_ordered_by_publisher with successful response."""
    with patch(
        "fdk_organization_bff.service.adapter.query_sparql_service"
    ) as mock_query:
        mock_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "organizationNumber": {"value": "12345678"},
                        "count": {"value": "2"},
                    }
                ]
            }
        }

        mock_session = MagicMock()
        result = await query_all_concepts_ordered_by_publisher(
            FilterEnum.NONE, mock_session
        )

        assert result == [{"org": "12345678", "count": "2"}]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_all_informationmodels_ordered_by_publisher_success() -> None:
    """Test query_all_informationmodels_ordered_by_publisher with successful response."""
    with patch(
        "fdk_organization_bff.service.adapter.query_sparql_service"
    ) as mock_query:
        mock_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "organizationNumber": {"value": "12345678"},
                        "count": {"value": "1"},
                    }
                ]
            }
        }

        mock_session = MagicMock()
        result = await query_all_informationmodels_ordered_by_publisher(
            FilterEnum.NONE, mock_session
        )

        assert result == [{"org": "12345678", "count": "1"}]
