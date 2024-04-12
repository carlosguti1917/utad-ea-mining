# Import the DataPrepare class
from owlready2 import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_gateway_load import configs

onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
#onto = get_ontology("EA Mining OntoUML Teste V1_3.owl").load()
onto = get_ontology(configs.OWL_FILE["file_name"]).load()

from service import LoaderCalls as loader
from service.ontology import ExtractOntoCore
from service.ontology.process_view import ExtractOntoProcessView
from service import DataPrepare

beginDate = "2024-03-07T09:36:56.042Z"

#Loader Calls from Elastic

loader.LoaderCalls(beginDate)
print("LoaderCalls com sucesso")

#Data Preparetion
data_prep = DataPrepare.DataPrepare(beginDate)
print("DataPrepare com sucesso")

#Core extration to Ongology
extract_onto_core = ExtractOntoCore.ExtractOntoCore(beginDate)
#exists = extract_onto_core.individual_exists(onto, "API_Call", "APICall1")
print("Extration of Core Ontology with success")

#remove_frequent_items(onto)
ExtractOntoProcessView.remove_frequent_items(onto)  
print("Remove Frequent Items with success")

ExtractOntoProcessView.mining_frequent_temporal_correlations(onto)
print("Mining Frequent Temporal Correlations with success")
