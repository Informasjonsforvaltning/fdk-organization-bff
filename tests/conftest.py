"""Conftest module."""

import os
import time
from typing import Any
from unittest.mock import Mock

from dotenv import load_dotenv
import pytest
import pytest_asyncio
import pytest_mock
import requests
from requests.exceptions import ConnectionError

load_dotenv()
HOST_PORT = int(os.environ.get("HOST_PORT", "8080"))


def is_responsive(url: Any) -> Any:
    """Return true if response from service is 200."""
    url = f"{url}/ready"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            time.sleep(2)  # sleep extra 2 sec
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def docker_service(docker_ip: Any, docker_services: Any) -> Any:
    """Ensure that HTTP service is up and responsive."""
    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("fdk-organization-bff", HOST_PORT)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: Any) -> Any:
    """Override default location of docker-compose.yml file."""
    return os.path.join(str(pytestconfig.rootdir), "./", "docker-compose.yml")


@pytest_asyncio.fixture(scope="function")
async def client(docker_service: str) -> Any:
    """Return an aiohttp client for testing."""
    # Use the Docker service URL to create a client that connects to the mocked services
    from aiohttp import ClientSession

    session = ClientSession(base_url=docker_service)
    yield session
    await session.close()


@pytest.fixture
def mock_fetch_org_dataset_catalog_scores(mocker: pytest_mock.MockFixture) -> Mock:
    """Mock fetch_org_dataset_catalog_scores."""
    mock = mocker.patch(
        "fdk_organization_bff.service.org_catalog_service.fetch_org_dataset_catalog_scores"
    )
    return mock
