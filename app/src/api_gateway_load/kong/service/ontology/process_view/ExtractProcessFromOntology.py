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
from api_gateway_load import configs
from api_gateway_load.utils import spmf_converter
from api_gateway_load.utils import onto_util

onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
onto = get_ontology(configs.OWL_FILE["file_name"]).load()
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
                
   
def record_frequent_items_to_ignore(onto):
    #record the attributes that are frequent in the resources of the API calls in files for further processing of mining.
    #TODO Talvez dê para simplificar buscando direto a lista de atributos.
    # Poderia obter a lista distinta de nomes de atributos
    # com a lista de nomes, buscar todos os atributos com o mesmo nome
    # Mas ainda tem que agrupar pelo nome do recurso, pois o atributo pode ser comum em diferentes recursos de uma API
    # por outro lado, os recursos devem estar agrupados por API, pois talvez dois recursos em APIs diferentes possam ter o mesmo nome
    # Não consegui resolver nos testes :-(
    
    try:
        #clean temp folder
        onto_util.clean_all_files('./temp/')
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
                            api_resource_name = api_resource.resource_name[0]
                            attributes = []
                            for attribute in api_resource.resource_data:
                                attribute_name = attribute.attribute_name[0]
                                attribute_value = attribute.attribute_value[0]
                                api_name = api_call.api_name[0]
                                #freq_attr_file_name = "frequent_attributes.ignore"
                                # verify it the attribute sould be ignored
                                if attribute_name in onto_util.get_ignored_attributes_from_file('./temp/', api_name):
                                    continue
                                # calculate the the variation of attribute_values in the other resources of the same api_call.name and with the same resource name
                                attribute_is_util = verify_attribute_utility(attribute_name, api_resource_name, api_name)
                                if attribute_is_util:
                                    attributes.append((attribute_name, attribute_value))
                                    #TODO registrar na ontologia resouce_equality . Algo como api_resource.AttributesEquality.append(attribute_name)
                                    # Mas tem uma questão na ontologia, pois quem é o primeiro recursou que vai ser comparado com os demais?
                                else:
                                    onto_util.add_ignored_attribute_to_file(attribute_name, './temp/', api_name)
                                    
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In remove_frequent_items module :", __name__)
        raise error



