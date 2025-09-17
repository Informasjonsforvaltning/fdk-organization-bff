"""Resource module for reports."""

from dataclasses import asdict
from typing import Optional

from aiohttp.web import json_response, Response, View

from fdk_organization_bff.service.report_service import (
    get_concept_report,
    get_data_service_report,
    get_dataset_report,
    get_information_model_report,
)
from .utils import fifteen_min_cache_header


class DatasetsReportView(View):
    """Class representing dataset report resource."""

    async def get(self: View) -> Response:
        """Get dataset report."""
        org_path: Optional[str] = self.request.rel_url.query.get("orgPath")
        theme_profile: Optional[str] = self.request.rel_url.query.get("themeprofile")
        report = await get_dataset_report(org_path, theme_profile)
        return json_response(asdict(report), headers=fifteen_min_cache_header)


class DataServiceReportView(View):
    """Class representing data service report resource."""

    async def get(self: View) -> Response:
        """Get data service report."""
        org_path: Optional[str] = self.request.rel_url.query.get("orgPath")
        report = await get_data_service_report(org_path)
        return json_response(asdict(report), headers=fifteen_min_cache_header)


class ConceptReportView(View):
    """Class representing concept report resource."""

    async def get(self: View) -> Response:
        """Get concept report."""
        org_path: Optional[str] = self.request.rel_url.query.get("orgPath")
        report = await get_concept_report(org_path)
        return json_response(asdict(report), headers=fifteen_min_cache_header)


class InformationModelReportView(View):
    """Class representing information model report resource."""

    async def get(self: View) -> Response:
        """Get information model report."""
        org_path: Optional[str] = self.request.rel_url.query.get("orgPath")
        report = await get_information_model_report(org_path)
        return json_response(asdict(report), headers=fifteen_min_cache_header)
