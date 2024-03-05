from owlready2 import *
import sys
import os
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from api_gateway_load import configs

# Load the OWL ontology
#onto_path.append(".")  # Set the path to load the ontology
#onto_path.append("c:/gitHub/utad/utad-ea-mining/app/src/studies/OWL Converter/")  # Set the path to load the ontology
onto_path.append("app/src/studies/OWL Converter/")  # Set the path to load the ontology
print("onto_path = ", onto_path)
#onto = get_ontology("file://ontoeamining.owl").load()
onto = get_ontology("onto_query_test.owl").load()
classes = list(onto.classes())  
individuals = list(onto.individuals())
propertis = list(onto.properties())

#results = onto.sparql(query)
#result = list(results)
result2 = onto.search(iri = "*APICall*")
result21 = onto.search_one(iri = "*APICall*")
result3 = onto.search(iri = "APICall1")

#result4 = onto.search_one(is_a = "core.API_Call")


for i in result2:
    print("teste = ", i.name)
    #    print("teste namespade = ", i.namespace())
    print("teste iri = ", i.iri)
    print("teste classes = ", i.is_a)

    
 # Check if the individual is an instance of the ontology class "API Call"
# Check if "APICall1" is a valid individual

# Get the class object using get_cls_by_name
#cls = onto.get_cls_by_name("API_Call")
ns = onto.get_namespace("http://apieamining.edu.pt/core#")
#cls = onto.get_class("http://apieamining.edu.pt/core#API_Call")
cls = ns.API_Call
#cls = IRIS["http://apieamining.edu.pt/core#API_Call"]

for i in onto.individuals():
    print(cls)
    if isinstance(i, cls):
        print(i,"is an instance of API Call class")
    else:
        print(i, " is not an instance of API Call class")
else:
    print("APICall1 is not a valid individual in the ontology")

#list: A list of individuals that match the query.
    #with onto:
query = "ASK {:" + "APICall1" + " a :" + "http://apieamining.edu.pt/core#API_Call" + "}"
print("query: ", query)
#result = list(onto.sparql(query))
#result = list(onto.individuals(name="APICall1"))
#print(result)
