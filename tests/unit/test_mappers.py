"""Unit test cases for mappers."""

from typing import Any
from unittest.mock import patch

import pytest

from fdk_organization_bff.classes import (
    CatalogQualityScore,
    OrganizationCatalogSummary,
    OrganizationDataservices,
    OrganizationDatasets,
)
from fdk_organization_bff.utils.mappers import (
    add_org_counts,
    categorise_summaries_by_municipality,
    categorise_summaries_by_parent_org,
    count_list_from_sparql_response,
    empty_datasets,
    map_catalog_quality_score,
    map_org_dataservices,
    map_org_datasets,
    map_org_details,
    map_org_summaries,
    map_org_summary,
    org_and_count_value_from_sparql_response,
    org_is_stat_fylk_or_komm,
    remove_empty_summaries,
)


@pytest.mark.unit
def test_map_catalog_quality_score_handles_bad_data() -> None:
    """Check that map_catalog_quality_score handles bad data."""
    rating_0 = map_catalog_quality_score(
        {"aggregations": [{"max_score": "100"}, {"max_score": "100"}]}
    )
    rating_1 = map_catalog_quality_score(
        {"aggregations": [{"score": "100"}, {"score": "100"}]}
    )
    rating_2 = map_catalog_quality_score({"aggregations": []})
    rating_3 = map_catalog_quality_score(
        {
            "aggregations": [
                {"score": "56", "max_score": "str"},
                {"score": "56", "max_score": "100"},
            ]
        }
    )
    rating_4 = map_catalog_quality_score(
        {
            "aggregations": [
                {"score": "str", "max_score": "100"},
                {"score": "56", "max_score": "100"},
            ]
        }
    )
    rating_5 = map_catalog_quality_score(
        {
            "aggregations": [
                {"score": "56", "max_score": "100"},
                {"score": "56", "max_score": "100"},
            ]
        }
    )

    assert rating_0 is None
    assert rating_1 is None
    assert rating_2 is None
    assert rating_3 is None
    assert rating_4 is None
    assert rating_5 == CatalogQualityScore(score=112, percentage=56)


@pytest.mark.unit
def test_map_catalog_quality_score_with_valid_data() -> None:
    """Test map_catalog_quality_score with valid data."""
    result = map_catalog_quality_score(
        {
            "aggregations": [
                {"score": "80", "max_score": "100"},
                {"score": "20", "max_score": "100"},
            ]
        }
    )
    assert result == CatalogQualityScore(score=100, percentage=50)


@pytest.mark.unit
def test_map_catalog_quality_score_with_no_aggregations() -> None:
    """Test map_catalog_quality_score with no aggregations."""
    result = map_catalog_quality_score({})
    assert result is None


@pytest.mark.unit
def test_map_org_details_handles_missing_data() -> None:
    """Response from map_org_details is None when data is missing."""
    details = map_org_details({}, {})

    assert details is None


@pytest.mark.unit
def test_map_org_details_with_valid_data() -> None:
    """Test map_org_details with valid data."""
    org_cat_data = {
        "organizationId": "12345678",
        "prefLabel": {"nb": "Test Org"},
        "name": "Test Organization",
        "orgPath": "/test/path",
    }
    brreg_data = {
        "organisasjonsform": {"beskrivelse": "Test Form"},
        "naeringskode1": {"kode": "123", "beskrivelse": "Test Industry"},
        "institusjonellSektorkode": {"kode": "456", "beskrivelse": "Test Sector"},
        "hjemmeside": "https://test.org",
        "antallAnsatte": "100",
    }

    result = map_org_details(org_cat_data, brreg_data)

    assert result is not None
    assert result.organizationId == "12345678"
    assert result.name == "Test Organization"
    assert result.orgPath == "/test/path"
    assert result.orgType == "Test Form"
    assert result.sectorCode == "456 Test Sector"
    assert result.industryCode == "123 Test Industry"
    assert result.homepage == "https://test.org"
    assert result.numberOfEmployees == 100
    assert result.icon == "https://orglogo.digdir.no/api/logo/org/12345678"


