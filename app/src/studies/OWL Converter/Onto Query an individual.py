from owlready2 import *
import sys
import os
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

onto_path.append("app/src/studies/OWL Converter/")  # Set the path to load the ontology
print("onto_path = ", onto_path)
#onto = get_ontology("file://ontoeamining.owl").load()
onto = get_ontology("onto_query_test.owl").load()

#list: A list of individuals that match the query.
# Define the individual name and class URL
individual_name = "APICall1"
class_url = "http://apieamining.edu.pt/core#API_Call"

# Search for individuals matching the query
#individuals = onto.search(type=onto[class_url], name=individual_name)
""" individuals = onto.search(iri="http://apieamining.edu.pt/core##APICall1")
print("individuals = ", individuals)
individuals = onto.search(type=IRIS["http://apieamining.edu.pt/core#API_Call"], iri="*APICall1")
print("individuals = ", individuals)
individuals = onto.search(name=individual_name, type=IRIS["http://apieamining.edu.pt/core#API_Call"])
print("individuals = ", individuals) """

ns = onto.get_namespace("http://apieamining.edu.pt/core#")
cls = ns.API_Call
inst = ns.APICall1
#individuals = onto.search(type=IRIS["http://apieamining.edu.pt/core#API_Call"], iri="*APICall1") # Isso funciona
individuals = onto.search(type=cls, iri="*"+ individual_name)
print("individuals = ", individuals)

# Check if the individual exists
if individuals:
    individual = individuals[0]  # Assuming there's only one matching individual
    print(f"Found individual: {individual.name}")
    # Access individual properties or perform further operations
else:
    print(f"Individual '{individual_name}' of class '{class_url}' not found.")
