import pandas as pd
import re
import pickle
from owlready2 import *
import pm4py
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

def get_event_log():
    """
        Get the event log from the ontology
        returns:
            event_log: event log
            activies_connections: list of activities ontology connections objects
    """
    event_log = None
    try:
        # select the activities connections from the ontology
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                PREFIX ns_core: <http://eamining.edu.pt/core#>
                PREFIX ns_process_view: <http://eamining.edu.pt/process-view#>

                SELECT ?activity_connection
                WHERE {
                    ?activity_connection a ns_process_view:APIActivitiesConnection .
                }
        """
        activies_connections = list(default_world.sparql(query)) 
        df_activies = pd.DataFrame(columns=['case_id', 'activity_connection', 'antecedent_activity_name', 'antecedent_request_time'])
        for activity_connection_tuple in activies_connections:
            activity_connection = activity_connection_tuple[0]
            case_id = activity_connection.label[0]
            antecedent_activity = activity_connection.isEventProperPartOf[0]
            antecedent_id = antecedent_activity.name
            antecedent_activity_method = antecedent_activity.participatedIn[0].method[0]
            antecedent_activity_uri = antecedent_activity.api_uri[0]
            activity_connection = activity_connection
            # antecedent_activity_route = antecedent.participatedIn[0].endpoint[0]
            # pattern = r"/v\d+/(.*)"
            # match = re.search(pattern, antecedent_activity_route)
            # if match:
            #     operation_name = match.group(1)
            #     antecedent_activity_name = antecedent_activity_method + "_" + operation_name           
            antecedent_activity_name = antecedent_activity_method + "_" + antecedent_activity_uri            
            #antecedent_request_time = antecedent_activity.request_time[0].isoformat()
            antecedent_request_time = antecedent_activity.request_time[0].isoformat()
            
            #dt_activities = pm4py.format_dataframe(log_file, case_id='case_id', activity_key='activity a', timestamp_key='antecedent_request_time')                     
            
            df_activies.loc[len(df_activies)] = [case_id, activity_connection, antecedent_activity_name, antecedent_request_time]
        
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
            event_log, activies_connections = get_event_log()
            start_activities = pm4py.get_start_activities(event_log, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')
            #end_activities = pm4py.get_end_activities(event_log, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time') 

            # remove cases with less than two activities
            start_activities = remove_isolated_activies(event_log, start_activities)
                    
            # remove not pure start activities, those that are also part of another flow started by other activity
            start_activities = remove_not_pure_start_activies(event_log, start_activities)
            
            filtered_dataframe = pm4py.filter_start_activities(event_log, start_activities, retain=True, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')  
            # Iterate through each remaining start activity and filter the dataframe by the start and end activities as a separate process
            for start_activity in start_activities:
                # calculate the similarity between the process flows of different cases and group cases with high similarity using k-means
                test_k = pm4py.filter_variants_top_k(filtered_dataframe, 5, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')
                # save each process in a heuristics net
                #heu_net = pm4py.discover_heuristics_net(test_k, dependency_threshold=0.5)
                heu_net = pm4py.discover_heuristics_net(test_k)            
                #pm4py.view_heuristics_net(heu_net)
                # Save the Heuristics Net visualization to a file
                process_name = re.match(r'(\w+)_', start_activity).group(1) + " " + re.search(r'/(\w+)$', start_activity).group(1)
                directory = "./temp/process/"
                os.makedirs(directory, exist_ok=True)
                pm4py.save_vis_heuristics_net(heu_net, f"{directory}heuristics_net_{process_name}.png")
                with open(f"{directory}heuristics_net{process_name}.pkl", 'wb') as f:
                    pickle.dump(heu_net, f)               
                # Save the start_activity as process and create the hostorical dependency with the activies
                process_list.append(add_process_to_ontology(process_name, start_activity, test_k))
            
            # Save the ontology
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
            process = ns_process_view.Process()
            process.label.append(f"{process_name}")
            process.name = process_name
            #process.isPartOf.append(ns_process_view.ProcessView)
            process.label.append(f"start_activity: {start_activity}")
            
            #iterate through the process_variant_log and for each activity get the corresponding activity connection in activies_connections.           
            for case in process_variant_log:
                for event in case:
                    activity_name = event['concept:name']
                    #antecedent_actitivy_id = event['antecedent_id']
                    activity_connection = event['activity_connection']
                    activity_connection.historicallyDependsOn.append(process)
                                       
                    # for activity_connection in activies_connections:
                    #     activity_uri = activity_connection[0].isEventProperPartOf[0].api_uri[0] 
                    #     method = activity_connection[0].isEventProperPartOf[0].participatedIn[0].method[0]
                    #     full_activity_name = method + "_" + activity_uri   
                    #     #activies_connections_id = activity_connection[0].isEventProperPartOf[0].
                    #     if full_activity_name == activity_name:
                    #         # Add the activity connection to the process
                    #         activity_connection[0].historicallyDependsOn.append(process)
                    #         #break
        return process
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In save_process_into_ontology module :", __name__)
        raise error       
        
def remove_isolated_activies(event_log, start_activities):
    """
        Remove start activities that are part of another start activity
        args:
            start_activities: list of start activities
    """
   
    # Discover process models
    alpha_miner_result = alpha_miner.apply(event_log)
    #inductive_miner_result = inductive_miner.apply(event_log)
    isolated_start_activities = start_activities
    
    # Check activity in other flows
    for net in [alpha_miner_result]:
        # Unpack the tuple to access the process model
        net, initial_marking, final_marking = net
        count_activities = 0
        for transition in net.transitions:
            if transition.label in start_activities:
                count_activities += 1
                # Check if the transition is not a start activity
                # for arc in transition.in_arcs:
        if count_activities < 2:
            isolated_start_activities.pop(transition.label)
    return isolated_start_activities
        
def remove_not_pure_start_activies(event_log, start_activities):
    """
        Remove start activities that are part of another start activity
        args:
            start_activities: list of start activities
    """
   
    # Discover process models
    alpha_miner_result = alpha_miner.apply(event_log)
    #inductive_miner_result = inductive_miner.apply(event_log)
    pure_start_activities = start_activities
    
    # Check activity in other flows
    for net in [alpha_miner_result]:
        # Unpack the tuple to access the process model
        net, initial_marking, final_marking = net
        for transition in net.transitions:
            # print(f"'{transition.label}'")
            if transition.label in start_activities:
                # Check if the transition is not a start activity
                for arc in transition.in_arcs:
                    # print(f"arc.source: {arc.source}")
                    # print(f"arc.target: {arc.target}")
                    if arc.source.name != 'start': 
                        # print(f"{transition.label} is present in another position of the process flow that is not a start activity.")
                        pure_start_activities.pop(transition.label)
                        break
    
    return pure_start_activities


if __name__ == "__main__":
    processes_discovery()    