"""Configure fdk-organization-bff."""
import os
from typing import Dict, Type, TypeVar


T = TypeVar("T", bound="Config")


class Config:
    """Configuration class."""

    _ORG_CATALOG_PATH = "/organizationcatalogs"

    _ROUTES = {
        "PING": "/ping",
        "READY": "/ready",
        "ORG_CATALOG": _ORG_CATALOG_PATH + "/{id}",
        "ORG_CATALOGS": _ORG_CATALOG_PATH,
    }
    _ORGANIZATION_CATALOGUE_URI = os.getenv(
        "ORGANIZATION_CATALOGUE_URI",
        "https://organization-catalogue.staging.fellesdatakatalog.digdir.no",
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
        "https://metadata-quality.staging.fellesdatakatalog.digdir.no",
    )

    @classmethod
    def routes(cls: Type[T]) -> Dict[str, str]:
        """Return a dict with route-value for available views."""
        return cls._ROUTES

    @classmethod
    def org_cat_uri(cls: Type[T]) -> str:
        """Organization Catalogue URI."""
        return cls._ORGANIZATION_CATALOGUE_URI

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
