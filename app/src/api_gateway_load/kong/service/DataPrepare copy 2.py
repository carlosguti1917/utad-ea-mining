import pymongo
import json
import sys
import os.path
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..')))
# Now you can import the config module and use it
from api_gateway_load import configs
from api_gateway_load.kong.repository.MongoDbRepository4Kong import MongoDbRepository4Kong
from api_gateway_load.kong import ignore

class DataPrepare:
# This class aims to clean the data and prepare data to be mined. 
    
    def __init__(self):
        pass

    def __init__(self, begindate):
        call_list = []
        try:
            call_list = self.getCalls(begindate)
            if (call_list is not None and len(call_list) > 0):
                for call_info in call_list:
                    #jsonobj = json.dumps(call_info)
                    #listOfJsonDic = json.loads(jsonobj)
                    self.removeNoise(call_info)
            #self.saveCallDetails(call_info)
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In save_correlation_matched_values module :", __name__)              


    @staticmethod
    def getCalls(begindate) -> list:
        """
        Get the calls from mongo data base.
        the list is a DataFrame
        """
        ret = []
        try:
            ret = MongoDbRepository4Kong.getApiCallsDetails()

            # req_body = LoaderCalls.getElasticRequestBody(begindate)
            # req = requests.get(url, headers=my_headers, data=req_body, verify=False)
            # resp_body = req.json()
            # #call_list = []
            # #print("qtde de calls", len(resp_body))
            # jsonobj = json.dumps(resp_body)
            # dicJsonResponse = json.loads(jsonobj)
            # return dicJsonResponse      
            return ret

        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In save_correlation_matched_values module :", __name__)   


    def removeNoise(self, param_data):
        self.ignore_list = ignore.ignore_field_name  # Import the list of ignored attributes from ignore.py
        cleaned_data = []
        try:
            #json_data  = json.loads(jsonObj, parse_float=lambda x: float('nan') if x == 'nan' else float(x))
            for idx, row in param_data.iterrows():
                cleaned_document  = {}
                for attribute, value in row.items():
                    if attribute not in self.ignore_list and value is not None and pd.notnull(value):
                        if isinstance(value, dict):
                            cleaned_document[attribute] = {k: v for k, v in value.items() if k not in self.ignore_list}
                        else:
                            cleaned_document[attribute] = value
                cleaned_data.append(cleaned_document)  # Append the cleaned dictionary to the result list            
            print("removeNoise", str(cleaned_data))
            return cleaned_data
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In save_correlation_matched_values module :", __name__)         
      

# Connect to MongoDB
""" 
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
collection = db["your_collection_name"] 


# Query Kong Gateway logs
kong_logs = collection.find({ "source": "kong_gateway" })

# Clean the JSON data
cleaned_logs = []
for log in kong_logs:
    # Perform data cleaning operations here, such as removing noise or normalizing data
    cleaned_logs.append(cleaned_log)

# Store the cleaned JSON data in a new table
prepared_collection = db["kong-api-call-prepared"]
prepared_collection.insert_many(cleaned_logs)
"""