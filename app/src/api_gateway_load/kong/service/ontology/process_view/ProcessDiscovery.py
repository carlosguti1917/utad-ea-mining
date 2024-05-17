import pandas as pd
import re
import pickle
from owlready2 import *
import pm4py
from collections import defaultdict
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.process_tree import converter as pt_converter
import networkx as nx
import matplotlib.pyplot as plt
from pm4py.algo.discovery.log_skeleton import algorithm as log_skeleton_discovery
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
import os
import os.path
import sys # Add missing import statement for sys module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..", "..")))
from api_gateway_load import configs
from api_gateway_load.utils import onto_util

onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
#onto = get_ontology("EA Mining OntoUML Teste V1_3.owl").load()
onto = get_ontology(configs.OWL_FILE["file_name"]).load()
ns_gufo = onto.get_namespace("http://purl.org/nemo/gufo#")
ns_core = onto.get_namespace("http://eamining.edu.pt/core#")
ns_process_view = onto.get_namespace("http://eamining.edu.pt/process-view#")


# Opções:
#Obter a lista de atividades de início e fim
#start_activities = pm4py.get_start_activities(event_log, activity_key='activity a', case_id_key='case_id', timestamp_key='antecedent_request_time')
#obter as abstraçãos do processo
#print(pm4py.llm.abstract_dfg(event_log))
# Eliminar da lista de atividades de início aquelas que fizerem parte de alguma abstração cujo o início é outra start activity
# Deve sobrar duas atividades de início, que são os processos.
# Salvar cada um destes processos em um arquivo .bpmn usando 
# filtered_dataframe = pm4py.filter_start_activities(dataframe, ['Act. A'], activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
#Também é possivel filtrar pelo inicio e fim
#filtered_dataframe = pm4py.filter_between(dataframe, 'A', 'D', activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
#Uma opção é:
# dentify Cases Belonging to the Same Process:
# Use clustering algorithms (e.g., k-means) to group cases that have similar process flows.
# Calculate the similarity between process flows of different cases and group cases with high similarity.
#Filtrar pelo início e fim e top k-means

# file_path = './temp/'   
# file_nm = "ftc_list.csv"
# log_file = pd.read_csv(file_path + file_nm, sep=';')
# dataframe = pm4py.format_dataframe(log_file, case_id='case_id', activity_key='activity a', timestamp_key='antecedent_request_time')
# #imestamp format is %Y-%m-%d %H:%M:%S%z
# event_log = pm4py.convert_to_event_log(dataframe)

