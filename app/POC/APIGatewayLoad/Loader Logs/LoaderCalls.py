from ast import Load
import requests
import json
import pandas as pd
import pymongo
from io import open
import sys
import os.path
from app.src.api_gateway_load import configs
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

print("sys.path",   sys.path)







class LoaderCalls:

    def __init__(self, begindate):
        call_list = []
        call_list = self.getCalls(begindate)
        print("qtde de calls", len(call_list))
        for call_info in call_list['calls']:
            jsonobj = json.dumps(call_info)
            dicJsonResponse = json.loads(jsonobj)
            call_detail = self.getCallDetails(dicJsonResponse["id"])
            self.saveCallDetails(call_detail)

    @staticmethod
    def getCalls(begindate):
        url = 'https://manager-apiplatform.sensedia.com/api-manager/api/v3/calls?baseUris=https://apiplatform.sensedia.com/sandbox/commerce/v1&apiId=1578&beginDate=' + beginDate
        sesssion = requests.session()
        sesssion.headers.update()
        my_headers = {
            'Content-Type': 'application/json',
            'Sensedia-Auth': '306ae5fd-c4dc-3592-b12c-2b3f9a6e0e22'
        }
        req = requests.get(url, headers=my_headers)
        resp_body = req.json()
        #call_list = []
        print("qtde de calls", len(resp_body))
        jsonobj = json.dumps(resp_body)
        dicJsonResponse = json.loads(jsonobj)
        return dicJsonResponse

    @staticmethod
    def getCallDetails(request_id):
        print(request_id)
        url_calls_id = 'https://manager-apiplatform.sensedia.com/api-manager/api/v3/calls/' + request_id
        session_calls_id = requests.session()
        session_calls_id.headers.update()
        my_headers_calls_id = {
            'Content-Type': 'application/json',
            'Sensedia-Auth': '306ae5fd-c4dc-3592-b12c-2b3f9a6e0e22'
        }
        req_calss_id = requests.get(url_calls_id, headers=my_headers_calls_id)
        resp_body_call = req_calss_id.json()
        print("response_body", resp_body_call)
        return resp_body_call

    @staticmethod
    def saveCallDetails(dicJson):
        myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
        mydb = myclient[configs.MONGO_DB_SERVER["databasename"]]
        collection_calls = mydb["api-calls"]
        collection_call_detail = mydb["api-call-details"]
        x = collection_call_detail.insert_one(dicJson)
        print("****dicJson ****", dicJson)


# Executa rotina de loader
beginDate = "2022-06-27T00:00:00.015Z"
x = LoaderCalls(beginDate)
# TODO evitar gravar novo registro, para isso verificar se o id do request já não está gravado
