from io import open
from pprint import pprint

import requests
import json
import pandas as pd
import pymongo

import config

# Somente teste, não grava

url='https://manager-apiplatform.sensedia.com/api-manager/api/v3/calls'

sesssion = requests.session()
sesssion.headers.update()

my_headers = {'Content-Type' : 'application/json',
                'Sensedia-Auth' : '306ae5fd-c4dc-3592-b12c-2b3f9a6e0e22',
                'baseUris' : 'https://apiplatform.sensedia.com/sandbox/commerce/v1',
                'apiId' : '1578'
              }

req=requests.get(url, headers=my_headers)

#print("result of test",  req)

#rjson=req.json()
#print(rjson)

# response = req.text
# response_body = json.loads(response)
# type(response_body)
# dict
# Acho que esta linha resume as 3 acima
resp_body2=req.json()
print("response_body", resp_body2)


resp_body2['calls']

call_dic= json.dumps(resp_body2)
print("call_dic: ", call_dic)

call_list = []
call_dic2 = {}
for call_info in resp_body2['calls']:
    call_list.append([call_info['apiName'],
        call_info['apiId'],
        call_info['baseUrl'],
        call_info['appName'],
        call_info['callDate'],
        call_info['clientId'],
        call_info['callerAddress'],
        call_info['operationName'],
        call_info['resourceName'],
        call_info['transactionID'],
        #call_info['customerid'] - Parece não estar disponível pela API
        #call_info['requestPayload'],
        #call_info['responsePayload']
        call_info['trace']
    ])


print("calls_info:", call_info)

#usando Pandas DataFrame

"""
calls_df = pd.DataFrame(data=call_list, columns=['apiName', 'apiId', 'appName', 'baseUrl', 'callDate', 'clientId', 'callerAddress',
                                                  'operationName', 'resourceName', 'transactionID', 'trace'])

pring("pandas: calss_df")
print(calls_df.head(25))
"""


#myclient = pymongo.MongoClient("mongodb://localhost:27017")
#myclient = pymongo.MongoClient("mongodb://192.168.0.109:27017")
myclient = pymongo.MongoClient(config.MONGO_DB_SERVER["host"])
mydb = myclient["mydatabase"]
mycollection = mydb["api-calls"]

# incluindo o json na collection
#x = mycollection.insert_many(call_list)
pprint(myclient.list_database_names())

