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
    onto = None
    def __init__(self):
        # Connect to MongoDB
        self.myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
        self.mydb = self.myclient[configs.MONGO_DB_SERVER["databasename"]]
        self.collection_call_cleaned = self.mydb["kong-api-call-cleaned"]
        # open ontologia
        onto = self.getOntology("Onto EA Mining v0.1-RDFXML.owl")
        #ont = self.onto
        self.define_ontology_classes(onto)
        self.extractAPIs(onto)
        

    def define_ontology_classes(self, onto):
        # Define the ontology classes and data property
        try:    
            with onto:
                
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
                
                #API Service
                class Service(Thing):
                    pass
                
                class url(DataProperty):
                    pass
                
                # API Service Destination
                class Service_Destination(Thing):
                    pass
                
                class endpoint_route(DataProperty):
                    pass
                
                class method(DataProperty):
                    pass
                
                #API Operation
                class API_Operation(Thing):
                    pass
                
                #API Resource
                class API_Resource(Thing):
                    pass
                
                class name(DataProperty):
                    pass
                                               
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In defineOntologyClasses module :", __name__)  

        
    def extractAPIs(self, onto):
        # iterar no MongoDB
        #Registrar classes na ontologia.       
        
        ns = onto.get_namespace("http://apieamining.edu.pt/core#")
        cls = ns.API_Call
        try:
            api_calls = self.getApiCallsCleaned()
            for call in api_calls:
                #Consumer App.client_id
                #if "id" in call["_source"]["consumer"]:
                Consumer_app_id = None
                Consumer_app_name = None
                if "_source" in call and "consumer" in call["_source"] and "id" in call["_source"]["consumer"]:
                    Consumer_app_id = call["_source"]["consumer"]["id"] 
                    print("client_id = ", Consumer_app_id)
                #Consumer App.app_name
                if "_source" in call and "consumer" in call["_source"] and "username" in call["_source"]["consumer"]:
                    Consumer_app_name = call["_source"]["consumer"]["username"] 
                    #print("Consumer_app_name = ", Consumer_app_name) 
                    
                if Consumer_app_id is not None and Consumer_app_name is not None:
                    #consumer_app = ConsumerApp(Consumer_app_name)
                    aux_onto = onto
                    onto_consumer_app = self.get_individual(aux_onto, cls, Consumer_app_name)
                    if onto_consumer_app is not None:
                        aux_onto.ConsumerApp()
                        aux_onto.ConsumerApp.client_id.append(Consumer_app_id)
                        aux_onto.ConsumerApp.app_name.append(Consumer_app_name) 
                        #consumer_app = self.onto.get_or_create_consumer_app(Consumer_app_name, Consumer_app_name, Consumer_app_id)
                        #print("consumer_app = ", onto.ConsumerApp.)


                    #API Call.request_time
                    # create the individuo for ontology classe API Call, and set its properties started=at as request_time and @timestamp as response_time
                    #API Call.request_time
                    aux_onto.API_Call()
                    if "@timestamp" in call["_source"]:
                        time_stamp = call["_source"]["@timestamp"]
                        aux_onto.API_Call.request_time.append(call["_source"]["@timestamp"])
                    #API Call.response_time
                    #TODO confirmar o response_time
                    if "response" in call["_source"] and "headers" in call["_source"]["response"] and "date" in call["_source"]["response"]["headers"]:
                        response_time_stamp = call["_source"]["response"]["headers"]["date"]
                        aux_onto.API_Call.response_time.append(call["_source"]["response"]["headers"]["date"])                      
                    #API Call.result_status
                    if "response" in call["_source"] and "status" in call["_source"]["response"]:
                        #result_status = call["_source"]["response"]["status"]
                        aux_onto.API_Call.result_status.append(call["_source"]["response"]["status"])               
                    #API Call.uri
                    if "request" in call["_source"] and "uri" in call["_source"]["request"]:
                        api_uri = call["_source"]["request"]["uri"]
                        print("api_uri = ", api_uri)                
                        aux_onto.API_Call.uri.append(call["_source"]["request"]["uri"])
                    #API Call.api_name
                    if "route" in call["_source"] and "name" in call["_source"]["route"]:
                        api_name = call["_source"]["route"]["name"]
                        print("api_name = ", api_name) 
                        # TODO tem que fazer o split para pegar o nome
                        aux_onto.API_Call.api_name.append(call["_source"]["route"]["name"])           
                    #ApiOperation.method
                    aux_onto.Service_Destination()
                    aux_onto.API_Operation()
                    if "request" in call["_source"] and "method" in call["_source"]["request"]:
                        api_operation_method = call["_source"]["request"]["method"]
                        print("api_operation_method = ", api_operation_method)  
                        aux_onto.API_Operation.method.append(call["_source"]["request"]["method"])               
                    #APIOperation.endpoint_route
                    if "request" in call["_source"] and "url" in call["_source"]["request"]:
                        api_endpoint_route = call["_source"]["request"]["url"]
                        print("api_endpoint_route = ", api_endpoint_route) 
                        aux_onto.API_Operation.endpoint_route.append(call["_source"]["request"]["url"])                              
                    #ServiceDestination.endpoint_route
                    if "service" in call["_source"] and "host" in call["_source"]["service"] and "path" in call["_source"]["service"]:
                        destination_endpoint_route = call["_source"]["service"]["host"] + call["_source"]["service"]["path"]
                        print("destination_endpoint_route = ", destination_endpoint_route)  
                        aux_onto.Service_Destination.endpoint_route.append(call["_source"]["service"]["host"] + call["_source"]["service"]["path"])
                    #API Resource
                    #API Resource.name
                    print("API Resource.name = ", aux_onto.API_Resource.name)
                    if "route" in call["_source"] and "name" in call["_source"]["route"] and call["_source"]["route"]["name"]:
                        #if self.individual_exists(aux_onto, "API_Resource", call["_source"]["route"]["name"] ) is False:
                            aux_onto.API_Resource(call["_source"]["route"]["name"])
                            print("API Resource.name = ", aux_onto.API_Resource.name)                        
                            #aux_onto.API_Resource.name = call["_source"]["route"]["name"]
                            print("API Resource.name = ", aux_onto.API_Resource.name)
                    #TODO Pendente, acho que vou ter que splitar a URI para pegar o nome do recurso                 
                    #API Resource.uri
                    if "request" in call["_source"] and "uri" in call["_source"]["request"]:
                        resource_uri = call["_source"]["request"]["uri"]
                        aux_onto.API_Resource.uri.append(call["_source"]["request"]["uri"])
                    
                    #API Resource.data []
                    
                    #save the individuals
                    aux_onto.save(format="rdfxml")
                    #self.saveOntology(onto)              

            # save the whole new classes ontologies       
            #self.saveOntology(self.onto) 
           
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
        
    def getOntology(self, onto_name):
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
            
    def saveOntology(onto):
        try:
            #onto.save(format='rdfxml')
            #onto.save(file="Onto EA Mining v0.1-RDFXML.owl", format="xml")
            onto.save(format="rdfxml")
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


    def get_individual(self, onto, cls, individual_name):
        """
        Retrieves individuals from the ontology based on the provided class name and individual name.

        Args:
            onto: The ontology to query.
            class_name: The name of the class to query for.
            individual_name: The name of the individual to query for.

        Returns:
            list: A list of individuals that match the query.
        """
        result = None
        try:
            #with onto:
            individuals = onto.search(type=cls, iri="*"+ individual_name)
            # Check if the individual exists
            if individuals and len(individuals) == 1:
                result = individuals[0] 
                # Access individual properties or perform further operations
            elif individuals and len(individuals) > 1:
                raise Exception(f"More than one individual '{individual_name}' of class '{cls}' was found.")
            return result
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In get_individuals module :", __name__)  
            
    def individual_exists(self, onto, class_name, individual_name) -> bool:
        """
        Check if an individual exists in the ontology.

        :param onto: The ontology to search in.
        :param class_name: The class name to search for.
        :param individual_name: The individual name to search for.
        :return: True if the individual exists, False otherwise.
        :rtype: bool
        """
        try:
            result = self.get_individuals(onto, class_name, individual_name)
            if len(result) > 0:
                return True
            else:
                return False
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In get_individuals module :", __name__)                   
        
    


extract_onto_core = ExtractOntoCore()
#onto = extract_onto_core.extract_onto_core.getOntologia("Onto EA Mining v0.1-RDFXML.owl")
exists = extract_onto_core.individual_exists(extract_onto_core, "API_Call", "APICall1")
print("exists: ", exists)



# Call the getCalls method
#calls = data_prep.getCalls('your_begindate_here')

# Print the result
#print(data_prep)

print("ExtractOntoCore com sucesso")