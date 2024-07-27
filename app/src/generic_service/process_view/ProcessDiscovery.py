import pandas as pd
import re
import pickle
import networkx as nx
import matplotlib.pyplot as plt
import pm4py
from owlready2 import *
from collections import defaultdict
from datetime import datetime
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.algo.discovery.log_skeleton import algorithm as log_skeleton_discovery
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.obj import EventLog
import os
import os.path
import sys # Add missing import statement for sys module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..")))
from app.src import configs
from app.src.utils import onto_util

onto_path.append(configs.OWL_FILE["file_path"])  # Set the path to load the ontology
onto = get_ontology(configs.OWL_FILE["file_name"]).load()
ns_gufo = onto.get_namespace("http://purl.org/nemo/gufo#")
ns_core = onto.get_namespace("http://eamining.edu.pt/core#")
ns_process_view = onto.get_namespace("http://eamining.edu.pt/process-view#")


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
        df_activies = pd.DataFrame(columns=['case_id', 'activity_connection', 'antecedent_activity_name', 'antecedent_request_time', 'partner_name', 'context'])
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
            antecedent_request_time = antecedent_activity.request_time[0].isoformat()
            
            activity_context = re.search(r'/([^/]+)/v1', antecedent_activity_route).group(1)
            
            df_activies.loc[len(df_activies)] = [case_id, activity_connection, antecedent_activity_name, antecedent_request_time, partner_name, activity_context]
        
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
    heu_net_list= []
    try:
        with onto:
            consumer_apps = onto_util.get_consumer_apps()
            for consumer_app in consumer_apps:
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
                variants = pm4py.get_variants(filtered_dataframe, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')
                filtered_dataframe_variant = pm4py.filter_variants(filtered_dataframe, variants, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')
                filtered_dataframe_variant = resolve_duplicated_process(filtered_dataframe_variant)
                event_log2 = pm4py.convert_to_event_log(filtered_dataframe_variant)
                start_activities = pm4py.get_start_activities(event_log2, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')
               

                # Iterate through each remaining start activity and filter the dataframe by the start and end activities as a separate process
                for start_activity in start_activities:
                    # calculate the similarity between the process flows of different cases and group cases with high similarity using k-means
                    top_k_value = configs.PM4PI_ARGS["TOP_K"]
                    test_k = pm4py.filter_variants_top_k(filtered_dataframe, top_k_value, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')
                    # save each process in a heuristics net
                    #heu_net = pm4py.discover_heuristics_net(test_k, dependency_threshold=0.5)
                    heu_net = pm4py.discover_heuristics_net(test_k)            
                    #pm4py.view_heuristics_net(heu_net)
                    heu_net_list.append(heu_net) 
                
                #heu_net = resolve_duplicated_process(heu_net, start_activities)
                    
                for heu_net in heu_net_list:
                    # Save the Heuristics Net visualization to a file
                    # process_name = re.match(r'(\w+)_', start_activity).group(1) + " " + re.search(r'.*/([^/]+)$', start_activity).group(1)
                    process_name = re.search(r'/([^/]+)/v1', start_activity).group(1)
                    directory = "./temp/process"
                    os.makedirs(directory, exist_ok=True)
                    datahora = datetime.now().strftime("%Y%m%d%H%M")
                    pm4py.save_vis_heuristics_net(heu_net, f"{directory}/heu_net_{process_name}_{datahora}.png")
                    with open(f"{directory}/heu_net_{process_name}.pkl", 'wb') as f:
                        pickle.dump(heu_net, f)               
                    # Save the start_activity as process and create the historical dependency with the activies
                    process_list.append(add_process_to_ontology(process_name, start_activity, test_k))
                
                # Save the ontology
                print(f"Closing Process Discovery for {consumer_app.name}")
                sync_reasoner()
                onto.save()
        return process_list
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In processes_discovery module :", __name__)
        raise error     
    
def processes_discovery_contextless():
    """
        Descovers the processes from the event log with APIs without context
    """
    process_list = []
    heu_net_list= []
    try:
        with onto:
            consumer_apps = onto_util.get_consumer_apps()
            for consumer_app in consumer_apps:
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
                variants = pm4py.get_variants(filtered_dataframe, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')
                filtered_dataframe_variant = pm4py.filter_variants(filtered_dataframe, variants, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')
                filtered_dataframe_variant = resolve_duplicated_process(filtered_dataframe_variant)
                event_log2 = pm4py.convert_to_event_log(filtered_dataframe_variant)
                start_activities = pm4py.get_start_activities(event_log2, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')
               

                # Iterate through each remaining start activity and filter the dataframe by the start and end activities as a separate process
                for start_activity in start_activities:
                    # calculate the similarity between the process flows of different cases and group cases with high similarity using k-means
                    top_k_value = configs.PM4PI_ARGS["TOP_K"]
                    test_k = pm4py.filter_variants_top_k(filtered_dataframe, top_k_value, activity_key='antecedent_activity_name', case_id_key='case_id', timestamp_key='antecedent_request_time')
                    # save each process in a heuristics net
                    #heu_net = pm4py.discover_heuristics_net(test_k, dependency_threshold=0.5)
                    heu_net = pm4py.discover_heuristics_net(test_k)            
                    #pm4py.view_heuristics_net(heu_net)
                    heu_net_list.append(heu_net) 
                
                #heu_net = resolve_duplicated_process(heu_net, start_activities)
                    
                for heu_net in heu_net_list:
                    # Save the Heuristics Net visualization to a file
                    # process_name = re.match(r'(\w+)_', start_activity).group(1) + " " + re.search(r'.*/([^/]+)$', start_activity).group(1)
                    process_name = re.search(r'/([^/]+)/v1', start_activity).group(1)
                    directory = "./temp/process"
                    os.makedirs(directory, exist_ok=True)
                    datahora = datetime.now().strftime("%Y%m%d%H%M")
                    pm4py.save_vis_heuristics_net(heu_net, f"{directory}/heu_net_{process_name}_{datahora}.png")
                    with open(f"{directory}/heu_net_{process_name}.pkl", 'wb') as f:
                        pickle.dump(heu_net, f)               
                    # Save the start_activity as process and create the hostorical dependency with the activies
                    process_list.append(add_process_to_ontology(process_name, start_activity, test_k))
                
                # Save the ontology
                print(f"Closing Process Discovery for {consumer_app.name}")
                sync_reasoner()
                onto.save()
        return process_list
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In processes_discovery module :", __name__)
        raise error        

  

def resolve_duplicated_process(event_log: pm4py.objects.log.obj.EventLog) -> pm4py.objects.log.obj.EventLog:
    """
    Resolve duplicated processes in an event log by eliminating duplicated cases.
    
    Args:
        event_log (EventLog): The event log to be processed.
        
    Returns:
        EventLog: A new event log with duplicated processes resolved.
    """
    
    # Initialize a new event log
    filtered_event_log = pm4py.objects.log.obj.EventLog()
    try:
        variants_count = pm4py.stats.get_variants(event_log)
        variants = list(variants_count.keys())  # Extracting variants as lists of activities
        subprocesses = detect_subprocesses(variants) 
        
        
           
        filtered_variants = [variant for variant in variants if variant not in subprocesses]
        
        # Filter the original event log based on filtered variants
        #filtered_event_log = filter_event_log(event_log, filtered_variants)
        # filtered_event_log = log_converter.apply(filtered_variants, variant=log_converter.Variants.TO_EVENT_LOG)
        
        # Iterate over each trace in the original event log
        for trace in event_log:
            # Convert trace to its variant (sequence of activities)
            #trace_variant = ", ".join([event["concept:name"] for event in trace])
            trace_variant_list = [event["concept:name"] for event in trace]
            trace_variant = tuple(trace_variant_list)  # Convert list to tuple to match the original format
            
            # If the trace's variant is in the filtered variants, add it to the new event log
            if trace_variant in filtered_variants:
                filtered_event_log.append(trace)        
        
                
        return filtered_event_log
    except Exception as e:
        print(f"An error occurred: {e}")
        return event_log  # Return the original event log in case of error

def detect_subprocesses(variants):
    """Detect subprocesses within the given variants, optimizing to avoid redundant comparisons."""
    subprocesses = set()
    for i, variant1 in enumerate(variants):
        for variant2 in variants[i+1:]:
            #print(f"detect_subprocesses Variant1: {variant1}" and f"Variant2: {variant2}")
            # Priority for the longer variant
            if is_subsequence(variant2, variant1):
                subprocesses.add(variant2)
            elif is_subsequence(variant1, variant2):
                subprocesses.add(variant1)
    return subprocesses

def is_subsequence(smaller, larger):
    """Check if the smaller sequence is a subsequence of the larger sequence."""
    it = iter(larger)
    ret = all(any(x == y for y in it) for x in smaller)
    return ret

def filter_event_log(event_log: EventLog, filtered_variants):
    """Filter the original event log based on the filtered variants."""
    filtered_log = EventLog()
    for trace in event_log:
        variant = [event["concept:name"] for event in trace]
        print(f"Variant: {variant}")
        if variant in filtered_variants:
            filtered_log.append(trace)
    return filtered_log

# def resolve_duplicated_process_v2(heu_net_list[HeuristicsNet], start_activities) -> list[HeuristicsNet]:
#     """
#         Get the list of heuristic nets and resolve the duplicated processes.
#         It vavigate through the heuristic nets and check if there are duplicated processes
#         This process mining targets to discover the unique sequences of activities that represent a process.
#         Therefore, the duplicated processes are those that have the same sequence of activities or part of sequence of activities.
#         If two or more start activites have the same sequence of activities, then they are considered duplicated processes. 
#         In this case, we need to chose only one of them to represent the process. 
#         That will be the start activity that has the most cases and more activities.
#         there are two or more start activities witn the same cases and exctly the same activities sequence, the first one will be chosen.            
#         args:
#             heu_net_list: list of pm4py.objects.heuristics_net.obj.HeuristicsNet
#         returns:
#             heu_net: heuristic net list of pm4py.objects.heuristics_net.obj.HeuristicsNet
#     """
        
#     # The goal of this function is to resolve duplicated processes in the heuristic nets chosing only one of them to represent the process.
#     # Navigate through the heuristic nets in heu_net_list and check if there are duplicated processes
#     # This process mining targets to discover the unique sequences of activities that represent a process.
#     # Therefore, the duplicated processes are those that have the same sequence of activities or part of sequence of activities.
#     # If two or more start activites have the same sequence of activities, then they are considered duplicated processes. 
#     # In this case, we need to chose only one of them to represent the process. 
#     # That will be the start activity that has the most cases and more activities.
#     # there are two or more start activities witn the same cases and exctly the same activities sequence, the first one will be chosen.
        
#     pass
        


def resolve_duplicated_process_v1(heu_net_list, start_activities) -> list:
    """
        Get the list of heuristic nets and resolve the duplicated processes.
        It vavigate through the heuristic nets and check if there are duplicated processes
        This process mining targets to discover the unique sequences of activities that represent a process.
        Therefore, the duplicated processes are those that have the same sequence of activities or part of sequence of activities.
        If two or more start activites have the same sequence of activities, then they are considered duplicated processes. 
        In this case, we need to chose only one of them to represent the process. 
        That will be the start activity that has the most cases and more activities.
        there are two or more start activities witn the same cases and exctly the same activities sequence, the first one will be chosen.            
        args:
            heu_net_list: list of heuristic nets
        returns:
            heu_net: heuristic net list
    """
        
        # Navigate through the heuristic nets and check if there are duplicated processes
        # This process mining targets to discover the unique sequences of activities that represent a process.
        # Therefore, the duplicated processes are those that have the same sequence of activities or part of sequence of activities.
        # If two or more start activites have the same sequence of activities, then they are considered duplicated processes. 
        # In this case, we need to chose only one of them to represent the process. 
        # That will be the start activity that has the most cases and more activities.
        # there are two or more start activities witn the same cases and exctly the same activities sequence, the first one will be chosen.
        
        
    resolved_heu_nets = []
    for heu_net in heu_net_list:
        # Assuming each heu_net has a structure where we can access start activities
        # and their sequences, and each activity has a 'cases' attribute.
        # This part of the implementation is highly dependent on the structure of heu_net.
        unique_activities = {} # Dict to store unique activities based on their sequence.       
        for start_activity in start_activities:
            sequence = get_activity_sequence(start_activity)  # get the sequence of activities for a given start activity.
            sequence_key = tuple(sequence)  # Convert list to tuple to use as a dict key.
            
            if sequence_key not in unique_activities:
                unique_activities[sequence_key] = start_activity
            else:
                # Compare based on the criteria: most cases, then most activities.
                existing_activity = unique_activities[sequence_key]
                if (start_activity.cases > existing_activity.cases or
                    (start_activity.cases == existing_activity.cases and len(sequence) > len(get_activity_sequence(existing_activity)))):
                    unique_activities[sequence_key] = start_activity
        
        # Remove duplicates from heu_net based on unique_activities.
        # This step requires modifying the heu_net to remove the non-selected start activities.
        # The exact implementation depends on the structure of heu_net.
        heu_net = remove_duplicates(heu_net, unique_activities.values())  # Placeholder function.
        
        resolved_heu_nets.append(heu_net)
    
    return resolved_heu_nets

def get_activity_sequence(activity):
    # Return the sequence of activities for a given start activity.
    pass
        
def remove_duplicates(heu_net, selected_activities):
    # Modify heu_net to only include the selected start activities and their sequences.
    heu_net = heu_net.copy()  # Copy heu_net to avoid modifying the original.
    return heu_net        
        
        # for start_activity in start_activities:
        #     duplicated_processes = []
        #     for heu_net in heu_net_list:
        #     if heu_net.start_activities == start_activity:
        #         duplicated_processes.append(heu_net)
        #     if len(duplicated_processes) > 1:
        #     duplicated_processes.sort(key=lambda x: (len(x.cases), len(x.activities)), reverse=True)
        #     chosen_process = duplicated_processes[0]
        #     heu_net_list.remove(chosen_process)
        #     heu_net_list.extend(duplicated_processes[1:])
        #

    

def add_process_to_ontology(process_name, start_activity, process_variant_log):
    # Create the process in the ontology and relate to the activities connections dependencies
    process = None
    try:
        with onto:
            # Create the process
            process = onto_util.get_individual(onto, ns_process_view.Process, "http://eamining.edu.pt/", process_name)
            if process is None:
                process = ns_process_view.Process()
                process.label.append(f"{process_name}")
                process.name = process_name
                process.label.append(f"start_activity: {start_activity}")
            
            #iterate through the process_variant_log and for each activity get the corresponding activity connection in activies_connections. 
            #TODO - Aqui tá esquisito, parece estar mistrurando os consumers.          
            for case in process_variant_log:
                for event in case:
                    activity_name = event['concept:name']
                    activity_connection = event['activity_connection']
                    activity_connection.historicallyDependsOn.append(process)
                    partner_name = event['partner_name']
                    label = f"partner: {partner_name}"
                    if label not in process.label:
                        process.label.append(label) 
                    # Add the context pool to the process
                    context_pool = event['context']
                    context_pool_label = f"context_pool: {context_pool}"
                    if context_pool_label not in process.label:
                        process.label.append(context_pool_label)
                          
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
            #print(f"Start Activity: {start_activity}")  
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
            if activity in start_activities:
                start_activities.pop(activity)
                   
        return start_activities
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In remove_isolated_activies module :", __name__)
        raise error    
        

if __name__ == "__main__":
    processes_discovery()    