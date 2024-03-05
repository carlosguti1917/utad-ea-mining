"""
Este código não funciona bem, o reasoner_sync() não funciona corretamente
"""

from pymongo import MongoClient
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
onto = get_ontology("Onto EA Mining v0.1-RDFXML.nt").load()

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
                              

class ExtractOntoCore:
    def __init__(self):
        # Connect to MongoDB
        self.myclient = pymongo.MongoClient(configs.MONGO_DB_SERVER["host"])
        self.mydb = self.myclient[configs.MONGO_DB_SERVER["databasename"]]
        self.collection_call_cleaned = self.mydb["kong-api-call-cleaned"]
        # open ontologia
        #onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
        #onto = get_ontology("Onto EA Mining v0.1-RDFXML.nt").load()
        #self.define_ontology_classes(onto)
        #self.extractAPIs(onto)
        self.extractAPIs()
        

    def define_ontology_classes(self, onto):
        # Define the ontology classes and data property
        try:  
            pass  
                             
        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("In defineOntologyClasses module :", __name__)  

        
    #def extractAPIs(self, onto):
    def extractAPIs(self):
        # iterar no MongoDB
        #Registrar classes na ontologia.       
        
        ns = onto.get_namespace("http://apieamining.edu.pt/core#")
        with onto:
            try:
                api_calls = self.getApiCallsCleaned()
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
                        cls = ns.ConsumerApp
                        onto_consumer_app = self.get_individual(onto, cls, Consumer_app_name)
                        if onto_consumer_app is None:
                            #consumer_app = onto.ConsumerApp(Consumer_app_name)
                            consumer_app = ConsumerApp(Consumer_app_name)                            
                            consumer_app.client_id.append(Consumer_app_id)
                            consumer_app.app_name.append(Consumer_app_name)

                        print(consumer_app.iri)
                    
                        #check de ontology consistency before saving
                        sync_reasoner()
                        inconsistency_list = list(default_world.inconsistent_classes())
                        print('inconsistency_list', inconsistency_list)
                    
                        #save the individuals
                        #onto.save(format="rdfxml")
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

print("ExtractOntoCore com sucesso")