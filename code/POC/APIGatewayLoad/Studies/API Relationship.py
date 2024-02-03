import json
from pprint import pprint

import jsons as jsons
import pymongo

import config

myclient = pymongo.MongoClient(config.MONGO_DB_SERVER["host"])
mydb = myclient[config.MONGO_DB_SERVER["databasename"]]
collection_calls = mydb["api-calls"]

stage_lookup_calls = {
    '$lookup': {
        'from': 'api-call-detals',
        'localField': 'id',
        'foreignField': 'id',
        'as': 'teste',
    }
}

stage_limit_1 = { "$limit": 30 }

pipeline = [
    stage_lookup_calls,
    stage_limit_1,
]

results = collection_calls.aggregate(pipeline)

for x in results:
    #pprint(x)
    """pprint(" ** {apiId}, {trace}".format(
            apiId=x['apiId'],
            trace=x['trace'],
            #body=x['body'],
            )
        )
    """
    obj1 = x['trace']
    #print('*** obj1', obj1)
    dicJson = json.loads(obj1)
    #pprint(obj1[0])

def find(key, dictionary):
    print("** key", key, )
    data = {}
    for k, v in dictionary.iteritems():
        if k == key:
            print("** v", v )
            #yield v
            data[k] = find(v)
        elif isinstance(v, dict):
            for result in find(key, v):
                print("** v dict", v)
                #yield result
                data[result] = find(v)
        elif isinstance(v, list):
            for d in v:
                if isinstance(d, dict):
                    for result in find(key, d):
                        print("** d", d, " key ", key)
                        #yield result
                        data[result] = find(d)

def seach_json_recursively(json_object, target_key):
    search_result = set()
    if type(json_object) is dict and json_object:
        for key in json_object:
            if key == target_key:
                print("{}: {}".format(target_key, json_object[key]))
                search_result.add(json_object[key])
            seach_json_recursively(json_object[key], target_key)
    elif type(json_object) is list and json_object:
        for item in json_object:
            seach_json_recursively(item, target_key)
    return search_result



print("*** teste x1***")
for x1 in dicJson:
    #if "data" in x1:
        #print(x1.get('data'))
    target_key = "body"
    #find(target_key, x1)
    seach_json_recursively(dicJson, target_key)
    #print x1.get('data')
    #if x1['data']:
        #pprint(x1'data'])

print("*** fim teste x1***")


# Associar AppID, clientid, AppName
# cart.cartid = order.cartid
# cart.cliente.codigo = order.cliente

# Pegar o body do trace e tentar pintar os valores.

