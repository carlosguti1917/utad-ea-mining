import pymongo
#import .configs as configs

import pandas
import re
import sys
import os.path
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import configs as configs
import domain.Uri

class MongoDbRepository4Kong:

    def __init__(self):
        pass

    @staticmethod
    def saveCallDetails(dicJson):
        """
        A function to save call details to a MongoDB database.
        Args:
            dicJson (dict): The JSON data to be saved.
        Returns:
            None
        """
        try:
            myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
            mydb = myclient[configs.MONGO_DB_SERVER["databasename"]]
            collection_call_detail = mydb["kong-api-call-details"]
            x = collection_call_detail.insert_one(dicJson)
            #print("****dicJson ****", dicJson)

        except Exception as error:
            print("MongoDvRepository.saveCallDetails()")
            print(__class__, __name__, __file__)
            print('MongoDvRepository.saveCallDetails() Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))