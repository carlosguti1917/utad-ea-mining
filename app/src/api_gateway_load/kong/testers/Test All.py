# Import the DataPrepare class
from owlready2 import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from api_gateway_load import configs

onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
#onto = get_ontology("EA Mining OntoUML Teste V1_3.owl").load()
onto = get_ontology(configs.OWL_FILE["file_name"]).load()

from api_gateway_load.kong.service import LoaderCalls as loader
from api_gateway_load.kong.service import DataPrepare
from api_gateway_load.kong.service.ontology import ExtractOntoCore
from api_gateway_load.kong.service.ontology.process_view import ExtractOntoProcessView

beginDate = "2024-03-07T09:36:56.042Z"

#Loader Calls from Elastic
#loader.LoaderCalls(beginDate) # Recupera as chamadas da API do Elastic
print("LoaderCalls com sucesso")

#Data Preparetion # Vale para versão final
#data_prep = DataPrepare.DataPrepare(beginDate)
print("DataPrepare com sucesso")

#Core extration to Ongology
#extract_onto_core = ExtractOntoCore.ExtractOntoCore(beginDate) # Vale para versão final
#exists = extract_onto_core.individual_exists(onto, "API_Call", "APICall1")
print("Extration of Core Ontology with success")

#remove_frequent_items
#ExtractOntoProcessView.remove_frequent_items(onto)  # Vale para versão final
print("Remove Frequent Items with success")

ExtractOntoProcessView.mining_frequent_temporal_correlations(onto)
print("Mining Frequent Temporal Correlations with success")
