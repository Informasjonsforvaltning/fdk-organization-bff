"""Module for starting an aiohttp API."""

import logging
import os

from aiohttp import web
from aiohttp_middlewares import cors_middleware

from fdk_organization_bff.config import Config
from fdk_organization_bff.resources import (
    ConceptReportView,
    DataServiceReportView,
    DatasetsReportView,
    InformationModelReportView,
    MunicipalityCategories,
    OrgCatalog,
    OrgCatalogs,
    Ping,
    Ready,
    StateCategories,
)


def setup_routes(app: web.Application) -> None:
    """Add active routes to application."""
    app.add_routes(
        [
            web.get(Config.routes()["PING"], Ping),
            web.get(Config.routes()["READY"], Ready),
            web.get(Config.routes()["ORG_CATALOG"], OrgCatalog),
            web.get(Config.routes()["ORG_CATALOGS"], OrgCatalogs),
            web.get(Config.routes()["STATE_CATEGORIES"], StateCategories),
            web.get(Config.routes()["MUNICIPALITY_CATEGORIES"], MunicipalityCategories),
            web.get(Config.routes()["CONCEPT_REPORT"], ConceptReportView),
            web.get(Config.routes()["DATA_SERVICE_REPORT"], DataServiceReportView),
            web.get(Config.routes()["DATASETS_REPORT"], DatasetsReportView),
            web.get(
                Config.routes()["INFORMATION_MODEL_REPORT"], InformationModelReportView
            ),
        ]
    )


async def create_app() -> web.Application:
    """Create aiohttp application."""
    origins = os.getenv("CORS_ORIGIN_PATTERNS", "*").split(",")
    origins = [origin.strip() for origin in origins]

    allow_all = "*" in origins

    app = web.Application(
        middlewares=[
            cors_middleware(
                allow_all=allow_all,
                origins=None if allow_all else origins,
                allow_methods=["GET"],
                allow_headers=["*"],
            )
        ]
    )

    logging.basicConfig(level=logging.INFO)
    setup_routes(app)

    return app
