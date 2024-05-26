import json
from owlready2 import *
from datetime import datetime
#from owlready2 import Reasoner
import sys
import os
import os.path
import pymongo
from rdflib import XSD
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..")))
from app.src import configs
from app.src.utils import onto_util

#onto = get_ontology("app/src/api_gateway_load/repository/Onto EA Mining v0.1-RDFXML.owl").load()
onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
#onto = get_ontology("Onto EA Mining v0.1-RDFXML.owl").load()
#onto = get_ontology("EA Mining OntoUML Teste V1_3.rdf").load()
onto = get_ontology(configs.OWL_FILE["file_name"]).load()
ns_core = onto.get_namespace("http://eamining.edu.pt/core#")

# Connect to MongoDB
myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
mydb = myclient[configs.MONGO_DB_SERVER["databasename"]]
collection_call_cleaned = mydb["kong-api-call-cleaned"]

           
# iterar no MongoDB
#Registrar classes na ontologia.  

#print("classes = ",list(onto.classes()))

class ExtractOntoCore:
    
    def __init__(self, begindate):
        # self.myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
        # self.mydb = self.myclient[configs.MONGO_DB_SERVER["databasename"]]
        # self.collection_call_cleaned = self.mydb["kong-api-call-cleaned"]
        api_calls = list(collection_call_cleaned.find({"_source.@timestamp": {"$gt": begindate}}))
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
                
                if not onto_util.validate_json_to_extraction(call):
                    continue
                
                cls_api_call = ns_core.APICall
                
                #verifica se existe consumer e request_id e se API Call já está registrada na ontologia
                if "_source" in call and "consumer" in call["_source"] and "id" in call["_source"]["consumer"]:
                    Consumer_app_id = call["_source"]["consumer"]["id"] 
                if "_source" in call and "consumer" in call["_source"] and "username" in call["_source"]["consumer"]:
                    Consumer_app_name = call["_source"]["consumer"]["username"]           
                if "@timestamp" in call["_source"] and "request" in call["_source"] and "id" in call["_source"]["request"]:  # o nome da classe e label da API Call é o request_id  
                    request_id = call["_source"]["request"]["id"]  
                          
                if request_id is None and Consumer_app_id is None and Consumer_app_name is None:
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
                    
                    #API Call.request_time
                    # create the individuo for ontology classe API Call, and set its properties started=at as request_time and @timestamp as response_time
                    #API Call.request_time
                    cls_api_call = ns_core.APICall
                    # TODO tem que verificar se a chamada já não existe
                    # onto_api_call = get_individual(cls, Consumer_app_name)
                    if "@timestamp" in call["_source"]:
                        # o nome da classe e label da API Call é o request_id
                        api_call = cls_api_call(request_id)
                        api_call.label.append(request_id)
                        #api_call.request_time.append(call["_source"]["@timestamp"])
                        parsed_datetime = datetime.fromisoformat(call["_source"]["@timestamp"])
                        #xsd_timestamp = datetime(parsed_datetime)
                        api_call.request_time.append(parsed_datetime)
                        # #TODO confirmar o response_time
                        if "response" in call["_source"] and "headers" in call["_source"]["response"] and "date" in call["_source"]["response"]["headers"]:
                            parsed_datetime = datetime.strptime(call["_source"]["response"]["headers"]["date"], '%a, %d %b %Y %H:%M:%S %Z')
                            xsd_timestamp = parsed_datetime.isoformat() + 'Z'                    
                        if "response" in call["_source"] and "status" in call["_source"]["response"]:
                            api_call.result_status.append(call["_source"]["response"]["status"])               
                        if "request" in call["_source"] and "uri" in call["_source"]["request"]:
                            api_call.api_uri.append(call["_source"]["request"]["uri"])
                        if "route" in call["_source"] and "name" in call["_source"]["route"]:
                            # TODO tem que fazer o split para pegar o nome
                            api_call.api_name.append(call["_source"]["route"]["name"])   
                            #  ConsumerApp participation  in Property participadIn with API Call
                            consumer_app.participatedIn.append(api_call)
                        #sync_reasoner()                                
                        #ApiOperation.method
                        if "request" in call["_source"] and "method" in call["_source"]["request"] and "request" in call["_source"] and "uri" in call["_source"]["request"]:
                            pattern = r"/(\d+)(?=/|$)"
                            route_aux = call["_source"]["request"]["uri"]
                            route = re.sub(pattern, '/x', route_aux)                             
                            operation_route = call["_source"]["request"]["method"] + "_" + route
                            api_operation = onto_util.get_individual(onto, ns_core.APIOperation, 'http://eamining.edu.pt/', operation_route)
                            if api_operation is None:
                                api_operation = ns_core.APIOperation(operation_route)
                                api_operation.label.append(operation_route)
                                api_operation.endpoint_route.append(operation_route) 
                                api_operation.method.append(call["_source"]["request"]["method"])               
                            api_call.participatedIn.append(api_operation)
                        #ServiceDestination.endpoint_route
                        if "service" in call["_source"] and "host" in call["_source"]["service"] and "path" in call["_source"]["service"]:
                            api_destination_route = call["_source"]["service"]["host"] + call["_source"]["service"]["path"]
                            api_destination = onto_util.get_individual(onto, ns_core.APIOperation, 'http://eamining.edu.pt/', api_destination_route)                        
                            if api_destination is None:
                                api_destination = ns_core.ServiceDestination(api_destination_route)
                                api_destination.label.append(api_destination_route)
                                api_destination.endpoint_route.append(api_destination_route)
                                #api_destination.participatedIn.append(api_call)
                            api_destination.participatedIn.append(api_call)
                        #API Resource Resouce.uri Resource.data
                        #inicializing the attributes_list
                        attributes_list = []
                        # Request Data
                        if "request" in call["_source"] and "uri" in call["_source"]["request"]:
                            resource_uri = call["_source"]["request"]["uri"]
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
                            if "request" in call["_source"] and "body" in call["_source"]["request"]:
                                request_body = call["_source"]["request"]["body"]
                                if request_body.strip() != "":
                                    request_body_json = json.loads(request_body)
                                    get_onto_resource_attributes_from_json(attributes_list, api_resource, request_body_json, "")
                            #Wheather the request body is empty the attibute may is in the path
                            elif '/' in resource_name:
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
                        #api_resource.data.append(call["_source"]["request"]["body"])     
                        if "response" in call["_source"] and "body" in call["_source"]["response"]:
                            #Não dá para verificar se o recurso existe pois precisa guardar os dados                                           
                            # Transform the body into a datatype Attribute (array of name-value pairs)
                            response_body = call["_source"]["response"]["body"]
                            if response_body.strip() != "":
                                response_body_json = json.loads(response_body)
                                get_onto_resource_attributes_from_json(attributes_list, api_resource, response_body_json, "") 
                        
                        # Api Operation Modifies API Resource
                        if api_operation and api_resource:
                            relator_operation_executed = ns_core.OperationExecuted()
                            relator_operation_executed.mediates.append(api_operation)
                            relator_operation_executed.mediates.append(api_resource)                       
                            #api_operation.modifies.append(api_resource)
                            # Não consegui atribuir o a associação materail modifies
                        
            try:
                #save the individuals                  
                #check de ontology consistency before saving                        
                sync_reasoner()
                onto.save(format="rdfxml")
                #pass
                #TODO Ao final tem que criar um API Documentation e criar a relação material is documented by
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


    
     
                 
   
#print("ExtractOntoCore Chegou ao final com sucesso")