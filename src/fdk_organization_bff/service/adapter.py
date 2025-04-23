"""Adapter layer module for fdk-organization-bff."""

from typing import Dict, List, Optional, Union

from aiohttp import ClientSession

from fdk_organization_bff.classes import FilterEnum
from fdk_organization_bff.config import Config
from fdk_organization_bff.sparql.concept_queries import (
    build_concepts_by_publisher_query,
    build_org_concepts_query,
)
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
from fdk_organization_bff.sparql.informationmodel_queries import (
    build_informationmodels_by_publisher_query,
    build_org_informationmodels_query,
)
from fdk_organization_bff.utils.mappers import count_list_from_sparql_response
from fdk_organization_bff.utils.utils import url_with_params


async def fetch_json_data(
    url: str, params: Optional[Dict[str, str]], session: ClientSession
) -> Optional[Union[Dict, List]]:
    """Fetch json data from url."""
    async with session.get(
        url_with_params(url, params), headers={"Accept": "application/json"}
    ) as response:
        return await response.json() if response.status == 200 else None


async def fetch_json_data_with_post(
    url: str, data: Dict, session: ClientSession
) -> Optional[Union[Dict, List]]:
    """Fetch json data from url."""
    async with session.post(
        url, json=data, headers={"Accept": "application/json"}
    ) as response:
        return await response.json() if response.status == 200 else None


async def fetch_org_cat_data(id: str, session: ClientSession) -> Dict:
    """Fetch organization data from organization-catalog."""
    url = f"{Config.org_cat_uri()}/organizations/{id}"
    org_cat_data = await fetch_json_data(url, None, session)
    if org_cat_data and isinstance(org_cat_data, Dict):
        return org_cat_data
    else:
        return dict()


async def fetch_organizations_from_organization_catalog(
    session: ClientSession, org_path: Optional[str]
) -> Dict:
    """Fetch organizations from organization-catalog."""
    params = {"orgPath": org_path} if org_path else None
    url = f"{Config.org_cat_uri()}/organizations"
    org_list = await fetch_json_data(url, params, session)
    return {org["organizationId"]: org for org in org_list} if org_list else dict()


async def fetch_brreg_data(id: str, session: ClientSession) -> Dict:
    """Fetch organization data from Enhetsregisteret."""
    url = f"{Config.data_brreg_uri()}/enhetsregisteret/api/enheter/{id}"
    brreg_data = await fetch_json_data(url, None, session)
    if brreg_data and isinstance(brreg_data, Dict):
        return brreg_data
    else:
        return dict()


async def fetch_reference_data(path: str, session: ClientSession) -> Dict:
    """Fetch reference data from reference-data."""
    url = f"{Config.reference_data_uri()}/reference-data{path}"
    reference_data = await fetch_json_data(url, None, session)
    if reference_data and isinstance(reference_data, Dict):
        return reference_data
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


async def query_publisher_informationmodels(
    id: str, filter: FilterEnum, session: ClientSession
) -> List:
    """Query publisher informationmodels from fdk-sparql-service."""
    if filter is FilterEnum.NAP:
        return list()

    results = (
        await query_sparql_service(build_org_informationmodels_query(id), session)
    ).get("results")
    org_concepts = results.get("bindings") if results else []

    return org_concepts if org_concepts else []


async def query_publisher_concepts(
    id: str, filter: FilterEnum, session: ClientSession
) -> List:
    """Query publisher concepts from fdk-sparql-service."""
    if filter is FilterEnum.NAP:
        return list()

    results = (await query_sparql_service(build_org_concepts_query(id), session)).get(
        "results"
    )
    org_concepts = results.get("bindings") if results else []

    return org_concepts if org_concepts else []


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


async def query_all_concepts_ordered_by_publisher(
    filter: FilterEnum, session: ClientSession
) -> List:
    """Query all dataservices from fdk-sparql-service and order by publisher."""
    if filter is FilterEnum.NAP:
        return list()
    else:
        response = await query_sparql_service(
            build_concepts_by_publisher_query(), session
        )
        return count_list_from_sparql_response(response)


async def query_all_informationmodels_ordered_by_publisher(
    filter: FilterEnum, session: ClientSession
) -> List:
    """Query all dataservices from fdk-sparql-service and order by publisher."""
    if filter is FilterEnum.NAP:
        return list()
    else:
        response = await query_sparql_service(
            build_informationmodels_by_publisher_query(), session
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


async def fetch_org_dataset_catalog_scores(
    uris: List[str], session: ClientSession
) -> Dict:
    """Fetch rating for organization's dataset catalog from fdk-metadata-quality-service."""
    url = f"{Config.metadata_uri()}/api/scores"

    if len(uris) > 500:
        return dict()
    else:
        scores = await fetch_json_data_with_post(url, {"datasets": uris}, session)

        if scores and isinstance(scores, Dict):
            return scores
        else:
            return dict()
