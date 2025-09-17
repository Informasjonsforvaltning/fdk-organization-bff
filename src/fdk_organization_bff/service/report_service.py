"""Service layer module for reports."""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from aiohttp import ClientSession

from fdk_organization_bff.classes import (
    ConceptReport,
    DataServiceReport,
    DatasetsReport,
    InformationModelReport,
)
from fdk_organization_bff.service.adapter import (
    query_concepts_report,
    query_data_services_report,
    query_format_dataset_report_metrics,
    query_general_dataset_report_metrics,
    query_information_models_report,
    query_publisher_dataset_report_metrics,
)


def _gather_dataset_metrics(
    format_result: list, general_result: list, publisher_result: list
) -> dict:
    """Gather dataset metrics from sparql bindings."""
    metrics: Dict = dict()

    for row in format_result:
        format_dataset_uri = row["dataset"]["value"]
        metrics[format_dataset_uri] = metrics.get(
            format_dataset_uri, {"formats": set(), "allThemes": set()}
        )
        if row.get("format", {}).get("value") is not None:
            metrics[format_dataset_uri]["formats"].add(row["format"]["value"])
        if row.get("mediaType", {}).get("value") is not None:
            metrics[format_dataset_uri]["formats"].add(row["mediaType"]["value"])

    for row in general_result:
        general_dataset_uri = row["dataset"]["value"]
        metrics[general_dataset_uri] = metrics.get(
            general_dataset_uri, {"formats": set(), "allThemes": set()}
        )
        metrics[general_dataset_uri]["firstHarvested"] = row["firstHarvested"]["value"]
        metrics[general_dataset_uri]["isOpenData"] = row.get("isOpenData", {}).get(
            "value"
        )
        metrics[general_dataset_uri]["transportportal"] = row.get(
            "transportportal", {}
        ).get("value")
        metrics[general_dataset_uri]["provenance"] = row.get("provenance", {}).get(
            "value"
        )
        metrics[general_dataset_uri]["accessRights"] = row.get("accessRights", {}).get(
            "value", "MISSING"
        )
        if row.get("theme", {}).get("value") is not None:
            metrics[general_dataset_uri]["allThemes"].add(row["theme"]["value"])

    for row in publisher_result:
        publisher_dataset_uri = row["dataset"]["value"]
        metrics[publisher_dataset_uri] = metrics.get(
            publisher_dataset_uri, {"formats": set(), "allThemes": set()}
        )
        metrics[publisher_dataset_uri]["orgId"] = row.get("orgId", {}).get("value")
        metrics[publisher_dataset_uri]["orgPath"] = row.get("orgPath", {}).get(
            "value", "/MISSING"
        )

    return metrics


def _gather_concept_metrics(sparql_result: list) -> dict:
    """Gather concept metrics from sparql bindings."""
    metrics: Dict = dict()

    for row in sparql_result:
        concept_uri = row["concept"]["value"]
        metrics[concept_uri] = metrics.get(concept_uri, {"referrers": set()})
        metrics[concept_uri]["firstHarvested"] = row["firstHarvested"]["value"]
        metrics[concept_uri]["orgId"] = row.get("orgId", {}).get("value")
        metrics[concept_uri]["orgPath"] = row.get("orgPath", {}).get(
            "value", "/MISSING"
        )
        if row.get("referer", {}).get("value") is not None:
            metrics[concept_uri]["referrers"].add(row["referer"]["value"])

    return metrics


def _gather_data_service_metrics(sparql_result: list) -> dict:
    """Gather data service metrics from sparql bindings."""
    metrics: Dict = dict()

    for row in sparql_result:
        data_service_uri = row["service"]["value"]
        metrics[data_service_uri] = metrics.get(data_service_uri, {"formats": set()})
        metrics[data_service_uri]["firstHarvested"] = row["firstHarvested"]["value"]
        metrics[data_service_uri]["orgId"] = row.get("orgId", {}).get("value")
        metrics[data_service_uri]["orgPath"] = row.get("orgPath", {}).get(
            "value", "/MISSING"
        )
        if row.get("format", {}).get("value") is not None:
            metrics[data_service_uri]["formats"].add(row["format"]["value"])
        if row.get("mediaType", {}).get("value") is not None:
            metrics[data_service_uri]["formats"].add(row["mediaType"]["value"])

    return metrics


