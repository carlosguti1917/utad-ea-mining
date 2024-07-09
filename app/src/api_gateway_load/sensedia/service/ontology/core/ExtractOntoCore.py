import json
from owlready2 import *
from datetime import datetime
import pandas as pd
import pandas
#from owlready2 import Reasoner
import sys
import os
import os.path
import pymongo
from rdflib import XSD
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..")))
from app.src import configs
from app.src.utils import onto_util

#onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
onto_path.append(configs.OWL_FILE["file_path"])  # Set the path to load the ontology
onto = get_ontology(configs.OWL_FILE["file_name"]).load()
ns_core = onto.get_namespace("http://eamining.edu.pt/core#")

# Connect to MongoDB
myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
mydb = myclient[configs.MONGO_DB_SERVER["databasename"]]
collection_call_cleaned = mydb["sensedia-api-call-cleaned"]
          
# iterar no MongoDB  and Registrar classes na ontologia.  

class ExtractOntoCore:
    
    def __init__(self, beginDate, endDate):
        query = {"_source.date_received": {'$gt': beginDate, '$lt': endDate}}
        api_calls = list(collection_call_cleaned.find(query))      
        tranform_to_ontology(api_calls)

def get_onto_resource_attributes_from_json(attributes_list, api_resource, json_obj, key_hierarchy):
    if attributes_list is None:
        attributes_list = []
    attribute_name = None
    attribute_value = None

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if isinstance(value, dict):
                if key_hierarchy == "":
                    key_hierarchy = key_hierarchy + key
                else:
                    key_hierarchy = key_hierarchy + "." + key                    
                get_onto_resource_attributes_from_json(attributes_list, api_resource, value, key_hierarchy)
            elif isinstance(value, list):
                if key_hierarchy == "":
                    key_hierarchy = key_hierarchy + key
                else:
                    key_hierarchy = key_hierarchy + "." + key
                for item in value:
                    get_onto_resource_attributes_from_json(attributes_list, api_resource, item, key_hierarchy)
            elif value:
                # initializing the attribute_name and label
                if key_hierarchy == "":
                    attribute_name = key
                else:
                    attribute_name = key_hierarchy + "." + key
                attribute_value = str(value)
                ## As the value may repeat in the request and respose of the same API Call, it is necessary to check if the attribute already exists                
                attribute_exists = False
                for i in attributes_list:
                    if i.attribute_name[0] == attribute_name and i.attribute_value[0] == attribute_value:
                        #print("Attribute already exists in attributes_list: ", attribute_name, " = ", attribute_value)
                        attribute_exists = True
                        break                       
                if not attribute_exists and api_resource.resource_data.__len__() > 0:
                    for resource_data in api_resource.resource_data:
                        if resource_data.attribute_name[0] == attribute_name and resource_data.attribute_value[0] == attribute_value:
                            attribute_exists = True
                            #print("Attribute already exists in api_resource.resource_data: ", resource_data.attribute_name[0], " = ", resource_data.attribute_value[0])
                            break 
                # if the attribute value is null ignore it
                if attribute_value.strip() =="" or attribute_value == "null":
                    continue
                
                if not attribute_exists:                    
                    attr = ns_core.Attribute()
                    if key_hierarchy == "":
                        attr.attribute_name.append(attribute_name) 
                        attr.label.append(attribute_name)
                    else:
                        attr.attribute_name.append(attribute_name) 
                        attr.label.append(attribute_name)
                    attr.attribute_value.append(attribute_value)  
                                                              
                    api_resource.resource_data.append(attr)
                    attributes_list.append(attr)
                    #print("Attribute added: ", attr.attribute_name[0], " = ", attr.attribute_value[0])
                    
    elif isinstance(json_obj, list):
        for item in json_obj:
            if item:
                get_onto_resource_attributes_from_json(attributes_list, api_resource, json_obj)

    return attributes_list
                             
def setOntolgyIndividuals(self, onto, className, individuoName):
    try:
        onto[className] = individuoName
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print("In setOntolgyIndividuals module :", __name__)
        raise error
 


