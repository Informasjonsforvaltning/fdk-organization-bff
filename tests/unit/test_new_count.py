"""Unit test cases for newCount calculation."""

import datetime
from typing import Any
from unittest.mock import patch

import pytest

from fdk_organization_bff.utils.mappers import map_org_dataservices, map_org_datasets
from fdk_organization_bff.utils.utils import resource_is_new


class TestResourceIsNew:
    """Test cases for resource_is_new function."""

    @pytest.mark.unit
    def test_resource_is_new_with_recent_date(self: "TestResourceIsNew") -> None:
        """Test that a resource with a recent issued date is marked as new."""
        # Mock today to be 2024-01-15
        with patch("fdk_organization_bff.utils.utils.get_today") as mock_today:
            mock_today.return_value = datetime.date(2024, 1, 15)

            # Resource issued 3 days ago (within 7 days)
            resource = {"issued": {"value": "2024-01-12T10:00:00.000Z"}}

            assert resource_is_new(resource) is True

    @pytest.mark.unit
    def test_resource_is_new_with_old_date(self: "TestResourceIsNew") -> None:
        """Test that a resource with an old issued date is not marked as new."""
        # Mock today to be 2024-01-15
        with patch("fdk_organization_bff.utils.utils.get_today") as mock_today:
            mock_today.return_value = datetime.date(2024, 1, 15)

            # Resource issued 10 days ago (outside 7 days)
            resource = {"issued": {"value": "2024-01-05T10:00:00.000Z"}}

            assert resource_is_new(resource) is False

    @pytest.mark.unit
    def test_resource_is_new_with_exactly_7_days_ago(self: "TestResourceIsNew") -> None:
        """Test that a resource issued exactly 7 days ago is marked as new."""
        # Mock today to be 2024-01-15
        with patch("fdk_organization_bff.utils.utils.get_today") as mock_today:
            mock_today.return_value = datetime.date(2024, 1, 15)

            # Resource issued exactly 7 days ago
            resource = {"issued": {"value": "2024-01-08T10:00:00.000Z"}}

            assert resource_is_new(resource) is True

    @pytest.mark.unit
    def test_resource_is_new_with_future_date(self: "TestResourceIsNew") -> None:
        """Test that a resource with a future issued date is marked as new."""
        # Mock today to be 2024-01-15
        with patch("fdk_organization_bff.utils.utils.get_today") as mock_today:
            mock_today.return_value = datetime.date(2024, 1, 15)

            # Resource issued in the future
            resource = {"issued": {"value": "2024-01-20T10:00:00.000Z"}}

            assert resource_is_new(resource) is True

    @pytest.mark.unit
    def test_resource_is_new_without_issued_field(self: "TestResourceIsNew") -> None:
        """Test that a resource without issued field is not marked as new."""
        resource = {"some_other_field": "value"}
        assert resource_is_new(resource) is False

    @pytest.mark.unit
    def test_resource_is_new_with_invalid_date_format(
        self: "TestResourceIsNew",
    ) -> None:
        """Test that a resource with invalid date format is not marked as new."""
        resource = {"issued": {"value": "invalid-date-format"}}
        assert resource_is_new(resource) is False

    @pytest.mark.unit
    def test_resource_is_new_with_none_issued(self: "TestResourceIsNew") -> None:
        """Test that a resource with None issued is not marked as new."""
        resource = {"issued": None}
        assert resource_is_new(resource) is False