def _gather_information_model_metrics(sparql_result: list) -> dict:
    """Gather information model metrics from sparql bindings."""
    metrics: Dict = dict()

    for row in sparql_result:
        info_model_uri = row["model"]["value"]
        metrics[info_model_uri] = metrics.get(info_model_uri, {})
        metrics[info_model_uri]["firstHarvested"] = row["firstHarvested"]["value"]
        metrics[info_model_uri]["orgId"] = row.get("orgId", {}).get("value")
        metrics[info_model_uri]["orgPath"] = row.get("orgPath", {}).get(
            "value", "/MISSING"
        )

    return metrics


def _split_org_path(org_path: str) -> list:
    """Split org path into the different part blocks."""
    parts = org_path.strip("/").split("/")
    result = []
    for i in range(1, len(parts) + 1):
        result.append("/" + "/".join(parts[:i]))
    return result


def _dict_to_key_count_list(dictionary: dict) -> list:
    """Convert str -> int dict to key count objects."""
    result = list()
    for key in dictionary:
        result.append({"key": key, "count": dictionary[key]})
    return result


def _check_if_timestamp_is_after_date(timestamp: Optional[str], date: datetime) -> bool:
    if timestamp is None:
        return False
    else:
        format_with_ms = "%Y-%m-%dT%H:%M:%S.%fZ"
        format_without_ms = "%Y-%m-%dT%H:%M:%SZ"
        for fmt in [format_with_ms, format_without_ms]:
            try:
                date_object = datetime.strptime(timestamp, fmt)
                return date_object.replace(tzinfo=timezone.utc) > date
            except ValueError:
                continue

        return False


async def get_dataset_report(
    org_path: Optional[str], theme_profile: Optional[str]
) -> DatasetsReport:
    """Return datasets report."""
    async with ClientSession() as session:
        datasets_format_response = await query_format_dataset_report_metrics(session)
        datasets_general_response = await query_general_dataset_report_metrics(session)
        datasets_publisher_response = await query_publisher_dataset_report_metrics(
            session
        )

    metrics = _gather_dataset_metrics(
        format_result=datasets_format_response,
        general_result=datasets_general_response,
        publisher_result=datasets_publisher_response,
    )
    total = 0
    orgs = set()
    open_data_datasets = 0
    national_component_datasets = 0
    new_last_week = 0
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    access_rights_counts: Dict = dict()
    org_path_counts: Dict = dict()
    format_counts: Dict = dict()
    theme_counts: Dict = dict()
    for dataset_uri in metrics:
        if (
            theme_profile == "transport"
            and metrics[dataset_uri]["transportportal"] != "true"
        ):
            continue
        elif org_path and org_path not in metrics[dataset_uri].get("orgPath", ""):
            continue
        else:
            total += 1
            if metrics[dataset_uri].get("accessRights") is not None:
                access_right = metrics[dataset_uri]["accessRights"]
                access_rights_counts[access_right] = (
                    access_rights_counts.get(access_right, 0) + 1
                )
            if metrics[dataset_uri].get("orgId") is not None:
                orgs.add(metrics[dataset_uri]["orgId"])
            if metrics[dataset_uri].get("isOpenData") == "true":
                open_data_datasets += 1
            if (
                metrics[dataset_uri].get("provenance")
                == "http://data.brreg.no/datakatalog/provinens/nasjonal"
            ):
                national_component_datasets += 1
            if metrics[dataset_uri].get(
                "firstHarvested"
            ) is not None and _check_if_timestamp_is_after_date(
                metrics[dataset_uri]["firstHarvested"], seven_days_ago
            ):
                new_last_week += 1
            for format_value in metrics[dataset_uri]["formats"]:
                format_counts[format_value] = format_counts.get(format_value, 0) + 1
            for theme_value in metrics[dataset_uri]["allThemes"]:
                theme_counts[theme_value] = theme_counts.get(theme_value, 0) + 1
            for part in _split_org_path(
                metrics[dataset_uri].get("orgPath", "/MISSING")
            ):
                org_path_counts[part] = org_path_counts.get(part, 0) + 1

    return DatasetsReport(
        totalObjects=total,
        newLastWeek=new_last_week,
        organizationCount=len(orgs),
        opendata=open_data_datasets,
        nationalComponent=national_component_datasets,
        orgPaths=_dict_to_key_count_list(org_path_counts),
        formats=_dict_to_key_count_list(format_counts),
        allThemes=_dict_to_key_count_list(theme_counts),
        accessRights=_dict_to_key_count_list(access_rights_counts),
    )


