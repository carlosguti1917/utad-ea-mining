import pymongo
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD

import sys
import os
import os.path

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from api_gateway_load import configs

# Connect to MongoDB
myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
mydb = myclient[configs.MONGO_DB_SERVER["databasename"]]
collection_call_detail = mydb["kong-api-call-cleaned"]

# Retrieve specific attributes from the collection
# Replace this with the actual query to retrieve the attributes
result = collection_call_detail.find({}, {"_source.request.headers.client_id": 1})

# Create an RDF graph
g = Graph()
ns = Namespace("http://apieamining.edu.pt#")
owl = Namespace("http://www.w3.org/2002/07/owl#")
core = Namespace("http://apieamining.edu.pt/core#")
gufo = Namespace("http://purl.org/nemo/gufo#")

for doc in collection_call_detail.find():
    if '_source' in doc and 'request' in doc['_source'] and 'headers' in doc['_source']['request'] and 'client_id' in doc['_source']['request']['headers']:
        client_id = doc['_source']['request']['headers']['client_id']

        # Create RDF triples
        subject = ns["APICall"]  # You need to define the subject appropriately
        predicate = core["clint_id"]
        object_ = Literal(client_id)
        g.add((subject, predicate, object_))

g.serialize(destination="Onto_EA_Mining_v0.1.owl", format="turtle")


# # Define the OWL file and individual
# owl_file = "Onto EA Mining v0.1.owl"
# individual_uri = URIRef("http://apieamining.edu.pt#PartnerTeste1")  # Replace with an appropriate URI

# # Add the data property to the individual
# g.add((individual_uri, RDF.type, owl.NamedIndividual))
# g.add((individual_uri, core['consumerApp:App3'], Literal("Value of client_id", datatype=XSD.string)))

# # Save the RDF graph to the OWL file
# g.serialize(destination=owl_file, format='xml')