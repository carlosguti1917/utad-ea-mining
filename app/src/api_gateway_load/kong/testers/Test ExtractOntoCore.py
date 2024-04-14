# Import the DataPrepare class
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service.ontology import ExtractOntoCore

from owlready2 import *


beginDate = "2024-03-07T09:36:56.042Z"

#extract_onto_core = ExtractOntoCore.ExtractOntoCore(beginDate)

#onto = ExtractOntoCore.ExtractOntoCore.onto
#exists = extract_onto_core.individual_exists(onto, "API_Call", "APICall1")
#print("ExtractOntoCore exists")

#test json


# Print the result
#print(data_prep)
print("ExtractOntoCore com sucesso")



#test json
# file_path = "C:/gitHub/utad/utad-ea-mining/app/src/api_gateway_load/repository/EA Mining OntoUML Teste V1_3.owl"
# onto = get_ontology(file_path).load()

# attribute_list = []
# ns_core = onto.get_namespace("http://eamining.edu.pt/core#")
# api_resource = ns_core.APIResource("teste")
# json_obj = """
# {
#     "numPedido": 1001,
#     "dataPedido": "2021-08-06T12:59:59.550-03:00",
#     "codigo": 12345,
#     "statusPedidos": "APROVADO",
#     "origem": "App IOS",
#     "cart" : {
#         "numPedido": 1001,
#         "dataPedido": "2021-08-06T12:59:59.550-03:00",
#         "codigo": 12345,
#         "statusPedidos": "APROVADO",
#         "origem": "App IOS",        
#         "cartid": 3456,
#         "cliente": 12345,
#         "itens": [
#             {
#                 "sku": 12,
#                 "produto": "Produto 1",
#                 "valor": 99.99
#             },
#             {
#                 "sku": 34,
#                 "produto": "Produto 2",
#                 "valor": 199.99
#             },
#             {
#                 "sku": 12,
#                 "produto": "Produto 1",
#                 "valor": 99.99
#             }
#         ]
#     }    
# }"""

# json_obj_res = """
# {
#     "numPedido": 1001,
#     "dataPedido": "2021-08-06T12:59:59.550-03:00",
#     "codigo": 12345,
#     "statusPedidos": "APROVADO",
#     "origem": "App IOS",
#     "cart" : {
#         "itens": [
#             {
#                 "sku": 12,
#                 "produto": "Produto 1",
#                 "valor": 99.99
#             }
#     }  
# }"""
# request_body_json = json.loads(json_obj)
# response_body_json = json.loads(json_obj)
# t1 = ExtractOntoCore.get_onto_resource_attributes_from_json(attribute_list, api_resource, request_body_json, '')
# t2 = ExtractOntoCore.get_onto_resource_attributes_from_json(t1, api_resource, response_body_json, '')
# print(t1)
# print(t2)
