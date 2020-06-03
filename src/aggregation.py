import asyncio

from src.responses import OrganizationCatalogResponse, OrganizationCatalogListResponse
from src.service_requests import get_organizations, get_organizations_fdk_content
from src.utils import FetchFromServiceException


def get_organization_catalog_list():
    try:
        organizations = get_organizations()
        es_result = get_organizations_fdk_content()
        return OrganizationCatalogListResponse(organizations=organizations, es_result=es_result)
    except FetchFromServiceException as err:
        return err.__dict__
