import json
from owlready2 import *
from datetime import datetime
#from owlready2 import Reasoner
import sys
import os
import os.path
import csv
from rdflib import Graph
import pandas as pd
from spmf import Spmf
import sys # Add missing import statement for sys module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..", "..")))
from api_gateway_load.utils import spmf_converter
from api_gateway_load.utils import onto_util

onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
onto = get_ontology("EA Mining OntoUML Teste V1_1.owl").load()
ns_gufo = onto.get_namespace("http://purl.org/nemo/gufo#")
ns_core = onto.get_namespace("http://eamining.edu.pt/core#")
ns_process_view = onto.get_namespace("http://eamining.edu.pt/process-view#")

#TODO seria bom ter um pre-processing, talvez usando algum algoritmo de feature extration ou feature selection para remover 
# atributos que irão gerar alta correlação, e selecionar aqueles que mais interessam.

'''
Remover atritubos que são categóricos e que irão gerar alta correlação, como nome do produto, nome do cliente, etc.
Considering the ontology onto, the following steps should be performed:
1- Query distinct api_name of APICall through sparql - ok
2- For each api_name query the all APICall with the same api_name -ok
3- For each APICall, query the resource_data -ok 
4- For each resource_data, query the attribute_name and attribute_value -ok
5- For each attribute_name, check if it is low dimension by querying the values in the APICall collection with the same attribute_name and using the rare item mining algorithm
7- If it is high dimension or rare, keep it in the list of attributes to be processed, otherwise discard it
9- save the result in a text file separated by tab witn the APICall and the resulting list of attributes for further processing - ok


1-Selecionar os consummers / partners - ok
2-iterar nos consumers e selecionar as APIs - ok
    3-iterar nas chamadas das APIs e obter os recursos (via operationExecuted) -ok
        4-para cada recurso, obter os atributos e valores (resource_data) - ok
            5-iterar nos atributos e procurar valores repetidos nos demais recursos - ok
                6- Para cada valor repetido adicionar ao relator FTC com os valores ligando as APIs e incrementando o valor de igualdade e registrando os eventos Antecedents e Consequentes
                Fim da Iteração
                
Nova interação para obter os candidatos ao Activiti Connection
1-Obter os relatores FTC
2-Utilizar alguma técnica de ARM para detectar itens de baixa dimensão e elemina-los.
    2.1 Talvez usando rare item mining para gerar outro set e eliminar a feature (atributo) da pesquisa, ou high utility item mining.
    2.2 Haverá exceção, como nome do produto, pode aparecer bastante, mas queremos eliminar aqueles items categóricos que irão gerar alta associação
    2.3 O Activites Connection liga duas atividades
    2.4 O process é uma sequencia de activies connection
    2.5 A partir desta sequência extrair para o xml do archimate
'''

 
def add_ignored_attribute_to_file(attribute_name, file_path, file_name):
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
        if os.path.exists(file_path + file_name):
            with open(file_path + file_name, 'r') as file:
                data = file.read()
                #check if the attribute is already in the list, if not, add it
                if attribute_name not in data:
                    with open(file_path + file_name, 'a') as file:
                        file.write(attribute_name + '\n')
                        file.close()
        else:
            with open(file_path + file_name, 'w') as file:
                file.write(attribute_name + '\n')
                file.close()
        #return data
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In add_ignored_attribute_to_json_file module({attribute_name}, {file_path}, {file_name}) :", __name__)        
        raise error      
    
