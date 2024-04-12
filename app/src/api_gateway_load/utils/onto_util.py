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

# #onto = get_ontology("app/src/api_gateway_load/repository/Onto EA Mining v0.1-RDFXML.owl").load()
# onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
# #onto = get_ontology("Onto EA Mining v0.1-RDFXML.owl").load()
# onto = get_ontology("EA Mining OntoUML Teste V1_1.owl").load()
# ns_core = onto.get_namespace("http://eamining.edu.pt/core#")

#print("classes = ",list(onto.classes()))


def get_individual(onto, onto_class, iri_base, individual_name):
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
        individuals = onto.search(type=onto_class, iri=f"{iri_base}{individual_name}")     
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
 
   
#print("ExtractOntoCore Chegou ao final com sucesso")