@pytest.mark.unit
def test_map_org_details_with_partial_brreg_data() -> None:
    """Test map_org_details with partial brreg data."""
    org_cat_data = {"organizationId": "12345678", "name": "Test Organization"}
    brreg_data = {"organisasjonsform": {"beskrivelse": "Test Form"}}

    result = map_org_details(org_cat_data, brreg_data)

    assert result is not None
    assert result.organizationId == "12345678"
    assert result.name == "Test Organization"
    assert result.orgType == "Test Form"
    assert result.sectorCode is None
    assert result.industryCode is None
    assert result.homepage is None
    assert result.numberOfEmployees is None


@pytest.mark.unit
def test_map_org_details_with_no_brreg_data() -> None:
    """Test map_org_details with no brreg data."""
    org_cat_data = {"organizationId": "12345678", "name": "Test Organization"}

    result = map_org_details(org_cat_data, {})

    assert result is not None
    assert result.organizationId == "12345678"
    assert result.name == "Test Organization"
    assert result.orgType is None
    assert result.sectorCode is None
    assert result.industryCode is None
    assert result.homepage is None
    assert result.numberOfEmployees is None


@patch("fdk_organization_bff.utils.utils.get_today")
@pytest.mark.unit
def test_map_org_datasets_with_valid_data(mock_today: Any) -> None:
    """Test map_org_datasets with valid data."""
    import datetime

    mock_today.return_value = datetime.date(2024, 1, 15)

    org_datasets = [
        {
            "dataset": {"value": "http://example.com/dataset1"},
            "issued": {"value": "2024-01-12T10:00:00.000Z"},
            "isAuthoritative": {"value": "true"},
            "isOpenData": {"value": "true"},
        },
        {
            "dataset": {"value": "http://example.com/dataset2"},
            "issued": {"value": "2024-01-05T10:00:00.000Z"},
            "isAuthoritative": {"value": "false"},
            "isOpenData": {"value": "false"},
        },
    ]

    score_data = {"aggregations": [{"score": "80", "max_score": "100"}]}

    result = map_org_datasets(org_datasets, score_data)

    assert isinstance(result, OrganizationDatasets)
    assert result.totalCount == 2
    assert result.newCount == 1
    assert result.authoritativeCount == 1
    assert result.openCount == 1
    assert result.quality is not None


@pytest.mark.unit
def test_map_org_datasets_with_empty_data() -> None:
    """Test map_org_datasets with empty data."""
    result = map_org_datasets([], {})

    assert isinstance(result, OrganizationDatasets)
    assert result.totalCount == 0
    assert result.newCount == 0
    assert result.authoritativeCount == 0
    assert result.openCount == 0
    assert result.quality is None


@patch("fdk_organization_bff.utils.utils.get_today")
@pytest.mark.unit
def test_map_org_dataservices_with_valid_data(mock_today: Any) -> None:
    """Test map_org_dataservices with valid data."""
    import datetime

    mock_today.return_value = datetime.date(2024, 1, 15)

    org_dataservices = [
        {
            "service": {"value": "http://example.com/service1"},
            "issued": {"value": "2024-01-12T10:00:00.000Z"},
        },
        {
            "service": {"value": "http://example.com/service2"},
            "issued": {"value": "2024-01-05T10:00:00.000Z"},
        },
    ]

    result = map_org_dataservices(org_dataservices)

    assert isinstance(result, OrganizationDataservices)
    assert result.totalCount == 2
    assert result.newCount == 1


@pytest.mark.unit
def test_map_org_dataservices_with_empty_data() -> None:
    """Test map_org_dataservices with empty data."""
    result = map_org_dataservices([])

    assert isinstance(result, OrganizationDataservices)
    assert result.totalCount == 0
    assert result.newCount == 0


@pytest.mark.unit
def test_empty_datasets() -> None:
    """Test empty_datasets function."""
    result = empty_datasets()

    assert isinstance(result, OrganizationDatasets)
    assert result.totalCount == 0
    assert result.newCount == 0
    assert result.authoritativeCount == 0
    assert result.openCount == 0
    assert result.quality is None


