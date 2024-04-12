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
from api_gateway_load import configs

#onto = get_ontology("app/src/api_gateway_load/repository/Onto EA Mining v0.1-RDFXML.owl").load()
onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
#onto = get_ontology("Onto EA Mining v0.1-RDFXML.owl").load()
onto = get_ontology("EA Mining OntoUML Teste V1_3.rdf").load()
#ns_core = onto.get_namespace("http://apieamining.edu.pt/core#")
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

def get_onto_resource_attributes_from_json(api_resource, json_obj, key_hierarchy):
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if isinstance(value, dict):
                    if key_hierarchy == "":
                        key_hierarchy = key_hierarchy + key
                    else:
                        key_hierarchy = key_hierarchy + "." + key                    
                    get_onto_resource_attributes_from_json(api_resource, value, key_hierarchy)
                elif isinstance(value, list):
                    if key_hierarchy == "":
                        key_hierarchy = key_hierarchy + key
                    else:
                        key_hierarchy = key_hierarchy + "." + key
                    for item in value:
                        get_onto_resource_attributes_from_json(api_resource, item, key_hierarchy)
                elif value:
                    attr = ns_core.Attribute()
                    if key_hierarchy == "":
                        attr.attribute_name.append(key) 
                        attr.label.append(key)
                    else:
                        attr.attribute_name.append(key_hierarchy + "." + key) 
                        attr.label.append(key_hierarchy + "." + key)
                    attr.attribute_value.append(str(value))
                    ## As the value may repeat in the request and respose of the same API Call, it is necessary to check if the attribute already exists
                    attribute_exists = False
                    if api_resource.resource_data.__len__() > 0:
                        for resource_data in api_resource.resource_data:
                            if resource_data.attribute_name[0] == attr.attribute_name[0] and resource_data.attribute_value[0] == attr.attribute_value[0]:
                                attribute_exists = True
                                print("Attribute already exists: ", attr.attribute_name[0], " = ", attr.attribute_value[0])
                                break
                    if not attribute_exists:
                        api_resource.resource_data.append(attr)
                        print("Attribute added: ", attr.attribute_name[0], " = ", attr.attribute_value[0])
                        
        elif isinstance(json_obj, list):
            for item in json_obj:
                if item:
                    get_onto_resource_attributes_from_json(api_resource, json_obj) 

def get_individual(onto_class, individual_name):
    """
    Retrieves individuals from the ontology based on the provided class name and individual name.

    Args:
        onto: The ontology to query.
        class_name: The name of the class to query for.
        individual_name: The name of the individual to query for.

    Returns:
        list: A list of individuals that match the query.
    """
    try:
        #with onto:
        #individuals = onto.search(type=onto_class, iri="*"+ individual_name) #funciona mas pega mais por causa do *
        individuals = onto.search(type=onto_class, iri="http://eamining.edu.pt#"+individual_name+"")     
        # Check if the individual exists
        if individuals and len(individuals) == 1:
            return individuals[0] 
            # Access individual properties or perform further operations
        elif individuals and len(individuals) > 1:
            raise Exception(f"More than one individual '{individual_name}' of class '{onto_class}' was found.")          
        return None    
    except Exception as error:
        print('An error occurred: {} '.format(error.__class__))
        print("Message:", str(error))
        print("In get_individuals module :", __name__)
        raise error
                              
def setOntolgyIndividuals(self, onto, className, individuoName):
    try:
        onto[className] = individuoName
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print("In setOntolgyIndividuals module :", __name__)
        raise error
 


