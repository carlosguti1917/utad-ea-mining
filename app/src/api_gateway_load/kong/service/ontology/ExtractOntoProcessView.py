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
onto = get_ontology("EA Mining OntoUML Teste V1_1.owl").load()
ns_core = onto.get_namespace("http://eamining.edu.pt/core#")
ns_process_view = onto.get_namespace("http://eamining.edu.pt/process-view#")


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
        #individuals = onto.search(type=onto_class, iri="http://eamining.edu.pt#acmeapp") 
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

def get_all_api_calls(onto):
    """
    Retrieves all individuals of the APICall class from the ontology.

    Args:
        onto: The ontology to query.

    Returns:
        list: A list of all APICall individuals in the ontology.
    """
    try:
        cls_api_call = ns_core.APICall
        with onto:
            api_calls = list(onto.individuals(cls_api_call))
            return api_calls
    except Exception as error:
        print('An error occurred: {} '.format(error.__class__))
        print("Message:", str(error))
        print("In get_all_api_calls module :", __name__)
        raise error

api_calls = get_all_api_calls(onto)

with onto:
    #try:      
        for call in api_calls:
            Consumer_app_id = None
            Consumer_app_name = None
            request_id = None
            cls_api_call = ns_core.APICall

            if request_id is None and Consumer_app_id is None and Consumer_app_name is None:
                continue
            if get_individual(cls_api_call, request_id):
                continue
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
            #self.saveOntology(onto)              

        # save the whole new classes ontologies       
        #self.saveOntology(self.onto) 
    
    # except Exception as error:
    #     print('Ocorreu problema {} '.format(error.__class__))
    #     print("mensagem", str(error))
    #     print("In extractAPIConcepts module :", __name__)        
                 
   
print("ExtractOntoCore Chegou ao final com sucesso")