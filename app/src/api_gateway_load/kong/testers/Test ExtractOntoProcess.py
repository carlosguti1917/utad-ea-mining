from owlready2 import *
import sys
import os
import os.path
from rdflib import XSD

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from api_gateway_load.kong.service.ontology.process_view import ExtractOntoProcessView

onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
onto = get_ontology("EA Mining OntoUML Teste V1_1.owl").load()

beginDate = "2024-03-07T09:36:56.042Z"

#Core extration to Ongology
#extract_onto_core = ExtractOntoProcessView.navigate_and_export_ontology(onto)
#exists = extract_onto_core.individual_exists(onto, "API_Call", "APICall1")

attribute_is_util = ExtractOntoProcessView.verify_attribute_utility("cliente.chanelSource", "ecommerce-carts")


print("Extration of Core Ontology with success")
