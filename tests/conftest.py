import asyncio
import re
import time
import pytest
import requests
from urllib3.exceptions import MaxRetryError, NewConnectionError

from src.utils import ServiceKey
from tests.test_data import info_model_response, concept_response, dataset_response, dataservice_response, org_1, org_3, \
    org_2


@pytest.fixture(scope="session")
def wait_for_ready():
    timeout = time.time() + 20
    try:
        while True:
            response = requests.get("http://localhost:8000/ready")
            if response.status_code == 200:
                break
            if time.time() > timeout:
                pytest.fail(
                    'Test function setup: timed out while waiting for organization-bff, last response '
                    'was {0}'.format(response.status_code))
            time.sleep(1)
    except (requests.exceptions.ConnectionError, ConnectionRefusedError, MaxRetryError, NewConnectionError):
        pytest.fail('Test function setup: could not contact fdk-organization-bff')
    yield


async def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            print("status check")

    response_json = {}
    if re.findall("organization", kwargs['url']).__len__() > 0:
        response_json = [org_1, org_2, org_3]
    if re.findall("informationmodels", kwargs['url']).__len__() > 0:
        response_json = info_model_response(19)
    elif re.findall("concept", kwargs['url']).__len__() > 0:
        response_json = concept_response(76)
    elif re.findall("dataset", kwargs['url']).__len__() > 0:
        response_json = dataset_response(51)
    elif re.findall("api", kwargs['url']).__len__() > 0:
        response_json = dataservice_response(69)
    await asyncio.sleep(1)
    return MockResponse(json_data=response_json,
                        status_code=200)


def get_xhttp_mock(status_code, service_key: None):
    class MockResponse:
        def __init__(self, status):
            if service_key == ServiceKey.ORGANIZATIONS:
                self.json_data = [org_1, org_2, org_3]
            else:
                self.json_data = {"page": {"totalElements": 0}}
            self.status_code = status

        def json(self):
            return self.json_data

        def raise_for_status(self):
            print("status check")

    return MockResponse(status_code)


@pytest.fixture
def mock_get_xhttp_organizations(mocker):
    mock_values = get_xhttp_mock(status_code=200, service_key=ServiceKey.ORGANIZATIONS)
    return mocker.patch('httpx.AsyncClient.get',
                        return_value=mock_values
                        )


@pytest.fixture
def mock_get_xhttp_informationmodels_empty(mocker):
    mock_values = get_xhttp_mock(status_code=200, service_key="empty")
    return mocker.patch('httpx.AsyncClient.get',
                        return_value=mock_values
                        )
