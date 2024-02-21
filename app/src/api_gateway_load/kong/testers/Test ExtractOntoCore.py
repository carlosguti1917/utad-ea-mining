# Import the DataPrepare class
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service.ontology import ExtractOntoCore


#beginDate = "2023-02-07T09:36:56.042Z"

# Create an instance of DataPrepare
# Replace 'your_begindate_here' with the actual value
extract_onto_core = ExtractOntoCore.ExtractOntoCore()

# Call the getCalls method
#calls = data_prep.getCalls('your_begindate_here')

# Print the result
#print(data_prep)
print("ExtractOntoCore com sucesso")