@pytest.mark.unit
def test_count_list_from_sparql_response_with_valid_data() -> None:
    """Test count_list_from_sparql_response with valid data."""
    sparql_response = {
        "results": {
            "bindings": [
                {"organizationNumber": {"value": "12345678"}, "count": {"value": "10"}},
                {"organizationNumber": {"value": "87654321"}, "count": {"value": "5"}},
            ]
        }
    }

    result = count_list_from_sparql_response(sparql_response)

    assert len(result) == 2
    assert result[0] == {"org": "12345678", "count": "10"}
    assert result[1] == {"org": "87654321", "count": "5"}


@pytest.mark.unit
def test_count_list_from_sparql_response_with_no_results() -> None:
    """Test count_list_from_sparql_response with no results."""
    sparql_response: dict[str, dict[str, list]] = {"results": {"bindings": []}}

    result = count_list_from_sparql_response(sparql_response)

    assert result == []


@pytest.mark.unit
def test_count_list_from_sparql_response_with_no_bindings() -> None:
    """Test count_list_from_sparql_response with no bindings."""
    sparql_response: dict[str, dict] = {"results": {}}

    result = count_list_from_sparql_response(sparql_response)

    assert result == []


@pytest.mark.unit
def test_count_list_from_sparql_response_with_no_results_key() -> None:
    """Test count_list_from_sparql_response with no results key."""
    sparql_response: dict = {}

    result = count_list_from_sparql_response(sparql_response)

    assert result == []


@pytest.mark.unit
def test_org_and_count_value_from_sparql_response_with_valid_data() -> None:
    """Test org_and_count_value_from_sparql_response with valid data."""
    sparql_response = {
        "organizationNumber": {"value": "12345678"},
        "count": {"value": "10"},
    }

    result = org_and_count_value_from_sparql_response(sparql_response)

    assert result == {"org": "12345678", "count": "10"}


@pytest.mark.unit
def test_org_and_count_value_from_sparql_response_with_spaces() -> None:
    """Test org_and_count_value_from_sparql_response with spaces in org number."""
    sparql_response = {
        "organizationNumber": {"value": "123 456 78"},
        "count": {"value": "10"},
    }

    result = org_and_count_value_from_sparql_response(sparql_response)

    assert result == {"org": "12345678", "count": "10"}


@pytest.mark.unit
def test_org_and_count_value_from_sparql_response_with_missing_org() -> None:
    """Test org_and_count_value_from_sparql_response with missing org."""
    sparql_response = {"count": {"value": "10"}}

    result = org_and_count_value_from_sparql_response(sparql_response)

    assert result is None


@pytest.mark.unit
def test_org_and_count_value_from_sparql_response_with_missing_count() -> None:
    """Test org_and_count_value_from_sparql_response with missing count."""
    sparql_response = {"organizationNumber": {"value": "12345678"}}

    result = org_and_count_value_from_sparql_response(sparql_response)

    assert result is None


@pytest.mark.unit
def test_org_and_count_value_from_sparql_response_with_empty_values() -> None:
    """Test org_and_count_value_from_sparql_response with empty values."""
    sparql_response = {"organizationNumber": {"value": ""}, "count": {"value": ""}}

    result = org_and_count_value_from_sparql_response(sparql_response)

    assert result is None


@pytest.mark.unit
def test_map_org_summary_with_valid_data() -> None:
    """Test map_org_summary with valid data."""
    org_id = "12345678"
    org_counts: dict[str, str] = {
        "datasets": "10",
        "dataservices": "5",
        "concepts": "3",
        "informationmodels": "2",
    }
    org_data = {
        "name": "Test Org",
        "prefLabel": {"nb": "Test Org"},
        "orgPath": "/test/path",
    }

    result = map_org_summary(org_id, org_counts, org_data)

    assert isinstance(result, OrganizationCatalogSummary)
    assert result.id == "12345678"
    assert result.datasetCount == 10
    assert result.dataserviceCount == 5
    assert result.conceptCount == 3
    assert result.informationmodelCount == 2


