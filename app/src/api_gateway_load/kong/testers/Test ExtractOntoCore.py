# Import the DataPrepare class
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service.ontology import ExtractOntoCore


beginDate = "2024-03-07T09:36:56.042Z"

extract_onto_core = ExtractOntoCore.ExtractOntoCore(beginDate)

#onto = ExtractOntoCore.ExtractOntoCore.onto
#exists = extract_onto_core.individual_exists(onto, "API_Call", "APICall1")
#print("ExtractOntoCore exists")


# Print the result
#print(data_prep)
print("ExtractOntoCore com sucesso")