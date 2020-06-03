import asyncio
import logging
import httpx
from httpcore import ConnectError, ConnectTimeout
from httpx import HTTPError

from src.elasticsearch import es_client, organization_aggs_query
from src.utils import ServiceKey, FetchFromServiceException, service_urls


def error_msg(reason: str, serviceKey: ServiceKey):
    return {
        "status": "error",
        "service": serviceKey,
        "reason": f"{reason}"
    }


def connection_error_msg(serviceKey: ServiceKey):
    return {
        "status": 500,
        "service": serviceKey,
        "reason": f"Connection error on {service_urls[serviceKey]}"
    }


def service_error_msg(serviceKey: ServiceKey):
    return {
        "service": serviceKey,
        "reason": f"Connection error on {service_urls[serviceKey]}"
    }


async def check_available(service: ServiceKey, header=None):
    async with httpx.AsyncClient() as client:
        try:
            result = await client.get(url=service_urls[service], headers=header, timeout=10)
            result.raise_for_status()
            return True
        except (ConnectError, HTTPError, ConnectTimeout) as err:
            error_log_msg = f"error when attempting to contact {service} on {service_urls[service]}"
            if isinstance(err, HTTPError):
                logging.error(f"HttpError: {error_log_msg}")
            else:
                logging.error(error_log_msg)
            return False


def is_ready():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    availability_requests = asyncio.gather(
        check_available(ServiceKey.ORGANIZATIONS, header={"Accept": "application/json"}),
        check_available(ServiceKey.ELASTIC_SEARCH)
    )
    org = loop.run_until_complete(availability_requests)

    if not org:

        return connection_error_msg(serviceKey=ServiceKey.ORGANIZATIONS)
    if not es_client.ping():
        breakpoint()
        return connection_error_msg(serviceKey=ServiceKey.ELASTIC_SEARCH)
    response = {
        "status": 200,
        "message": "service is running",
    }

    return response


def get_organizations():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    organizations = loop.run_until_complete(get_organizations_async())
    loop.close()
    return organizations


async def get_organizations_async():
    async with httpx.AsyncClient() as client:
        try:
            result = await client.get(url=service_urls[ServiceKey.ORGANIZATIONS],
                                      headers={"Accept": "application/json"},
                                      timeout=10)
            result.raise_for_status()
            return result.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point=ServiceKey.ORGANIZATIONS,
                url=service_urls[ServiceKey.ORGANIZATIONS]
            )


def get_organizations_fdk_content():
    try:
        return es_client.search(body=organization_aggs_query)
    except ConnectionError:
        FetchFromServiceException(execution_point="Connecting to elasticsearch")