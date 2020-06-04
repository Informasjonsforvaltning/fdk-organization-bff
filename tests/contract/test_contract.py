import pytest
import requests

service_url = "http://localhost:8000"
org_catalog_url = f"{service_url}/organizationcatalogs"
# update if change in mockdata
expected_size = 272


class TestSearchAll:

    @pytest.mark.contract
    def test_has_correct_format(self, wait_for_ready):
        result = requests.get(url=org_catalog_url, timeout=10)
        assert result.status_code == 200
        assert len(result.json()["organizations"]) == expected_size
        for org in result.json()["organizations"]:
            keys = org.keys()
            assert "id" in keys
            assert "organization" in keys
            assert "dataset_count" in keys
            assert "concept_count" in keys
            assert "informationmodel_count" in keys
            assert "dataservice_count" in keys
            organization = org["organization"]
            org_keys = organization.keys()
            assert "name" in org_keys
            assert is_language_object_with_content(organization["name"]), "Error: found organization without name: {0}"\
                .format(organization)
            assert "orgPath" in org_keys


def is_language_object_with_content(entry: dict):
    keys = entry.keys()
    return ("nn" in keys and entry["nn"] != "") \
           or ("nb" in keys and entry["nb"] != "") \
           or ("en" in keys and entry["en"] != "") \
           or ("no" in keys and entry["no"] != "")
