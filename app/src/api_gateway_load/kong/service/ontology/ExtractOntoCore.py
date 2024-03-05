import json
from owlready2 import *
#from owlready2 import Reasoner
import sys
import os
import os.path
import pymongo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..")))
from api_gateway_load import configs

#onto = get_ontology("app/src/api_gateway_load/repository/Onto EA Mining v0.1-RDFXML.owl").load()
onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
#onto = get_ontology("Onto EA Mining v0.1-RDFXML.owl").load()
onto = get_ontology("EA Mining OntoUML Teste V1_1.owl").load()
#ns_core = onto.get_namespace("http://apieamining.edu.pt/core#")
ns_core = onto.get_namespace("http://eamining.edu.pt/core#")

#print("classes = ",list(onto.classes()))

def get_onto_attributes_from_json(api_resource, json_obj, key_hierarchy):
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if isinstance(value, dict):
                    if key_hierarchy == "":
                        key_hierarchy = key_hierarchy + key
                    else:
                        key_hierarchy = key_hierarchy + "." + key                    
                    get_onto_attributes_from_json(api_resource, value, key_hierarchy)
                elif isinstance(value, list):
                    if key_hierarchy == "":
                        key_hierarchy = key_hierarchy + key
                    else:
                        key_hierarchy = key_hierarchy + "." + key
                    for item in value:
                        get_onto_attributes_from_json(api_resource, item, key_hierarchy)
                elif value:
                    attr = ns_core.Attribute()
                    if key_hierarchy == "":
                        #attr.name.append(key) #key= [key]
                        attr.name = key #key= (key) #key= [key]
                    else:
                        attr.name = key_hierarchy + "." + key
                    attr.value.append(value) 
                    api_resource.data.append(attr)  
                #api_resource.hasValueComponent.append(attr)
                #owl2ready.setProperty(api_resource, "http://purl.org/nemo/gufo#hasValueComponent", attr)                   
        elif isinstance(json_obj, list):
            for item in json_obj:
                if item:
                    get_onto_attributes_from_json(api_resource, json_obj) 

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
        individuals = onto.search(type=onto_class, iri="*"+ individual_name)
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

# with onto:
                
#     # Consumer App
#     class ConsumerApp(Thing):
#         pass

#     class client_id(DataProperty):
#         pass
    
#     class app_name(DataProperty):
#         pass

# Connect to MongoDB
myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
mydb = myclient[configs.MONGO_DB_SERVER["databasename"]]
collection_call_cleaned = mydb["kong-api-call-cleaned"]
            
# iterar no MongoDB
#Registrar classes na ontologia.       


api_calls = api_calls = list(collection_call_cleaned.find())

sync_reasoner()

