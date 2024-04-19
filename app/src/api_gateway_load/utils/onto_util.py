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
import os

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
                file.close()
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

def attribute_pairs_selection(api_resource_correlations):
    aux_corr_dict = {} # Auxiliary Dictionary to store the attributes pair and the number of times they appear in the correlations
    selected_correlations = [] # List of attributes pair selected to be used in the FTC
    aux_operations_dic = {}
    try:
        for corr_aux in api_resource_correlations:
            #counter_operations = 0                
            aux_operations_pair = f"{corr_aux[0][2]} | {corr_aux[0][5]}"        
            for attributes_corr_aux in corr_aux:
                if len(aux_corr_dict) == 0:
                    aux_corr_dict[aux_operations_pair] = {attributes_corr_aux[0] : 1}
                    #aux_corr_dict[attributes_corr_aux[0]] = 1
                elif not aux_operations_pair in aux_corr_dict: #inicialize the nested dictionary with the first attribute
                    aux_corr_dict[aux_operations_pair] = {attributes_corr_aux[0] : 1}                                               
                elif attributes_corr_aux[0] in aux_corr_dict[aux_operations_pair]:
                    if aux_corr_dict[aux_operations_pair][attributes_corr_aux[0]] > 0:
                        counter_attributes = aux_corr_dict[aux_operations_pair][attributes_corr_aux[0]] + 1
                        aux_corr_dict[aux_operations_pair][attributes_corr_aux[0]] = counter_attributes
                    else:
                        print("este código não deveria executar pois os contadores começam em 1em for attributes_corr_aux in corr_aux:")
                        aux_corr_dict[aux_operations_pair][attributes_corr_aux[0]] = 1
                        # aux_corr_dict[attributes_corr_aux[0]] = 1
                else:
                    aux_corr_dict[aux_operations_pair][attributes_corr_aux[0]] = 1
            #counter_operations += 1
            if "total_operations_pair" in aux_corr_dict[aux_operations_pair]:
                aux_corr_dict[aux_operations_pair]["total_operations_pair"] = aux_corr_dict[aux_operations_pair]["total_operations_pair"] + 1
            else:
                aux_corr_dict[aux_operations_pair]["total_operations_pair"] = 1

    
        sorted_aux_corr_dict = dict(sorted(aux_corr_dict.items(), key=lambda item: item[0]))
        print(f"sorted_aux_corr_dict len: {len(sorted_aux_corr_dict)}")
        for key_a in sorted_aux_corr_dict:
            total_operations = sorted_aux_corr_dict[key_a]["total_operations_pair"]
            #print(F"Total Operations = {total_operations}")
            for key_b in sorted_aux_corr_dict[key_a]:
                if key_b == "total_operations_pair":
                    continue    
                attribute_pair_size = sorted_aux_corr_dict[key_a][key_b]
                attribute_weight = attribute_pair_size / total_operations # Some attributes may have more weight than other operations
                #print(f"Total Operations = {total_operations} - attribute_pair_size {attribute_pair_size} - attribute_weight {attribute_weight}" )
                if (attribute_weight >= 1) and attribute_pair_size > 1: # eliminate the attributes that appear only once because may be false positive
                    if key_b not in selected_correlations:
                        selected_correlations.append(key_b)
                        #print(f"Feature Selected key_: {key_b}")                       
                    
        return selected_correlations
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In attributes_correlation_selection module :", __name__)        
        raise error      


def get_api_resources_correlations(api_call_a, api_call_resource_a, api_call_b, api_call_resource_b):
    """ Verify the correlation between the attributes of the resources
        all the repeated values sould match among the resources_a and resources_b attibutes
        return a list of correlated attributes in a correlation set, that with not duplicated entries
        the correlation have 6 attributes: correlation_key, api_name_a, api_name_b, attribute_a, attribute_a_value attribute_b, attribute_b_alue
        args:
        return a list of correlated attributes in a correlation set, that with not duplicated entries
                        correlation_list structure([0-correlation_key, 1-api_call_a, 2-operation_a_label, 
                                        3-attribute_a [0-attribute_name[0], 1-attribute_value[0]], 
                                        4-api_call_b, 5-operation_b_label, 
                                        6-attribute_b [0-attribute_name[0], 1-attribute_value[0]])
    """
    correlations_list = []  
    cont_size = 0 # used to calculate the weight of the correlations. The weight is the number the correlations found for each attibute. Each correlation should corresponde a 100% of the correlations
    # Find all attributes 
    try:
        for attribute_a in api_call_resource_a.resource_data:
            attribute_a_name = attribute_a.attribute_name[0]
            if attribute_a_name in get_ignored_attributes_from_file('./temp/', api_call_a.api_name[0]):
                continue
            else:
                # search in other attributes of the api resources for the same attribute value
                for attribute_b in api_call_resource_b.resource_data:
                    attribute_b_name = attribute_b.attribute_name[0]
                    if attribute_b_name in get_ignored_attributes_from_file('./temp/', api_call_b.api_name[0]):
                        continue
                    else:
                        if attribute_a.attribute_value[0] == attribute_b.attribute_value[0]:
                            #print(f"attribute correlation identified {attribute_a.attribute_name} : {attribute_a.attribute_value} ->  {attribute_b.attribute_name}, {attribute_b.attribute_value}")                        
                            operation_a_label = api_call_a.participatedIn[0].label[0]
                            operation_b_label = api_call_b.participatedIn[0].label[0]
                            correlation_key = f"{operation_a_label}/{attribute_a.attribute_name} | {operation_b_label}/{attribute_b.attribute_name}"
                            #correlations_list.append([correlation_key, api_call_a, operation_a_label, attribute_a.attribute_name[0], attribute_a.attribute_value[0], api_call_b, operation_b_label, attribute_b.attribute_name[0], attribute_b.attribute_value[0]]) 
                            correlations_list.append([correlation_key, api_call_a, operation_a_label, attribute_a, api_call_b, operation_b_label,  attribute_b]) 
                
                            #TODO talvez registrar na ontologia resouce equality. Algo como api_resource.AttributesEquality.append(attribute_name)                    
        return correlations_list      
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In get_api_resources_correlations({api_call_a}, {api_call_b}) :", __name__)        
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
   
