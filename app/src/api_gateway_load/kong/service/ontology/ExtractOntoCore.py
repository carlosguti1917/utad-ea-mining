from pymongo import MongoClient
from owlready2 import *
import sys
import os
import os.path

import pymongo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..")))
from api_gateway_load import configs

#onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
#print("onto_path = ", onto_path)
#onto = get_ontology("file://ontoeamining.owl").load()
#onto = get_ontology("app/src/api_gateway_load/repository/Onto EA Mining v0.1-RDFXML.owl").load()

class ExtractOntoCore:
    
    def __init__(self):
        # Connect to MongoDB
        self.myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
        self.mydb = self.myclient[configs.MONGO_DB_SERVER["databasename"]]
        self.collection_call_cleaned = self.mydb["kong-api-call-cleaned"]
        # open ontologia
        self.onto = self.getOntologia("Onto EA Mining v0.1-RDFXML.owl")
        self.defineOntologyClasses(self)
        self.extractAPIs(self)
        

    def defineOntologyClasses(self):
    # Define the ontology classes and data property
        try:    
            with self.onto:
                
                # Consumer App
                class ConsumerApp(Thing):
                    pass

                class Partner(Thing):
                    pass

                class client_id(DataProperty):
                    pass
                
                class app_name(DataProperty):
                    pass

                # Consumer API Call                    
                class API_Call(Thing):
                    pass
                
                class api_name(DataProperty):
                    pass
                
                class request_time(DataProperty):
                    pass
                
                class response_time(DataProperty):
                    pass
                
                class result_status(DataProperty):
                    pass
                
                class result_code(DataProperty):
                    pass
                
                class uri(DataProperty):
                    pass
                
                # API Service Destination
                class Service_Destination(Thing):
                    pass
                
                #API Operation
                class API_Operation(Thing):
                    pass
                
                #API Resource
                class API_Resource(Thing):
                    pass
                                               
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In defineOntologyClasses module :", __name__)  

        
    def extractAPIs(self):
        # iterar no MongoDB
        #Registrar classes na ontologia.
        
        try:
            api_calls = self.getApiCallsCleaned()
            for call in api_calls:
                #Consumer App.client_id
                if "client_id" in call["_source"]["request"]["headers"]:
                    client_id = call["_source"]["request"]["headers"]["client_id"] 
                    #print("client_id = ", client_id)
                if "client_id" in call["_source"]["consumer"]["id"]:
                    Consumer_app_id = call["_source"]["consumer"]["id"] 
                    #print("client_id = ", Consumer_app_id)
                #Consumer App.app_name
                if "username" in call["_source"]["consumer"]:
                    Consumer_app_name = call["_source"]["consumer"]["username"] 

                    #print("Consumer_app_name = ", Consumer_app_name) 
                    self.onto.ConsumerApp(Consumer_app_name)
                    self.onto.ConsumerApp.client_id.append(Consumer_app_id)
                    self.onto.ConsumerApp.app_name.append(Consumer_app_name) 
                #API Call.request_time
                if "started_at" in call["_source"]:
                    request_time = call["_source"]["started_at"]
                    print("request_time = ", request_time)   
                if "@timestamp" in call["_source"]:
                    time_stamp = call["_source"]["@timestamp"]
                    print("@timestamp = ", time_stamp)                     
                #API Call.response_time
                
                #API Call.result_status
                if "status" in call["_source"]["response"]:
                    result_status = call["_source"]["response"]["status"]
                    print("result_status = ", result_status)                     
                #API Call.uri
                if "uri" in call["_source"]["request"]:
                    api_uri = call["_source"]["request"]["uri"]
                    print("api_uri = ", api_uri)                
                #API Call.api_name
                if "name" in call["_source"]["route"]:
                    api_name = call["_source"]["route"]["name"]
                    print("api_name = ", api_name)                 
                #ApiOperation.method
                if "method" in call["_source"]["request"]:
                    api_operation_method = call["_source"]["request"]["method"]
                    print("api_operation_method = ", api_operation_method)                 
                #APIOperation.endpoint_route
                if "url" in call["_source"]["request"]:
                    api_endpoint_route = call["_source"]["request"]["url"]
                    print("api_endpoint_route = ", api_endpoint_route)                               
                #ServiceDestination.endpoint_route
                if "host" in call["_source"]["service"] and "path" in call["_source"]["service"]:
                    destination_endpoint_route = call["_source"]["service"]["host"] + call["_source"]["service"]["path"]
                    print("destination_endpoint_route = ", destination_endpoint_route)  
                #API Resource
                #API Resource.name
                #Pendente, acho que vou ter que splitar a URI para pegar o nome do recurso                 
                #API Resource.uri
                if "uri" in call["_source"]["request"]:
                    resource_uri = call["_source"]["request"]["url"]
                    print("resource_uri = ", resource_uri)
                
                #API Resource.data []
                
                

            # save the whole new classes ontologies       
            self.saveOntology(self.onto) 
           
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In extractAPIConcepts module :", __name__)        
            
    def extractAPIConcepts(api_call):
        ret = None
        pass
        try:
            #if isinstance(api_call, dict):
            #     for key, value in obj.items():
            #         if isinstance(value, dict):
            #             cleaned_obj[key] = self.cleanIgnoredAttributes(value, aux_path_key, new_path)
            #         elif isinstance(value, list):
            #             cleaned_obj[key] = [self.cleanIgnoredAttributes(item, aux_path_key, new_path) for item in value if item]
            #         elif value or (isinstance(value, list) and value):
            #             cleaned_obj[key] = value
            #     ret = cleaned_obj                             
            # elif isinstance(obj, list):
            #     ret = [self.cleanIgnoredAttributes(item, aux_path_key, new_path) for item in obj if item]
            # else:
            #     ret = obj 
            #return ret      
            pass
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In extractAPIConcepts module :", __name__)                   
        
    def getOntologia(self, onto_name):
        onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
        onto = get_ontology(onto_name).load()
        return onto  
       
    def getApiCallsCleaned(self):
        try:
            api_calls = list(self.collection_call_cleaned.find())
            return api_calls        
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In getApiCallsCleaned module :", __name__)     
            
    def saveOntology(self):
        try:
            self.onto.save(format='rdfxml')
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In saveOntologia module :", __name__)              
            
    def setOntolgyIndividuals(self, onto, className, individuoName):
        try:
            onto[className] = individuoName
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In setOntolgyIndividuals module :", __name__)
