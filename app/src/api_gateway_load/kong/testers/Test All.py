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

# observação, esta hora é UTC - para o Brasil considerar 3h de avanço em relação a hora desejada.
beginDate = "2024-04-15T03:01:00.000Z"

#Loader Calls from Elastic
#loader.LoaderCalls(beginDate) # Recupera as chamadas da API do Elastic e grava no MongoDB
print("LoaderCalls com sucesso")

#Data Preparetion # Vale para versão final - Recupera as chamadas cruas do MongoDB e grava no MongoDB as chamadas limpas de dados do Kong que não interessam
#data_prep = DataPrepare.DataPrepare(beginDate)
print("DataPrepare com sucesso")

#Core extration to Ongology
#extract_onto_core = ExtractOntoCore.ExtractOntoCore(beginDate) # Vale para versão final 
print("Extration of Core Ontology with success")

#remove_frequent_items
#ExtractOntoProcessView.record_frequent_items_to_ignore(onto)  # Vale para versão final
print("Remove Frequent Items with success")

#mining process view
ExtractOntoProcessView.mining_frequent_temporal_correlations(onto) # Vale para versão final
#TODO a lógica está gerando um número muito grande de FTCs. Revisar
#Calcular uma amostra de Calls para testar a lógica
# Ainda assim, tá gerando FTC de mais

print("Mining Frequent Temporal Correlations with success")
