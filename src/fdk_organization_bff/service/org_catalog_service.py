"""Service layer module for fdk-organization-bff."""
import asyncio
import logging
from typing import Dict, List, Optional, Union

from aiohttp import ClientSession

from fdk_organization_bff.classes import (
    FilterEnum,
    OrganizationCatalog,
    OrganizationCatalogList,
)
from fdk_organization_bff.config import Config
from fdk_organization_bff.sparql.dataservice_queries import (
    build_dataservices_by_publisher_query,
    build_org_dataservice_query,
)
from fdk_organization_bff.sparql.dataset_queries import (
    build_datasets_by_publisher_query,
    build_nap_datasets_by_publisher_query,
    build_nap_org_datasets_query,
    build_org_datasets_query,
)
from fdk_organization_bff.utils.mappers import (
    count_list_from_sparql_response,
    map_org_dataservices,
    map_org_datasets,
    map_org_details,
    map_org_summaries,
)
from fdk_organization_bff.utils.utils import url_with_params


async def fetch_json_data(
    url: str, params: Optional[Dict[str, str]], session: ClientSession
) -> Optional[Union[Dict, List]]:
    """Fetch json data from url."""
    async with session.get(url_with_params(url, params)) as response:
        return await response.json() if response.status == 200 else None


async def fetch_org_cat_data(id: str, session: ClientSession) -> Dict:
    """Fetch organization data from organization-catalogue."""
    url = f"{Config.org_cat_uri()}/organizations/{id}"
    org_cat_data = await fetch_json_data(url, None, session)
    if org_cat_data and isinstance(org_cat_data, Dict):
        return org_cat_data
    else:
        return dict()


async def fetch_all_organizations(session: ClientSession) -> Dict:
    """Fetch all organizations from organization-catalogue."""
    url = f"{Config.org_cat_uri()}/organizations"
    org_list = await fetch_json_data(url, None, session)
    return {org["organizationId"]: org for org in org_list} if org_list else dict()


async def fetch_brreg_data(id: str, session: ClientSession) -> Dict:
    """Fetch organization data from Enhetsregisteret."""
    url = f"{Config.data_brreg_uri()}/enhetsregisteret/api/enheter/{id}"
    brreg_data = await fetch_json_data(url, None, session)
    if brreg_data and isinstance(brreg_data, Dict):
        return brreg_data
    else:
        return dict()


async def query_sparql_service(query: str, session: ClientSession) -> Dict:
    """Query fdk-sparql-service."""
    url = f"{Config.sparql_uri()}"
    params = {"query": query}
    datasets = await fetch_json_data(url, params, session)
    if datasets and isinstance(datasets, Dict):
        return datasets
    else:
        return dict()


async def query_publisher_datasets(
    id: str, filter: FilterEnum, session: ClientSession
) -> List:
    """Query publisher datasets from fdk-sparql-service."""
    if filter is FilterEnum.NAP:
        query = build_nap_org_datasets_query(id)
    else:
        query = build_org_datasets_query(id)

    response = await query_sparql_service(query, session)
    results = response.get("results")
    org_datasets = results.get("bindings") if results else []
    return org_datasets if org_datasets else []


async def query_publisher_dataservices(
    id: str, filter: FilterEnum, session: ClientSession
) -> List:
    """Query publisher dataservices from fdk-sparql-service."""
    if filter is FilterEnum.NAP:
        return list()
    else:
        response = await query_sparql_service(build_org_dataservice_query(id), session)
        results = response.get("results")
        org_dataservices = results.get("bindings") if results else []
        return org_dataservices if org_dataservices else []


async def query_all_dataservices_ordered_by_publisher(
    filter: FilterEnum, session: ClientSession
) -> List:
    """Query all dataservices from fdk-sparql-service and order by publisher."""
    if filter is FilterEnum.NAP:
        return list()
    else:
        response = await query_sparql_service(
            build_dataservices_by_publisher_query(), session
        )
        return count_list_from_sparql_response(response)


async def query_all_datasets_ordered_by_publisher(
    filter: FilterEnum, session: ClientSession
) -> List:
    """Query all datasets from fdk-sparql-service and order by publisher."""
    if filter is FilterEnum.NAP:
        query = build_nap_datasets_by_publisher_query()
    else:
        query = build_datasets_by_publisher_query()

    response = await query_sparql_service(query, session)
    return count_list_from_sparql_response(response)


async def fetch_org_dataset_catalog_rating(
    id: str, filter: FilterEnum, session: ClientSession
) -> Dict:
    """Fetch rating for organization's dataset catalog from fdk-metadata-quality-service."""
    url = f"{Config.metadata_uri()}/rating/catalog"
    params = {"entityType": "dataset", "catalogId": id}

    if filter is FilterEnum.NAP:
        params.update({"contexts": "NAP"})

    rating = await fetch_json_data(url, params, session)

    if rating and isinstance(rating, Dict):
        return rating
    else:
        return dict()


async def get_organization_catalog(
    id: str, filter: FilterEnum
) -> Optional[OrganizationCatalog]:
    """Return specific organization catalog."""
    logging.debug(f"Fetching catalog for organization with id {id}")

    async with ClientSession() as session:
        (
            org_cat_data,
            brreg_data,
            org_datasets,
            org_datasets_rating,
            org_dataservices,
        ) = await asyncio.gather(
            asyncio.ensure_future(fetch_org_cat_data(id, session)),
            asyncio.ensure_future(fetch_brreg_data(id, session)),
            asyncio.ensure_future(query_publisher_datasets(id, filter, session)),
            asyncio.ensure_future(
                fetch_org_dataset_catalog_rating(id, filter, session)
            ),
            asyncio.ensure_future(query_publisher_dataservices(id, filter, session)),
        )

    """Respond with None if no datasets are found."""
    if org_datasets and len(org_datasets) > 0:
        return OrganizationCatalog(
            organization=map_org_details(
                org_cat_data=org_cat_data, brreg_data=brreg_data
            ),
            datasets=map_org_datasets(
                org_datasets=org_datasets,
                assessment_data=org_datasets_rating,
            ),
            dataservices=map_org_dataservices(org_dataservices=org_dataservices),
        )
    else:
        return None


async def get_organization_catalogs(filter: FilterEnum) -> OrganizationCatalogList:
    """Return all organization catalogs."""
    logging.debug("Fetching all catalogs")

    async with ClientSession() as session:
        organizations, datasets, dataservices = await asyncio.gather(
            asyncio.ensure_future(fetch_all_organizations(session)),
            asyncio.ensure_future(
                query_all_datasets_ordered_by_publisher(filter, session)
            ),
            asyncio.ensure_future(
                query_all_dataservices_ordered_by_publisher(filter, session)
            ),
        )
    return OrganizationCatalogList(
        organizations=map_org_summaries(
            organizations=organizations, datasets=datasets, dataservices=dataservices
        )
    )
