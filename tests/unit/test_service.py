"""Unit test cases for service."""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fdk_organization_bff.classes import FilterEnum
from fdk_organization_bff.service import org_catalog_service


def async_test(coro: Any) -> Any:
    """Async test wrapper."""

    def wrapper(*args: str, **kwargs: int) -> Any:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()

    return wrapper


@patch("aiohttp.ClientSession.closed")
@async_test
@pytest.mark.unit
async def test_get_organization_catalog_with_closed_session(mock: MagicMock) -> None:
    """Mock closed session and get organization catalog."""
    mock.return_value.__aenter__.return_value = AsyncMock(side_effect=True)
    org = await org_catalog_service.get_organization_catalog(
        "12345678", FilterEnum.NONE
    )
    assert org is None


@patch("aiohttp.ClientSession.closed")
@async_test
@pytest.mark.unit
async def test_get_organization_catalogs_with_closed_session(mock: MagicMock) -> None:
    """Mock closed session and get organization catalogs."""
    mock.return_value.__aenter__.return_value = AsyncMock(side_effect=True)
    org = await org_catalog_service.get_organization_catalogs(FilterEnum.NONE, None)
    assert len(org.organizations) == 0


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_get_organization_catalog_no_org_data(mock_session: MagicMock) -> None:
    """Test get_organization_catalog when no organization data is found."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock the adapter functions to return empty data
    with patch(
        "fdk_organization_bff.service.org_catalog_service.fetch_org_cat_data"
    ) as mock_fetch_org:
        mock_fetch_org.return_value = {}

        result = await org_catalog_service.get_organization_catalog(
            "12345678", FilterEnum.NONE
        )

        assert result is None


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_get_organization_catalogs_empty_response(
    mock_session: MagicMock,
) -> None:
    """Test get_organization_catalogs with empty response."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock all the data fetching functions to return empty results
    with patch(
        "fdk_organization_bff.service.org_catalog_service.fetch_organizations_for_org_paths"
    ) as mock_fetch_orgs, patch(
        "fdk_organization_bff.service.org_catalog_service.query_all_datasets_ordered_by_publisher"
    ) as mock_datasets, patch(
        "fdk_organization_bff.service.org_catalog_service.query_all_dataservices_ordered_by_publisher"
    ) as mock_dataservices, patch(
        "fdk_organization_bff.service.org_catalog_service.query_all_concepts_ordered_by_publisher"
    ) as mock_concepts, patch(
        "fdk_organization_bff.service.org_catalog_service.query_all_informationmodels_ordered_by_publisher"
    ) as mock_informationmodels:

        mock_fetch_orgs.return_value = {}
        mock_datasets.return_value = []
        mock_dataservices.return_value = []
        mock_concepts.return_value = []
        mock_informationmodels.return_value = []

        result = await org_catalog_service.get_organization_catalogs(
            FilterEnum.NONE, None
        )

        assert result is not None
        assert len(result.organizations) == 0


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_get_organization_catalog_with_exceptions(
    mock_session: MagicMock,
) -> None:
    """Test get_organization_catalog with exceptions in async operations."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock the adapter functions to raise exceptions
    with patch(
        "fdk_organization_bff.service.org_catalog_service.fetch_org_cat_data"
    ) as mock_fetch_org:
        with patch(
            "fdk_organization_bff.service.org_catalog_service.fetch_brreg_data"
        ) as mock_fetch_brreg:
            with patch(
                "fdk_organization_bff.service.org_catalog_service.query_publisher_datasets"
            ) as mock_query_datasets:
                with patch(
                    "fdk_organization_bff.service.org_catalog_service.query_publisher_dataservices"
                ) as mock_query_services:
                    with patch(
                        "fdk_organization_bff.service.org_catalog_service.query_publisher_concepts"
                    ) as mock_query_concepts:
                        with patch(
                            "fdk_organization_bff.service.org_catalog_service.query_publisher_informationmodels"
                        ) as mock_query_models:
                            with patch(
                                "fdk_organization_bff.service.org_catalog_service.fetch_org_dataset_catalog_scores"
                            ) as mock_scores:

                                # Setup mock returns with exceptions
                                mock_fetch_org.return_value = {
                                    "organizationId": "12345678",
                                    "name": "Test Org",
                                }
                                mock_fetch_brreg.side_effect = Exception(
                                    "Network error"
                                )
                                mock_query_datasets.side_effect = Exception(
                                    "SPARQL error"
                                )
                                mock_query_services.return_value = []
                                mock_query_concepts.return_value = []
                                mock_query_models.return_value = []
                                mock_scores.return_value = {}

                                result = (
                                    await org_catalog_service.get_organization_catalog(
                                        "12345678", FilterEnum.NONE
                                    )
                                )

                                # Should still return a catalog even with some exceptions
                                assert result is not None


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_get_organization_catalog_with_dataset_scores_exception(
    mock_session: MagicMock,
) -> None:
    """Test get_organization_catalog with exception in dataset scores fetch."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock the adapter functions
    with patch(
        "fdk_organization_bff.service.org_catalog_service.fetch_org_cat_data"
    ) as mock_fetch_org:
        with patch(
            "fdk_organization_bff.service.org_catalog_service.fetch_brreg_data"
        ) as mock_fetch_brreg:
            with patch(
                "fdk_organization_bff.service.org_catalog_service.query_publisher_datasets"
            ) as mock_query_datasets:
                with patch(
                    "fdk_organization_bff.service.org_catalog_service.query_publisher_dataservices"
                ) as mock_query_services:
                    with patch(
                        "fdk_organization_bff.service.org_catalog_service.query_publisher_concepts"
                    ) as mock_query_concepts:
                        with patch(
                            "fdk_organization_bff.service.org_catalog_service.query_publisher_informationmodels"
                        ) as mock_query_models:
                            with patch(
                                "fdk_organization_bff.service.org_catalog_service.fetch_org_dataset_catalog_scores"
                            ) as mock_scores:

                                # Setup mock returns
                                mock_fetch_org.return_value = {
                                    "organizationId": "12345678",
                                    "name": "Test Org",
                                }
                                mock_fetch_brreg.return_value = {}
                                mock_query_datasets.return_value = [
                                    {"dataset": {"value": "http://example.com/dataset"}}
                                ]
                                mock_query_services.return_value = []
                                mock_query_concepts.return_value = []
                                mock_query_models.return_value = []
                                mock_scores.return_value = Exception("Scores error")

                                result = (
                                    await org_catalog_service.get_organization_catalog(
                                        "12345678", FilterEnum.NONE
                                    )
                                )

                                # Should still return a catalog even with scores exception
                                assert result is not None


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_get_organization_catalog_with_empty_data_but_org_exists(
    mock_session: MagicMock,
) -> None:
    """Test get_organization_catalog with empty data but organization exists."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock the adapter functions
    with patch(
        "fdk_organization_bff.service.org_catalog_service.fetch_org_cat_data"
    ) as mock_fetch_org:
        with patch(
            "fdk_organization_bff.service.org_catalog_service.fetch_brreg_data"
        ) as mock_fetch_brreg:
            with patch(
                "fdk_organization_bff.service.org_catalog_service.query_publisher_datasets"
            ) as mock_query_datasets:
                with patch(
                    "fdk_organization_bff.service.org_catalog_service.query_publisher_dataservices"
                ) as mock_query_services:
                    with patch(
                        "fdk_organization_bff.service.org_catalog_service.query_publisher_concepts"
                    ) as mock_query_concepts:
                        with patch(
                            "fdk_organization_bff.service.org_catalog_service.query_publisher_informationmodels"
                        ) as mock_query_models:
                            with patch(
                                "fdk_organization_bff.service.org_catalog_service.fetch_org_dataset_catalog_scores"
                            ) as mock_scores:

                                # Setup mock returns - org exists but no data
                                mock_fetch_org.return_value = {
                                    "organizationId": "12345678",
                                    "name": "Test Org",
                                }
                                mock_fetch_brreg.return_value = {}
                                mock_query_datasets.return_value = []
                                mock_query_services.return_value = []
                                mock_query_concepts.return_value = []
                                mock_query_models.return_value = []
                                mock_scores.return_value = {}

                                result = (
                                    await org_catalog_service.get_organization_catalog(
                                        "12345678", FilterEnum.NONE
                                    )
                                )

                                # Should return a catalog with empty datasets
                                assert result is not None
                                assert result.organization is not None


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_get_organization_catalogs_with_exceptions(
    mock_session: MagicMock,
) -> None:
    """Test get_organization_catalogs with exceptions in async operations."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock the adapter functions
    with patch(
        "fdk_organization_bff.service.org_catalog_service.fetch_organizations_from_organization_catalog"
    ) as mock_fetch_orgs:
        with patch(
            "fdk_organization_bff.service.org_catalog_service.query_all_datasets_ordered_by_publisher"
        ) as mock_query_datasets:
            with patch(
                "fdk_organization_bff.service.org_catalog_service.query_all_dataservices_ordered_by_publisher"
            ) as mock_query_services:
                with patch(
                    "fdk_organization_bff.service.org_catalog_service.query_all_concepts_ordered_by_publisher"
                ) as mock_query_concepts:
                    with patch(
                        "fdk_organization_bff.service.org_catalog_service."
                        "query_all_informationmodels_ordered_by_publisher"
                    ) as mock_query_models:

                        # Setup mock returns with exceptions
                        mock_fetch_orgs.side_effect = Exception("Network error")
                        mock_query_datasets.side_effect = Exception("SPARQL error")
                        mock_query_services.return_value = []
                        mock_query_concepts.return_value = []
                        mock_query_models.return_value = []

                        result = await org_catalog_service.get_organization_catalogs(
                            FilterEnum.NONE, None
                        )

                        # Should still return a catalog list even with exceptions
                        assert result is not None
                        assert len(result.organizations) == 0


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_get_state_categories_success(mock_session: MagicMock) -> None:
    """Test get_state_categories with successful response."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock the summarize function
    with patch(
        "fdk_organization_bff.service.org_catalog_service.summarize_catalog_data_for_organizations"
    ) as mock_summarize:
        mock_summarize.return_value = []

        result = await org_catalog_service.get_state_categories(FilterEnum.NONE, "true")

        assert result is not None
        assert hasattr(result, "categories")


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_get_municipality_categories_success(mock_session: MagicMock) -> None:
    """Test get_municipality_categories with successful response."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock the functions
    with patch(
        "fdk_organization_bff.service.org_catalog_service.summarize_catalog_data_for_organizations"
    ) as mock_summarize:
        with patch(
            "fdk_organization_bff.service.org_catalog_service.fetch_municipality_data"
        ) as mock_fetch_municipality:
            mock_summarize.return_value = []
            mock_fetch_municipality.return_value = {"fylke": {}, "kommune": {}}

            result = await org_catalog_service.get_municipality_categories(
                FilterEnum.NONE, "true"
            )

            assert result is not None
            assert hasattr(result, "categories")


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_fetch_municipality_data_success(mock_session: MagicMock) -> None:
    """Test fetch_municipality_data with successful response."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock the fetch_reference_data function
    with patch(
        "fdk_organization_bff.service.org_catalog_service.fetch_reference_data"
    ) as mock_fetch:
        mock_fetch.side_effect = [
            {"fylkeOrganisasjoner": {"org1": "data1"}},
            {"kommuneOrganisasjoner": {"org2": "data2"}},
        ]

        result = await org_catalog_service.fetch_municipality_data()

        assert result is not None
        assert "fylke" in result
        assert "kommune" in result


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_fetch_municipality_data_with_exceptions(mock_session: MagicMock) -> None:
    """Test fetch_municipality_data with exceptions."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock the fetch_reference_data function to raise exceptions
    with patch(
        "fdk_organization_bff.service.org_catalog_service.fetch_reference_data"
    ) as mock_fetch:
        mock_fetch.side_effect = [
            Exception("Network error"),
            Exception("Network error"),
        ]

        result = await org_catalog_service.fetch_municipality_data()

        assert result is not None
        assert "fylke" in result
        assert "kommune" in result
        assert result["fylke"] is None
        assert result["kommune"] is None


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_fetch_organizations_for_org_paths_with_paths(
    mock_session: MagicMock,
) -> None:
    """Test fetch_organizations_for_org_paths with org paths."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock the fetch_organizations_from_organization_catalog function
    with patch(
        "fdk_organization_bff.service.org_catalog_service.fetch_organizations_from_organization_catalog"
    ) as mock_fetch:
        mock_fetch.side_effect = [
            {"org1": {"id": "org1", "name": "Org 1"}},
            {"org2": {"id": "org2", "name": "Org 2"}},
        ]

        org_paths = ["/path1", "/path2"]
        result = await org_catalog_service.fetch_organizations_for_org_paths(
            org_paths, mock_session_instance
        )

        assert result is not None
        assert "org1" in result
        assert "org2" in result


@patch("aiohttp.ClientSession")
@async_test
@pytest.mark.unit
async def test_fetch_organizations_for_org_paths_no_paths(
    mock_session: MagicMock,
) -> None:
    """Test fetch_organizations_for_org_paths with no org paths."""
    # Mock the session methods
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Mock the fetch_organizations_from_organization_catalog function
    with patch(
        "fdk_organization_bff.service.org_catalog_service.fetch_organizations_from_organization_catalog"
    ) as mock_fetch:
        mock_fetch.return_value = {"org1": {"id": "org1", "name": "Org 1"}}

        result = await org_catalog_service.fetch_organizations_for_org_paths(
            None, mock_session_instance
        )

        assert result is not None
        assert "org1" in result
