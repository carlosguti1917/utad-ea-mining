from io import open

# Varre o mongodb para recuperar as calls e obtém no API Manager da Sensedia os detalhe calls e registra no MongoDB

import requests
import json
import pandas as pd
import pymongo
import config

myclient = pymongo.MongoClient(config.MONGO_DB_SERVER["host"])
mydb = myclient[config.MONGO_DB_SERVER["databasename"]]
collection_calls = mydb["api-calls"]
collection_call_detail = mydb["api-call-details"]

beginDate = "2022-06-27T00:00:00.015Z"

def insertCall(json_obj_call):

    #x = collection_call_detail.insert_one(json_obj_call)
    jsonobj = json.dumps(json_obj_call)
    dicJson = json.loads(jsonobj)
    x = collection_call_detail.insert_one(dicJson)
    print("****dicJson ****")
    print(dicJson)

    #call_list = []
    #for call_info in json_obj_call['calls']:
    # for call_info in json_obj_call:
    #     # incluindo o json na collection
    #     jsonobj = json.dumps(call_info)
    #     dicJson = json.loads(jsonobj)
    #     x = mycollection.insert_one(dicJson)

def getCallsById(calls_id):
    #calls_id = "D8KkloEBGjj1AzoTb38x"
    url_calls_id = 'https://manager-apiplatform.sensedia.com/api-manager/api/v3/calls/' + calls_id
    session_calls_id = requests.session()
    session_calls_id.headers.update()
    my_headers_calls_id = {
        'Content-Type': 'application/json',
        'Sensedia-Auth': '306ae5fd-c4dc-3592-b12c-2b3f9a6e0e22'
    }
    req_calss_id = requests.get(url_calls_id, headers=my_headers_calls_id)
    resp_body_calls_id = req_calss_id.json()
    print("response_body", resp_body_calls_id)
    insertCall(resp_body_calls_id)

for x in collection_calls.find({}, { "_id": 0, "id" : 1}):
    request_id = x["id"]
#    request_id = "D8KkloEBGjj1AzoTb38x"
    print(request_id)
    getCallsById(request_id)


