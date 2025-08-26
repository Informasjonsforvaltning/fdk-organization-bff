"""Nox sessions."""

import nox
from nox.sessions import Session
import nox_poetry

nox.options.envdir = ".cache"
nox.options.reuse_existing_virtualenvs = True
locations = "src", "tests", "noxfile.py"
nox.options.sessions = (
    "lint",
    "mypy",
    "unit_tests",
    "integration_tests",
    "contract_tests",
)


@nox_poetry.session(python=["3.12"])
def unit_tests(session: Session) -> None:
    """Run the unit test suite."""
    args = session.posargs
    session.install(
        ".",
        "pytest",
        "requests-mock",
        "pytest-mock",
        "pytest-asyncio",
    )
    session.run(
        "pytest",
        "-m unit",
        "-ra",
        *args,
        env={
            "ORGANIZATION_CATALOG_URI": "http://localhost:8000",
            "DATA_BRREG_URI": "http://localhost:8000",
            "REFERENCE_DATA_URI": "http://localhost:8000",
            "FDK_PORTAL_URI": "http://localhost:8000",
            "FDK_METADATA_QUALITY_URI": "http://localhost:8000",
            "FDK_SPARQL_URI": "http://localhost:8000/sparql",
            "CORS_ORIGIN_PATTERNS": "*",
        },
    )


@nox_poetry.session(python=["3.12"])
def integration_tests(session: Session) -> None:
    """Run the integration test suite."""
    args = session.posargs
    session.install(
        ".",
        "pytest",
        "pytest-docker",
        "requests-mock",
        "pytest-mock",
        "pytest-aiohttp",
    )
    session.run(
        "pytest",
        "-m integration",
        "-ra",
        *args,
        env={
            "ORGANIZATION_CATALOG_URI": "http://localhost:8000",
            "DATA_BRREG_URI": "http://localhost:8000",
            "REFERENCE_DATA_URI": "http://localhost:8000",
            "FDK_PORTAL_URI": "http://localhost:8000",
            "FDK_METADATA_QUALITY_URI": "http://localhost:8000",
            "FDK_SPARQL_URI": "http://localhost:8000/sparql",
            "CORS_ORIGIN_PATTERNS": "*",
        },
    )


@nox_poetry.session(python=["3.12"])
def tests(session: Session) -> None:
    """Run the coverage unit-test suite."""
    args = session.posargs or ["--cov"]
    session.install(
        ".",
        "coverage[toml]",
        "pytest",
        "pytest-cov",
        "pytest-docker",
        "requests-mock",
        "pytest-mock",
        "pytest-aiohttp",
    )
    session.run(
        "pytest",
        "-ra",
        *args,
        env={
            "ORGANIZATION_CATALOG_URI": "http://localhost:8000",
            "DATA_BRREG_URI": "http://localhost:8000",
            "REFERENCE_DATA_URI": "http://localhost:8000",
            "FDK_PORTAL_URI": "http://localhost:8000",
            "FDK_METADATA_QUALITY_URI": "http://localhost:8000",
            "FDK_SPARQL_URI": "http://localhost:8000/sparql",
            "CORS_ORIGIN_PATTERNS": "*",
        },
    )


@nox_poetry.session(python=["3.12"])
def contract_tests(session: Session) -> None:
    """Run the contract test suite."""
    args = session.posargs
    session.install(
        ".", "pytest", "pytest-docker", "requests_mock", "pytest_mock", "pytest-asyncio"
    )
    session.run(
        "pytest",
        "-m contract",
        "-ra",
        *args,
    )


@nox_poetry.session(python=["3.12"])
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@nox_poetry.session(python=["3.12"])
def lint(session: Session) -> None:
    """Lint using flake8."""
    args = session.posargs or locations
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "pep8-naming",
    )
    session.run("flake8", *args)


@nox_poetry.session(python=["3.12"])
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    session.install("mypy", "pytest-asyncio")
    session.run("mypy", *args)


@nox_poetry.session(python=["3.12"])
def coverage(session: Session) -> None:
    """Upload coverage data."""
    session.install("coverage[toml]")
    session.run("coverage", "xml", "--fail-under=0")
