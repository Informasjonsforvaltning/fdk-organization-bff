import asyncio
from json.decoder import JSONDecodeError
from os import environ as env
from typing import List

import logging
from xml.sax import SAXParseException

import httpx
from httpcore import ConnectError, ConnectTimeout
from httpx import HTTPError

from src.result_readers import read_sparql_table, read_alt_organization_rdf_xml, ParsedContent, parse_es_results
from src.utils import ServiceKey, FetchFromServiceException, sparql_queries, BadUriException, encode_for_sparql, \
    service_ready_urls, service_urls, BadRdfXmlException

SEARCH_FULLTEXT_HOST = env.get("SEARCH_FULLTEXT_HOST")
METADATA_QUALITY_ASSESSMENT_SERVICE_HOST = env.get("METADATA_QUALITY_ASSESSMENT_SERVICE_HOST")


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


async def get_default_org(name: str, org_id):
    orgpath = await get_orgpath_from_organization_catalog(name)
    return {
        "prefLabel": {
            "no": name
        },
        "orgPath": orgpath,
        "name": name,
        "organizationId": org_id
    }


async def get_orgpath_from_organization_catalog(name: str):
    catalog_url = f"{service_urls[ServiceKey.ORGANIZATIONS]}/orgpath/{name}"
    async with httpx.AsyncClient() as client:
        try:
            orgpath = await client.get(url=catalog_url,
                                       timeout=5)
            orgpath.raise_for_status()
            return orgpath.text
        except (HTTPError, ConnectError, TimeoutError, ConnectTimeout):
            raise FetchFromServiceException(execution_point=ServiceKey.ORGANIZATIONS,
                                            url=catalog_url,
                                            additional_info=" could not get generated orgpath"
                                            )


async def check_available(service: ServiceKey, header=None):
    async with httpx.AsyncClient() as client:
        try:
            if header:
                result = await client.get(url=service_ready_urls[service], headers=header, timeout=10)
            else:
                result = await client.get(url=service_ready_urls[service], timeout=10)
            result.raise_for_status()
            return True
        except (ConnectError, HTTPError, ConnectTimeout) as err:
            error_log_msg = f"error when attempting to contact {service} on {service_ready_urls[service]}"
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
        check_available(ServiceKey.DATASETS),
        check_available(ServiceKey.DATA_SERVICES, header={"Accept": "application/json"}),
        check_available(ServiceKey.CONCEPTS),
        check_available(ServiceKey.INFO_MODELS)
    )
    org, dataset, dataservice, concept, info_models = loop.run_until_complete(availability_requests)

    service_errors = []
    if not org:
        return connection_error_msg(serviceKey=ServiceKey.ORGANIZATIONS)
    if not dataset:
        service_errors.append(service_error_msg(serviceKey=ServiceKey.DATASETS))
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


async def get_organizations():
    async with httpx.AsyncClient() as client:
        try:
            result = await client.get(url=service_urls[ServiceKey.ORGANIZATIONS],
                                      headers={"Accept": "application/json"},
                                      timeout=5)
            return result.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point=ServiceKey.ORGANIZATIONS,
                url=service_urls[ServiceKey.ORGANIZATIONS]
            )


async def get_organization(missing_organization: ParsedContent):
    norwegian_id = missing_organization.get_norwegian_registry_id()
    try:
        if norwegian_id:
            return await get_organization_from_organization_catalogue(organization_id=norwegian_id)
        else:
            return await get_organization_from_alternative_registry(missing_organization.alternativeRegistry_iri)
    except (FetchFromServiceException, BadUriException,BadRdfXmlException):
        org_id = norwegian_id if norwegian_id else missing_organization.alternativeRegistry_iri if missing_organization.alternativeRegistry_iri else None
        return await get_default_org(name=missing_organization.name, org_id=org_id)


async def get_concepts():
    async with httpx.AsyncClient() as client:
        try:
            es_result_list = []
            i = 0
            while True:
                result = await client.get(url=f"{service_urls[ServiceKey.CONCEPTS]}",
                                          params={"returnfields": "publisher", "size": "1000", "page": i},
                                          timeout=5)
                result.raise_for_status()
                es_result_list.extend(result.json()["_embedded"]["concepts"])
                if es_result_list.__len__() >= result.json()["page"]["totalElements"]:
                    break
                else:
                    i += 1
            return parse_es_results(es_result_list, with_uri=True)
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


async def get_datasets():
    async with httpx.AsyncClient() as client:
        try:
            sparql_select_endpoint = f"{service_urls[ServiceKey.DATASETS]}/sparql/select"
            encoded_query = encode_for_sparql(sparql_queries[ServiceKey.DATASETS])
            print(encoded_query)
            url_with_query = f"{sparql_select_endpoint}?query={encoded_query}"
            result = await client.get(url=url_with_query, timeout=5)
            result.raise_for_status()
            return read_sparql_table(result.text)
        except (ConnectError, HTTPError, ConnectTimeout):
            logging.error("[datasets]: Error when attempting to execute SPARQL select query", )
            raise FetchFromServiceException(
                execution_point=ServiceKey.DATASETS,
                url=sparql_select_endpoint
            )