def tranform_to_ontology(api_calls):
    """tranform the api_calls to ontology
    Args:
        api_calls (list): list of json api calls to be transformed to ontology
    """
    
    #sync_reasoner()
    with onto:
        try:      
            for call in api_calls:
                Consumer_app_id = None
                Consumer_app_name = None
                request_id = None
                
                if not onto_util.validate_json_to_extraction(call, "sensedia"):
                    continue
                
                cls_api_call = ns_core.APICall
                
                #verifica se existe consumer e request_id e se API Call já está registrada na ontologia
                if "_source" in call and "sensedia.app.client_id" in call["_source"]: 
                    Consumer_app_id = call["_source"]["sensedia.app.client_id"]
                if "_source" in call and "sensedia.app.name" in call["_source"]:
                    Consumer_app_name = call["_source"]["sensedia.app.name"]          
                if "_source" in call and "sensedia.received_on_date" in call["_source"] and "sensedia.request_id" in call["_source"]:  # o nome da classe e label da API Call é o request_id  
                    request_id = call["_source"]["sensedia.request_id"]
                          
                if request_id is None or Consumer_app_id is None or Consumer_app_name is None:
                    continue
                if onto_util.get_individual(onto, cls_api_call, 'http://eamining.edu.pt/', request_id):
                    continue
                
                #Consumer App
                if Consumer_app_id is not None and Consumer_app_name is not None:
                    #cls = onto["http://eamining.edu.pt/core#ConsumerApp"]
                    cls_consumer_app = ns_core.ConsumerApp
                    consumer_app = onto_util.get_individual(onto, cls_consumer_app, 'http://eamining.edu.pt/', Consumer_app_name)
                    if consumer_app is None:
                        consumer_app = cls_consumer_app(Consumer_app_name)
                        consumer_app.label.append(Consumer_app_name)
                        consumer_app.client_id.append(Consumer_app_id)
                        consumer_app.app_name.append(Consumer_app_name)       
                    
                    # create the individuo for ontology classe API Call, and set its properties started=at as request_time and @timestamp as response_time
                    #API Call.request_time
                    cls_api_call = ns_core.APICall
                    # onto_api_call = get_individual(cls, Consumer_app_name)
                    if "sensedia.received_on_date" in call["_source"]:
                        # o nome da classe e label da API Call é o request_id
                        api_call = onto_util.get_individual(onto, ns_core.APICall, 'http://eamining.edu.pt/', request_id)
                        if api_call is None:
                            api_call = cls_api_call(request_id)
                            api_call.label.append(request_id)
                            parsed_datetime = datetime.fromisoformat(call["_source"]["sensedia.received_on_date"])
                            api_call.request_time.append(parsed_datetime)

                        # if "http.request_content_length" in call["_source"] 
                        #     parsed_datetime = datetime.strptime(call["_source"]["http.request_content_length"], '%a, %d %b %Y %H:%M:%S %Z')
                        #     xsd_timestamp = parsed_datetime.isoformat() + 'Z'                    
                        if "http.status_code" in call["_source"] :
                            result_status = int(call["_source"]["http.status_code"])
                            api_call.result_status.append(result_status)               
                        if "http.url" in call["_source"]:
                            api_call.api_uri.append(call["_source"]["http.url"])
                        if "sensedia.api.name" in call["_source"]:
                            # TODO tem que fazer o split para pegar o nome
                            api_call.api_name.append(call["_source"]["sensedia.api.name"])   
                            #  ConsumerApp participation  in Property participadIn with API Call
                            consumer_app.participatedIn.append(api_call)                           
                        #sync_reasoner()                        
                        #ApiOperation.method
                        if "http.method" in call["_source"]:
                            pattern = r"/(\d+)(?=/|$)"
                            url = call["_source"]["http.url"]
                            route_aux = url.removeprefix("https://api-demov3.sensedia.com")
                            route = re.sub(pattern, '/x', route_aux)                             
                            operation_route = call["_source"]["http.method"] + "_" + route
                            api_operation = onto_util.get_individual(onto, ns_core.APIOperation, 'http://eamining.edu.pt/', operation_route)
                            if api_operation is None:
                                api_operation = ns_core.APIOperation(operation_route)
                                api_operation.label.append(operation_route)
                                api_operation.endpoint_route.append(route) 
                                api_operation.method.append(call["_source"]["http.method"])               
                            api_call.participatedIn.append(api_operation)
                        
                        #ServiceDestination.endpoint_route
                        trace = call["_source"]["sensedia.trace"]
                        destination = get_api_destination_in_trace(trace)                        
                        if destination is not None:
                            api_destination_route = destination.removeprefix("https://")
                            api_destination = onto_util.get_individual(onto, ns_core.ServiceDestination, 'http://eamining.edu.pt/', api_destination_route)                        
                            if api_destination is None:
                                api_destination = ns_core.ServiceDestination(api_destination_route)
                                api_destination.label.append(api_destination_route)
                                api_destination.endpoint_route.append(api_destination_route)
                            api_destination.participatedIn.append(api_call)
                                
                            
                        #inicializing the attributes_list
                        #sync_reasoner()      
                        attributes_list = []
                        # Request Data
                        if route_aux is not None:
                            resource_uri = route_aux
                            #Não dá para verificar se o recurso existe pois precisa guardar os dados
                            api_resource = ns_core.APIResource()
                            api_resource.resource_uri.append(resource_uri)
                            api_resource.label.append(resource_uri)
                            api_resource.participatedIn.append(api_call)
                            #atribuir o resource_name 
                            #Define the updated pattern
                            pattern = r"/v\d+/(.*)"
                            match = re.search(pattern, resource_uri)
                            if match:
                                resource_name = match.group(1)
                                api_resource.resource_name.append(resource_name)
                            # Transform the body into a datatype Attribute (array of name-value pairs)
                            #if "request" in call["_source"] and "body" in call["_source"]["request"]:
                            print("API Operation Attribute add: ", api_operation.label[0])
                            if trace is not None and ("http.request_content_length" in call["_source"]):
                                request_len = int(call["_source"]["http.request_content_length"])
                                if request_len > 1:
                                    request_body = get_request_body_in_trace(trace)
                                    if request_body.strip() != "":
                                        request_body_json = json.loads(request_body)
                                        attributes_list = get_onto_resource_attributes_from_json(attributes_list, api_resource, request_body_json, "")
                                        # Following line is only for debug
                                        for attr in attributes_list:                                            
                                            print("Rquest Attribute added: ", attr.attribute_name[0], " = ", attr.attribute_value[0])
                            #Wheather the request body is empty the attibute may is in the path
                            if '/' in resource_name:
                                #TODO pegar os ids dos recursos, talvez verificar pelo resource name que tem no log do Sensedia
                                pairs = resource_name.split('/')
                                if len(pairs) % 2 == 0:
                                    for i in range(0, len(pairs), 2):
                                        att_name = pairs[i]
                                        att_value = pairs[i+1]
                                        attr = ns_core.Attribute()
                                        attr.attribute_name.append(att_name) 
                                        attr.label.append(att_name)
                                        attr.attribute_value.append(att_value)                                                                                 
                                        api_resource.resource_data.append(attr)
                            
                        #sync_reasoner()
                        # Response data
                        response_attributes_list = []
                        #TODO Verificar na lógica do Kong, pois estava com attributes_list herdado do request
                        if trace is not None and ("http.response_content_length" in call["_source"]):
                            response_len = int(call["_source"]["http.response_content_length"])
                            if response_len > 1:                        
                                response_body = get_response_body_in_trace(trace)
                                if response_body is not None:
                                    #Não dá para verificar se o recurso existe pois precisa guardar os dados                                           
                                    if response_body.strip() != "":
                                        response_body_json = json.loads(response_body)
                                        response_attributes_list = get_onto_resource_attributes_from_json(response_attributes_list, api_resource, response_body_json, "") 
                                        for resp_attr in response_attributes_list:
                                            print("Response Attribute added: ", resp_attr.attribute_name[0], " = ", resp_attr.attribute_value[0])
                        
                        # Api Operation Modifies API Resource
                        if api_operation and api_resource:
                            relator_operation_executed = ns_core.OperationExecuted()
                            relator_operation_executed.mediates.append(api_operation)
                            relator_operation_executed.mediates.append(api_resource)                       
                            #api_operation.modifies.append(api_resource)
                            # Não consegui atribuir o a associação materail modifies, acredito que seja só pelo relator mesmo    
                                                                                           
            try:
                #save the individuals                  
                #check de ontology consistency before saving                        
                sync_reasoner()
                onto.save(format="rdfxml")
            except Exception as error:
                inconsistent_cls_list = list(default_world.inconsistent_classes())
                for il in inconsistent_cls_list:
                    print(il)
                    print('inconsistency_list', il)                                                 
                print('Ocorreu problema {} '.format(error.__class__))
                print("mensagem", str(error))
                print("In tranform_to_ontology module :", __name__)  
                raise Exception(f"Ontology inconsistency found: {il}")  
        except Exception as error:
             print("call = ", call)
             print('Ocorreu problema {} '.format(error.__class__))
             print("mensagem", str(error))
             print("In tranform_to_ontology module :", __name__) 
             raise Exception(f"Error in tranforming Json to Ontology: {error}") 


