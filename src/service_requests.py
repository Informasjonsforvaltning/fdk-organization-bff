import asyncio
import os
from json.decoder import JSONDecodeError
import logging
import httpx
from httpcore import ConnectError, ConnectTimeout
from httpx import HTTPError
from src.utils import ServiceKey, FetchFromServiceException


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


service_urls = {
    ServiceKey.ORGANIZATIONS: os.getenv('ORGANIZATION_CATALOG_URL') or "http://localhost:8080/organizations",
    ServiceKey.INFO_MODELS: os.getenv('INFORMATIONMODELS_HARVESTER_URL') or "http://localhost:8080/informationmodels",
    ServiceKey.DATA_SERVICES: os.getenv('DATASERVICE_HARVESTER_URL') or "http://localhost:8080/apis",
    ServiceKey.DATA_SETS: os.getenv('DATASET_HARVESTER_URL') or "http://localhost:8080/datasets",
    ServiceKey.CONCEPTS: os.getenv('CONCEPT_HARVESTER_URL') or "http://localhost:8080/concepts"

}


async def check_available(service: ServiceKey, header=None):
    async with httpx.AsyncClient() as client:
        try:
            if header:
                result = await client.get(url=service_urls[service], headers=header, timeout=10)
            else:
                result = await client.get(url=service_urls[service], timeout=10)
            result.raise_for_status()
            return True
        except (ConnectError, HTTPError, ConnectTimeout) as err:
            error_log_msg = f"error when attempting to contact {service} on {service_urls[service]}"
            if isinstance(err, HTTPError):
                logging.error(f"{error_log_msg}: HttpStatus: {result.status_code}")
            else:
                logging.error(error_log_msg)
            return False


def is_ready():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    availability_requests = asyncio.gather(
        check_available(ServiceKey.ORGANIZATIONS, header={"Accept": "application/json"}),
        check_available(ServiceKey.DATA_SETS, header={"Accept": "application/json"}),
        check_available(ServiceKey.DATA_SERVICES, header={"Accept": "application/json"}),
        check_available(ServiceKey.CONCEPTS),
        check_available(ServiceKey.INFO_MODELS)
    )
    org, dataset, dataservice, concept, info_models = loop.run_until_complete(availability_requests)

    service_errors = []
    if not org:
        return connection_error_msg(serviceKey=ServiceKey.ORGANIZATIONS)
    if not dataset:
        service_errors.append(service_error_msg(serviceKey=ServiceKey.DATA_SETS))
    if not dataservice:
        service_errors.append(service_error_msg(serviceKey=ServiceKey.DATA_SERVICES))
    if not info_models:
        service_errors.append(service_error_msg(serviceKey=ServiceKey.INFO_MODELS))
    if not concept:
        service_errors.append(service_error_msg(serviceKey=ServiceKey.CONCEPTS))
    response = {
        "status": 200,
        "message": "service is running",
    }
    if service_errors.__len__() > 0:
        response["external_errors"] = service_errors
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


async def get_concepts_for_organization(orgPath):
    async with httpx.AsyncClient() as client:
        try:
            result = await client.get(url=f"{service_urls[ServiceKey.CONCEPTS]}?orgPath={orgPath}",
                                      timeout=10)
            result.raise_for_status()
            return result.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point=ServiceKey.CONCEPTS,
                url=service_urls[ServiceKey.CONCEPTS]
            )
        except JSONDecodeError:
            return {
                "page": {
                    "totalElements": 0
                }
            }


async def get_datasets_for_organization(orgPath):
    async with httpx.AsyncClient() as client:
        try:
            result = await client.get(url=f"{service_urls[ServiceKey.DATA_SETS]}?orgPath={orgPath}",
                                      headers={"Accept": "application/json"},
                                      timeout=10)
            result.raise_for_status()
            return result.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point=ServiceKey.DATA_SETS,
                url=service_urls[ServiceKey.DATA_SETS]
            )
        except JSONDecodeError:
            return {
                "page": {
                    "totalElements": 0
                }
            }


async def get_dataservices_for_organization(orgPath):
    async with httpx.AsyncClient() as client:
        try:
            result = await client.get(url=f"{service_urls[ServiceKey.DATA_SERVICES]}?orgPath={orgPath}",
                                      timeout=10)
            result.raise_for_status()
            return result.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point=ServiceKey.CONCEPTS,
                url=service_urls[ServiceKey.CONCEPTS]
            )
        except JSONDecodeError:
            return {
                "page": {
                    "totalElements": 0
                }
            }


async def get_informationmodels_for_organization(orgPath):
    async with httpx.AsyncClient() as client:
        try:
            result = await client.get(url=f"{service_urls[ServiceKey.INFO_MODELS]}?orgPath={orgPath}",
                                      timeout=10)
            result.raise_for_status()
            if result.json()["page"]["totalElements"] == 0:
                result = await client.get(url=f"{service_urls[ServiceKey.INFO_MODELS]}?orgPath=/{orgPath}",
                                          timeout=10)
                result.raise_for_status()
            return result.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point=ServiceKey.CONCEPTS,
                url=service_urls[ServiceKey.CONCEPTS]
            )
        except JSONDecodeError:
            return {
                "page": {
                    "totalElements": 0
                }
            }


def get_org_path_for_old_harvester(orgPath: str):
    if orgPath.startswith("/"):
        return orgPath
    else:
        return f"/{orgPath}"
