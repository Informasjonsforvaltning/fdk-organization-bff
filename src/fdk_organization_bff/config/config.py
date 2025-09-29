"""Configure fdk-organization-bff."""

import os
from typing import Dict, Type, TypeVar


T = TypeVar("T", bound="Config")


class Config:
    """Configuration class."""

    _ORG_CATALOG_PATH = "/organizationcatalogs"
    _ORG_CATEGORIES_PATH = "/organizationcategories"
    _REPORTS_PATH = "/reports"

    _ROUTES = {
        "PING": "/ping",
        "READY": "/ready",
        "ORG_CATALOG": _ORG_CATALOG_PATH + "/{id}",
        "ORG_CATALOGS": _ORG_CATALOG_PATH,
        "STATE_CATEGORIES": _ORG_CATEGORIES_PATH + "/state",
        "MUNICIPALITY_CATEGORIES": _ORG_CATEGORIES_PATH + "/municipality",
        "CONCEPT_REPORT": _REPORTS_PATH + "/concepts",
        "DATA_SERVICE_REPORT": _REPORTS_PATH + "/data-services",
        "DATASETS_REPORT": _REPORTS_PATH + "/datasets",
        "INFORMATION_MODEL_REPORT": _REPORTS_PATH + "/information-models",
    }
    _ORGANIZATION_CATALOG_URI = os.getenv(
        "ORGANIZATION_CATALOG_URI",
        "https://organization-catalog.staging.fellesdatakatalog.digdir.no",
    )
    _DATA_BRREG_URI = os.getenv(
        "DATA_BRREG_URI",
        "https://data.brreg.no",
    )
    _FDK_SPARQL_URI = os.getenv(
        "FDK_SPARQL_URI",
        "https://sparql.staging.fellesdatakatalog.digdir.no",
    )
    _FDK_METADATA_QUALITY_URI = os.getenv(
        "FDK_METADATA_QUALITY_URI",
        "https://mqa-scoring-api.staging.fellesdatakatalog.digdir.no",
    )
    _REFERENCE_DATA_URI = os.getenv(
        "REFERENCE_DATA_URI",
        "https://staging.fellesdatakatalog.digdir.no",
    )

    @classmethod
    def routes(cls: Type[T]) -> Dict[str, str]:
        """Return a dict with route-value for available views."""
        return cls._ROUTES

    @classmethod
    def org_cat_uri(cls: Type[T]) -> str:
        """Organization Catalog URI."""
        return cls._ORGANIZATION_CATALOG_URI

    @classmethod
    def data_brreg_uri(cls: Type[T]) -> str:
        """BRREG URI."""
        return cls._DATA_BRREG_URI

    @classmethod
    def sparql_uri(cls: Type[T]) -> str:
        """FDK SPARQL URI."""
        return cls._FDK_SPARQL_URI

    @classmethod
    def metadata_uri(cls: Type[T]) -> str:
        """FDK Metadata Quality Service URI."""
        return cls._FDK_METADATA_QUALITY_URI

    @classmethod
    def reference_data_uri(cls: Type[T]) -> str:
        """Return reference-data URI."""
        return cls._REFERENCE_DATA_URI