def verify_attribute_utility(attribute_name, resource_name, api_call_name):
#Verifica se atributo é útil. Um atributo é útil se ele é raro, ou seja, se ele é um atributo que não é comum em todas instancias dos recursos de mesmo nome de uma API.	
    util = False
    try:
        query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ns_core: <http://eamining.edu.pt/core#>
            PREFIX attr2: <attribute:>
            PREFIX aPIC: <aPICall:>
            PREFIX gufo: <http://purl.org/nemo/gufo#>
            PREFIX aPIR: <aPIResource:> 

            SELECT ?attribute 
            WHERE {{         
                ?resource rdf:type ns_core:APIResource .
                ?resource aPIR:resource_name ?resource_name .
                ?resource aPIR:resource_data ?resource_data .
                ?attribute <attribute:attribute_name> ?attribute_name .
                ?resource_data <attribute:attribute_name> ?attribute_name .
                FILTER(?resource_name = "{resource_name}" && ?attribute_name = "{attribute_name}")          
            }}
            """
            #TODO não consegui filtar por api_call_name, pois o recurso não tem a relação com a api_call, mas sim com a operação executada.
            # observe que pode haver duas apis com os memos nomes de recursos e atributos, embora no teste controlado não vá ocorrer. Mas precisa ser resolvido
                   
        attributes = list(default_world.sparql(query))
        # for calculate the weight of each attribute_value in the whole attributes collection.
        
        attribute_value_list = []
        for attribute_tuple in attributes:
            attribute_value_list.append((attribute_tuple[0].attribute_value[0])) 
       
        file_nm = f"api_resource_data_attribute_{attribute_name}.txt"
        file_path = './temp/'
        if  onto_util.file_exists(file_path, file_nm):
            #means that the file with the list of all values for the attibute_name already exists
            # Read the output file line by line. If any pattern is found, then the attribute is considered useful
            output_file_nm = f"api_resource_data_attribute_{attribute_name}.out"  
            output_file_full_name = os.path.join(file_path, output_file_nm)
            outFile = open(output_file_full_name,'r', encoding='utf-8')
            for string in outFile:
                #print(string)
                util = True
                break
            outFile.close()             
        else:
            #save the list of attibutes values in a file to be processed by the SPMF 
            onto_util.save_result_to_file(attribute_value_list, file_path, file_nm, None)
            #check the type of the attributes of the attribute_list
            has_attribute_types = []
            for attribute_value in attribute_value_list:
                if attribute_value == 'null':
                    has_attribute_types.append("null")
                else:
                    try:
                        # Try converting the value to an integer, if works, then it is a number
                        value = int(attribute_value)
                    except ValueError:
                        try:
                            # If conversion to int fails, try converting to float, if does not work, then tranform to integer
                            value = float(attribute_value)
                            has_attribute_types.append("float") 
                        except ValueError:
                            # If conversion to int and float fails, then it is a string 
                            has_attribute_types.append("text")                   
            
            ## if the attribute is text, then we need to convert it to a number
            if "null" in has_attribute_types:
                converter = spmf_converter.SPMFConverter()
                file_nm = converter.convert_nulls_to_number_items(file_path, file_nm)
            if "float" in has_attribute_types:
                converter = spmf_converter.SPMFConverter()
                file_nm = converter.convert_floats_to_number_items(file_path, file_nm)
            if "text" in has_attribute_types:
                converter = spmf_converter.SPMFConverter()
                file_nm = converter.convert_text_to_identified_items(file_path, file_nm)

                
            # Mining Perfectly Rare Itemsets Using The AprioriInverse Algorithm (SPMF Documentation) https://www.philippe-fournier-viger.com/spmf/AprioriInverse.php       
            # spmf = Spmf("AprioriInverse", input_file_path="./file_nm",
            #             output_file_path="output.txt", 
            #             spmf_jar_location_dir="./spmf.jar")

            #smpfa = Spmf(spmf_bin_location_dir="c:/gitHub/utad/utad-ea-mining/app/src/studies/spmf/spmf.jar",
            input_file_full_name = os.path.join(file_path, file_nm)
            output_file_nm = f"api_resource_data_attribute_{attribute_name}.out"
            output_file_full_name = os.path.join(file_path, output_file_nm)
            minsup = configs.APRIORI_INVERSE_ARGS["MIM_SUPPORT"]
            maxsup = configs.APRIORI_INVERSE_ARGS["MAX_SUPPORT"]
            smpfa = Spmf(spmf_bin_location_dir="c:/gitHub/utad/utad-ea-mining/app/src/studies/spmf",
                        algorithm_name="AprioriInverse", 
                        input_filename=input_file_full_name,
                        output_filename=output_file_full_name, 
                        arguments=[minsup, maxsup]) # to test with small set of data use 0.00, 0.5. 1 = element present in all transactions
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
        local_idenfication = f"verify_attribute_utility({attribute_name}, {resource_name}, {api_call_name}) :"
        print(local_idenfication, __name__)
        raise error


def save_ftc_to_preprocessing_file(ftc_list):
    #save the ftc_list to a file
    new_ftc_event_list = []
    #df = pd.Series(columns=['ftc_id', 'ftc_antedecent_timestamp', 'ftc_consequent_timestamp'])
    #df2 = pd.DataFrame(ftc_list)
    
    df = pd.DataFrame(columns=['correlation_id', 'antecedent_id', 'antecedent_activity_name', 'antecedent_request_time','consequent_id', 'consequent_response_time'])
    
    try:
        for ftc in ftc_list:
            ftc_id = ftc._name
            antecedent = ftc.mediates[0]
            antecedent_id = antecedent.name
            antecedent_activity_method = antecedent.participatedIn[0].method[0]
            antecedent_activity_uri = antecedent.api_uri[0]
            antecedent_activity_name = antecedent_activity_method + "_" + antecedent_activity_uri
            # antecedent_activity_route = antecedent.participatedIn[0].endpoint[0]
            # pattern = r"/v\d+/(.*)"
            # match = re.search(pattern, antecedent_activity_route)
            # if match:
            #     operation_name = match.group(1)
            #     antecedent_activity_name = antecedent_activity_method + "_" + operation_name
            antecedent_request_time = antecedent.request_time[0].isoformat()
            consequent = ftc.mediates[1]
            consequent_id = consequent.name
            consequent_request_time = consequent.request_time[0].isoformat()
            
            df.loc[len(df)] = [ftc_id, antecedent_id, antecedent_activity_name, antecedent_request_time, consequent_id, consequent_request_time]
               
        file_path = configs.TEMP_PROCESSING_FILES["file_path"]
        file_nm = configs.TEMP_PROCESSING_FILES["file_ftc_list_name"]
        # Save the Series to a CSV file
        if os.path.isfile(file_path + file_nm):
            os.remove(file_path + file_nm)
        df.to_csv(file_path + file_nm, index=False)
        #header = not os.path.isfile(file_path + file_nm)
        #df.to_csv(file_path + file_nm, mode='a', index=False, header=header) #If the file does exist, header is set to False so that the header will not be written again when the new data is appended.
     
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In save_ftc_to_file module :", __name__)
        raise error
    
def add_frequent_temporal_correlation(onto, correlation_list, ftc_list):      
    """
    calc the temporal dependency between api_call and inner_api_call based on the request_
    record the younger as Antecedent Activity and the older as Consequent Activity
    create the historicalDependsOn relation between the two activities
    create the relator Frequente Temporal Correlation (FTC) between the two activities
    create the mediation between the FTC do each of Activities
    record the attributes that are correlated in the api_correlations to reapeated_attributes in FTC
    args: 
        onto: the ontology
        api_call_a: the first api_call
        api_call_b: the second api_call
        correlation_list: the list of cleaned correlated attributes
            correlation_list structure([0-correlation_key, 1-api_call_a, 2-operation_a_label, 3-attribute_a, 
                                        4-api_call_b, 5-operation_b_label, 6-attribute_b]) 
    """

    # calc the temporal dependency between api_call and inner_api_call based on the property request_time of the api_call
    # record the younger as API Antecedent Activity and the older as API Consequent Activity in the ontology onto
    # create the historicalDependsOn relation between the API Antecedent Activity and the API Consequent Activity
    # create the relator Frequente Temporal Correlation and create the property mediates between this relator to the API Antecedent Activity and to the API Consequent Activity
    # record the attributes that are correlated in the correlated_attributes to reapeated_attributes in the created Frequente Temporal Correlation
    
    ftc = None
    new_ftc = False
    api_call_a = correlation_list[1]
    api_call_b = correlation_list[4]
       
    with onto:
    #     if api_call_a.api_uri != api_call_b.api_uri:
        if api_call_a.api_uri != api_call_b.api_uri:
            try:
                #verify FrequentTemporalCorrelation already exists, if not create it
                for e in ftc_list:
                    if e.mediates[0] == api_call_a and e.mediates[1] == api_call_b:
                        ftc = e
                        api_antecedent_activity = ftc.mediates[0]
                        api_consequent_activity = ftc.mediates[1]
                        break
                if ftc is None:                       
                    # Create the relator Frequente Temporal Correlation
                    ftc = ns_process_view.FrequentTemporalCorrelation()
                    new_ftc = True
                    
                    if api_call_a.request_time < api_call_b.request_time:   
                        api_antecedent_activity = ns_process_view.APIAntecedentActivity(api_call_a.name)
                        api_antecedent_activity.equivalent_to.append(api_call_a)
                        api_consequent_activity = ns_process_view.APIConsequentActivity(api_call_b.name)
                        api_consequent_activity.equivalent_to.append(api_call_b)
                    else:
                        print("This code in if ftc is not None: should not be executed")                                     
                
                    # Get the Consumer App related to api_call_a based on the inverse participatedIn property
                    cls_consumer_app = ns_core.ConsumerApp
                    cls_partner = ns_process_view.Partner
                    #consumer_app = api_call_a.INVERSE_participatedIn[0]
                    inverse_participations_a = api_call_a.INVERSE_participatedIn
                    inverse_participations_b = api_call_b.INVERSE_participatedIn
                    for inverse_participation_a in inverse_participations_a:
                        if cls_partner in inverse_participation_a.is_a or cls_consumer_app in inverse_participation_a.is_a:
                            consumer_app_a = inverse_participation_a
                        else:
                            continue
                        
                        for inverse_participation_b in inverse_participations_b:
                            if cls_partner in inverse_participation_b.is_a or cls_consumer_app in inverse_participation_b.is_a:
                                consumer_app_b = inverse_participation_b
                            else:
                                continue
                            
                            if consumer_app_a == consumer_app_b:
                                #verify if the partner is already exists and is related the antecedent activity and consequent activity
                                if consumer_app_a not in api_antecedent_activity.participatedIn and consumer_app_a not in api_consequent_activity.participatedIn:
                                    partner = onto_util.get_individual(onto, ns_process_view.Partner, "http://eamining.edu.pt/", consumer_app_a._name)
                                    if partner is None:
                                        partner = ns_process_view.Partner(consumer_app_a._name)
                                        partner.equivalent_to.append(consumer_app_a)
                                        partner.participatedIn.append(api_antecedent_activity)
                                        partner.participatedIn.append(api_consequent_activity) 

                            # Just checking if the attributes values are the same
                            if correlation_list[3].attribute_value[0] != correlation_list[6].attribute_value[0]:
                                continue

                            # Create the temporal dependency between the API Antecedent Activity and the API Consequent Activity
                            api_consequent_activity.historicallyDependsOn.append(api_antecedent_activity)
                                                
                            # Create the property mediates between the Frequente Temporal Correlation and the API Antecedent Activity
                            ftc.mediates.append(api_antecedent_activity)
                            ftc.mediates.append(api_consequent_activity)
                            
                    # Record the attributes that are correlated in the correlated_attributes to repeated_attributes in the created Frequente Temporal Correlation
                    #for attributes in correlation_list:
                        #verify the attribute order. If attribute[0] is from api_call_a, then it is the Antecedent Activity (attribute_name_a), otherwise it is the Consequent Activity (attribute_name_b)                                            
                    if api_antecedent_activity.name == api_call_a.name:
                        attribute_a = correlation_list[3]
                        attribute_b = correlation_list[6]
                    else:
                        attribute_a = correlation_list[6]
                        attribute_b = correlation_list[3]
                        
                    # Create the attribute pair
                    attribute_pair = ns_core.AttributePair()
                    attribute_pair.attribute_a.append(attribute_a)
                    attribute_pair.attribute_b.append(attribute_b)                          
                    # Add the attribute pair to the repeated_attributes property of the Frequente Temporal Correlation
                    ftc.repeated_attributes.append(attribute_pair)

                    if new_ftc:
                        ftc_list.append(ftc)
                    print(f"ftc_name {ftc.name} e.mediates[0]= {ftc.mediates[0].api_uri[0]} e.mediates[1]= {ftc.mediates[1].api_uri[0]} partner= {partner.name}")
                return ftc_list                     
            except Exception as error:
                print('Ocorreu problema {} '.format(error.__class__))
                print("mensagem", str(error))
                print(f"In save_frequent_temporal_correlation({api_call_a}, {api_call_b}) :", __name__)        
                raise error     

                    
def save_frequent_temporal_correlation(onto, api_call_a, api_call_b, correlated_attributes):      
    """
    calc the temporal dependency between api_call and inner_api_call based on the request_
    record the younger as Antecedent Activity and the older as Consequent Activity
    create the historicalDependsOn relation between the two activities
    create the relator Frequente Temporal Correlation (FTC) between the two activities
    create the mediation between the FTC do each of Activities
    record the attributes that are correlated in the api_correlations to reapeated_attributes in FTC
    """
    
    with onto:
        if api_call_a.api_uri != api_call_b.api_uri:
            try:
                #sync_reasoner()
                if api_call_a.request_time < api_call_b.request_time:   
                    api_antecedent_activity = ns_process_view.APIAntecedentActivity(api_call_a.name)
                    api_antecedent_activity.equivalent_to.append(api_call_a)
                    api_consequent_activity = ns_process_view.APIConsequentActivity(api_call_b.name)
                    api_consequent_activity.equivalent_to.append(api_call_b)
                else:
                    api_antecedent_activity = ns_process_view.APIAntecedentActivity(api_call_b.name)
                    api_antecedent_activity.equivalent_to.append(api_call_b)
                    api_consequent_activity = ns_process_view.APIAntecedentActivity(api_call_a.name)
                    api_consequent_activity.equivalent_to.append(api_call_a)
                    

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
                                    partner = onto_util.get_individual(onto, ns_process_view.Partner, "http://eamining.edu.pt/", consumer_app_a._name)
                                    if partner is None:
                                        partner = ns_process_view.Partner(consumer_app_a._name)
                                        partner.equivalent_to.append(consumer_app_a)
                                        partner.participatedIn.append(api_antecedent_activity)
                                        partner.participatedIn.append(api_consequent_activity) 

                    # Create the relator Frequente Temporal Correlation
                    ftc = ns_process_view.FrequentTemporalCorrelation()
                                       
                    # Create the temporal dependency between the API Antecedent Activity and the API Consequent Activity
                    api_consequent_activity.historicallyDependsOn.append(api_antecedent_activity)
                                        
                    # Create the property mediates between the Frequente Temporal Correlation and the API Antecedent Activity
                    ftc.mediates.append(api_antecedent_activity)
                    ftc.mediates.append(api_consequent_activity)
                    
                    # Record the attributes that are correlated in the correlated_attributes to repeated_attributes in the created Frequente Temporal Correlation
                    for attribute in correlated_attributes:
                        #verify the attribute order. If attribute[0] is from api_call_a, then it is the Antecedent Activity (attribute_name_a), otherwise it is the Consequent Activity (attribute_name_b)
                        if attribute[0] == api_call_a.api_name:
                            attribute_a = attribute[2]
                            attribute_b = attribute[3]
                        else:
                            attribute_a = attribute[3]
                            attribute_b = attribute[2]
                            
                        if attribute_a.attribute_value[0] != attribute_b.attribute_value[0]:
                            continue
                        # Create the attribute pair
                        attribute_pair = ns_core.AttributePair()
                        attribute_pair.attribute_a.append(attribute_a)
                        attribute_pair.attribute_b.append(attribute_b)                          
                        # Add the attribute pair to the repeated_attributes property of the Frequente Temporal Correlation
                        ftc.repeated_attributes.append(attribute_pair)
                          
                return ftc
            
            except Exception as error:
                print('Ocorreu problema {} '.format(error.__class__))
                print("mensagem", str(error))
                print(f"In save_frequent_temporal_correlation({api_call_a}, {api_call_b}) :", __name__)        
                raise error     
                 

def mining_activities_connection(onto, ftc_list, selected_transactions):
    # the goas is to find the activities that are creat a chain of activities that are connected by the same api_name and attributes
    # Scan the Frequent Temporal Correlations (FTC) and check que antecedent and consequent activities
    # the candidates are those that have the same api_name and APIOperation and the atecedent request_time and consequent request_time have no other activities between them
    # at least one attribute name of the attribute pair should be present in all individuals of the FTC with the same antecedent and consequent activities api_name and APIOperation
    # Select the antecedent to be part isEventProperPartOf the APIActivitiesConnection, thus it is exclusive. Use the same logic to the consequent
    # Select the consequent to be part isEventProperPartOf the APIActivitiesConnection
    # Order the FTC based on that the antecedent is the younger and the consequent is the older and the consequent is the same of the antecedent of the next FTC
    # the consequent of the next FTC should not have the same api_name and APIOperation that already exists in the APIActivietiesConnection chain as API Consequent Activity or API Antecedent Activity
    # the antecedent of the next FTC should not have the same api_name and APIOperation that already exists in the APIActivietiesConnection as API Antecedent Activity
    # generate the smpf file to be processed by the ARM
    # algorithm to find the frequent sequences

    try:
        ftc = None
        new_actitivities = False
        activities_list = []
        with onto:
            for index, row in selected_transactions.iterrows():
                # Get the Frequent Temporal Correlations in ftc_list that have an identifier in selected_transactions
                correlation_id = row['correlation_id']
                ftcs = [ftc for ftc in ftc_list if ftc.name == correlation_id]
                for ftc in ftcs:
                    antecedent = ftc.mediates[0]
                    consequent = ftc.mediates[1]
                    case_id = row['case_id']
                    #activity = ns_process_view.APIActivitiesConnection(name=f"{correlation_id}_{case_id}")                    
                    activity = ns_process_view.APIActivitiesConnection()
                    activity.name = f"{correlation_id}_case_id{case_id}"
                    activity.label.append(f"case_id : {case_id}")
                    activity.label.append(f"connection: {correlation_id}_{case_id}")
                    antecedent_endpoint_route = antecedent.participatedIn[0].endpoint_route[0]
                    consequent_endpoint_route = consequent.participatedIn[0].endpoint_route[0]
                    activity.label.append(f"references antecedent operation: {antecedent_endpoint_route} consequent: {consequent_endpoint_route} partner: {antecedent.INVERSE_participatedIn[0]}")
                    partner = antecedent.INVERSE_participatedIn[0]
                    partner_name = partner.name
                    activity.label.append(f"partner: {partner_name}")
                    activity.isEventProperPartOf.append(antecedent)
                    activity.isEventProperPartOf.append(consequent)
                    activities_list.append(activity)
                    new_actitivities = True
                    #print(f"activity: {activity.name} antecedent_id: {antecedent.api_uri[0]} consequent_id: {consequent.api_uri[0]} case_id: {case_id} partner: {antecedent.INVERSE_participatedIn[0]}")
                    
                # if new_actitivities:
                #     ftc_list.append(ftc)        
                                   
        return ftc_list, activities_list #return the ftc_list with the activities connections uptated 

    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In remove_frequent_items module :", __name__)
        raise error       

def mining_frequent_temporal_correlations(onto):
    """
        idenfity the frequent temporal correlations between two sequential API calls
        identigy API Activites Connections and save them into the ontology
    """
    ftc_list = []
    unified_ftc_list = []
    api_resource_correlations = []
    # Find all ConsumerApp 
    #consumer_apps = [individual for individual in onto.individuals() if individual.is_a[0] == ns_core.ConsumerApp]  
    query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX ns_core: <http://eamining.edu.pt/core#>
            PREFIX ns_process_view: <http://eamining.edu.pt/process-view#>

            SELECT DISTINCT ?consumerApp
            WHERE {
                ?consumerApp rdf:type ns_core:ConsumerApp .
                FILTER NOT EXISTS {
                    ?subclass rdf:type ns_process_view:Partner .
                    ?subclass rdfs:subClassOf ?consumerApp .
                    FILTER (?subclass != ?consumerApp)
                }
            }
        """
    consumer_apps = list(default_world.sparql(query))      
    try:
        # before start the mining, chech the ontology consistency
        #sync_reasoner()    
        for consumer_app_tuple in consumer_apps:
            consumer_app = consumer_app_tuple[0]
            
            if consumer_app.name == 'Partner':
                continue

            # Find API Calls associated with ConsumerApp and sort them by request_time
            api_calls = sorted(list(consumer_app.participatedIn), key=lambda x: x.request_time)
            conta_api_calls = len(api_calls)
            conta_api_call = 0
            ftc_list = []
            api_resource_correlations = []
            selected_attribute_pairs = []
            selected_api_res_corrls = []
            for api_call in api_calls:
                # Inicialize the variables api_call_resource and api_call_operation
                api_call_resource = None
                api_call_operation = None
                conta_api_call += 1
                # if conta_api_call == 3: # for testing purposes
                #     break
                # Ensuring that only instancs of API_Call
                if not ns_core.APICall in api_call.is_a:
                    continue 

                # get the modified resources of the api_call
                query_a = f"""
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX owl: <http://www.w3.org/2002/07/owl#>
                        PREFIX gufo: <http://purl.org/nemo/gufo#>
                        PREFIX ns_core: <http://eamining.edu.pt/core#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                        PREFIX aPIO: <aPIOperation:>

                        SELECT distinct ?resource ?operation
                        WHERE {{
                            ?operation a ns_core:APIOperation . 
                            ?operation ^gufo:participatedIn ?api_call .
                            ?api_call a ns_core:APICall .
                            ?operation ^gufo:mediates ?operationExecuted .
                            ?operationExecuted a ns_core:OperationExecuted .
                            ?operationExecuted gufo:mediates ?resource .
                            ?resource gufo:participatedIn ?api_call .
                            ?resource a ns_core:APIResource . 
                            FILTER(
                                IRI(?api_call) = <{api_call.iri}>
                            )
                        }}                    
                    """                       
                # Execute the query_a
                #api_call_resources = list(default_world.sparql(query_a))
                query_a_result = list(default_world.sparql(query_a))
                for result in query_a_result:
                    api_call_resource = result[0]  # Get the individual from the tuple of resources
                    api_call_operation = result[1]  # Get the individual from the tuple of operations
                
                if api_call_operation is None:
                    print(f"the APICall {api_call} does not have api_call_operation")
                    continue
                
                # search in other API calls and resources to correlate
                #inner_api_calls = sorted(list([inner_api_call for inner_api_call in consumer_app.participatedIn if inner_api_call.request_time > api_call.request_time]), key=lambda x: x.request_time)
                
                call_req_time  = api_call.request_time[0].isoformat()
                query_inner_call = f"""
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX owl: <http://www.w3.org/2002/07/owl#>
                        PREFIX gufo: <http://purl.org/nemo/gufo#>
                        PREFIX ns_core: <http://eamining.edu.pt/core#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                        PREFIX aPIC: <aPICall:>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                        SELECT distinct ?api_call
                        WHERE {{
                            ?api_call a ns_core:APICall .
                            ?api_call aPIC:request_time ?request_time.
                            ?consummer_app gufo:participatedIn ?api_call .
                            ?consummer_app a ns_core:ConsumerApp .
                            FILTER(
                                IRI(?consummer_app) = <{consumer_app.iri}>  
                                && ?request_time > '{call_req_time}'^^xsd:dateTime
                            )          
                        }}  
                        order by ?request_time                  
                    """     
                            
                # Execute the query_query_inner_call               
                inner_api_calls = list(default_world.sparql(query_inner_call))
                
                conta_inner_api_calls = len(inner_api_calls)
                conta_inner_api_call = 0
                for tuplas in inner_api_calls:
                    inner_api_call = tuplas[0]
                    inner_api_call_resource = None
                    inner_api_call_operation = None
                    
                    conta_inner_api_call += 1
                    # if conta_inner_api_call == 2:
                    #     break
                    print(f"conta_api_call app {consumer_app.name} call: {conta_api_call} de {conta_api_calls} -> conta_inner_api_call: {conta_inner_api_call}  de {conta_inner_api_calls}")
                    # if API Calls have the same api_uri, then ignore it, because we need only one to build the sequence, even in case of call back.
                    
                    # Ensuring that only instances of API_Call is keeped
                    if not ns_core.APICall in inner_api_call.is_a:
                        continue 
                    
                    if api_call.api_uri[0] == inner_api_call.api_uri[0]:
                        continue                        
                    # Cada chamada tem uma operação que modifica um recurso
                    # obter as duas operações
                    # obter os recursos modificados através do relator operationExecuted
                    # obter os atributos dos recursos
                    # comparar os atributos dos recursos evitando os atributos frequentes  
                    
                    # get the modified resources of the inner_api_call
                    query_i = f"""
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX gufo: <http://purl.org/nemo/gufo#>
                            PREFIX ns_core: <http://eamining.edu.pt/core#>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                            PREFIX aPIO: <aPIOperation:>

                        SELECT distinct ?resource ?operation
                        WHERE {{
                            ?operation a ns_core:APIOperation . 
                            ?operation ^gufo:participatedIn ?api_call .
                            ?api_call a ns_core:APICall .
                            ?operation ^gufo:mediates ?operationExecuted .
                            ?operationExecuted a ns_core:OperationExecuted .
                            ?operationExecuted gufo:mediates ?resource .
                            ?resource gufo:participatedIn ?api_call .
                            ?resource a ns_core:APIResource . 
                                FILTER(
                                    IRI(?api_call) = <{inner_api_call.iri}>
                                )
                            }}                    
                        """               

                    query_i_result = list(default_world.sparql(query_i))
                    for result_i in query_i_result:
                        inner_api_call_resource = result_i[0]  # Get the individual from the tuple of resources
                        inner_api_call_operation = result_i[1]  # Get the individual from the tuple of operations                        
                        #inner_api_call_resources = list(default_world.sparql(query_i))                          
                    
                    # If the operations are equals, then ignore it
                    if inner_api_call_operation is None:
                        print(f"the inner_api_call_operation APICall {inner_api_call} does not have api_call_operation")
                        continue

                    if api_call_operation.label[0] == inner_api_call_operation.label[0]:
                        continue 
                                                                
                    #check the correlation between the attributes of the resources:
                    corr = onto_util.get_api_resources_correlations(api_call, api_call_resource, inner_api_call, inner_api_call_resource)
                    if corr is not None and len(corr) > 0:
                        api_resource_correlations.append(corr)
                    else:
                        continue
                        #ftc_list.append(save_frequent_temporal_correlation(onto, api_call, inner_api_call, api_resource_correlations))
         
            # for each ConsumerApp save the ontology with the ftc_list
            # check if the correlations are consistent before saving the ontology. This measure how much de correlation repeated in the resources of the api_call
            # Only the correlation weight with 100% is saved on the repeated_attributes property of the ftc
            #sorted_api_resource_correlations = sorted(api_resource_correlations, key=lambda x: key_func(x))                      
            
            #Feature Selection to get the selection of correlations based on its attributes weight
            selected_attribute_pairs = onto_util.attribute_pairs_selection(api_resource_correlations)
            
            #Select the api_resource_correlations that have the selected_attribute_pairs
            selected_api_res_corrls = onto_util.resource_correlations_selection(api_resource_correlations, selected_attribute_pairs)
            
            #add ftc
            for selected_corr in selected_api_res_corrls:
                ftc_list = add_frequent_temporal_correlation(onto, selected_corr, ftc_list)
           
            # print(f"ftc_list: {len(ftc_list)}")
          
            try:                
                #check de ontology consistency and save the ontology             
                if len(ftc_list) > 0:
                    #sync_reasoner()
                    save_ftc_to_preprocessing_file(ftc_list)
                    file_path = configs.TEMP_PROCESSING_FILES["file_path"]
                    file_name = configs.TEMP_PROCESSING_FILES["file_ftc_list_name"]
                    #select the candidates to activities connections and save file_ftc_list_cleaned.csv
                    selected_transactions = onto_util.event_transactions_selection(file_path, file_name) 
                    #minint activities connections from selected_transactions e saving the ontology
                    ftc_list, activities_list = mining_activities_connection(onto, ftc_list, selected_transactions) 
                    print(f"activites_list len  : {len(activities_list)}")
                    unified_ftc_list.extend(ftc_list)
                sync_reasoner()
                onto.save(format="rdfxml")
            except RecursionError as error:
                print(f"RecursionError for entity: {error}")
                return str(error)   
            except Exception as error:
                inconsistent_cls_list = list(default_world.inconsistent_classes())
                for il in inconsistent_cls_list:
                    print(il)
                    print('inconsistency_list', il)                                                 
                print('Ocorreu problema {} '.format(error.__class__))
                print("mensagem", str(error))
                print("In extractAPIConcepts module :", __name__)  
                raise Exception(f"Ontology inconsistency found: {il}")                 
        return unified_ftc_list                         
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In mining_frequent_temporal_correlations() :", __name__)        
        raise error 
    
def mining_processes(onto):   
    # opem the smpf file with the frequent sequences
    # Apply the ARM algorithm to find the frequent sequences
    # select the longest sequences of activities 
    # each of the longest exclusive sequences of activities is a process, that is recorded in the ontology as a ProcessView.Process.
    # Create a Archimate XML file with the processes and the activities
    # save the archimate file
    pass
    

def key_func(x):
    value = x[1][0]
    print(value)
    return value