class TestNewCountInMappers:
    """Test cases for newCount calculation in mapper functions."""

    @patch("fdk_organization_bff.utils.utils.get_today")
    @pytest.mark.unit
    def test_map_org_datasets_new_count(
        self: "TestNewCountInMappers", mock_today: Any
    ) -> None:
        """Test newCount calculation in map_org_datasets."""
        # Mock today to be 2024-01-15
        mock_today.return_value = datetime.date(2024, 1, 15)

        # Sample datasets with different issued dates
        org_datasets = [
            {
                "dataset": {"value": "http://example.com/dataset1"},
                "issued": {"value": "2024-01-12T10:00:00.000Z"},  # 3 days ago - NEW
            },
            {
                "dataset": {"value": "http://example.com/dataset2"},
                "issued": {"value": "2024-01-05T10:00:00.000Z"},  # 10 days ago - OLD
            },
            {
                "dataset": {"value": "http://example.com/dataset3"},
                "issued": {"value": "2024-01-08T10:00:00.000Z"},  # 7 days ago - NEW
            },
            {
                "dataset": {"value": "http://example.com/dataset4"},
                "issued": {"value": "2024-01-20T10:00:00.000Z"},  # Future - NEW
            },
        ]

        score_data = {"aggregations": [{"score": "10", "max_score": "30"}]}

        result = map_org_datasets(org_datasets, score_data)

        assert result.totalCount == 4
        assert result.newCount == 3  # 3 datasets are new (within 7 days or future)
        assert result.authoritativeCount == 0
        assert result.openCount == 0

    @patch("fdk_organization_bff.utils.utils.get_today")
    @pytest.mark.unit
    def test_map_org_dataservices_new_count(
        self: "TestNewCountInMappers", mock_today: Any
    ) -> None:
        """Test newCount calculation in map_org_dataservices."""
        # Mock today to be 2024-01-15
        mock_today.return_value = datetime.date(2024, 1, 15)

        # Sample dataservices with different issued dates
        org_dataservices = [
            {
                "service": {"value": "http://example.com/service1"},
                "issued": {"value": "2024-01-12T10:00:00.000Z"},  # 3 days ago - NEW
            },
            {
                "service": {"value": "http://example.com/service2"},
                "issued": {"value": "2024-01-05T10:00:00.000Z"},  # 10 days ago - OLD
            },
            {
                "service": {"value": "http://example.com/service3"},
                "issued": {"value": "2024-01-08T10:00:00.000Z"},  # 7 days ago - NEW
            },
        ]

        result = map_org_dataservices(org_dataservices)

        assert result.totalCount == 3
        assert result.newCount == 2  # 2 services are new (within 7 days)

    @patch("fdk_organization_bff.utils.utils.get_today")
    @pytest.mark.unit
    def test_map_org_datasets_with_2021_data(
        self: "TestNewCountInMappers", mock_today: Any
    ) -> None:
        """Test newCount calculation with 2021 data (like in the integration test)."""
        # Mock today to be 2025-08-27 (current date)
        mock_today.return_value = datetime.date(2025, 8, 27)

        # Sample datasets with 2021 issued dates (from the mock data)
        org_datasets = [
            {
                "dataset": {"value": "http://example.com/dataset1"},
                "issued": {"value": "2021-04-23T10:00:04.16Z"},  # 2021 date - OLD
            },
            {
                "dataset": {"value": "http://example.com/dataset2"},
                "issued": {"value": "2021-03-17T10:00:04.16Z"},  # 2021 date - OLD
            },
        ]

        score_data = {"aggregations": [{"score": "10", "max_score": "30"}]}

        result = map_org_datasets(org_datasets, score_data)

        assert result.totalCount == 2
        assert result.newCount == 0  # No datasets from 2021 are new in 2025

    @patch("fdk_organization_bff.utils.utils.get_today")
    @pytest.mark.unit
    def test_map_org_dataservices_with_2021_data(
        self: "TestNewCountInMappers", mock_today: Any
    ) -> None:
        """Test newCount calculation with 2021 data (like in the integration test)."""
        # Mock today to be 2025-08-27 (current date)
        mock_today.return_value = datetime.date(2025, 8, 27)

        # Sample dataservices with 2021 issued dates (from the mock data)
        org_dataservices = [
            {
                "service": {"value": "http://example.com/service1"},
                "issued": {"value": "2021-04-23T10:00:04.16Z"},  # 2021 date - OLD
            },
            {
                "service": {"value": "http://example.com/service2"},
                "issued": {"value": "2021-03-17T10:00:04.16Z"},  # 2021 date - OLD
            },
        ]

        result = map_org_dataservices(org_dataservices)

        assert result.totalCount == 2
        assert result.newCount == 0  # No services from 2021 are new in 2025

    @pytest.mark.unit
    def test_map_org_datasets_empty_list(self: "TestNewCountInMappers") -> None:
        """Test newCount calculation with empty dataset list."""
        org_datasets: list = []
        score_data: dict = {}

        result = map_org_datasets(org_datasets, score_data)

        assert result.totalCount == 0
        assert result.newCount == 0

    @pytest.mark.unit
    def test_map_org_dataservices_empty_list(self: "TestNewCountInMappers") -> None:
        """Test newCount calculation with empty dataservice list."""
        org_dataservices: list = []

        result = map_org_dataservices(org_dataservices)

        assert result.totalCount == 0
        assert result.newCount == 0