def check_api_resource_correlation(api_call_id_a, api_call_resource_a, api_call_id_b, api_call_resource_b):
    # Prepare data
    line_data = []
    # Find all attributes 
    for attribute_a in api_call_resource_a.resource_data:
        attribute_a_name = attribute_a.attribute_name
        if attribute_a_name in get_ignored_attributes_from_file('./temp/', 'frequent_attributes.ignore'):
            continue
        else:
            # search in other API calls and resources for the same attribute value
            for attribute_b in api_call_resource_b.resource_data:
                #print(attribute_a.attribute_name, attribute_a.attribute_value, attribute_b.attribute_name, attribute_b.attribute_value)
                if attribute_b.attribute_value == attribute_a.attribute_value:
                    line_data.append([api_call_id_a, api_call_id_b, attribute_a, attribute_b])
                    # so verificar se há repetição
                    teste = line_data.count([api_call_id_a, api_call_id_b, attribute_a, attribute_b])
                    #print(f"{attribute_a.name}  --> {attribute_b.name}  :  {teste}")
                    #print(f"{attribute_a.attribute_name}={attribute_a.attribute_value}  --> {attribute_b.attribute_name}={attribute_b.attribute_value}")
                        
    return line_data
            # search in other API calls and resources for the same attribute value
            # inner_api_calls = sorted([inner_api_call for inner_api_call in consumer_app.participatedIn if inner_api_call.request_time > api_call.request_time], key=lambda x: x.request_time)
    

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


def get_ignored_attributes_from_file(file_path, file_name):
    
    data = []
    try:    
        if os.path.exists(file_path + file_name):
            with open(file_path + file_name, 'r') as file:
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


def remove_frequent_items(onto):
    
    attributes_to_ignore = []
    # Step 1: Query distinct api_name of APICall through sparql
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX gufo: <http://purl.org/nemo/gufo#>
        PREFIX ns_core: <http://eamining.edu.pt/core#>
        PREFIX aPIC: <aPICall:>

        SELECT distinct ?api_name
        WHERE {
            ?api_call rdf:type ns_core:APICall .
            ?api_call aPIC:api_name ?api_name .
            #FILTER(?api_name = "ecommerce-carts")
        }
        """
    api_names = list(default_world.sparql(query))

    # Step 2: For each api_calls_geral query the all APICall with the same api_name, grouping then
    for api_name_tuple in api_names:
        api_name = api_name_tuple[0]
        query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX gufo: <http://purl.org/nemo/gufo#>
            PREFIX ns_core: <http://eamining.edu.pt/core#>
            PREFIX aPIC: <aPICall:>
            SELECT ?api_call
            WHERE {{
                ?api_call rdf:type ns_core:APICall .
                ?api_call aPIC:api_name "{api_name}" .
            }}
            """
        api_calls = list(default_world.sparql(query))

        # Step 3: For each APICall, query the resource_data
        for api_call_tuple in api_calls:
            api_call = api_call_tuple[0]
            if not ns_core.APICall in api_call.is_a:
                continue
            # Find API Resources associated with API Call
            api_operations = list(api_call.participatedIn)     
            for api_operation in api_operations:
                query = f"""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX gufo: <http://purl.org/nemo/gufo#>
                            PREFIX ns_core: <http://eamining.edu.pt/core#>

                            SELECT ?resource
                            WHERE {{
                                ?operationExecuted rdf:type ns_core:OperationExecuted .
                                ?operationExecuted gufo:mediates ?resource .
                                ?resource rdf:type ns_core:APIResource .
                                ?operationExecuted gufo:mediates <{api_operation.iri}> .
                            }}
                        """                                                   
                # Execute the query
                api_resources = list(default_world.sparql(query))
                for api_resource_tuple in api_resources:
                    api_resource = api_resource_tuple[0]  # Get the individual from the tuple
                    # Check if resource is an instance of ns_core.APIResource
                    if ns_core.APIResource in api_resource.is_a:
                        #attribute_values = [attr.attribute_value for attr in resource.resource_data] 
                        attributes = []
                        for attribute in api_resource.resource_data:
                            attribute_name = attribute.attribute_name[0]
                            attribute_value = attribute.attribute_value[0]
                            api_name = api_call.api_name[0]
                            freq_attr_file_name = f"{api_name}_frequent_attributes.ignore"
                            # verify it the attribute sould be ignored
                            if attribute_name in get_ignored_attributes_from_file('./temp/', freq_attr_file_name):
                                break
                            # calculate the the variation of attribute_values in the other resources of the same api_call.name
                            attribute_is_util = verify_attribute_utility(attribute_name, api_name)
                            if attribute_is_util:
                                attributes.append((attribute_name, attribute_value))
                            else:
                                add_ignored_attribute_to_file(attribute_name, './temp/', freq_attr_file_name)
                                

