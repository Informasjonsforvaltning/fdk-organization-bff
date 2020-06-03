from src.utils import IndexKey


def get_name(organization):
    org_keys = organization.keys()
    if "prefLabel" in org_keys and organization["prefLabel"] is not None:
        return organization["prefLabel"]
    else:
        return {
            "no": organization["name"]
        }


class OrganizationCatalogResponse:
    def __init__(self, organization: dict, es_results: dict, es_results_2=None):
        self.id = organization["organizationId"]
        self.organization = {
            "orgPath": organization["orgPath"],
            "name": get_name(organization),
        }
        if es_results:
            self.bucket_1 = es_results["docs_pr_publisher"]["buckets"]
        if es_results_2:
            self.bucket_2 = es_results_2["docs_pr_publisher"]["buckets"]
        self.informationmodel_count = self.get_doc_count_for_index(IndexKey.INFORMATIONMODELS) or 0
        self.dataservice_count = self.get_doc_count_for_index(IndexKey.DATASERVICES) or 0
        self.dataset_count = self.get_doc_count_for_index(IndexKey.DATASETS) or 0
        self.concept_count = self.get_doc_count_for_index(IndexKey.CONCEPT) or 0

    def get_doc_count_for_index(self, index_key: IndexKey):
        total_docs = 0
        if not hasattr(self, "bucket_1"):
            return 0
        for doc_count in self.bucket_1:
            if doc_count["key"] == index_key:
                total_docs += doc_count["doc_count"]
        if hasattr(self, "bucket_2"):
            for doc_count in self.bucket_2:
                if doc_count["key"] == index_key:
                    total_docs += doc_count["doc_count"]
        return total_docs

    def map(self) -> dict:
        response = self.__dict__
        if "bucket_1" in response.keys():
            del response["bucket_1"]
        if "bucket_2" in response.keys():
            del response["bucket_2"]
        return response


class OrganizationCatalogListResponse:
    def __init__(self, organizations, es_result: dict):
        self.es_buckets = es_result["aggregations"]['group_by_res']['buckets']
        self.response_list = []
        for organization in organizations:
            self.add_organization_catalog(organization)

    def add_organization_catalog(self, organization):
        es_bucket, es_bucket2 = self.get_es_buckets_for_organization(organization["orgPath"])
        organization_catalog = OrganizationCatalogResponse(organization=organization,
                                                           es_results=es_bucket,
                                                           es_results_2=es_bucket2)
        self.response_list.append(organization_catalog.map())

    def map_response(self) -> dict:
        return {
            "organizations": self.response_list
        }

    def keys(self) -> dict:
        return {
            "status": "OK"
        }

    def get_es_buckets_for_organization(self, orgPath: str) -> list:
        org_buckets = []
        for bucket in self.es_buckets:
            if bucket["key"] == orgPath:
                org_buckets.append(bucket.copy())
                del bucket
            elif bucket["key"] == f"/{orgPath}":
                org_buckets.append(bucket.copy())
                del bucket
            elif bucket["key"] == orgPath[1:]:
                org_buckets.append(bucket.copy())
                del bucket
            if org_buckets.__len__() == 2:
                break
        return (org_buckets + [None] * 2)[:2]
