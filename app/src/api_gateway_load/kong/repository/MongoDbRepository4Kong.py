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

        except Exception as error:
            print("MongoDvRepository.saveCallDetails()")
            print(__class__, __name__, __file__)
            print('saveCallDetails() Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))


    def getApiCallsDetails() -> list:
        # itera sobre os logs obtidos no banco de dados e retorna a lista destes logs
        try:
            myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
            mydb = myclient[configs.MONGO_DB_SERVER["databasename"]]
            collection_calls = mydb["kong-api-call-details"]

            # isso aqui Recupera um cursor a partir do filtro
            """     for x in collection_calls.find({}, { "_id": 0, "id" : 1}):
                request_id = x["id"]
            #    request_id = "D8KkloEBGjj1AzoTb38x"
                print(request_id)
                getCallsById(request_id) """


            """ usando o pandas"""
            cursor_of_docs = list(collection_calls.find())
            documents = []

            for doc in cursor_of_docs:
                #document = pandas.DataFrame(columns=[])
                document = pandas.DataFrame([doc])
                doc_id = doc["_id"]
                serial_obj = pandas.Series(doc, name=doc_id)
                document = pandas.concat([document, serial_obj], axis=0)  # Concatenate the serial_obj to the document DataFrame
                document.dropna
                #documents.append(document.to_dict('records'))
                documents.append(document)
                
            return documents # list of pandas.DataFrame documents
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print(__class__, __name__, __file__)
            print("getApiCallsDetails() Ocorreu problema {} ".format(error.__class__))
            print("mensagem", str(error))            