def tranform_to_ontology(api_calls):
    sync_reasoner()

    with onto:
        try:      
            for call in api_calls:
                Consumer_app_id = None
                Consumer_app_name = None
                request_id = None
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
                if get_individual(cls_api_call, request_id):
                    continue
                
                #Consumer App
                if Consumer_app_id is not None and Consumer_app_name is not None:
                    #cls = onto["http://eamining.edu.pt/core#ConsumerApp"]
                    cls_consumer_app = ns_core.ConsumerApp
                    consumer_app = get_individual(cls_consumer_app, Consumer_app_name)
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
                            #api_call.response_time.append(xsd_timestamp)                      
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
                        if "request" in call["_source"] and "method" in call["_source"]["request"] and "request" in call["_source"] and "url" in call["_source"]["request"]:
                            operation_route = call["_source"]["request"]["method"] + "_" + call["_source"]["request"]["url"]
                            api_operation = get_individual(ns_core.APIOperation, operation_route)
                            if api_operation is None:
                                api_operation = ns_core.APIOperation(operation_route)
                                api_operation.label.append(operation_route)
                                api_operation.endpoint_route.append(operation_route) 
                                api_operation.method.append(call["_source"]["request"]["method"])               
                                api_call.participatedIn.append(api_operation)
                        #ServiceDestination.endpoint_route
                        if "service" in call["_source"] and "host" in call["_source"]["service"] and "path" in call["_source"]["service"]:
                            api_destination_route = call["_source"]["service"]["host"] + call["_source"]["service"]["path"]
                            api_destination = get_individual(ns_core.APIOperation, api_destination_route)                        
                            if api_destination is None:
                                api_destination = ns_core.ServiceDestination(api_destination_route)
                                api_destination.label.append(api_destination_route)
                                api_destination.endpoint_route.append(api_destination_route)
                                api_destination.participatedIn.append(api_call)
                        #sync_reasoner()    
                        #API Resource Resouce.uri Resource.data
                        # Request Data
                        if "request" in call["_source"] and "uri" in call["_source"]["request"]:
                            resource_uri = call["_source"]["request"]["uri"]
                            #Não dá para verificar se o recurso existe pois precisa guardar os dados
                            api_resource = ns_core.APIResource(resource_uri)
                            api_resource.resource_uri.append(resource_uri)
                            api_resource.label.append(resource_uri)
                            #atribuir o resource_name 
                            #Define the updated pattern
                            pattern = r"/v\d+/(.*?)/(\d+)"
                            match = re.search(pattern, resource_uri)
                            if match:
                                resource_name = match.group(1)
                                api_resource.resource_name.append(resource_name)                                              
                            # Transform the body into a datatype Attribute (array of name-value pairs)
                            if "request" in call["_source"] and "body" in call["_source"]["request"]:
                                request_body = call["_source"]["request"]["body"]
                                request_body_json = json.loads(request_body)
                                get_onto_resource_attributes_from_json(api_resource, request_body_json, "")
                        #sync_reasoner()
                        # Response data
                        #api_resource.data.append(call["_source"]["request"]["body"])     
                        if "response" in call["_source"] and "body" in call["_source"]["response"]:
                            #Não dá para verificar se o recurso existe pois precisa guardar os dados                                           
                            # Transform the body into a datatype Attribute (array of name-value pairs)
                            response_body = call["_source"]["response"]["body"]
                            response_body_json = json.loads(response_body)
                            get_onto_resource_attributes_from_json(api_resource, response_body_json, "") 
                        
                        # Api Operation Modifies API Resource
                        if api_operation and api_resource:
                            relator_operation_executed = ns_core.OperationExecuted()
                            relator_operation_executed.mediates.append(api_operation)
                            relator_operation_executed.mediates.append(api_resource)                       
                            #api_operation.modifies.append(api_resource)
                            # Não consegui atribuir o a associação
                        
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
                            print("In extractAPIConcepts module :", __name__)  
                            raise Exception(f"Ontology inconsistency found: {il}")  
                        
        except Exception as error:
             print('Ocorreu problema {} '.format(error.__class__))
             print("mensagem", str(error))
             print("In extractAPIConcepts module :", __name__)                           


    
     
                 
   
#print("ExtractOntoCore Chegou ao final com sucesso")