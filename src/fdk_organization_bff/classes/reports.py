"""Organization catalog data class."""

from dataclasses import dataclass


@dataclass
class DatasetsReport:
    """Data class wrapping dataset report."""

    totalObjects: int
    newLastWeek: int
    organizationCount: int
    opendata: int
    nationalComponent: int
    orgPaths: list
    allThemes: list
    formats: list
    accessRights: list


@dataclass
class DataServiceReport:
    """Data class wrapping data service report."""

    totalObjects: int
    newLastWeek: int
    organizationCount: int
    orgPaths: list
    formats: list


@dataclass
class ConceptReport:
    """Data class wrapping concept report."""

    totalObjects: int
    newLastWeek: int
    organizationCount: int
    orgPaths: list
    mostInUse: list


@dataclass
class InformationModelReport:
    """Data class wrapping information model report."""

    totalObjects: int
    newLastWeek: int
    organizationCount: int
    orgPaths: list
