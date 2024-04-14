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


def add_ignored_attribute_to_file(attribute_name, file_path, api_name):
    # add to the list of ignored attributes for the API from the file of ignored attributes    
    """
    open the json file
    set the json object to a variable
    Add a new attribute_ to the json file with the list of ignored attribute
    save the json file
    close the json file
    update the json object variable with the new attribute
    return de json object variable
    """
    #data = []
    try:
        file_name = configs.FREQUENT_API_ATTRIBUTES["file_name"]
        full_file_name = f"{api_name}_{file_name}"
        if os.path.exists(file_path + full_file_name):
            with open(file_path + full_file_name, 'r') as file:
                data = file.read()
                #check if the attribute is already in the list, if not, add it
                if attribute_name not in data:
                    with open(file_path + full_file_name, 'a') as file:
                        file.write(attribute_name + '\n')
                        file.close()
        else:
            with open(file_path + full_file_name, 'w') as file:
                file.write(attribute_name + '\n')
                file.close()
        #return data
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In add_ignored_attribute_to_json_file module({attribute_name}, {file_path}, {file_name}) :", __name__)        
        raise error      
    

def get_ignored_attributes_from_file(file_path, api_name):
    # get the list of ignored attributes for the API from the file of ignored attributes
    data = []
    try: 
        file_name = configs.FREQUENT_API_ATTRIBUTES["file_name"]
        full_file_name = f"{api_name}_{file_name}"
        if os.path.exists(file_path + full_file_name):
            with open(file_path + full_file_name, 'r') as file:
                data = file.read()
                #check if the attribute is already in the list, if not, add it
                data = data.splitlines()
                file.close()
        return data
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In get_ignored_attributes_from_file({file_path}, {file_name}) :", __name__)        
        raise error      

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
 
def export_to_file(line_data, file_path, file_name, headers):
# Export to CSV
    # csv_file = 'api_resource_data.csv'
    # with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(headers)
    #     for row in line_data:
    #         writer.writerow(row)

    # Export to txt
    file_full_name = os.path.join(file_path, file_name)
    with open(file_full_name, 'w', encoding='utf-8') as file:
        # Write headers
        if headers is not None:
            file.write('\t'.join(headers) + '\n')
        # Write data rows
        for row in line_data:
            file.write('\t'.join(map(str, row)) + '\n')         

    print(f'Data exported to {file_full_name}')    
   
#print("ExtractOntoCore Chegou ao final com sucesso")