async def get_concept_report(org_path: Optional[str]) -> ConceptReport:
    """Return concepts report."""
    async with ClientSession() as session:
        concepts_response = await query_concepts_report(session)

    metrics = _gather_concept_metrics(concepts_response)
    total = 0
    orgs = set()
    new_last_week = 0
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    org_path_counts: Dict = dict()
    referer_counts: Dict = dict()
    for concept_uri in metrics:
        if org_path and org_path not in metrics[concept_uri]["orgPath"]:
            continue
        else:
            total += 1
            if metrics[concept_uri]["orgId"] is not None:
                orgs.add(metrics[concept_uri]["orgId"])
            if _check_if_timestamp_is_after_date(
                metrics[concept_uri]["firstHarvested"], seven_days_ago
            ):
                new_last_week += 1
            if len(metrics[concept_uri]["referrers"]) > 0:
                referer_counts[concept_uri] = len(metrics[concept_uri]["referrers"])
            for part in _split_org_path(metrics[concept_uri]["orgPath"]):
                org_path_counts[part] = org_path_counts.get(part, 0) + 1

    return ConceptReport(
        totalObjects=total,
        newLastWeek=new_last_week,
        organizationCount=len(orgs),
        orgPaths=_dict_to_key_count_list(org_path_counts),
        mostInUse=_dict_to_key_count_list(referer_counts),
    )


async def get_data_service_report(org_path: Optional[str]) -> DataServiceReport:
    """Return data services report."""
    async with ClientSession() as session:
        data_services_response = await query_data_services_report(session)

    metrics = _gather_data_service_metrics(data_services_response)
    total = 0
    orgs = set()
    new_last_week = 0
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    org_path_counts: Dict = dict()
    format_counts: Dict = dict()
    for data_service_uri in metrics:
        if org_path and org_path not in metrics[data_service_uri]["orgPath"]:
            continue
        else:
            total += 1
            if metrics[data_service_uri]["orgId"] is not None:
                orgs.add(metrics[data_service_uri]["orgId"])
            if _check_if_timestamp_is_after_date(
                metrics[data_service_uri]["firstHarvested"], seven_days_ago
            ):
                new_last_week += 1
            for format_value in metrics[data_service_uri]["formats"]:
                format_counts[format_value] = format_counts.get(format_value, 0) + 1
            for part in _split_org_path(metrics[data_service_uri]["orgPath"]):
                org_path_counts[part] = org_path_counts.get(part, 0) + 1

    return DataServiceReport(
        totalObjects=total,
        newLastWeek=new_last_week,
        organizationCount=len(orgs),
        orgPaths=_dict_to_key_count_list(org_path_counts),
        formats=_dict_to_key_count_list(format_counts),
    )


async def get_information_model_report(
    org_path: Optional[str],
) -> InformationModelReport:
    """Return information models report."""
    async with ClientSession() as session:
        info_models_response = await query_information_models_report(session)

    metrics = _gather_information_model_metrics(info_models_response)
    total = 0
    orgs = set()
    new_last_week = 0
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    org_path_counts: Dict = dict()
    for info_model_uri in metrics:
        if org_path and org_path not in metrics[info_model_uri]["orgPath"]:
            continue
        else:
            total += 1
            if metrics[info_model_uri]["orgId"] is not None:
                orgs.add(metrics[info_model_uri]["orgId"])
            if _check_if_timestamp_is_after_date(
                metrics[info_model_uri]["firstHarvested"], seven_days_ago
            ):
                new_last_week += 1
            for part in _split_org_path(metrics[info_model_uri]["orgPath"]):
                org_path_counts[part] = org_path_counts.get(part, 0) + 1

    return InformationModelReport(
        totalObjects=total,
        newLastWeek=new_last_week,
        organizationCount=len(orgs),
        orgPaths=_dict_to_key_count_list(org_path_counts),
    )
