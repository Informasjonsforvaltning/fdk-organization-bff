"""Module for Dataset SPARQL-queries."""

from string import Template


def build_org_datasets_query(organization_id: str) -> str:
    """Build query for an organizations datasets."""
    query_template = Template("""
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX fdk: <https://raw.githubusercontent.com/Informasjonsforvaltning/fdk-reasoning-service/main/src/main/resources/ontology/fdk.owl#>

SELECT DISTINCT ?dataset ?issued ?isAuthoritative ?isOpenData
WHERE {{
    ?dataset a dcat:Dataset .
    ?record foaf:primaryTopic ?dataset .
    ?record a dcat:CatalogRecord .
    ?record dct:issued ?issued .
    OPTIONAL {{ ?dataset fdk:isOpenData ?isOpenData . }}
    OPTIONAL {{ ?dataset fdk:isAuthoritative ?isAuthoritative . }}
    ?dataset dct:publisher ?publisher .
    ?publisher dct:identifier "$org_id" .
}}""")

    return query_template.substitute(org_id=organization_id)


def build_nap_org_datasets_query(organization_id: str) -> str:
    """Build query for an organizations NAP datasets."""
    query_template = Template("""
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX fdk: <https://raw.githubusercontent.com/Informasjonsforvaltning/fdk-reasoning-service/main/src/main/resources/ontology/fdk.owl#>

SELECT DISTINCT ?dataset ?issued ?isAuthoritative ?isOpenData
WHERE {{
    ?dataset a dcat:Dataset .
    ?dataset fdk:isRelatedToTransportportal ?isNAP .
    FILTER (STR(?isNAP) = "true")
    ?record foaf:primaryTopic ?dataset .
    ?record a dcat:CatalogRecord .
    ?record dct:issued ?issued .
    OPTIONAL {{ ?dataset fdk:isOpenData ?isOpenData . }}
    OPTIONAL {{ ?dataset fdk:isAuthoritative ?isAuthoritative . }}
    ?dataset dct:publisher ?publisher .
    ?publisher dct:identifier "$org_id" .
}}""")

    return query_template.substitute(org_id=organization_id)


def build_datasets_by_publisher_query() -> str:
    """Build query to count datasets grouped by publisher."""
    return """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?organizationNumber (COUNT(DISTINCT ?dataset) AS ?count)
WHERE {{
    ?dataset a dcat:Dataset .
    ?record foaf:primaryTopic ?dataset .
    ?record a dcat:CatalogRecord .
    ?dataset dct:publisher ?publisher .
    ?publisher dct:identifier ?organizationNumber .
}}
GROUP BY ?organizationNumber"""


def build_nap_datasets_by_publisher_query() -> str:
    """Build query to count NAP datasets grouped by publisher."""
    return """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX fdk: <https://raw.githubusercontent.com/Informasjonsforvaltning/fdk-reasoning-service/main/src/main/resources/ontology/fdk.owl#>

SELECT ?organizationNumber (COUNT(DISTINCT ?dataset) AS ?count)
WHERE {{
    ?dataset a dcat:Dataset .
    ?record foaf:primaryTopic ?dataset .
    ?record a dcat:CatalogRecord .
    ?dataset fdk:isRelatedToTransportportal ?isNAP .
    FILTER (STR(?isNAP) = "true")
    ?dataset dct:publisher ?publisher .
    ?publisher dct:identifier ?organizationNumber .
}}
GROUP BY ?organizationNumber"""


def datasets_general_report_query() -> str:
    """Query general metrics for datasets report."""
    return """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX fdk: <https://raw.githubusercontent.com/Informasjonsforvaltning/fdk-reasoning-service/main/src/main/resources/ontology/fdk.owl#>
SELECT ?dataset ?firstHarvested ?theme ?accessRights ?provenance ?isOpenData ?transportportal
 WHERE {
  ?dataset a dcat:Dataset .
  ?record foaf:primaryTopic ?dataset .
  ?record a dcat:CatalogRecord .
  ?record dct:issued ?firstHarvested .

  OPTIONAL { ?dataset dcat:theme ?theme . }
  OPTIONAL { ?dataset dct:accessRights ?accessRights . }
  OPTIONAL { ?dataset dct:provenance ?provenance . }
  OPTIONAL { ?dataset fdk:isOpenData ?isOpenData . }
  OPTIONAL { ?dataset fdk:isRelatedToTransportportal ?transportportal . }
}"""


def datasets_format_report_query() -> str:
    """Query format metrics for datasets report."""
    return """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dct: <http://purl.org/dc/terms/>
SELECT ?dataset ?mediaType ?format
WHERE {
  ?dataset a dcat:Dataset .
  ?record foaf:primaryTopic ?dataset .
  ?record a dcat:CatalogRecord .

  ?dataset dcat:distribution ?distribution .
  ?distribution dcat:mediaType ?mediaType .
  ?distribution dct:format ?format .
}"""


def datasets_publisher_report_query() -> str:
    """Query publisher metrics for datasets report."""
    return """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX br: <https://raw.githubusercontent.com/Informasjonsforvaltning/organization-catalog/main/src/main/resources/ontology/organization-catalog.owl#>
SELECT ?dataset ?orgId ?orgPath
WHERE {
  ?dataset a dcat:Dataset .
  ?record foaf:primaryTopic ?dataset .
  ?record a dcat:CatalogRecord .

  ?dataset dct:publisher ?publisher .
  ?publisher dct:identifier ?orgId .
  ?publisher br:orgPath ?orgPath .
}"""