def mining_frequent_temporal_correlations(onto):
    # Prepare data
    line_data = []
    # Find all ConsumerApp 
    consumer_apps = [individual for individual in onto.individuals() if individual.is_a[0] == ns_core.ConsumerApp]
    for consumer_app in consumer_apps:
        # Find API Calls associated with ConsumerApp and sort them by request_time
        api_calls = sorted(list(consumer_app.participatedIn), key=lambda x: x.request_time)
        #api_calls = iter(apps_api_calls)
        for api_call in api_calls:
            # Only instancs of API_Call
            if not ns_core.APICall in api_call.is_a:
                continue
            # Find API Resources associated with API Call
            api_operations = list(api_call.participatedIn)     
            for api_operation in api_operations:
                query = f"""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX gufo: <http://purl.org/nemo/gufo#>
                            PREFIX ns_core: <http://eamining.edu.pt/core#>
                            SELECT ?operationExecuted
                            WHERE {{
                                ?operationExecuted rdf:type ns_core:OperationExecuted .
                                ?operationExecuted gufo:mediates <{api_operation.iri}> .
                            }}
                        """                       
                # Execute the query
                operations_executed = list(default_world.sparql(query))
                for operation_executed_tuple in operations_executed:
                    operation_executed = operation_executed_tuple[0]  # Get the individual from the tuple
                    resources = list(operation_executed.mediates)
                    for resource in resources:
                            # Check if resource is an instance of ns_core.APIResource
                            if ns_core.APIResource in resource.is_a:
                                #attribute_values = [attr.attribute_value for attr in resource.resource_data] 
                                attributes = []
                                for attribute in resource.resource_data:
                                    attribute_name = attribute.attribute_name
                                    attribute_value = attribute.attribute_value
                                    print(attribute_name, attribute_value)
                                    # search in other API calls and resources for the same attribute value
                                    inner_api_calls = sorted([inner_api_call for inner_api_call in consumer_app.participatedIn if inner_api_call.request_time > api_call.request_time], key=lambda x: x.request_time)
                                    for inner_api_call in inner_api_calls:
                                        if inner_api_call != api_call and inner_api_call.api_uri != api_call.api_uri:
                                            inner_operations = inner_api_call.participatedIn
                                            for inner_operation in inner_operations:
                                                inner_query = f"""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                                                            PREFIX gufo: <http://purl.org/nemo/gufo#>
                                                            PREFIX ns_core: <http://eamining.edu.pt/core#>
                                                            SELECT ?operationExecuted
                                                            WHERE {{
                                                                ?operationExecuted rdf:type ns_core:OperationExecuted .
                                                                ?operationExecuted gufo:mediates <{inner_operation.iri}> .
                                                            }}
                                                        """ 
                                                inner_operations_executed = list(default_world.sparql(inner_query))
                                                for inner_operation_executed_tuple in inner_operations_executed:
                                                    inner_operation_executed = inner_operation_executed_tuple[0]  # Get the individual from the tuple
                                                    inner_resources = list(inner_operation_executed.mediates) 
                                                    for inner_resource in inner_resources:
                                                        if ns_core.APIResource in inner_resource.is_a:
                                                            api_correlations = check_api_resource_correlation(api_call, resource, inner_api_call, inner_resource)
                                                            if api_correlations is not None:
                                                                save_frequent_temporal_correlation(onto, api_call, inner_api_call, api_correlations)
                                                                                                   

                    #Append to CSV data
                    #line_data.append([api_call, attributes])
                    #print("line_data", line_data)
                    
