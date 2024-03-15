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
ns = onto.get_namespace("http://apieamining.edu.pt/core#")
resource_address = "http://apieamining.edu.pt#"
cls = ns.API_Call
inst = ns.APICall1

resource_about= "http://apieamining.edu.pt#APICall1"
# Define the SPARQL query
query = f"SELECT ?individual WHERE {{ ?individual a <{class_url}> . ?individual rdfs:label '{individual_name}' }}" # Isso funciona
#query = f"SELECT ?individual WHERE {{ ?individual a <http://apieamining.edu.pt/core#API_Call> . ?individual rdf:resource '{resource_address}{individual_name}'^^xsd:string . }}"""

# Execute the SPARQL query
graph = default_world.as_rdflib_graph()
result1 = list(graph.query(query))
print("individuals = ", result1)
#results = list(default_world.sparql(query))
#print("individuals = ", results)

# Check if the individual exists
if result1:
    for result in result1:
        individual_name = result['individual']
        print(f"Found individual: {individual_name}")
        # Access individual properties or perform further operations
else:
    print(f"Individual '{individual_name}' of class '{class_url}' not found.")

#query2 = f"SELECT ?individual WHERE {{ ?individual <{resource_about}>  'APICall1' }}"    
#query2 = f"SELECT ?i WHERE {{ ?i <http://apieamining.edu.pt/core#API_Call> <http://apieamining.edu.pt#APICall1> }}"
query2 = f"SELECT ?individual WHERE {{ ?individual a <{class_url}> . ?individual rdf:about <http://apieamining.edu.pt#APICall1> }}" # 

# Execute the SPARQL query
graph = default_world.as_rdflib_graph()
result2 = list(graph.query(query2))
print("individuals = ", result2)

