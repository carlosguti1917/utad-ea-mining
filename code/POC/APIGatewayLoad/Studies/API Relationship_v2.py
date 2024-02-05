from distutils.command.config import config
import json
from pprint import pprint

import jsons as jsons
import pymongo
import config


myclient = pymongo.MongoClient(config.MONGO_DB_SERVER["host"])
mydb = myclient["mydatabase"]
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
    print("*** dicJson inicio ***")
    print(dicJson)
    print("*** dicJson fim***")

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


def pretty_search(dict_or_list, key_to_search):
    """
    Give it a dict or a list of dicts and a dict key (to get values of),
    it will search through it and all containing dicts and arrays
    for all values of dict key you gave, and will return you set of them
    unless you wont specify search_for_first_only=True

    :param dict_or_list:
    :param key_to_search:
    :param search_for_first_only:
    :return:
    """

    print("pretty_search(dict_or_list, key_to_search) ->", key_to_search)
    search_result = set()
    if isinstance(dict_or_list, dict):
        for key in dict_or_list:
            key_value = dict_or_list[key]
            if key == key_to_search:
               search_result.add(key_value)
               print("key == key_to_search")
               print("{}: {}".format(key_to_search, dict_or_list[key]))
            if isinstance(key_value, dict) or isinstance(key_value, list) or isinstance(key_value, set):
                _search_result = pretty_search(key_value, key_to_search)
                if _search_result:
                     for result in _search_result:
                        search_result.add(result)
                        print("result in _search_result")
                        print("{}: {}".format(result, dict_or_list[key]))
    elif isinstance(dict_or_list, list) or isinstance(dict_or_list, set):
        for element in dict_or_list:
            if isinstance(element, list) or isinstance(element, set) or isinstance(element, dict):
                _search_result = pretty_search(element, key_to_search)
                if _search_result:
                    for result in _search_result:
                        search_result.add(result)
                        print("if isinstance(element, list) or isinstance(element, set) or isinstance(element, dict):")
                        print("{}: {}".format(result, dict_or_list[element]))

    print("** pretty_search search_result ->", search_result)
    return search_result

print("*** teste x5***")
#key_to_search = "cartid"
key_to_search = "body"
cont = 0
#seach_json_recursively(dicJson, key_to_search)
for x5 in dicJson:
    x6 = pretty_search(x5, key_to_search)
    print("*** x6.set -> ", x6, " * x5.set.size ->", len(x6))
    cont = cont + 1
"""
def function(json_object, name):
    for dict in json_object:
        if dict['name'] == name:
            return dict['price']
            """

# Associar AppID, clientid, AppName
# cart.cartid = order.cartid
# cart.cliente.codigo = order.cliente

# Pegar o body do trace e tentar pintar os valores.