@pytest.mark.unit
def test_map_org_summary_with_missing_counts() -> None:
    """Test map_org_summary with missing counts."""
    org_id = "12345678"
    org_counts: dict[str, str] = {"datasets": "10"}
    org_data = {
        "name": "Test Org",
        "prefLabel": {"nb": "Test Org"},
        "orgPath": "/test/path",
    }

    result = map_org_summary(org_id, org_counts, org_data)

    assert isinstance(result, OrganizationCatalogSummary)
    assert result.id == "12345678"
    assert result.datasetCount == 10
    assert result.dataserviceCount == 0
    assert result.conceptCount == 0
    assert result.informationmodelCount == 0


@pytest.mark.unit
def test_map_org_summary_with_none_counts() -> None:
    """Test map_org_summary with None counts."""
    org_id = "12345678"
    org_data = {
        "name": "Test Org",
        "prefLabel": {"nb": "Test Org"},
        "orgPath": "/test/path",
    }

    result = map_org_summary(org_id, None, org_data)

    assert isinstance(result, OrganizationCatalogSummary)
    assert result.id == "12345678"
    assert result.datasetCount == 0
    assert result.dataserviceCount == 0
    assert result.conceptCount == 0
    assert result.informationmodelCount == 0


@pytest.mark.unit
def test_add_org_counts_new_org() -> None:
    """Test add_org_counts with new organization."""
    label = "datasets"
    sparql_results = [{"org": "12345678", "count": "10"}]
    org_counts: dict[str, str] = {}

    result = add_org_counts(label, sparql_results, org_counts)

    assert result == {"12345678": {"datasets": "10"}}


@pytest.mark.unit
def test_add_org_counts_existing_org() -> None:
    """Test add_org_counts with existing organization."""
    label = "dataservices"
    sparql_results = [{"org": "12345678", "count": "5"}]
    org_counts: dict[str, dict[str, str]] = {"12345678": {"datasets": "10"}}

    result = add_org_counts(label, sparql_results, org_counts)

    assert result == {"12345678": {"datasets": "10", "dataservices": "5"}}


@pytest.mark.unit
def test_map_org_summaries_include_empty() -> None:
    """Test map_org_summaries with include_empty=True."""
    organizations = {
        "12345678": {
            "name": "Test Org 1",
            "prefLabel": {"nb": "Test Org 1"},
            "orgPath": "/test/path1",
        },
        "87654321": {
            "name": "Test Org 2",
            "prefLabel": {"nb": "Test Org 2"},
            "orgPath": "/test/path2",
        },
    }
    datasets = [{"org": "12345678", "count": "10"}]
    dataservices = [{"org": "87654321", "count": "5"}]
    concepts: list = []
    informationmodels: list = []

    result = map_org_summaries(
        organizations, datasets, dataservices, concepts, informationmodels, True
    )

    assert len(result) == 2
    assert result[0].id == "12345678"
    assert result[1].id == "87654321"


@pytest.mark.unit
def test_map_org_summaries_not_include_empty() -> None:
    """Test map_org_summaries with include_empty=False."""
    organizations = {
        "12345678": {
            "name": "Test Org 1",
            "prefLabel": {"nb": "Test Org 1"},
            "orgPath": "/test/path1",
        }
    }
    datasets = [{"org": "12345678", "count": "10"}]
    dataservices: list = []
    concepts: list = []
    informationmodels: list = []

    result = map_org_summaries(
        organizations, datasets, dataservices, concepts, informationmodels, False
    )

    assert len(result) == 1
    assert result[0].id == "12345678"


@pytest.mark.unit
def test_categorise_summaries_by_parent_org_valid_path() -> None:
    """Test categorise_summaries_by_parent_org with valid orgPath."""
    summary1 = OrganizationCatalogSummary(
        id="12345678",
        name="Test Org 1",
        prefLabel={"nb": "Test Org 1"},
        orgPath="/FYLKE/12/12345678",
        datasetCount=10,
        conceptCount=0,
        dataserviceCount=0,
        informationmodelCount=0,
    )
    summary2 = OrganizationCatalogSummary(
        id="87654321",
        name="Test Org 2",
        prefLabel={"nb": "Test Org 2"},
        orgPath="/FYLKE/12/87654321",
        datasetCount=5,
        conceptCount=0,
        dataserviceCount=0,
        informationmodelCount=0,
    )

    result = categorise_summaries_by_parent_org([summary1, summary2], True)

    assert len(result) == 1
    assert result[0].category.id == "12"


