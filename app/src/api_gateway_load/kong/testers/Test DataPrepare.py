# Import the DataPrepare class
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service import DataPrepare

beginDate = "2024-03-14T09:36:56.042Z"

# Create an instance of DataPrepare
# Replace 'your_begindate_here' with the actual value
data_prep = DataPrepare.DataPrepare(beginDate)

# Call the getCalls method
#calls = data_prep.getCalls('your_begindate_here')

# Print the result
#print(data_prep)
print("DataPrepare com sucesso")