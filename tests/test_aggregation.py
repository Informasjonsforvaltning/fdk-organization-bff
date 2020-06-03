from unittest.mock import MagicMock

import pytest
from src.aggregation import get_organization_catalog_list
from src.utils import FetchFromServiceException
from src.service_requests import ServiceKey
from tests.test_data import org_1, org_2, org_3, org_5


@pytest.fixture
def mock_get_organizations(mocker):
    return mocker.patch('src.aggregation.get_organizations',
                        return_value=[org_1, org_2, org_3, org_5]
                        )


@pytest.fixture
def mock_get_organizations_exception(mocker):
    return mocker.patch('src.aggregation.get_organizations',
                        side_effect=FetchFromServiceException(
                            execution_point=ServiceKey.ORGANIZATIONS,
                            url="http://mock.grape/organizations"
                        ))


@pytest.mark.unit
def test_get_organization_catalog_list(mock_get_organizations):
    result = get_organization_catalog_list()
    assert mock_get_organizations.call_count == 1
    assert result.response_list.__len__() == 4


@pytest.mark.unit
def test_get_organization_catalog_should_return_error_msg_for_organizations(mock_get_organizations_exception):
    result = get_organization_catalog_list()
    assert "status" in result.keys()
    assert result["status"] == "error"
    assert "reason" in result.keys()
    assert "organization" in result["reason"]
