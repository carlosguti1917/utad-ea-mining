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
import sys  # Add missing import statement for sys module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..")))

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
9- save the result in a text file separated by tab witn the APICall and the resulting list of attributes for further processing


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

def verify_attribute_utility(attribute_name, resource_name, api_call_name, onto):
#Calcula o quanto o atributo varia em relação aos demais recursos da mesma chamada de API ou seja para APIs do mesmo nome   
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
            attibute_value = attribute_tuple[0].attribute_value[0]
            attribute_list.append((attibute_value)) 
       
        file_nm = f"api_resource_data_attribute_{attribute_name}.txt"
        file_path = './temp/'
        save_result_to_file(attribute_list, file_path, file_nm, None)
        
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
        print("In calculate_attribute_variation module :", __name__)
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
                            print(attribute_name, ":", attribute_value, ":", api_name) 
                            # calculate the the variation of attribute_values in the other resources of the same api_call.name
                            attribute_is_util = verify_attribute_utility(attribute_name, attribute_value, api_name, onto)
                            if attribute_is_util:
                                attributes.append((attribute_name, attribute_value))
                            else:
                                
                            # poderia gerar uma lista de atributos e valores a serem ignorados, ou seja, que não serão considerados na análise de correlação




    # Step 9: save the result in a text file separated by tab with the APICall and the resulting list of attributes for further processing
    #save_result_to_file(result_data, file_path, file_name)


def mining_frequent_temporal_correlations(onto):
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
                    print("line_data", line_data)

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


# Example usage:
remove_frequent_items(onto)
# mining_frequent_temporal_correlations(onto)
                 
   
print("ExtractOntoProcessView Chegou ao final com sucesso")