def clean_all_files(file_path):
    # delete all the files in the directory in file_path
    try:
        file_list = os.listdir(file_path)
        for file_name in file_list:
            file_path_name = os.path.join(file_path, file_name)
            if os.path.isfile(file_path_name):
                os.remove(file_path_name)
        print(f'Directory cleaned clean_all_files({file_path})')
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In clean_all_files({file_path}) module :", __name__)
        raise error
 
def file_exists(file_path, file_name):
    #verify if the file already exists
    if os.path.exists(file_path + file_name):
        return True
    else:
        return False    
  
def save_result_to_file(result_data, file_path, file_name, headers):
    # Prepare data
  
    # Convert result_data to line_data format
    #line_data = []    
    # for api_call, attributes in result_data.items():
    #     line_data.append([api_call, ', '.join(attributes)])
    
    # Export to txt
    file_full_name = os.path.join(file_path, file_name)
      
    with open(file_full_name, 'w', encoding='utf-8') as file:
        # Write headers
        if headers is not None:
            file.write('\t'.join(headers) + '\n')
        # Write data rows
        for r in result_data:
            file.write(r + '\n') 
        
        file.close()        

    print(f'Data exported to {file_full_name}')

def resource_correlations_selection(api_resource_correlations, selected_attribute_pairs):
    """
        Select the resource correlations based on the selected attribute pairs.
        args:
            api_resource_correlations: list of API resource correlations
            selected_attribute_pairs: list of selected attribute pairs
    """
    #new_api_resource_correlations = api_resource_correlations.copy()
    new_correlations_list = []
    count = 0
    try:
        # for i in range(len(new_api_resource_correlations)):
        #     for j in range(len(new_api_resource_correlations[i])):
        #         correlation_key = new_api_resource_correlations[i][j][0]                          
        #         if new_api_resource_correlations[i][j][0] in selected_attribute_pairs:
        #             new_api_resource_correlations.remove(new_api_resource_correlations[i][j][0])
        #         else:
        #             print(f"Attribute {correlation_key} not in the selected_attribute_pairs")

        for correlations in api_resource_correlations:
            for attribute_correlation in correlations:
                correlation_key = attribute_correlation[0]                           
                if correlation_key in selected_attribute_pairs:
                    if not [correlation_key, attribute_correlation[1], attribute_correlation[2], attribute_correlation[3], attribute_correlation[4], attribute_correlation[5], 
                            attribute_correlation[6]] in new_correlations_list:
                        
                        # new_correlations_list.append([attribute_correlation[0], attribute_correlation[1], attribute_correlation[2], attribute_correlation[3], 
                        #                               attribute_correlation[4], attribute_correlation[5], attribute_correlation[6], attribute_correlation[7], 
                        #                               attribute_correlation[8]]) 
                        new_correlations_list.append([attribute_correlation[0], attribute_correlation[1], attribute_correlation[2], attribute_correlation[3], 
                                attribute_correlation[4], attribute_correlation[5], attribute_correlation[6]]) 
                        #TODO talvez registrar na ontologia resouce equality. Algo como api_resource.AttributesEquality.append(attribute_name)  
                                  
        return new_correlations_list
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In resource_correlations_selection module :", __name__)        
        raise error  
    
    