def get_trace(trace):
    "get the trace of the API request in json format"
    try:
        # tranform string trace to json
        trace_json = json.loads(trace)
        return trace_json
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print("In setOntolgyIndividuals module :", __name__)
        raise error    
     

def get_api_destination_in_trace(trace_body) -> str:
    ''' get the service destination in the trace in Sensedia API Gateway    
        Args: string with the trace_body
    '''
    trace_log = None
    api_destination = None
    try:
        json_parsed = json.loads(trace_body)
        for trace_log in json_parsed:
            msg = str(trace_log["message"])
            if msg.startswith("Found matching route:"):
                s1 = msg.split(" => ")
                for i in s1:
                    if i.startswith("http"):
                        s2 = i.split(" ")
                        for j in s2:
                            if j.startswith("http"):
                                api_destination = j
                                break
                        if api_destination is not None:
                            break
                if api_destination is not None:
                    break                        
        return api_destination
    except json.JSONDecodeError as excinfo:
        print("Não foi possivel converter para json: ", {trace_log}, {excinfo})
        print("in module ", __name__)
        raise
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print("in module ", __name__)
        raise                 

def get_request_body_in_trace(trace_body) -> str:
    ''' get the service destination in the trace in Sensedia API Gateway    
        Args: string with the trace_body
    '''
    trace_log = None
    request_body = None
    try:
        json_parsed = json.loads(trace_body)
        for trace_log in json_parsed:
            msg = str(trace_log["message"])
            if msg.startswith("Request log"):
                request_body = trace_log["data"]["log"]["body"]
                break
        return request_body
    except json.JSONDecodeError as excinfo:
        print("Não foi possivel converter para json: ", {trace_log}, {excinfo})
        print("in module ", __name__)
        raise
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print("in module ", __name__)
        raise                 
    
def get_response_body_in_trace(trace_body) -> str:
    ''' get the service destination in the trace in Sensedia API Gateway    
        Args: string with the trace_body
    '''
    trace_log = None
    response_body = None
    try:
        json_parsed = json.loads(trace_body)
        for trace_log in json_parsed:
            msg = str(trace_log["message"])
            if msg.startswith("Response log"):
                response_body = trace_log["data"]["log"]["body"]
                break
        return response_body
    except json.JSONDecodeError as excinfo:
        print("Não foi possivel converter para json: ", {trace_log}, {excinfo})
        print("in module ", __name__)
        raise
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print("in module ", __name__)
        raise              
   
#print("ExtractOntoCore Chegou ao final com sucesso")