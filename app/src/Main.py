# Import the DataPrepare class
from owlready2 import *
import sys
import os
from datetime import datetime, timedelta
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.src import configs
from app.src.utils import onto_util
from app.src.utils import archimate_util

onto_path.append(configs.OWL_FILE["file_path"])  # Set the path to load the ontology
onto = get_ontology(configs.OWL_FILE["file_name"]).load()

from app.src.api_gateway_load.kong.service import LoaderCalls as loader
from app.src.api_gateway_load.kong.service import DataPrepare
from app.src.api_gateway_load.kong.service.ontology.core import ExtractOntoCore
from app.src.generic_service.process_view import ExtractProcessFromOntology
from app.src.generic_service.process_view import ProcessDiscovery
from app.src.generic_service.process_view import ExtractArchimateProcessoView
from app.src.api_gateway_load.kong.service.ontology.core import ExtractApiDocumentation
from app.src.generic_service.data_relation_view import ExtractCorrelateDataObject
from app.src.generic_service.data_relation_view import ExtractArchimateDataRelationView

# observação, esta hora é UTC - para o Brasil considerar 3h de avanço em relação a hora desejada.
#beginDate = "2024-08-18T18:00:00.000Z" # Health
# beginDate = "2024-07-25T02:00:00.000Z" Loyalty Card
beginDate = "2024-06-03T22:37:40.000Z"
# observação, esta hora é UTC - para o Brasil considerar 3h de avanço em relação a hora desejada.
endDate = "2024-06-03T22:40:00.000Z" # Loyalty Card

start_time = datetime.now()


#Loader Calls from Elastic
#loader.LoaderCalls(beginDate, endDate) # Recupera as chamadas da API do Elastic e grava no MongoDB
print("LoaderCalls com sucesso")

# Data Preparetion # Vale para versão final - Recupera as chamadas cruas do MongoDB e grava no MongoDB as chamadas limpas de dados do Kong que não interessam
beginDate = datetime.strptime(beginDate, "%Y-%m-%dT%H:%M:%S.%fZ")
beginDate = beginDate - timedelta(hours=3) # Subtract 3 hours
beginDate = beginDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ") # Convert it back to a string in the ISO 8601 format
endDate = datetime.strptime(endDate, "%Y-%m-%dT%H:%M:%S.%fZ")
endDate = endDate - timedelta(hours=3) # Subtract 3 hours
endDate = endDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ") # Convert it back to a string in the ISO 8601 format

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
#process_list = ProcessDiscovery.processes_discovery() # Vale para versão final 
print("Processes Discovery with success")

# prepare the inicial xml of the archimate model
file_name = configs.ARCHIMATE_MODEL["archimate_file_name"]
root = archimate_util.prepare_archimate_exchange_model()
archimate_util.save_archimate_exchange_model(root, file_name)

#extract the process view in archimate model
#ExtractArchimateProcessoView.extract_archimate_process(file_name) #legado
ExtractArchimateProcessoView.extract_archimate_process_contexfull(file_name) # Vale para versão final plan
print("Process View in Archimate Extracted with success")

# obtain swaggers and save API Documentations to the ontology
#docs = ExtractApiDocumentation.get_api_documentations_from_files(onto) 
print("ApiDocumentation Extracted with success")

#correlate the API Resources to the API Documentations
#doc_api_relators = ExtractApiDocumentation.correlate_resources_to_documentations(onto)
print("ApiDocumentation Correlated to Resources with success")

#fddc_list = ExtractCorrelateDataObject.mining_frequent_data_domain_correlations(onto)
print("Frequent Data Domain Correlations created with success")

#data_correlations= ExtractCorrelateDataObject.mining_correlated_data_objects(onto)
print("Correlated Data Objects created with success")

#extractract archimate data relation 
ExtractArchimateDataRelationView.extract_archimate_data_relation_view(file_name)
print("ArchiMate Data Objects relation created with success")

end_time = datetime.now()

print(f"All tests executed with success in {end_time - start_time} milliseconds")

print(f"All tests executed with success")


