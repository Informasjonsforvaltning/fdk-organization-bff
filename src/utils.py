import os


class ServiceKey:
    ORGANIZATIONS = "organization"
    ELASTIC_SEARCH = "elasticsearch"


class IndexKey:
    CONCEPT = "concepts"
    DATASERVICES = "dataservices"
    DATASETS = "datasets"
    INFORMATIONMODELS = "informationmodels"


service_urls = {
    ServiceKey.ORGANIZATIONS: os.getenv('ORGANIZATION_CATALOG_URL') or "http://localhost:8080/organizations",
    ServiceKey.ELASTIC_SEARCH: f"{os.getenv('ELASTIC_HOST') or 'localhost'}:{os.getenv('ELASTIC_PORT') or 9200}"
}


class FetchFromServiceException(Exception):
    def __init__(self, execution_point: ServiceKey, url: str = None):
        self.status = "error"
        self.reason = f"Connection error when attempting to fetch {execution_point} from {url}"
