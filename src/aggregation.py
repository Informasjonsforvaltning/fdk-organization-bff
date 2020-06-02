import asyncio
import logging
import resource
import time

from src.responses import OrganizationCatalogResponse, OrganizationCatalogListResponse
from src.service_requests import get_organizations, get_concepts_for_organization, get_dataservices_for_organization, \
    get_datasets_for_organization, get_informationmodels_for_organization
from src.utils import FetchFromServiceException


def get_organization_catalog_list():
    response_list = OrganizationCatalogListResponse()
    try:
        organizations = get_organizations()
        response_list.org_list = get_organization_catalog_list_async(organizations)
        return response_list
    except FetchFromServiceException as err:
        return err.__dict__


def get_organization_catalog_list_async(organizations):
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    os_max_open_files, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (2000, hard))
    start_time = time.time()
    collection_tasks = asyncio.gather(*[get_catalog_for_organization(org) for org in organizations])

    result = loop.run_until_complete(collection_tasks)
    logging.debug("organization catalog collection took {0} seconds".format(time.time()-start_time))
    return result


async def get_catalog_for_organization(organization):
    old_format = get_old_org_path_format(organization["orgPath"])
    new_format = get_new_org_path_format(organization["orgPath"])
    organization["orgPath"] = old_format
    content_requests = asyncio.gather(get_concepts_for_organization(old_format),
                                      get_datasets_for_organization(old_format),
                                      get_dataservices_for_organization(old_format),
                                      get_informationmodels_for_organization(new_format)
                                      )
    concepts, datasets, dataservices, informationmodels = await content_requests
    return OrganizationCatalogResponse(
        organization=organization,
        concepts=concepts,
        informationmodels=informationmodels,
        datasets=datasets,
        dataservices=dataservices
    ).__dict__


def get_old_org_path_format(org_path: str):
    if org_path.startswith("/"):
        return org_path
    else:
        return f"/{org_path}"


def get_new_org_path_format(orgPath: str):
    if orgPath.startswith("/"):
        return orgPath[1:]
    else:
        return orgPath
