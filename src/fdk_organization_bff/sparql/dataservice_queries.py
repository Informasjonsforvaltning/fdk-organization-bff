"""Module for DataService SPARQL-queries."""

from string import Template


def build_dataservices_by_publisher_query() -> str:
    """Build query to count dataservices grouped by publisher."""
    return """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?organizationNumber (COUNT(DISTINCT ?service) AS ?count)
WHERE {{
    ?service a dcat:DataService .
    ?record foaf:primaryTopic ?service .
    ?record a dcat:CatalogRecord .
    ?service dct:publisher ?publisher .
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
WHERE {{
    ?service a dcat:DataService .
    ?record foaf:primaryTopic ?service .
    ?record a dcat:CatalogRecord .
    ?record dct:issued ?issued .
    ?service dct:publisher ?publisher .
    ?publisher dct:identifier "$org_id" .
}}"""
    )

    return query_template.substitute(org_id=organization_id)


def data_services_report_query() -> str:
    """Query for data services report."""
    return """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX br: <https://raw.githubusercontent.com/Informasjonsforvaltning/organization-catalog/main/src/main/resources/ontology/organization-catalog.owl#>
SELECT DISTINCT ?service ?firstHarvested ?mediaType ?format ?orgId ?orgPath
WHERE {
  ?service a dcat:DataService .
  ?record foaf:primaryTopic ?service .
  ?record a dcat:CatalogRecord .
  ?record dct:issued ?firstHarvested .

  OPTIONAL { ?service dcat:mediaType ?mediaType . }
  OPTIONAL { ?service dct:format ?format . }

  OPTIONAL {
    ?service dct:publisher ?publisher .
    ?publisher dct:identifier ?orgId .
    ?publisher br:orgPath ?orgPath .
  }
}"""