def save_frequent_temporal_correlation(onto, api_call_a, api_call_b, correlated_attributes):      
    """
    calc the temporal dependency between api_call and inner_api_call based on the request_
    record the younger as Antecedent Activity and the older as Consequent Activity
    create the historicalDependsOn relation between the two activities
    create the relator Frequente Temporal Correlation (FTC) between the two activities
    create the mediation between the FTC do each of Activities
    record the attributes that are correlated in the api_correlations to reapeated_attributes in FTC
    """

    # calc the temporal dependency between api_call and inner_api_call based on the property request_time of the api_call
    # record the younger as API Antecedent Activity and the older as API Consequent Activity in the ontology onto
    # create the historicalDependsOn relation between the API Antecedent Activity and the API Consequent Activity
    # create the relator Frequente Temporal Correlation and create the property mediates between this relator to the API Antecedent Activity and to the API Consequent Activity
    # record the attributes that are correlated in the correlated_attributes to reapeated_attributes in the created Frequente Temporal Correlation
    
    partner = None
    with onto:
        sync_reasoner()
        if api_call_a.api_uri != api_call_b.api_uri:
            try:
                if api_call_a.request_time < api_call_b.request_time:   
                    api_antecedent_activity = ns_process_view.APIAntecedentActivity(api_call_a)
                    api_consequent_activity = ns_process_view.APIConsequentActivity(api_call_b)
                else:
                    api_antecedent_activity = ns_process_view.APIAntecedentActivity(api_call_b)
                    api_consequent_activity = ns_process_view.APIAntecedentActivity(api_call_a)   

                # Get the Consumer App related to api_call_a based on the inverse participatedIn property
                cls_consumer_app = ns_core.ConsumerApp
                cls_partner = ns_process_view.Partner
                #consumer_app = api_call_a.INVERSE_participatedIn[0]
                inverse_participations_a = api_call_a.INVERSE_participatedIn
                inverse_participations_b = api_call_b.INVERSE_participatedIn
                for inverse_participation_a in inverse_participations_a:
                    if cls_partner in inverse_participation_a.is_a or cls_consumer_app in inverse_participation_a.is_a:
                        consumer_app_a = inverse_participation_a
                    for inverse_participation_b in inverse_participations_b:
                        if cls_partner in inverse_participation_b.is_a or cls_consumer_app in inverse_participation_b.is_a:
                            consumer_app_b = inverse_participation_b
                        if consumer_app_a == consumer_app_b:
                                #verify if the partner is already exists and is related the antecedent activity and consequent activity
                                if consumer_app_a not in api_antecedent_activity.participatedIn and consumer_app_a not in api_consequent_activity.participatedIn:
                                    #partner = onto_util.get_individual(onto, ns_process_view.Partner, consumer_app._name)
                                    #partner = ns_process_view.Partner()
                                    #partner.equivalent_to.append(consumer_app_a)
                                    #partner.participatedIn.append(api_antecedent_activity)
                                    #partner.participatedIn.append(api_consequent_activity) 
                                    pass
                                       
                    # Create the temporal dependency between the API Antecedent Activity and the API Consequent Activity
                    api_consequent_activity.historicallyDependsOn.append(api_antecedent_activity)
                                        
                    # Create the relator Frequente Temporal Correlation
                    ftc = ns_process_view.FrequentTemporalCorrelation()

                    # Create the property mediates between the Frequente Temporal Correlation and the API Antecedent Activity
                    ftc.mediates.append(api_antecedent_activity)
                    ftc.mediates.append(api_consequent_activity)
                    
                    # Record the attributes that are correlated in the correlated_attributes to repeated_attributes in the created Frequente Temporal Correlation
                    for attribute in correlated_attributes:
                        #verify the attribute order. If attribute[0] is from api_call_a, then it is the Antecedent Activity (attribute_name_a), otherwise it is the Consequent Activity (attribute_name_b)
                        if attribute[0] == api_call_a:
                            attribute_name_a = attribute[2]
                            attribute_name_b = attribute[3]
                        else:
                            attribute_name_a = attribute[3]
                            attribute_name_b = attribute[2]
                        #attribute_a = ns_core.Attribute(attribute_name_a)
                        #attribute_b = ns_core.Attribute(attribute_name_b)
                        attribute_pair = onto.AttributePair()
                        attribute_pair.attribute_name_a.append(attribute_name_a)
                        attribute_pair.attribute_name_b.append(attribute_name_b)                          
                        # TODO concertar na ontologia, pois está com erro de grafia - repeatead_attributes
                        #ftc.repeated_attributes.append(attribute_pair)
                        ftc.repeatead_attributes.append(attribute_pair)

                        try:
                            #save the individuals                  
                            #check de ontology consistency before saving                        
                            sync_reasoner()
                            onto.save(format="rdfxml")
                        except Exception as error:
                            inconsistent_cls_list = list(default_world.inconsistent_classes())
                            for il in inconsistent_cls_list:
                                print(il)
                                print('inconsistency_list', il)                                                 
                            print('Ocorreu problema {} '.format(error.__class__))
                            print("mensagem", str(error))
                            print("In extractAPIConcepts module :", __name__)  
                            raise Exception(f"Ontology inconsistency found: {il}")                          
                    return ftc
            except Exception as error:
                print('Ocorreu problema {} '.format(error.__class__))
                print("mensagem", str(error))
                print(f"In save_frequent_temporal_correlation({api_call_a}, {api_call_b}) :", __name__)        
                raise error     