async def get_dataservices():
    async with httpx.AsyncClient() as client:
        try:
            sparql_select_endpoint = f"{service_urls[ServiceKey.DATA_SERVICES]}/sparql/select"
            encoded_query = encode_for_sparql(sparql_queries[ServiceKey.DATA_SERVICES])
            print(encoded_query)
            url_with_query = f"{sparql_select_endpoint}?query={encoded_query}"
            result = await client.get(url=url_with_query, timeout=5)
            result.raise_for_status()
            return read_sparql_table(result.text)
        except (ConnectError, HTTPError, ConnectTimeout):
            logging.error("[dataservices]: Error when attempting to execute SPARQL select query", )
            raise FetchFromServiceException(
                execution_point=ServiceKey.DATA_SERVICES,
                url=sparql_select_endpoint
            )


async def get_informationmodels():
    async with httpx.AsyncClient() as client:
        try:
            es_result_list = []
            while True:
                result = await client.get(url=f"{service_urls[ServiceKey.INFO_MODELS]}",
                                          params={"returnfields": "publisher", "size": "10000", "page": 0},
                                          timeout=5)
                result.raise_for_status()
                es_result_list.extend(result.json()["_embedded"]["informationmodels"])
                if es_result_list.__len__() >= result.json()["page"]["totalElements"]:
                    break

            return parse_es_results(es_result_list, with_uri=True)
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point=ServiceKey.INFO_MODELS,
                url=service_urls[ServiceKey.INFO_MODELS]
            )
        except JSONDecodeError:
            return []


async def get_organization_from_organization_catalogue(organization_id: str) -> dict:
    catalog_url = f"{service_urls[ServiceKey.ORGANIZATIONS]}/{organization_id}"
    async with httpx.AsyncClient() as client:
        try:
            organization = await client.get(url=catalog_url,
                                            headers={"Accept": "application/json"},
                                            timeout=1)
            organization.raise_for_status()
            return organization.json()
        except HTTPError as err:
            if err.response.status_code == 404:
                raise BadUriException(execution_point=ServiceKey.ORGANIZATIONS, url=catalog_url)
            else:
                raise FetchFromServiceException(execution_point=ServiceKey.ORGANIZATIONS,
                                                url=catalog_url)
        except JSONDecodeError:
            raise FetchFromServiceException(execution_point=ServiceKey.ORGANIZATIONS,
                                            url=catalog_url)
        except ConnectError:
            raise FetchFromServiceException(execution_point=ServiceKey.ORGANIZATIONS,
                                            url=catalog_url)


async def get_organization_from_alternative_registry(organization_iri):
    async with httpx.AsyncClient() as client:
        try:
            result = await client.get(url=organization_iri,
                                      headers={"Accept": "application/rdf+xml"},
                                      timeout=2)
            result.raise_for_status()
            content_from_rdf = read_alt_organization_rdf_xml(result.text)
            content_from_rdf["organizationId"] = organization_iri
            return content_from_rdf
        except HTTPError as err:
            if err.response.status_code == 404:
                raise BadUriException(execution_point=ServiceKey.ORGANIZATIONS, url=organization_iri)
            else:
                raise FetchFromServiceException(execution_point=ServiceKey.ORGANIZATIONS,
                                                url=organization_iri)
        except (SAXParseException, TypeError):
            raise BadUriException(execution_point=ServiceKey.ORGANIZATIONS,
                                  url=organization_iri)
        except (ConnectError, ConnectTimeout):
            raise FetchFromServiceException(execution_point=ServiceKey.ORGANIZATIONS,
                                            url=organization_iri)


async def search_datasets(data):
    async with httpx.AsyncClient() as client:
        url = f"{SEARCH_FULLTEXT_HOST}/datasets"

        try:
            result = await client.post(
                url=url,
                json=data,
                timeout=5
            )
            result.raise_for_status()

            return result.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            logging.error("[datasets]: search request failed")
            raise FetchFromServiceException(execution_point=ServiceKey.DATASETS, url=url)


async def get_assessments_for_entities(entity_uris: List[str]):
    async with httpx.AsyncClient() as client:
        url = f"{METADATA_QUALITY_ASSESSMENT_SERVICE_HOST}/assessment/entities"
        params = {
            "entityUris": entity_uris
        }

        try:
            result = await client.get(
                url=url,
                params=params,
                timeout=5
            )
            result.raise_for_status()

            return result.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            logging.error("[assessments]: assessments for entities request failed")
            raise FetchFromServiceException(execution_point=ServiceKey.DATASETS, url=url)


async def get_assessment_for_entity(entity_uri: str):
    async with httpx.AsyncClient() as client:
        url = f"{METADATA_QUALITY_ASSESSMENT_SERVICE_HOST}/assessment/entity"
        params = {
            "entityUri": entity_uri
        }

        try:
            result = await client.get(
                url=url,
                params=params,
                timeout=5
            )
            result.raise_for_status()

            return result.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            logging.error("[assessments]: assessment for entity request failed")
            raise FetchFromServiceException(execution_point=ServiceKey.DATASETS, url=url)


async def get_catalog_assessment_rating_for_entity_type(catalog_uri: str, entity_type: str):
    async with httpx.AsyncClient() as client:
        url = f"{METADATA_QUALITY_ASSESSMENT_SERVICE_HOST}/assessment/catalog/rating"
        params = {
            "catalogUri": catalog_uri,
            "entityType": entity_type
        }

        try:
            result = await client.get(
                url=url,
                params=params,
                timeout=5
            )
            result.raise_for_status()

            return result.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            logging.error("[assessments]: catalog assessment rating for entity type request failed")
            raise FetchFromServiceException(execution_point=ServiceKey.DATASETS, url=url)
