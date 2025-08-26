"""Util module."""

import datetime
import logging
import traceback
from typing import Any, Dict, Optional
from urllib.parse import quote_plus

from fdk_organization_bff.classes import FilterEnum


def url_with_params(url: str, params: Optional[Dict[str, str]]) -> str:
    """Add parameters to a URL."""
    if params and len(params) > 0:
        params_list = []
        for key in params:
            params_list.append(f"{key}={quote_plus(params[key])}")

        seperator = "&"
        return f"{url}?{seperator.join(params_list)}"
    else:
        return url


def filter_param_to_enum(param: Optional[str]) -> FilterEnum:
    """Map filter param value to corresponding enum."""
    if param is None:
        return FilterEnum.NONE
    elif param == FilterEnum.NAP.value:
        return FilterEnum.NAP
    else:
        return FilterEnum.INVALID


def dataset_is_authoritative(dataset: Dict) -> bool:
    """Check if dataset is tagged as authoritative."""
    is_authoritative = dataset.get("isAuthoritative")
    if is_authoritative:
        return is_authoritative["value"] == "true"
    return False


def get_today() -> datetime.date:
    """Get today's date. This function can be easily mocked in tests."""
    return datetime.date.today()


def resource_is_new(resource: Dict) -> bool:
    """Check if resource was first published within the last 7 days."""
    issued = resource.get("issued")
    if issued:
        date_format = "%Y-%m-%d"
        try:
            issued_date = datetime.datetime.strptime(
                issued["value"][0:10], date_format
            ).date()
            seven_days_ago = get_today() - datetime.timedelta(days=7)
            return issued_date >= seven_days_ago
        except ValueError:
            logging.error(f"{traceback.format_exc()}: failed to parse issued date")
    return False


def dataset_is_open_data(dataset: Dict) -> bool:
    """Check if dataset is tagged as open data."""
    is_open_data = dataset.get("isOpenData")
    if is_open_data:
        return is_open_data["value"] == "true"
    return False


def to_int(value: Any) -> Optional[int]:
    """Convert value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        logging.warning(f"{traceback.format_exc()}: failed to convert {value} to int")
        return None
