"""Package with backend-for-frontend service that provides content for fdk portal's organization pages."""

from aiohttp import web

from fdk_organization_bff.app import create_app

if __name__ == "__main__":
    web.run_app(create_app())