def validate_json_to_extraction(call):
    """
        Verifica se o json de chamada da API é válido para extração de dados.
        Args:
            call: json da chamada da API
    """
    isValid = True
    try:
        #verifica se existe consumer e request_id e se API Call já está registrada na ontologia
        
        # Only matter if the call has a consumer and a request_id
        if not ("_source" in call and "consumer" in call["_source"] and "id" in call["_source"]["consumer"]):
            isValid = False 
        if not ("_source" in call and "consumer" in call["_source"] and "username" in call["_source"]["consumer"]):
            isValid = False         
        if not "@timestamp" in call["_source"] and "request" in call["_source"] and "id" in call["_source"]["request"]:  
            isValid = False

        # in case of resourc is not defined or is not present
        if "request" in call["_source"] and "uri" in call["_source"]["request"]:
            resource_uri = call["_source"]["request"]["uri"]
            if "null" in resource_uri:
                isValid = False
                print("The string 'null' is present in resource_uri")
            else:
                #atribuir o resource_name 
                #Define the updated pattern
                pattern = r"/v\d+/(.*)"
                match = re.search(pattern, resource_uri)
                if not match:
                    isValid = False
          
                      
        return isValid
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In validate_json_to_extraction module(:", __name__)        
        raise error      

def remove_ftc_noise(ftc_list, activity):
    """
        Remove the false positive from the FTC list
        args:
            ftc_list: list of ns_process_view.FrequentTemporalCorrelation instances
    """
    #   Inicialize a processing_list and a new_list
    #   get all the events in the file and store in a processing_list
    #   get the younger event in the processing_list and store in the under_analisys_event and anteceedent_event_id
    #   pre-processing to clean noise events passing the under_analisys_event
    #      store in a memory consequent_event_id the event id of the consequent event
    #      iterate through the file and select all the consequent event of the antecedent event 
    #      for each consequent event of the antecedent_event_id check if the start datetime is between the start and end datetime of the antecedent event, if yes, discart removing the line from the processing_list
    #      set the consequent_event_id to the under_analisys_event
    #      repeat the process until there is no more consequent event for the under_analisys_event
    
    #   get the younger APIAntecedenteActivity in the ftc_list and store it in a var under_analisys_event and other var antecedent_activity
    #      store in a memory var the consequent_event_id the event id of the consequent event
    #      iterate through the ftc_list and select all the consequent event of the antecedent event 
    #      for each consequent event of the antecedent_event_id check if the start datetime is between the start and end datetime of the antecedent event, if yes, discart removing the line from the list
    #      set the consequent_event_id to the under_analisys_event
    #      call the function again, passing the ftc_list and the under_analisys_event, repeating the process until there is no more consequent event for the under_analisys_event  

        
    
    new_ftc_list = []
    try:
        for ftc in ftc_list:
            if len(ftc) > 1:
                new_ftc_list.append(ftc)
        return new_ftc_list
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In remove_ftc_noise module :", __name__)        
        raise error
    
def event_transactions_selection(file_path, file_name):
    """
        Select the time series transactions based on the begin and end date.
        args:
            file_path: the path to the file
            file_name: the name of the file
    """
    
    # get the younger transaction in the file, that is the transaction with the smaler start datetime and store in the under_analisys_transaction
    # iterate through the file and select the transactions that start datetime between the begin and end date of the previous transaction
    
    # I have 
    #   correlation id between two events
    # Needs
    #   events id
    #   events start datetime and end datetime
    #   for each anteceedent event, I need the id of the consequent event
    # Logic
    #   Inicialize a processing_list and a new_list
    #   get all the events in the file and store in a processing_list
    #   get the younger event in the processing_list and store in the under_analisys_event and anteceedent_event_id
    #   pre-processing to clean noise events passing the under_analisys_event
    #      store in a memory consequent_event_id the event id of the consequent event
    #      iterate through the file and select all the consequent event of the antecedent event 
    #      for each consequent event of the antecedent_event_id check if the start datetime is between the start and end datetime of the antecedent event, if yes, discart removing the line from the processing_list
    #      set the consequent_event_id to the under_analisys_event
    #      repeat the process until there is no more consequent event for the under_analisys_event
    #   Event Chain Selection 
    #      get the younger event in the processing_list and store in the under_analisys_event and anteceedent_event_id
    #      store in a memory consequent_event_id the event id of the consequent event
    #      Create a chain id 
    #      add to new_list the chain id, correlation id, antecedent_event_id, antecedent_event_start_datetime, antecedent_event_end_datetime, consequent_event_id, consequent_event_start_datetime, consequent_event_end_datetime
    #      iterate through the file and select all the consequent event of the antecedent event 
    #      for each consequent event of the antecedent_event_id check if the start datetime is between the start and end datetime of the antecedent event, if yes, discart removing the line from the processing_list
    #      set the consequent_event_id to the under_analisys_event
    #      repeat the process until there is no more consequent event for the under_analisys_event 
    
    
    selected_transactions = []
    try:
        with open(file_path + file_name, 'r') as file:
            data = file.read()
            file.close()
            data = data.splitlines()
            for line in data:
                line_data = line.split('\t')
                transaction_date = line_data[0]
                if begin_date <= transaction_date <= end_date:
                    selected_transactions.append(line)
        return selected_transactions
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In time_series_transaction_selection module :", __name__)        
        raise error