def get_event_log(consumer_app):
    """
        Get the event log from the ontology
        returns:
            event_log: event log
            activies_connections: list of activities ontology connections objects that has the label partner : {consumer_app}
    """
    event_log = None
    try:
        # select the activities connections from the ontology
        # TODO - filtar pelo partner
        app_name = consumer_app.name
        query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX ns_core: <http://eamining.edu.pt/core#>
            PREFIX ns_process_view: <http://eamining.edu.pt/process-view#>

            SELECT ?activity_connection
            WHERE {{
                ?activity_connection a ns_process_view:APIActivitiesConnection .
                ?activity_connection rdfs:label ?label .
                FILTER(
                    ?label = "partner: {app_name}")
            }}
        """
        activies_connections = list(default_world.sparql(query)) 
        if activies_connections is None or len(activies_connections) == 0:
            return None, None
        df_activies = pd.DataFrame(columns=['case_id', 'activity_connection', 'antecedent_activity_name', 'antecedent_request_time', 'partner_name'])
        for activity_connection_tuple in activies_connections:
            activity_connection = activity_connection_tuple[0]
            case_id = activity_connection.label[0]
            antecedent_activity = activity_connection.isEventProperPartOf[0]
            antecedent_id = antecedent_activity.name
            antecedent_activity_method = antecedent_activity.participatedIn[0].method[0]
            antecedent_activity_uri = antecedent_activity.api_uri[0]
            antecedent_activity_route = antecedent_activity.participatedIn[0].endpoint_route[0]
            partner = antecedent_activity.INVERSE_participatedIn[0]
            partner_name = partner.name
            activity_connection = activity_connection
            # antecedent_activity_route = antecedent.participatedIn[0].endpoint[0]
            # pattern = r"/v\d+/(.*)"
            # match = re.search(pattern, antecedent_activity_route)
            # if match:
            #     operation_name = match.group(1)
            #     antecedent_activity_name = antecedent_activity_method + "_" + operation_name           
            #antecedent_activity_name = antecedent_activity_method + "_" + antecedent_activity_uri            
            antecedent_activity_name = antecedent_activity_route           
            #antecedent_request_time = antecedent_activity.request_time[0].isoformat()
            antecedent_request_time = antecedent_activity.request_time[0].isoformat()
            
            #dt_activities = pm4py.format_dataframe(log_file, case_id='case_id', activity_key='activity a', timestamp_key='antecedent_request_time')                     
            
            df_activies.loc[len(df_activies)] = [case_id, activity_connection, antecedent_activity_name, antecedent_request_time, partner_name]
        
        formated_df = pm4py.format_dataframe(df_activies, case_id='case_id', activity_key='antecedent_activity_name', timestamp_key='antecedent_request_time')
        event_log = pm4py.convert_to_event_log(formated_df)
        return event_log, activies_connections
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In get_event_log module :", __name__)
        raise error

    
def processes_discovery():
    
    process_list = []
    try:
        with onto:
            consumer_apps = onto_util.get_consumer_apps()
            for consumer_app in consumer_apps:
                print(f"Process Discovery for {consumer_app.name}")
                event_log, activies_connections = get_event_log(consumer_app)
                if event_log is None or len(event_log) == 0:
                    continue
                start_activities = pm4py.get_start_activities(event_log, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')

                # remove cases with less than two activities
                start_activities = remove_isolated_activities(event_log, start_activities)
                        
                # remove not pure start activities, those that also depends on (follows) another activity
                start_activities = remove_dependent_start_activities(event_log, start_activities)
                
                if start_activities is None or len(start_activities) == 0:
                    continue
                               
                filtered_dataframe = pm4py.filter_start_activities(event_log, start_activities, retain=True, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')  
                # Iterate through each remaining start activity and filter the dataframe by the start and end activities as a separate process
                for start_activity in start_activities:
                    # calculate the similarity between the process flows of different cases and group cases with high similarity using k-means
                    top_k_value = configs.PM4PI_ARGS["TOP_K"]
                    test_k = pm4py.filter_variants_top_k(filtered_dataframe, top_k_value, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')
                    # save each process in a heuristics net
                    #heu_net = pm4py.discover_heuristics_net(test_k, dependency_threshold=0.5)
                    heu_net = pm4py.discover_heuristics_net(test_k)            
                    #pm4py.view_heuristics_net(heu_net)
                    # Save the Heuristics Net visualization to a file
                    process_name = re.match(r'(\w+)_', start_activity).group(1) + " " + re.search(r'.*/([^/]+)$', start_activity).group(1)
                    directory = "./temp/process/"
                    os.makedirs(directory, exist_ok=True)
                    pm4py.save_vis_heuristics_net(heu_net, f"{directory}heuristics_net_{process_name}.png")
                    with open(f"{directory}heuristics_net_{process_name}.pkl", 'wb') as f:
                        pickle.dump(heu_net, f)               
                    # Save the start_activity as process and create the hostorical dependency with the activies
                    process_list.append(add_process_to_ontology(process_name, start_activity, test_k))
                
                # Save the ontology
                print(f"Closing Process Discovery for {consumer_app.name}")
                sync_reasoner()
                onto.save()
    
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In processes_discovery module :", __name__)
        raise error        


def add_process_to_ontology(process_name, start_activity, process_variant_log):
    # Create the process in the ontology and relate to the activities connections dependencies
    process = None
    try:
        with onto:
            # Create the process
            #TODO verificar antes de o processo já não existe, neste caso, só atualziar o label partner
            process = onto_util.get_individual(onto, ns_process_view.Process, "http://eamining.edu.pt/", process_name)
            if process is None:
                process = ns_process_view.Process()
                process.label.append(f"{process_name}")
                process.name = process_name
                #process.isPartOf.append(ns_process_view.ProcessView)
                process.label.append(f"start_activity: {start_activity}")
                #process.label.append(f"Partner: {}")
            
            #iterate through the process_variant_log and for each activity get the corresponding activity connection in activies_connections. 
            #TODO - Aqui tá esquisito, parece estar mistrurando os consumers.          
            for case in process_variant_log:
                for event in case:
                    activity_name = event['concept:name']
                    #antecedent_actitivy_id = event['antecedent_id']
                    activity_connection = event['activity_connection']
                    activity_connection.historicallyDependsOn.append(process)
                    partner_name = event['partner_name']
                    label = f"partner: {partner_name}"
                    if label not in process.label:
                        process.label.append(label)  
                          
        return process
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In save_process_into_ontology module :", __name__)
        raise error       
        
def remove_isolated_activities(event_log, start_activities):
    """
        Remove start activities that are part of another start activity
        args:
            start_activities: list of start activities
    """
    try:

        isolated_start_activities = start_activities    
        activity_counts = defaultdict(int)
        dfg = dfg_discovery.apply(event_log)
        # Check activity in other flows
        next_source = None
        #start_activity = None
        for source, target in dfg.items():
            # Create a dictionary to store the count of activities for each start activity
            print(f"{source[0]} -> {source[1]}")
            if next_source is None and source[0] in start_activities:
                start_activity = source[0]
                activity_counts[start_activity] += 1
                next_source = source[1]
            elif source[0] == next_source:
                activity_counts[start_activity] += 1
                next_source = source[1]
            elif source[0] in start_activities:
                print(f"Activity counts: {len(activity_counts)}")
                start_activity = source[0]
                activity_counts[start_activity] += 1                    
                next_source = source[1]
                
        for activity, count in activity_counts.items():
            print(f"Activity: {activity}, Count: {count}")
            if count < 3:
                isolated_start_activities.pop(activity)
                print(f"Activity: {activity} removed")
                    
        return isolated_start_activities
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In remove_isolated_activies module :", __name__)
        raise error   

def remove_dependent_start_activities(event_log, start_activities):
    """
        Remove start activities that follows another start activity
        args:
            start_activities: list of start activities
    """
    try:
        dfg = dfg_discovery.apply(event_log)
        activity_to_remove = []
        start_activities_in_start_path = []
        for start_activity in start_activities:
            print(f"Start Activity: {start_activity}")  
            for source, target in dfg.items():
                count_aux_path = 0            
                if source[0] != start_activity:
                    continue                    
                for source_aux, target_aux in dfg.items():
                    count_aux_path += 1
                    if count_aux_path > 2:
                        break                    
                    if source[0] == source_aux[1] and source_aux[1] in start_activities: 
                        print(f"count_aux_path: {count_aux_path}")
                        if count_aux_path == 2:
                            activity_to_remove.append(source[0])
                            print(f"removing start activity: {source[0]}")

        for activity in activity_to_remove:
            start_activities.pop(activity)
                   
        return start_activities
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In remove_isolated_activies module :", __name__)
        raise error    
        

if __name__ == "__main__":
    processes_discovery()    