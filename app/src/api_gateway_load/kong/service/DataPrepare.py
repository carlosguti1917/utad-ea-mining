# main.py
import pymongo
import json
import sys
import os
import os.path
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..')))
from api_gateway_load import configs
from api_gateway_load.kong import ignore
from api_gateway_load.utils import nested_dicts

class DataPrepare:

    def __init__(self, begindate):
        """
        Initializes the class with the given begindate. Sets up the MongoDB client, database, and collections. 
        Retrieves and processes the API call details from the beginDate as a filter and removes noise from the data.
        """
        self.myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
        self.mydb = self.myclient[configs.MONGO_DB_SERVER["databasename"]]
        self.collection_call_detail = self.mydb["kong-api-call-details"]
        self.collection_call_cleaned = self.mydb["kong-api-call-cleaned"]
        x = self.getApiCallsDetails(begindate)   
        y = self.removeNoise(x)


    def getApiCallsDetails(self, begindate):
        api_calls = list(self.collection_call_detail.find({"_source.@timestamp": {"$gt": begindate}}))
        return api_calls

    def removeNoise(self, api_calls):
        cleaned_api_calls = []
        aux_path_key = {} # inicializando aux  vazia, aux representa a hierarquia de um atributo
        try:
            for call in api_calls:
                #remove calls with empty Consummer 
                if "_source" in call and "consumer" in call["_source"] and "id" in call["_source"]["consumer"]:               
                    # remove useless kong attributes 
                    cleaned_call = self.cleanIgnoredAttributes(call, aux_path_key.copy())
                    # ignore if the key already exists in self.collection_call_cleaned
                    existing_doc = self.collection_call_cleaned.find_one({ "_id": cleaned_call["_id"] })
                    if existing_doc is None:
                        #save cleaned call in mongo collection
                        self.collection_call_cleaned.insert_one(cleaned_call)
                        cleaned_api_calls.append(cleaned_call)
            return cleaned_api_calls
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In removeNoise module :", __name__)        

    def cleanIgnoredAttributes(self, obj, aux_path_key, path=[]):
        #print("obj = ", str(obj))
        ret = None
        try:
            cleaned_obj = {}
            if isinstance(obj, dict):
                for key, value in obj.items():
                    #new_path = f"{path}.{key}" if path else key
                    new_path = path + [key]  # Add the current key to the path
                    if aux_path_key:
                        aux_path_key[key] = '.'.join(new_path)  # updating the key in the aux dictionary with the full path
                    else:
                        aux_path_key[key] = '.'.join(new_path)

                    if key not in ignore.ignore_field_name and new_path not in ignore.ignore_field_name:
                        if isinstance(value, dict):
                            cleaned_obj[key] = self.cleanIgnoredAttributes(value, aux_path_key, new_path)
                        elif isinstance(value, list):
                            cleaned_obj[key] = [self.cleanIgnoredAttributes(item, aux_path_key, new_path) for item in value if item]
                        elif value or (isinstance(value, list) and value):
                            cleaned_obj[key] = value
                ret = cleaned_obj                             
            elif isinstance(obj, list):
                ret = [self.cleanIgnoredAttributes(item, aux_path_key, new_path) for item in obj if item]
            else:
                ret = obj 
            return ret                     

        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In cleanIgnoredAttributes module :", __name__)          
    


