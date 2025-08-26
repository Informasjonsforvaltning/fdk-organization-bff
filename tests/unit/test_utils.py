"""Unit test cases for utils."""

import datetime
from typing import Any
from unittest.mock import patch

import pytest

from fdk_organization_bff.classes import FilterEnum
from fdk_organization_bff.utils.utils import (
    dataset_is_authoritative,
    dataset_is_open_data,
    filter_param_to_enum,
    get_today,
    resource_is_new,
    to_int,
    url_with_params,
)


@pytest.mark.unit
def test_url_with_params() -> None:
    """Test url_with_params with parameters."""
    url = "http://test.com"
    params = {"key1": "value1", "key2": "value2"}

    result = url_with_params(url, params)

    assert "http://test.com?" in result
    assert "key1=value1" in result
    assert "key2=value2" in result


@pytest.mark.unit
def test_url_with_params_no_params() -> None:
    """Test url_with_params with no parameters."""
    url = "http://test.com"

    result = url_with_params(url, None)

    assert result == "http://test.com"


@pytest.mark.unit
def test_url_with_params_empty_params() -> None:
    """Test url_with_params with empty parameters."""
    url = "http://test.com"
    params: dict[str, str] = {}

    result = url_with_params(url, params)

    assert result == "http://test.com"


@pytest.mark.unit
def test_url_with_params_special_chars() -> None:
    """Test url_with_params with special characters."""
    url = "http://test.com"
    params: dict[str, str] = {"key": "value with spaces", "special": "test&value"}

    result = url_with_params(url, params)

    assert "key=value+with+spaces" in result
    assert "special=test%26value" in result


@pytest.mark.unit
def test_filter_param_to_enum_none() -> None:
    """Test filter_param_to_enum with None."""
    result = filter_param_to_enum(None)

    assert result == FilterEnum.NONE


@pytest.mark.unit
def test_filter_param_to_enum_nap() -> None:
    """Test filter_param_to_enum with NAP value."""
    result = filter_param_to_enum("transportportal")

    assert result == FilterEnum.NAP


@pytest.mark.unit
def test_filter_param_to_enum_invalid() -> None:
    """Test filter_param_to_enum with invalid value."""
    result = filter_param_to_enum("invalid")

    assert result == FilterEnum.INVALID


@pytest.mark.unit
def test_dataset_is_authoritative_true() -> None:
    """Test dataset_is_authoritative with true value."""
    dataset: dict[str, dict[str, str]] = {"isAuthoritative": {"value": "true"}}

    result = dataset_is_authoritative(dataset)

    assert result is True


@pytest.mark.unit
def test_dataset_is_authoritative_false() -> None:
    """Test dataset_is_authoritative with false value."""
    dataset: dict[str, dict[str, str]] = {"isAuthoritative": {"value": "false"}}

    result = dataset_is_authoritative(dataset)

    assert result is False


@pytest.mark.unit
def test_dataset_is_authoritative_missing() -> None:
    """Test dataset_is_authoritative with missing field."""
    dataset: dict[str, dict[str, str]] = {}

    result = dataset_is_authoritative(dataset)

    assert result is False


@pytest.mark.unit
def test_dataset_is_open_data_true() -> None:
    """Test dataset_is_open_data with true value."""
    dataset: dict[str, dict[str, str]] = {"isOpenData": {"value": "true"}}

    result = dataset_is_open_data(dataset)

    assert result is True


@pytest.mark.unit
def test_dataset_is_open_data_false() -> None:
    """Test dataset_is_open_data with false value."""
    dataset: dict[str, dict[str, str]] = {"isOpenData": {"value": "false"}}

    result = dataset_is_open_data(dataset)

    assert result is False


@pytest.mark.unit
def test_dataset_is_open_data_missing() -> None:
    """Test dataset_is_open_data with missing field."""
    dataset: dict[str, dict[str, str]] = {}

    result = dataset_is_open_data(dataset)

    assert result is False


@pytest.mark.unit
def test_get_today() -> None:
    """Test get_today function."""
    result = get_today()

    assert isinstance(result, datetime.date)


@pytest.mark.unit
@patch("fdk_organization_bff.utils.utils.get_today")
def test_resource_is_new_recent_date(mock_today: Any) -> None:
    """Test resource_is_new with recent date."""
    mock_today.return_value = datetime.date(2024, 1, 15)

    resource: dict[str, dict[str, str]] = {
        "issued": {"value": "2024-01-12T10:00:00.000Z"}
    }

    result = resource_is_new(resource)

    assert result is True


@pytest.mark.unit
@patch("fdk_organization_bff.utils.utils.get_today")
def test_resource_is_new_old_date(mock_today: Any) -> None:
    """Test resource_is_new with old date."""
    mock_today.return_value = datetime.date(2024, 1, 15)

    resource: dict[str, dict[str, str]] = {
        "issued": {"value": "2024-01-05T10:00:00.000Z"}
    }

    result = resource_is_new(resource)

    assert result is False


@pytest.mark.unit
@patch("fdk_organization_bff.utils.utils.get_today")
def test_resource_is_new_exactly_7_days(mock_today: Any) -> None:
    """Test resource_is_new with exactly 7 days ago."""
    mock_today.return_value = datetime.date(2024, 1, 15)

    resource: dict[str, dict[str, str]] = {
        "issued": {"value": "2024-01-08T10:00:00.000Z"}
    }

    result = resource_is_new(resource)

    assert result is True


@pytest.mark.unit
@patch("fdk_organization_bff.utils.utils.get_today")
def test_resource_is_new_future_date(mock_today: Any) -> None:
    """Test resource_is_new with future date."""
    mock_today.return_value = datetime.date(2024, 1, 15)

    resource: dict[str, dict[str, str]] = {
        "issued": {"value": "2024-01-20T10:00:00.000Z"}
    }

    result = resource_is_new(resource)

    assert result is True


@pytest.mark.unit
def test_resource_is_new_no_issued() -> None:
    """Test resource_is_new with no issued field."""
    resource: dict[str, dict[str, str]] = {}

    result = resource_is_new(resource)

    assert result is False


@pytest.mark.unit
def test_resource_is_new_invalid_date() -> None:
    """Test resource_is_new with invalid date format."""
    resource: dict[str, dict[str, str]] = {"issued": {"value": "invalid-date"}}

    result = resource_is_new(resource)

    assert result is False


@pytest.mark.unit
def test_to_int_valid_string() -> None:
    """Test to_int with valid string."""
    result = to_int("123")

    assert result == 123


@pytest.mark.unit
def test_to_int_valid_int() -> None:
    """Test to_int with valid int."""
    result = to_int(456)

    assert result == 456


@pytest.mark.unit
def test_to_int_invalid_string() -> None:
    """Test to_int with invalid string."""
    result = to_int("invalid")

    assert result is None


@pytest.mark.unit
def test_to_int_none() -> None:
    """Test to_int with None."""
    result = to_int(None)

    assert result is None


@pytest.mark.unit
def test_to_int_float() -> None:
    """Test to_int with float."""
    result = to_int(123.45)

    assert result == 123
