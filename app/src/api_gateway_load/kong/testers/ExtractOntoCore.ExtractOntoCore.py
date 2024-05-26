# Import the DataPrepare class
from owlready2 import *
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.src import configs
from app.src.utils import onto_util

onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
#onto = get_ontology("EA Mining OntoUML Teste V1_3.owl").load()
onto = get_ontology(configs.OWL_FILE["file_name"]).load()

from api_gateway_load.kong.service import LoaderCalls as loader
from api_gateway_load.kong.service import DataPrepare
from app.src.api_gateway_load.kong.service.ontology.core import ExtractOntoCore
from app.src.generic_service.process_view import ExtractProcessFromOntology
from app.src.generic_service.process_view import ProcessDiscovery
from app.src.generic_service.process_view import ExtractArchimateProcessoView

# observação, esta hora é UTC - para o Brasil considerar 3h de avanço em relação a hora desejada.
beginDate = "2024-05-02T01:50:00.000Z"

#Loader Calls from Elastic
#loader.LoaderCalls(beginDate) # Recupera as chamadas da API do Elastic e grava no MongoDB
print("LoaderCalls com sucesso")

#Data Preparetion # Vale para versão final - Recupera as chamadas cruas do MongoDB e grava no MongoDB as chamadas limpas de dados do Kong que não interessam
beginDate = datetime.strptime(beginDate, "%Y-%m-%dT%H:%M:%S.%fZ")
beginDate = beginDate - timedelta(hours=3) # Subtract 3 hours
beginDate = beginDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ") # Convert it back to a string in the ISO 8601 format
#data_prep = DataPrepare.DataPrepare(beginDate)
print("DataPrepare com sucesso")

#Core extration to Ongology
#extract_onto_core = ExtractOntoCore.ExtractOntoCore(beginDate) # Vale para versão final 
print("Extration of Core Ontology with success")

#remove_frequent_items
#ExtractProcessFromOntology.record_frequent_items_to_ignore(onto)  # Vale para versão final
print("Remove Frequent Items with success")

#mining process view
#ftc_list = ExtractProcessFromOntology.mining_frequent_temporal_correlations(onto) # Vale para versão final
print("Mining Frequent Temporal Correlations with success")

#create Process in Ontology
ProcessDiscovery.processes_discovery() # Vale para versão final 
print("Processes Discovery with success")

#extract the process view in archimate model
ExtractArchimateProcessoView.extract_archimate_process() # Vale para versão final

print("All tests executed with success")
