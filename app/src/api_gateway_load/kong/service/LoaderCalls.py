from ast import Load
import requests
import json
#import pandas as pd
#import pymongo
from io import open
import sys
import os.path
import os
#from repository import MongoDbRepository4Kong
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..')))
# Now you can import the config module and use it
from app.src import configs
from api_gateway_load.kong.repository.MongoDbRepository4Kong import MongoDbRepository4Kong

class LoaderCalls:
    #TODO talvez um nome melhor seria API Scrapping e pssar para uma pasta scrapping
    
    def __init__(self, begindate, endDate):
        call_list = []
        call_list = self.getCalls(begindate, endDate)
        #print("qtde de calls", len(call_list['hits']['hits']))
        for call_info in call_list['hits']['hits']:
            jsonobj = json.dumps(call_info)
            dicJsonResponse = json.loads(jsonobj)
            #call_detail = self.getCallDetails(dicJsonResponse["id"])
            #self.saveCallDetails(call_detail)
            self.saveCallDetails(call_info)

    @staticmethod
    def getCalls(begindate, enddate):
        #url = 'https://manager-apiplatform.sensedia.com/api-manager/api/v3/calls?baseUris=https://apiplatform.sensedia.com/sandbox/commerce/v1&apiId=1578&beginDate=' + beginDate
        url = configs.ELASTIC['kong_log']
        sesssion = requests.session()
        sesssion.headers.update()
        my_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ZWxhc3RpYzphYmMxMjM='
        }
        req_body = LoaderCalls.getElasticRequestBody(begindate, enddate)
        req = requests.get(url, headers=my_headers, data=req_body, verify=False)
        resp_body = req.json()
        jsonobj = json.dumps(resp_body)
        dicJsonResponse = json.loads(jsonobj)
        return dicJsonResponse

    # @staticmethod
    # def getCallDetails(request_id):
    #     print(request_id)
    #     url_calls_id = 'https://manager-apiplatform.sensedia.com/api-manager/api/v3/calls/' + request_id
    #     session_calls_id = requests.session()
    #     session_calls_id.headers.update()
    #     my_headers_calls_id = {
    #         'Content-Type': 'application/json',
    #         'Sensedia-Auth': '306ae5fd-c4dc-3592-b12c-2b3f9a6e0e22'
    #     }
    #     req_calss_id = requests.get(url_calls_id, headers=my_headers_calls_id)
    #     resp_body_call = req_calss_id.json()
    #     print("response_body", resp_body_call)
    #     return resp_body_call

    @staticmethod
    def saveCallDetails(dicJson):
        try:
            MongoDbRepository4Kong.saveCallDetails(dicJson)
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In save_correlation_matched_values module :", __name__)        


    @staticmethod
    def getElasticRequestBody(begindate, enddate) -> str: 
        retorno = {
                    "query": {
                        "bool": {
                        "must": [
                            {
                            "match_all": {}
                            },
                            {
                            "range": {
                                "@timestamp": {
                                "gte": begindate,
                                "lte": enddate,
                                }
                            }
                            }
                        ]
                        }
                    },
                    "size": 10000,
                    #"from": 0,
                    "_source": [
                        "*"
                    ]
                }
        return json.dumps(retorno)

# Executa rotina de loader
#beginDate = "2024-02-14T09:00:56.042Z"
#x = LoaderCalls(beginDate)
# TODO evitar gravar novo registro, para isso verificar se o id do request já não está gravado