@pytest.mark.unit
def test_categorise_summaries_by_parent_org_invalid_path() -> None:
    """Test categorise_summaries_by_parent_org with invalid orgPath."""
    summary = OrganizationCatalogSummary(
        id="12345678",
        name="Test Org",
        prefLabel={"nb": "Test Org"},
        orgPath="/invalid/path",
        datasetCount=10,
        conceptCount=0,
        dataserviceCount=0,
        informationmodelCount=0,
    )

    result = categorise_summaries_by_parent_org([summary], True)

    assert len(result) == 1
    assert result[0].category.id == "path"


@pytest.mark.unit
def test_categorise_summaries_by_municipality() -> None:
    """Test categorise_summaries_by_municipality."""
    summary = OrganizationCatalogSummary(
        id="12345678",
        name="Test Org",
        prefLabel={"nb": "Test Org"},
        orgPath="/FYLKE/12/12345678",
        datasetCount=10,
        conceptCount=0,
        dataserviceCount=0,
        informationmodelCount=0,
    )

    municipalities = {
        "fylke": [
            {
                "fylkesnummer": "12",
                "organisasjonsnummer": "12345678",
                "fylkesnavn": "Test Fylke",
            }
        ],
        "kommune": [],
    }

    result = categorise_summaries_by_municipality([summary], municipalities, True)

    assert len(result) == 1
    assert result[0].category.id == "12345678"


@pytest.mark.unit
def test_remove_empty_summaries() -> None:
    """Test remove_empty_summaries."""
    summary1 = OrganizationCatalogSummary(
        id="12345678",
        name="Test Org 1",
        prefLabel={"nb": "Test Org 1"},
        orgPath="/test/path1",
        datasetCount=10,
        conceptCount=0,
        dataserviceCount=0,
        informationmodelCount=0,
    )
    summary2 = OrganizationCatalogSummary(
        id="87654321",
        name="Test Org 2",
        prefLabel={"nb": "Test Org 2"},
        orgPath="/test/path2",
        datasetCount=0,
        conceptCount=0,
        dataserviceCount=0,
        informationmodelCount=0,
    )

    result = remove_empty_summaries([summary1, summary2])

    assert len(result) == 1
    assert result[0].id == "12345678"


@pytest.mark.unit
def test_org_is_stat_fylk_or_komm_stat() -> None:
    """Test org_is_stat_fylk_or_komm with STAT orgPath."""
    org = {"orgPath": "/STAT/12345678"}

    result = org_is_stat_fylk_or_komm(org)

    assert result is True


@pytest.mark.unit
def test_org_is_stat_fylk_or_komm_fylke() -> None:
    """Test org_is_stat_fylk_or_komm with FYLKE orgPath."""
    org = {"orgPath": "/FYLKE/12/12345678"}

    result = org_is_stat_fylk_or_komm(org)

    assert result is True


@pytest.mark.unit
def test_org_is_stat_fylk_or_komm_kommune() -> None:
    """Test org_is_stat_fylk_or_komm with KOMMUNE orgPath."""
    org = {"orgPath": "/KOMMUNE/1234/12345678"}

    result = org_is_stat_fylk_or_komm(org)

    assert result is True


@pytest.mark.unit
def test_org_is_stat_fylk_or_komm_other() -> None:
    """Test org_is_stat_fylk_or_komm with other orgPath."""
    org = {"orgPath": "/OTHER/12345678"}

    result = org_is_stat_fylk_or_komm(org)

    assert result is False


@pytest.mark.unit
def test_org_is_stat_fylk_or_komm_no_path() -> None:
    """Test org_is_stat_fylk_or_komm with no orgPath."""
    org: dict[str, str] = {}

    result = org_is_stat_fylk_or_komm(org)

    assert result is False
