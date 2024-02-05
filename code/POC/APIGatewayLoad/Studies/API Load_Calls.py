from io import open

import requests
import json
import pandas as pd

import pymongo

import config

# Obtem no mongodb o timestamp da ultima chamda
# Obtém no API Manager da Sensedia as calls e registra no MongoDB

beginDate = "2022-06-27T00:00:00.015Z"

url='https://manager-apiplatform.sensedia.com/api-manager/api/v3/calls?baseUris=https://apiplatform.sensedia.com/sandbox/commerce/v1&apiId=1578&beginDate='+beginDate

sesssion = requests.session()
sesssion.headers.update()

my_headers = {'Content-Type' : 'application/json', 'Sensedia-Auth' : '306ae5fd-c4dc-3592-b12c-2b3f9a6e0e22' }

req=requests.get(url, headers=my_headers)

resp_body2=req.json()
print("response_body", resp_body2)


resp_body2['calls']

#call_dic = json.dumps(resp_body2)
#print("call_dic: ", call_dic)

myclient = pymongo.MongoClient(config.MONGO_DB_SERVER["host"])
mydb = myclient[config.MONGO_DB_SERVER["databasename"]]
mycollection = mydb["api-calls"]

call_list = []
print("qtde de calls", len(resp_body2))
for call_info in resp_body2['calls']:
    # incluindo o json na collection
    jsonobj = json.dumps(call_info)
    dicJson = json.loads(jsonobj)
    x = mycollection.insert_one(dicJson)




