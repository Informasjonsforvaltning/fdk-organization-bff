from elasticsearch import Elasticsearch

from src.utils import service_urls, ServiceKey


es_client = Elasticsearch(service_urls[ServiceKey.ELASTIC_SEARCH])

organization_aggs_query = {
    "size": 0,
    "aggs": {
        "group_by_res": {
            "terms": {
                "field": "publisher.orgPath",
                "missing": "MISSING",
                "size": 1000000000
            },
            "aggs": {
                "docs_pr_publisher": {
                    "terms": {
                        "field": "_index"
                    }
                }
            }
        }
    }
}