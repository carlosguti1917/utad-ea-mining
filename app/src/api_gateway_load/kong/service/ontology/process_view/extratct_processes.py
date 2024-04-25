import pandas as pd
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

file_path = './temp/'   
file_nm = "ftc_list.csv"

log_file = pd.read_csv(file_path + file_nm, sep=';')
dataframe = pm4py.format_dataframe(log_file, case_id='case_id', activity_key='activity a', timestamp_key='antecedent_request_time')
#imestamp format is %Y-%m-%d %H:%M:%S%z
event_log = pm4py.convert_to_event_log(dataframe)

def processes_discovery():
  
    start_activities = pm4py.get_start_activities(event_log, activity_key='activity a', case_id_key='case_id', timestamp_key='antecedent_request_time')
    end_activities = pm4py.get_end_activities(event_log, activity_key='activity a', case_id_key='case_id', timestamp_key='antecedent_request_time') 
    #TODO remover os cases com menos de tres atividades, talvez tenha que ser antes
    
    # remove not pure start activities, those that are also part of another flow started by other activity
    start_activities = remove_not_pure_start_activies(start_activities)
    
    filtered_dataframe = pm4py.filter_start_activities(event_log, start_activities, retain=True, activity_key='activity a', case_id_key='case_id', timestamp_key='antecedent_request_time')  
    # Iterate through each remaining start activity and filter the dataframe by the start and end activities as a separate process
    for start_activity in start_activities:
        # calculate the similarity between the process flows of different cases and group cases with high similarity using k-means
        test_k = pm4py.filter_variants_top_k(filtered_dataframe, 5, activity_key='activity a', case_id_key='case_id', timestamp_key='antecedent_request_time')
        # save each process in a heuristics net
        #heu_net = pm4py.discover_heuristics_net(test_k, dependency_threshold=0.5)
        heu_net = pm4py.discover_heuristics_net(test_k)
        pm4py.view_heuristics_net(heu_net)
        
        
        
def remove_not_pure_start_activies(start_activities):
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
            print(f"'{transition.label}'")
            if transition.label in start_activities:
                # Check if the transition is not a start activity
                for arc in transition.in_arcs:
                    print(f"arc.source: {arc.source}")
                    print(f"arc.target: {arc.target}")
                    if arc.source.name != 'start': 
                        print(f"{transition.label} is present in another position of the process flow that is not a start activity.")
                        pure_start_activities.pop(transition.label)
                        break
    
    return pure_start_activities


# if __name__ == "__main__":
#     processes_discovery()    