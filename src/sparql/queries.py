from src.sparql.builder import SparqlSelect, SparqlWhere, SparqlGraphTerm, SparqlOptional, SparqlBuilder, SparqlFunction
from src.sparql.rdf_namespaces import NamespaceProperty, DCT, FOAF, OWL, RDF, SparqlFunctionString, DCAT
from src.utils import ContentKeys


def build_dataset_publisher_query() -> str:
    dct = DCT(NamespaceProperty.TTL)
    foaf = FOAF(NamespaceProperty.TTL)
    owl = OWL(NamespaceProperty.TTL)
    rdf = RDF(NamespaceProperty.TTL)

    item_var = "item"
    prefixes = [dct, foaf, owl]
    select = SparqlSelect(
        variable_names=[ContentKeys.PUBLISHER, ContentKeys.SAME_AS, ContentKeys.ORG_NAME],
        functions=[
            SparqlFunction(
                function=SparqlFunctionString.COUNT,
                var=item_var,
                as_var="count"
            )
        ]
    )
    publisher_a_foaf_agent = SparqlGraphTerm.build_graph_pattern(
        subject=SparqlGraphTerm(var=ContentKeys.PUBLISHER),
        predicate=SparqlGraphTerm(namespace_property=rdf.type),
        obj=SparqlGraphTerm(namespace_property=foaf.agent),
        close_pattern_with="."
    )
    publisher_foaf_name = SparqlGraphTerm.build_graph_pattern(
        subject=SparqlGraphTerm(var=ContentKeys.PUBLISHER),
        predicate=SparqlGraphTerm(namespace_property=foaf.name),
        obj=SparqlGraphTerm(var=ContentKeys.ORG_NAME),
        close_pattern_with="."
    )
    item_dct_publisher = SparqlGraphTerm.build_graph_pattern(
        subject=SparqlGraphTerm(var=item_var),
        predicate=SparqlGraphTerm(namespace_property=dct.publisher),
        obj=SparqlGraphTerm(var=ContentKeys.PUBLISHER),
        close_pattern_with="."
    )
    optional_publisher_same_as = SparqlOptional(
        graphs=[
            SparqlGraphTerm.build_graph_pattern(
                subject=SparqlGraphTerm(var=ContentKeys.PUBLISHER),
                predicate=SparqlGraphTerm(namespace_property=owl.sameAs),
                obj=SparqlGraphTerm(var=ContentKeys.SAME_AS),
                close_pattern_with="."
            )
        ]
    )
    where = SparqlWhere(
        graphs=[
            publisher_a_foaf_agent,
            publisher_foaf_name,
            item_dct_publisher
        ],
        optional=optional_publisher_same_as
    )

    return SparqlBuilder(
        prefix=prefixes,
        select=select,
        where=where,
        group_by_vars=[ContentKeys.PUBLISHER, ContentKeys.ORG_NAME, ContentKeys.SAME_AS]
    ).build()


def build_dataservices_publisher_query() -> str:
    "PREFIX dct: <http://purl.org/dc/terms/> " \
    "PREFIX foaf: <http://xmlns.com/foaf/0.1/> " \
    "PREFIX owl: <http://www.w3.org/2002/07/owl%23> " \
    "PREFIX dcat: <http://www.w3.org/ns/dcat%23> " \
    "SELECT ?publisher ?sameAs (COUNT(?service) AS ?count) " \
    "WHERE { " \
    "?catalog dct:publisher ?publisher . " \
    "?catalog dcat:service ?service . " \
    "OPTIONAL{ ?publisher owl:sameAs ?sameAs } } " \
    "GROUP BY ?publisher ?sameAs"

    dct = DCT(NamespaceProperty.TTL)
    foaf = FOAF(NamespaceProperty.TTL)
    owl = OWL(NamespaceProperty.TTL)
    dcat = DCAT(NamespaceProperty.TTL)

    catalog_var = "catalog"
    service_var = "service"
    catalog_graph_term = SparqlGraphTerm(var=catalog_var)
    publisher_graph_term = SparqlGraphTerm(var=ContentKeys.PUBLISHER)

    prefixes = [dct, foaf, owl, dcat]
    select = SparqlSelect(
        variable_names=[ContentKeys.PUBLISHER, ContentKeys.SAME_AS],
        functions=[
            SparqlFunction(
                function=SparqlFunctionString.COUNT,
                var=service_var,
                as_var=ContentKeys.COUNT
            )
        ]
    )
    catalog_dct_publisher = SparqlGraphTerm.build_graph_pattern(
        subject=catalog_graph_term,
        predicate=SparqlGraphTerm(namespace_property=dct.publisher),
        obj=publisher_graph_term,
        close_pattern_with="."
    )
    catalog_dcat_service = SparqlGraphTerm.build_graph_pattern(
        subject=catalog_graph_term,
        predicate=SparqlGraphTerm(namespace_property=dcat.service),
        obj=SparqlGraphTerm(var=service_var),
        close_pattern_with="."
    )
    optional_publisher_same_as = SparqlOptional(
        graphs=[
            SparqlGraphTerm.build_graph_pattern(
                subject=SparqlGraphTerm(var=ContentKeys.PUBLISHER),
                predicate=SparqlGraphTerm(namespace_property=owl.sameAs),
                obj=SparqlGraphTerm(var=ContentKeys.SAME_AS),
                close_pattern_with="."
            )
        ]
    )

    where = SparqlWhere(
        graphs=[catalog_dct_publisher, catalog_dcat_service],
        optional=optional_publisher_same_as
    )

    return SparqlBuilder(
        prefix=prefixes,
        select=select,
        where=where,
        group_by_vars=[ContentKeys.PUBLISHER, ContentKeys.SAME_AS]
    ).build()