with onto:
    #try:      
        for call in api_calls:
            #Consumer App.client_id
            Consumer_app_id = None
            Consumer_app_name = None
            if "_source" in call and "consumer" in call["_source"] and "id" in call["_source"]["consumer"]:
                Consumer_app_id = call["_source"]["consumer"]["id"] 
            #Consumer App.app_name
            if "_source" in call and "consumer" in call["_source"] and "username" in call["_source"]["consumer"]:
                Consumer_app_name = call["_source"]["consumer"]["username"] 
                
            if Consumer_app_id is not None and Consumer_app_name is not None:
                #cls = onto["http://eamining.edu.pt/core#ConsumerApp"]
                cls_consumer_app = ns_core.ConsumerApp
                consumer_app = get_individual(cls_consumer_app, Consumer_app_name)
                if consumer_app is None:
                    #consumer_app = onto.ConsumerApp(Consumer_app_name)
                    #consumer_app = ConsumerApp(Consumer_app_name)  
                    consumer_app = cls_consumer_app(Consumer_app_name)
                    consumer_app.client_id.append(Consumer_app_id)
                    consumer_app.app_name.append(Consumer_app_name)
            
                    
                #API Call.request_time
                # create the individuo for ontology classe API Call, and set its properties started=at as request_time and @timestamp as response_time
                #API Call.request_time
                cls_api_call = ns_core.APICall
                # TODO tem que verificar se a chamada já não existe
                # onto_api_call = get_individual(cls, Consumer_app_name)
                if "@timestamp" in call["_source"]:
                    api_call = cls_api_call()
                    api_call.request_time.append(call["_source"]["@timestamp"])
                    #TODO confirmar o response_time
                    if "response" in call["_source"] and "headers" in call["_source"]["response"] and "date" in call["_source"]["response"]["headers"]:
                        api_call.response_time.append(call["_source"]["response"]["headers"]["date"])                      
                    if "response" in call["_source"] and "status" in call["_source"]["response"]:
                        api_call.result_status.append(call["_source"]["response"]["status"])               
                    if "request" in call["_source"] and "uri" in call["_source"]["request"]:
                        api_call.api_uri.append(call["_source"]["request"]["uri"])
                    if "route" in call["_source"] and "name" in call["_source"]["route"]:
                        # TODO tem que fazer o split para pegar o nome
                        api_call.api_name.append(call["_source"]["route"]["name"])   
                        #  ConsumerApp participation  in Property participadIn with API Call
                        consumer_app.participatedIn.append(api_call)
                                                    
                    #ApiOperation.method
                    if "request" in call["_source"] and "method" in call["_source"]["request"] and "request" in call["_source"] and "url" in call["_source"]["request"]:
                        operation_route = call["_source"]["request"]["method"] + "_" + call["_source"]["request"]["url"]
                        api_operation = get_individual(ns_core.APIOperation, operation_route)
                        if api_operation is None:
                            api_operation = ns_core.APIOperation(operation_route)
                            api_operation.endpoint_route.append(operation_route) 
                            api_operation.method.append(call["_source"]["request"]["method"])               
                        api_call.participatedIn.append(api_operation)
                    #ServiceDestination.endpoint_route
                    if "service" in call["_source"] and "host" in call["_source"]["service"] and "path" in call["_source"]["service"]:
                        api_destination_route = call["_source"]["service"]["host"] + call["_source"]["service"]["path"]
                        api_destination = get_individual(ns_core.APIOperation, api_destination_route)                        
                        if api_destination is None:
                            api_destination = ns_core.ServiceDestination(api_destination_route)
                            api_destination.endpoint_route.append(api_destination_route)
                        api_destination.participatedIn.append(api_call)
                        
                    #API Resource Resouce.uri Resource.data
                    # Request Data
                    if "request" in call["_source"] and "uri" in call["_source"]["request"]:
                        resource_uri = call["_source"]["request"]["uri"]
                        api_resource = ns_core.APIResource(resource_uri)
                        #api_resource.API_Resource.uri.append(call["_source"]["request"]["uri"])
                        api_resource.resource_uri.append(resource_uri)
                        api_operation.modifies.append(api_resource) # API operation modifies API resource
                        
                    #TODO tranformar body em datatype Attribute (array de par name - value)
                    if "request" in call["_source"] and "body" in call["_source"]["request"]:
                        request_body = call["_source"]["request"]["body"]
                        request_body_json = json.loads(request_body)
                        get_onto_attributes_from_json(api_resource, request_body_json, "")

                    # Response data
                    #api_resource.data.append(call["_source"]["request"]["body"])                        
                        
                    #save the individuals
                    
                    #check de ontology consistency before saving
                    sync_reasoner()
                    inconsistent_cls_list = list(default_world.inconsistent_classes())
                    for il in inconsistent_cls_list:
                        print(il)
                        print('inconsistency_list', il)      
                        raise Exception(f"Ontology inconsistency found: {il}")                      
                    try:
                        onto.save(format="rdfxml")
                    except Exception as error:
                        print('Ocorreu problema {} '.format(error.__class__))
                        print("mensagem", str(error))
                        print("In extractAPIConcepts module :", __name__)  
                        raise error              
                #self.saveOntology(onto)              

        # save the whole new classes ontologies       
        #self.saveOntology(self.onto) 
    
    # except Exception as error:
    #     print('Ocorreu problema {} '.format(error.__class__))
    #     print("mensagem", str(error))
    #     print("In extractAPIConcepts module :", __name__)        
                 
   
print("ExtractOntoCore Chegou ao final com sucesso")