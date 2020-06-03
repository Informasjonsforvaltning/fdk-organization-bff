import pytest
from httpcore import ConnectError

from src.service_requests import ServiceKey,  get_organizations_async
from src.utils import FetchFromServiceException

get_request = "httpx.AsyncClient.get"

service_urls = {
    ServiceKey.ORGANIZATIONS: "http://localhost:8080/organizations",

}

@pytest.mark.unit
def test_get_organizations_async(event_loop, mock_get_xhttp_organizations):
    event_loop.run_until_complete(get_organizations_async())
    mock_get_xhttp_organizations.assert_called_once_with(url="http://localhost:8080/organizations",
                                                         headers={"Accept": "application/json"},
                                                         timeout=10)


@pytest.mark.unit
def test_get_organizations_async_should_throw_error(event_loop, mocker):
    mocker.patch(get_request, side_effect=ConnectError())
    with pytest.raises(FetchFromServiceException):
        event_loop.run_until_complete(get_organizations_async())