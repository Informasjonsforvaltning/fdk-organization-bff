"""Module for Concept SPARQL-queries."""

from string import Template


def build_concepts_by_publisher_query() -> str:
    """Build query to count concepts grouped by publisher."""
    return """
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?organizationNumber (COUNT(DISTINCT ?concept) AS ?count)
        WHERE {{
            ?concept a skos:Concept .
            ?record foaf:primaryTopic ?concept .
            ?record a dcat:CatalogRecord .
            ?concept dct:publisher ?publisher .
            ?publisher dct:identifier ?organizationNumber .
        }}
        GROUP BY ?organizationNumber
    """


def build_org_concepts_query(organization_id: str) -> str:
    """Build query for an organizations concepts."""
    return Template("""
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT DISTINCT ?concept ?issued
        WHERE {{
            ?concept a skos:Concept .
            ?record foaf:primaryTopic ?concept .
            ?record a dcat:CatalogRecord .
            ?record dct:issued ?issued .
            ?concept dct:publisher ?publisher .
            ?publisher dct:identifier "$org_id" .
        }}
    """).substitute(org_id=organization_id)


def concepts_report_query() -> str:
    """Query for concepts report."""
    return """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX br: <https://raw.githubusercontent.com/Informasjonsforvaltning/organization-catalog/main/src/main/resources/ontology/organization-catalog.owl#>
SELECT DISTINCT ?concept ?firstHarvested ?referer ?orgId ?orgPath
WHERE {
  ?concept a skos:Concept .
  ?record foaf:primaryTopic ?concept .
  ?record a dcat:CatalogRecord .
  ?record dct:issued ?firstHarvested .

  OPTIONAL {
    ?concept dct:publisher ?publisher .
    ?publisher dct:identifier ?orgId .
    ?publisher br:orgPath ?orgPath .
  }

  OPTIONAL {
    ?referer dct:subject ?concept .
    ?refererRecord foaf:primaryTopic ?referer .
    ?refererRecord a dcat:CatalogRecord .
  }
}"""
