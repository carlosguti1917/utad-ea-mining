# Import the DataPrepare class
from owlready2 import *
import sys
import os

import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from api_gateway_load import configs

# onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
# #onto = get_ontology("EA Mining OntoUML Teste V1_3.owl").load()
# onto = get_ontology(configs.OWL_FILE["file_name"]).load()

# from api_gateway_load.kong.service import LoaderCalls as loader
# from api_gateway_load.kong.service import DataPrepare
# from api_gateway_load.kong.service.ontology import ExtractOntoCore
# from api_gateway_load.kong.service.ontology.process_view import ExtractOntoProcessView
from api_gateway_load.utils import onto_util

# observação, esta hora é UTC - para o Brasil considerar 3h de avanço em relação a hora desejada.
#beginDate = "2024-04-15T03:01:00.000Z"

# select the frequent temporal correlation from csv file
file_path = './temp/'   
file_nm = "ftc_list.csv"
#onto_util.event_transactions_selection(file_path, file_nm)


df = pd.read_csv(file_path + file_nm)
#cleaned_data = onto_util.remove_ftc_noise(df, None)
#file_nm = "ftc_list_cleaned.csv"     
#cleaned_data.to_csv(file_path + file_nm, index=False)

file_path = './temp/'   
file_nm = "ftc_list_cleaned.csv"
df = pd.read_csv(file_path + file_nm)
data_case_id = onto_util.case_id_generation(df, None, True)
file_nm = "ftc_list_with_case_id.csv"
data_case_id.to_csv(file_path + file_nm, index=False)

print("OntoUtil executed with success")
