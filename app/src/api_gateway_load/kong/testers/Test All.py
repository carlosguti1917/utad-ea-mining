# Import the DataPrepare class
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service import LoaderCalls as loader
from service.ontology import ExtractOntoCore
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