def navigate_and_export_ontology(onto):
    # Prepare data
    line_data = []
    headers = ['API Call', 'Resource Data Attributes']
    # Find ConsumerApp by client_id
    #consumer_apps = onto.search(type=onto.ConsumerApp, client_id=client_id_value)
    consumer_apps = onto.search(type=ns_core.ConsumerApp)
    #TODO tem que pegar só os ConsumerApp sem as subclasses. Está retornando o Partner.
    for consumer_app in consumer_apps:
        # Find API Calls associated with ConsumerApp
        # api_calls = onto.search(type=ns_core.APICall, participatedIn=consumer_app) . Isso aqui teria que ser por sparql, pois não existe o param object property
        api_calls = list(consumer_app.participatedIn)
        for api_call in api_calls:
            # Find API Resources associated with API Call
            api_operations = list(api_call.participatedIn)
            #classe = ns_core.OperationExecuted           
            for api_operation in api_operations:
                #g = Graph()
                # Parse in an RDF file hosted at some location
                query = f"""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX gufo: <http://purl.org/nemo/gufo#>
                            PREFIX ns_core: <http://eamining.edu.pt/core#>
                            SELECT ?operationExecuted
                            WHERE {{
                                ?operationExecuted rdf:type ns_core:OperationExecuted .
                                ?operationExecuted gufo:mediates <{api_operation.iri}> .
                            }}
                        """                       
                # Execute the query
                operations_executed = list(default_world.sparql(query))
                for operation_executed_tuple in operations_executed:
                    operation_executed = operation_executed_tuple[0]  # Get the individual from the tuple
                    resources = list(operation_executed.mediates)
                    for resource in resources:
                            # Check if resource is an instance of ns_core.APIResource
                            if ns_core.APIResource in resource.is_a:
                                #attribute_values = [attr.attribute_value for attr in resource.resource_data] 
                                attribute_values = []
                                for att in resource.resource_data:
                                    for value in att.attribute_value:
                                        at = value
                                    attribute_values.append(value)
                                print(attribute_values)
                    #Append to CSV data
                    line_data.append([api_call, attribute_values])
    export_to_file(line_data, '.', 'api_resource_data.txt', headers)                    

            


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

    print(f'Data exported to {file_full_name}')




