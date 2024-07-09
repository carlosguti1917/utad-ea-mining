from ast import Load
import requests
import json
import pandas as pd
import pymongo
from io import open
import sys
import os.path
from app.src import configs
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
print("sys.path",   sys.path)

class LoaderCalls:
    
    def __init__(self, beginDate, endDate):
        call_list = []
        call_list = self.getCalls(beginDate, endDate)
        print("qtde de calls", len(call_list['hits']['total']))
        for call_detail in call_list['hits']['hits']:
            self.saveCallDetails(call_detail)


    @staticmethod
    def getCalls(beginDate, endDate):
        url = f"{configs.SENSEDIA['domain_url']}/analytics/v1/products/api-gateway/calls/query"        
        sesssion = requests.session()
        sesssion.headers.update()
        my_headers = {
            'Content-Type': 'application/json',
            'Sensedia-Auth': f'{configs.SENSEDIA["sensedia_auth"]}'
        }
        qfilter = get_query_sensedia_analytics(beginDate, endDate)       
        print("qfilter : ", qfilter)
        resp = requests.post(url, headers=my_headers, data=qfilter)
        resp_body = resp.json()
        jsonobj = json.dumps(resp_body)
        dicJsonResponse = json.loads(jsonobj)
        return dicJsonResponse

    @staticmethod
    def saveCallDetails(dicJson):
        myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
        mydb = myclient[configs.MONGO_DB_SERVER["databasename"]]
        #collection_calls = mydb["api-calls"]
        collection_call_detail = mydb["sensedia-api-call-details"]
        x = collection_call_detail.insert_one(dicJson)
        print("****dicJson ****", dicJson)


def get_query_sensedia_analytics(beginDate, endDate):
    query = f'''
        {{
            "version": true,
            "size": 5000,
            "stored_fields": [
                "*"
            ],
            "script_fields": {{}},
            "docvalue_fields": [
                {{
                "field": "date_received",
                "format": "date_time"
                }},
                {{
                "field": "sensedia.received_on",
                "format": "date_time"
                }}
            ],
            "_source": {{
                "excludes": []
            }},
            "query": {{
                "bool": {{
                "must": [],
                "filter": [
                    {{
                    "match_all": {{}}
                    }},
                    {{
                    "match_phrase": {{
                        "sensedia.app.client_id": "bf214d8a191e75c2d58ec038e61b4dd2"
                    }}
                    }},
                    {{
                    "range": {{
                        "sensedia.received_on": {{
                        "gte": "{beginDate}",
                        "lte": "{endDate}",
                        "format": "strict_date_optional_time"
                        }}
                    }}
                    }}
                ],
                "should": [],
                "must_not": [
                    {{
                    "range": {{
                        "http.status_code": {{
                        "gte": 300,
                        "lt": 599
                        }}
                    }}
                    }}        
                ]
                }}
            }}
        }}    
    '''
       
    return query

