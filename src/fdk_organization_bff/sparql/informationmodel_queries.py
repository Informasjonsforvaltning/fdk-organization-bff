"""Module for Information Model SPARQL-queries."""

from string import Template


def build_informationmodels_by_publisher_query() -> str:
    """Build query to count informationmodels grouped by publisher."""
    return """
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX modelldcatno: <https://data.norge.no/vocabulary/modelldcatno#>
        SELECT ?organizationNumber (COUNT(DISTINCT ?informationmodel) AS ?count)
        WHERE { GRAPH ?g {
            ?informationmodel a modelldcatno:InformationModel .
            ?record foaf:primaryTopic ?informationmodel .
            ?record a dcat:CatalogRecord .
            ?informationmodel dct:publisher ?publisher .
            ?publisher dct:identifier ?organizationNumber .
        }}
        GROUP BY ?organizationNumber
    """


def build_org_informationmodels_query(organization_id: str) -> str:
    """Build query for an organizations informationmodels."""
    return Template(
        """
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX modelldcatno: <https://data.norge.no/vocabulary/modelldcatno#>
        SELECT DISTINCT ?informationmodel ?issued
        WHERE { GRAPH ?g {
            ?informationmodel a modelldcatno:InformationModel .
            ?record foaf:primaryTopic ?informationmodel .
            ?record a dcat:CatalogRecord .
            ?record dct:issued ?issued .
            ?informationmodel dct:publisher ?publisher .
            ?publisher dct:identifier "$org_id" .
        }}
    """
    ).substitute(org_id=organization_id)
