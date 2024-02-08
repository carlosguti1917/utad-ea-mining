from arango import ArangoClient
from pyArango.connection import *
#import arango.client.ArangoClient
#from arangordf import ar
from arango_rdf import ArangoRDF
from rdflib import URIRef

import config

conn = Connection(arangoURL=config.ARANGO_DB_SERVER["host"], username=config.ARANGO_DB_SERVER["user"], password=config.ARANGO_DB_SERVER["password"])
db1 = conn["_system"]



if db1.hasGraph("default_graph"):
    print("graph ok")

ddGraph = db1.graphs['transversalGraph_CorrelationsV4']

db = ArangoClient(hosts=config.ARANGO_DB_SERVER["host"]).db("_system", username=config.ARANGO_DB_SERVER["user"], password=config.ARANGO_DB_SERVER["password"])

if db.has_graph("default_graph"):
    print("ok default_graph")

# Initializes default_graph and sets RDF graph identifier (ArangoDB sub_graph)
# Optional: sub_graph (stores graph name as the 'graph' attribute on all edges in Statement collection)
# Optional: default_graph (name of ArangoDB Named Graph, defaults to 'default_graph',
#           is root graph that contains all collections/relations)
#adb_rdf = ArangoRDF(db, sub_graph="http://data.sfgov.org/ontology")
adb_rdf = ArangoRDF(db, "transversalGraph_CorrelationsV4")
#config = {"normalize_literals": False}  # default: False
#config = adb_rdf.get_config_by_key_value('graph', 'transversalGraph_CorrelationsV4')
uriref = URIRef("teste")
adb_rdf.build_statement_edge(uriref, "_from", "_to", "transversalGraph_CorrelationsV4")
#adb_rdf.init_rdf_collections(edge="Correlation_V4")
print("initialized collections")


#rdf_graph = adb_rdf.export_rdf(f"./examples/data/rdfExport.xml", format="xml")
rdf_graph = adb_rdf.export_rdf(f"C:/Temp/Utad/Arangodb_Import/Ontology/rdfExport.xml", format="xml", query_options="_key=@key")
