"""Module for DataService SPARQL-queries."""
from string import Template


def build_dataservices_by_publisher_query() -> str:
    """Build query to count dataservices grouped by publisher."""
    return """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
SELECT ?organizationNumber (COUNT(DISTINCT ?service) AS ?count)
FROM <https://dataservices.fellesdatakatalog.digdir.no>
WHERE {{
    ?service a dcat:DataService .
    ?catalog dcat:service ?service .
    OPTIONAL {{ ?service dct:publisher ?servicePublisher . }}
    OPTIONAL {{ ?catalog dct:publisher ?catPublisher . }}
    BIND ( IF( EXISTS {{ ?service dct:publisher ?servicePublisher . }},
        ?servicePublisher, ?catPublisher ) AS ?publisher ) .
    ?publisher dct:identifier ?organizationNumber .
}}
GROUP BY ?organizationNumber"""


def build_org_dataservice_query(organization_id: str) -> str:
    """Build query for an organizations dataservices."""
    query_template = Template(
        """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>

SELECT DISTINCT ?service ?issued
FROM <https://dataservices.fellesdatakatalog.digdir.no>
WHERE {{
    ?service a dcat:DataService .
    ?record foaf:primaryTopic ?service .
    ?record dct:issued ?issued .
    ?catalog dcat:service ?service .
    OPTIONAL {{ ?service dct:publisher ?dsPublisher . }}
    OPTIONAL {{ ?catalog dct:publisher ?catPublisher . }}
    BIND ( IF( EXISTS {{ ?service dct:publisher ?dsPublisher . }},
        ?dsPublisher, ?catPublisher ) AS ?publisher ) .
    ?publisher dct:identifier "$org_id" .
}}"""
    )

    return query_template.substitute(org_id=organization_id)
