# Import the DataPrepare class
from owlready2 import *
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from api_gateway_load import configs
from api_gateway_load.utils import onto_util

onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
#onto = get_ontology("EA Mining OntoUML Teste V1_3.owl").load()
onto = get_ontology(configs.OWL_FILE["file_name"]).load()

from api_gateway_load.kong.service import LoaderCalls as loader
from api_gateway_load.kong.service import DataPrepare
from api_gateway_load.kong.service.ontology import ExtractOntoCore
from app.src.api_gateway_load.kong.service.ontology.process_view import ExtractProcessFromOntology
from app.src.api_gateway_load.kong.service.ontology.process_view import ProcessDiscovery
from app.src.api_gateway_load.kong.service.ontology.process_view import ExtractArchimateProcessoView
from app.src.api_gateway_load.kong.service.ontology.data_relation_view import ExtractApiDocumentation
from app.src.api_gateway_load.kong.service.ontology.data_relation_view import ExtractCorrelateDataObject
from app.src.api_gateway_load.kong.service.ontology.data_relation_view import ExtractArchimateDataRelationView

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
#ProcessDiscovery.processes_discovery() # Vale para versão final 
print("Processes Discovery with success")

#extract the process view in archimate model
#ExtractArchimateProcessoView.extract_archimate_process() # Vale para versão final

# obtain swaggers and save API Documentations to the ontology
#docs = ExtractApiDocumentation.get_api_documentations_from_files(onto) 
print("ApiDocumentation Extracted with success")

#correlate the API Resources to the API Documentations
#doc_api_relators = ExtractApiDocumentation.correlate_resources_to_documentations(onto)
print("ApiDocumentation Correlated to Resources with success")

#fddc_list = ExtractCorrelateDataObject.mining_frequent_data_domain_correlations(onto)
print("Frequent Data Domain Correlations created with success")

#cod= ExtractCorrelateDataObject.mining_correlated_data_objects(onto)
print("Correlated Data Objects created with success")

#extractract archimate data relation 
ExtractArchimateDataRelationView.extract_archimate_data_relation_view()

print("All tests executed with success")