def verify_attribute_utility(attribute_name, api_call_name):
#Verifica se atributo é útil. Um atributo é útil se ele é raro, ou seja, se ele é um atributo que não é comum em todos os recursos de uma chamada de API.	
   
    util = False
    try:
        query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX gufo: <http://purl.org/nemo/gufo#>
            PREFIX ns_core: <http://eamining.edu.pt/core#>
            PREFIX attr: <http://eamining.edu.pt/core#Attribute>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX aPIC: <aPICall:>
            PREFIX attr2: <attribute:> 

            SELECT ?attribute 
            WHERE {{         
                ?api_call rdf:type ns_core:APICall .
                ?api_call aPIC:api_name "{api_call_name}" .
                ?resource rdf:type ns_core:APIResource .
                ?attribute rdf:type <http://eamining.edu.pt/core#Attribute> .        
                ?attribute attr2:attribute_name "{attribute_name}" .             
            }}
            """
        print(query)
        
        attributes = list(default_world.sparql(query))
        # for calculate the weight of each attribute_value in the whole attributes collection.
        
        attribute_list = []
        for attribute_tuple in attributes:
            attribute_value = attribute_tuple[0].attribute_value[0]
            attribute_list.append((attribute_value)) 
       
        file_nm = f"api_resource_data_attribute_{attribute_name}.txt"
        file_path = './temp/'
        save_result_to_file(attribute_list, file_path, file_nm, None)
        ## if the attribute is text, then we need to convert it to a number
        #try:
        value = attribute_list[1]
        attribute_type = type(value)        
        print(attribute_name, attribute_type, value)
        #if attribute_type is int or float, then pass
        if attribute_type is int:
            pass
        else:
            try:
                # Try converting the value to an integer, if works, then it is a number
                value = int(value)
            except ValueError:
                try:
                    # If conversion to int fails, try converting to float, if does not work, then tranform to integer
                    value = float(value)
                    converter = spmf_converter.SPMFConverter()
                    file_nm = converter.convert_floats_to_number_items(file_path, file_nm)
                except ValueError:
                    # If conversion to int and float fails, then it is a string 
                    converter = spmf_converter.SPMFConverter()
                    file_nm = converter.convert_text_to_identified_items(file_path, file_nm)

            #int(attribute_list[1])
            #float(attribute_list[1])
        # except ValueError:
        #     converter = spmf_converter.SPMFConverter()
        #     file_nm = converter.convert_text_to_identified_items(file_path, file_nm)
        #     pass
                
        # Mining Perfectly Rare Itemsets Using The AprioriInverse Algorithm (SPMF Documentation) https://www.philippe-fournier-viger.com/spmf/AprioriInverse.php       
        # spmf = Spmf("AprioriInverse", input_file_path="./file_nm",
        #             output_file_path="output.txt", 
        #             spmf_jar_location_dir="./spmf.jar")

        #smpfa = Spmf(spmf_bin_location_dir="c:/gitHub/utad/utad-ea-mining/app/src/studies/spmf/spmf.jar",
        input_file_full_name = os.path.join(file_path, file_nm)
        output_file_nm = f"api_resource_data_attribute_{attribute_name}.out"
        output_file_full_name = os.path.join(file_path, output_file_nm)
        smpfa = Spmf(spmf_bin_location_dir="c:/gitHub/utad/utad-ea-mining/app/src/studies/spmf",
                    algorithm_name="AprioriInverse", 
                    input_filename=input_file_full_name,
                    output_filename=output_file_full_name, 
                    arguments=[0.1, 0.6])
        smpfa.run()
        
        # Read the output file line by line. If any pattern is found, then the attribute is considered useful
        outFile = open(output_file_full_name,'r', encoding='utf-8')
        for string in outFile:
            print(string)
            util = True
            break
        outFile.close() 
              
        #pd_rare = smpfa.to_pandas_dataframe(pickle=True)      
        #smpfa.to_csv(f"AprioriInverse{attribute_name}.csv")  
        
        return util
        
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        local_idenfication = f"verify_attribute_utility({attribute_name}, {api_call_name}) :"
        print(local_idenfication, __name__)
        raise error

def old_mining_frequent_temporal_correlations(onto):
    # Prepare data
    line_data = []
    # Find ConsumerApp by client_id
    #consumer_apps = onto.search(type=onto.ConsumerApp, client_id=client_id_value)
    #consumer_apps = onto.search(type=ns_core.ConsumerApp)
    consumer_apps = [individual for individual in onto.individuals() if individual.is_a[0] == ns_core.ConsumerApp]
    for consumer_app in consumer_apps:
        # Find API Calls associated with ConsumerApp
        api_calls = sorted(list(consumer_app.participatedIn), key=lambda x: x.request_time)
        #api_calls = iter(apps_api_calls)
        for api_call in api_calls:
            # Only instancs of API_Call
            if not ns_core.APICall in api_call.is_a:
                continue
            # Find API Resources associated with API Call
            api_operations = list(api_call.participatedIn)     
            for api_operation in api_operations:
                query = f"""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX gufo: <http://purl.org/nemo/gufo#>
                            PREFIX ns_core: <http://eamining.edu.pt/core#>
                            SELECT ?operationExecuted
                            WHERE {{
                                ?operationExecuted rdf:type ns_core:OperationExecuted .
                                ?operationExecuted gufo:mediates <{api_operation.iri}> .
                            }}
                        """                       
                # Execute the query
                operations_executed = list(default_world.sparql(query))
                for operation_executed_tuple in operations_executed:
                    operation_executed = operation_executed_tuple[0]  # Get the individual from the tuple
                    resources = list(operation_executed.mediates)
                    for resource in resources:
                            # Check if resource is an instance of ns_core.APIResource
                            if ns_core.APIResource in resource.is_a:
                                #attribute_values = [attr.attribute_value for attr in resource.resource_data] 
                                attributes = []
                                for attribute in resource.resource_data:
                                    attribute_name = attribute.attribute_name
                                    attribute_value = attribute.attribute_value
                                    print(attribute_name, attribute_value)
                                    # search in other API calls and resources for the same attribute value
                                    inner_api_calls = sorted([inner_api_call for inner_api_call in consumer_app.participatedIn if inner_api_call.request_time > api_call.request_time], key=lambda x: x.request_time)
                                    for inner_api_call in inner_api_calls:
                                        if inner_api_call != api_call:
                                            inner_operations = inner_api_call.participatedIn
                                            for inner_operation in inner_operations:
                                                inner_query = f"""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                                                            PREFIX gufo: <http://purl.org/nemo/gufo#>
                                                            PREFIX ns_core: <http://eamining.edu.pt/core#>
                                                            SELECT ?operationExecuted
                                                            WHERE {{
                                                                ?operationExecuted rdf:type ns_core:OperationExecuted .
                                                                ?operationExecuted gufo:mediates <{inner_operation.iri}> .
                                                            }}
                                                        """ 
                                                inner_operations_executed = list(default_world.sparql(inner_query))
                                                for inner_operation_executed_tuple in inner_operations_executed:
                                                    inner_operation_executed = inner_operation_executed_tuple[0]  # Get the individual from the tuple
                                                    inner_resources = list(inner_operation_executed.mediates) 
                                                    for inner_resource in inner_resources:
                                                        if ns_core.APIResource in inner_resource.is_a:
                                                            for inner_attribute in inner_resource.resource_data:
                                                                if inner_attribute.attribute_value == attribute_value:
                                                                    api_call_x = api_call.api_uri
                                                                    #api_call_y = inner_resource.parent.parent.parent.API_Call.api_uri
                                                                    api_call_y = inner_api_call.api_uri
                                                                    attributes.append((api_call, inner_api_call, attribute_name, attribute_value, inner_attribute.attribute_name, inner_attribute.attribute_value)) 
                                                                                                   

                    #Append to CSV data
                    line_data.append([api_call, attributes])
                    #print("line_data", line_data)

# Example usage:
#remove_frequent_items(onto)
mining_frequent_temporal_correlations(onto)
#verify_attribute_utility("produt_price", "ecommerce-carts") 
#add_ignored_attribute_to_file("produt_test1", "./temp/", "arm_attributes.ignore")
# teste = get_ignored_attributes_from_file("./temp/", "arm_attributes.ignore")
# if ('produt_test2' in teste):
#     print("produt_test1 está na lista")
   
print("ExtractOntoProcessView Chegou ao final com sucesso")