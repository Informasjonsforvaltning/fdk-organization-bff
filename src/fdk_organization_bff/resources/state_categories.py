"""Resource module for state categories."""

from dataclasses import asdict
from typing import Optional

from aiohttp.web import json_response, Response, View

from fdk_organization_bff.classes import FilterEnum
from fdk_organization_bff.service.org_catalog_service import get_state_categories
from fdk_organization_bff.utils.utils import filter_param_to_enum
from .utils import fifteen_min_cache_header


class StateCategories(View):
    """Class representing state categories resource."""

    async def get(self: View) -> Response:
        """Get state categories."""
        filter = filter_param_to_enum(self.request.rel_url.query.get("filter"))
        include_empty: Optional[str] = self.request.rel_url.query.get("includeEmpty")
        if filter is FilterEnum.INVALID:
            return Response(status=400)
        else:
            categories = await get_state_categories(filter, include_empty)
            return json_response(asdict(categories), headers=fifteen_min_cache_header)
