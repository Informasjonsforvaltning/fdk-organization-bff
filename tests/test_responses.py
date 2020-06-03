import json
import os

import pytest

from src.responses import OrganizationCatalogResponse, OrganizationCatalogListResponse
from tests.test_data import org_5, org4, org_1


@pytest.mark.unit
def test_organization_catalog_response():
    expected = {
        "id": "915429785",
        "organization": {
            "name": {
                "no": "POLITI- OG LENSMANNSETATEN"
            },
            "orgPath": "STAT/972417831/915429785"
        },
        "dataset_count": 841,
        "concept_count": 354,
        "dataservice_count": 100,
        "informationmodel_count": 2
    }

    test_org = {
        "key": "/STAT/972417831/915429785",
        "doc_count": 1297,
        "docs_pr_publisher": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
            "buckets": [
                {
                    "key": "concepts",
                    "doc_count": 354
                },
                {
                    "key": "datasets",
                    "doc_count": 841
                },
                {
                    "key": "dataservices",
                    "doc_count": 100
                },
                {
                    "key": "informationmodels",
                    "doc_count": 2
                }
            ]
        }
    }

    result = OrganizationCatalogResponse(organization=org_5, es_results=test_org).map()
    assert result == expected


@pytest.mark.unit
def test_organization_catalog_response_with_no_datasets():
    expected = {
        "id": "915429785",
        "organization": {
            "name": {
                "no": "POLITI- OG LENSMANNSETATEN"
            },
            "orgPath": "STAT/972417831/915429785"
        },
        "dataset_count": 0,
        "concept_count": 354,
        "dataservice_count": 100,
        "informationmodel_count": 2
    }

    test_org = {
        "key": "/STAT/972417831/915429785",
        "doc_count": 1297,
        "docs_pr_publisher": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
            "buckets": [
                {
                    "key": "concepts",
                    "doc_count": 354
                },
                {
                    "key": "dataservices",
                    "doc_count": 100
                },
                {
                    "key": "informationmodels",
                    "doc_count": 2
                }
            ]
        }
    }
    result = OrganizationCatalogResponse(organization=org_5, es_results=test_org).map()
    assert result == expected


@pytest.mark.unit
def test_organization_catalog_response_with_no_content():
    expected = {
        "id": "915429785",
        "organization": {
            "name": {
                "no": "POLITI- OG LENSMANNSETATEN"
            },
            "orgPath": "STAT/972417831/915429785"
        },
        "dataset_count": 0,
        "concept_count": 0,
        "dataservice_count": 0,
        "informationmodel_count": 0
    }

    test_org = {
        "key": "/STAT/972417831/915429785",
        "doc_count": 0,
        "docs_pr_publisher": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
            "buckets": [
                {
                    "key": "concepts",
                    "doc_count": 0
                },
                {
                    "key": "dataservices",
                    "doc_count": 0
                },
                {
                    "key": "informationmodels",
                    "doc_count": 0
                }
            ]
        }
    }

    result = OrganizationCatalogResponse(organization=org_5, es_results=test_org).map()
    assert result == expected


@pytest.mark.unit
def test_organization_without_prefLabel_catalog_response():
    expected = {
        "id": "961181399",
        "organization": {
            "name": {
                "no": "ARKIVVERKET"
            },
            "orgPath": "STAT/972417866/961181399"
        },
        "dataset_count": 3,
        "concept_count": 0,
        "dataservice_count": 100,
        "informationmodel_count": 200
    }
    test_es_result = {
        "key": "/STAT/972417866/961181399",
        "doc_count": 0,
        "docs_pr_publisher": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
            "buckets": [
                {
                    "key": "concepts",
                    "doc_count": 0
                },
                {
                    "key": "dataservices",
                    "doc_count": 100
                },
                {
                    "key": "datasets",
                    "doc_count": 3
                },
                {
                    "key": "informationmodels",
                    "doc_count": 200
                }
            ]
        }
    }

    result = OrganizationCatalogResponse(organization=org4, es_results=test_es_result).map()
    assert result == expected


@pytest.mark.unit
def test_organization_catalog_response_with_two_es_results():
    es_res = {
        "key": "STAT/912660680/974760673",
        "doc_count": 25,
        "docs_pr_publisher": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
            "buckets": [
                {
                    "key": "informationmodels",
                    "doc_count": 88
                }
            ]
        }
    }
    es_res_2 = {
        "key": "/STAT/912660680/974760673",
        "doc_count": 251,
        "docs_pr_publisher": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
            "buckets": [
                {
                    "key": "informationmodels",
                    "doc_count": 1
                },
                {
                    "key": "concepts",
                    "doc_count": 52
                },
                {
                    "key": "dataservices",
                    "doc_count": 10
                }
            ]
        }
    }
    result = OrganizationCatalogResponse(organization=org_1, es_results=es_res, es_results_2=es_res_2).map()
    assert result["informationmodel_count"] == 89
    assert result["concept_count"] == 52
    assert result["dataset_count"] == 0
    assert result["dataservice_count"] == 10

@pytest.mark.unit
def test_organization_catalog_list_response():
    test_data_file = open(f"{os.getcwd().split('/tests')[0]}/mock/different_orgpath_aggregations.json")
    es_test_result = json.loads(test_data_file.read())

    result = OrganizationCatalogListResponse(organizations=[org_1, org_5, org4],
                                             es_result=es_test_result).map_response()
    assert "organizations" in result.keys()
    assert result["organizations"].__len__() == 3


@pytest.mark.unit
def test_organization_catalog_list_response_correct_calculation():
    test_data_file = open(f"{os.getcwd().split('/tests')[0]}/mock/different_orgpath_aggregations_numbers.json")
    es_test_result = json.loads(test_data_file.read())

    result = OrganizationCatalogListResponse(organizations=[org_1],
                                             es_result=es_test_result).map_response()
    assert "organizations" in result.keys()
    list_result = result["organizations"]
    assert list_result.__len__() == 1
    org_result = list_result[0]
    assert org_result["informationmodel_count"] == 25
    assert org_result["concept_count"] == 241
    assert org_result["dataset_count"] == 10
    assert org_result["dataservice_count"] == 0
