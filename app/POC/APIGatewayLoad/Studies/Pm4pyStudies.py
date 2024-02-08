import pandas as pd
import pm4py
import os
from pm4py.algo.discovery.ocel.link_analysis import algorithm as link_analysis
import pm4py as pm4py


def import_csv(file_path):
    event_log = pd.read_csv(file_path, sep=';')

    # the format_dataframe()-function creates a copy of the input event log, and renames the assigned columns
    # to standardized column names used in pm4py.
    # In our example, the column case_id is renamed to
    # case:concept:name, the activity column is renamed to concept:name and
    # the timestamp column is renamed to time:timestamp.
    # event_log = pm4py.format_dataframe(pd.read_csv(file_path, sep=';'), case_id='case_id', activity_key='activity',timestamp_key='timestamp')

    num_events = len(event_log)
    num_cases = len(event_log.case_id.unique())
    print("Number of events: {}\nNumber of cases: {}".format(num_events, num_cases))


def import_xes(file_path):
    event_log = pm4py.read_xes(file_path)
    start_activities = pm4py.get_start_activities(event_log)
    end_activities = pm4py.get_end_activities(event_log)
    print("Start activities: {}\nEnd activities: {}".format(start_activities, end_activities))
    # exporting to .xes
    pm4py.write_xes(event_log, 'C:/Temp/Utad/PM4PY/running-example-exported.xes')

def export_to_xes(event_log):
    pm4py.write_xes(event_log, 'C:/Temp/Utad/PM4PY/running-example-exported.xes')

def filters(file_path):
    log = pm4py.read_xes(file_path)
    for t in log:
        print(len(t))

    long_traces = pm4py.filter_log(lambda t: len(t) > 5, log)
    print("Loong Traces")
    for t in long_traces:
        print(len(t))

    short_traces = pm4py.filter_log(lambda t: len(t) <= 5, log)
    print("Short Traces")
    for t in short_traces:
        print(len(t))

    print(type(long_traces))
    print(type(long_traces[0]))
    ## Funcoes para filtrar log e trace. Trace é uma sequência no log que se refere ao mesmo case
    #pm4py.filter_log(f, log); filters the log according to function f.
    #pm4py.filter_trace(f,log); filters the trace according to function f.
    #pm4py.sort_log(log, key, reverse); sorts the event log according to a given key, reversed order if reverse is True.
    #pm4py.sort_trace(trace, key, reverse); sorts the trace according to a given key, reversed order if reverse is True

def process_discovery_bpm(file_path):
    log = pm4py.read_xes(file_path)
    process_tree = pm4py.discover_process_tree_inductive(log)
    bpmn_model = pm4py.convert_to_bpmn(process_tree)
    pm4py.view_bpmn(bpmn_model)

def process_discovery_tree(file_path):
    log = pm4py.read_xes(file_path)
    process_tree = pm4py.discover_process_tree_inductive(log)
    pm4py.view_process_tree(process_tree)

def process_discovery_process_map(file_path):
    log = pm4py.read_xes(file_path)
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    pm4py.view_dfg(dfg, start_activities, end_activities)

def process_discovery_heuristic_miner(file_path):
    log = pm4py.read_xes(file_path)
    map = pm4py.discover_heuristics_net(log)
    pm4py.view_heuristics_net(map)

def import_ocel_and_statistics():
    path = "C:/Temp/Utad/PM4PY/example_log.jsonocel"
    ocel = pm4py.read_ocel(path)
    print(ocel)

def timestamp_based_interleaving():
    dataframe1 = pd.read_csv("C:/Temp/Utad/PM4PY/receipt_even.csv")
    dataframe1 = pm4py.format_dataframe(dataframe1)
    dataframe2 = pd.read_csv("C:/Temp/Utad/PM4PY/receipt_odd.csv")
    dataframe2 = pm4py.format_dataframe(dataframe2)
    case_relations = pd.read_csv("C:/Temp/Utad/PM4PY/case_relations.csv")
    from pm4py.algo.discovery.ocel.interleavings import algorithm as interleavings_discovery
    interleavings = interleavings_discovery.apply(dataframe1, dataframe2, case_relations)
    from pm4py.visualization.ocel.interleavings import visualizer as interleavings_visualizer
    # visualizes the frequency of the interleavings
    gviz_freq = interleavings_visualizer.apply(dataframe1, dataframe2, interleavings, parameters={"annotation": "frequency", "format": "svg"})
    interleavings_visualizer.view(gviz_freq)

def network_analysis():
    log = pm4py.read_xes(os.path.join("tests", "input_data", "C:/Temp/Utad/PM4PY/receipt.xes"))
    frequency_edges = pm4py.discover_network_analysis(log, out_column="case:concept:name", in_column="case:concept:name", node_column_source="org:group", node_column_target="org:group", edge_column="concept:name", performance=False)
    #pm4py.view_network_analysis(frequency_edges, variant="frequency", format="svg", edge_threshold=10)
    pm4py.view_network_analysis(frequency_edges, variant="frequency", edge_threshold=10)

def link_analysis():
    #log = pm4py.read_xes(os.path.join("tests", "input_data", "C:/Temp/Utad/PM4PY/receipt.xes"))
    dataframe = pd.read_csv(os.path.join("tests", "input_data", "ocel", "C:/Temp/Utad/PM4PY/VBFA.zip"), compression="zip", dtype="str")
    dataframe["time:timestamp"] = dataframe["ERDAT"] + " " + dataframe["ERZET"]
    dataframe["time:timestamp"] = pd.to_datetime(dataframe["time:timestamp"], format="%Y%m%d %H%M%S")
    dataframe["RFWRT"] = dataframe["RFWRT"].astype(float)
    dataframe = link_analysis.apply(dataframe, parameters={"out_column": "VBELN", "in_column": "VBELV", "sorting_column": "time:timestamp", "propagate": True})
    #At this point, several analysis could be performed.
    # For example, findings the interconnected documents for which the currency differs between the two documents can be done as follows.
    df_currency = dataframe[(dataframe["WAERS_out"] != " ") & (dataframe["WAERS_in"] != " ") & (dataframe["WAERS_out"] != dataframe["WAERS_in"])]
    print(df_currency[["WAERS_out", "WAERS_in"]].value_counts())

    #It is also possible to evaluate the amount of the documents, in order to identify discrepancies.
    df_amount = dataframe[(dataframe["RFWRT_out"] > 0) & (dataframe["RFWRT_out"] < dataframe["RFWRT_in"])]
    print(df_amount[["RFWRT_out", "RFWRT_in"]])

def object_centric_flows_multigraphs():
    ocel = pm4py.read_ocel(os.path.join("tests", "input_data", "ocel", "C:/Temp/Utad/PM4PY/example_log_oc.jsonocel"))
    ocdfg = pm4py.discover_ocdfg(ocel)
    # views the model with the frequency annotation
    pm4py.view_ocdfg(ocdfg, format="svg")
    # views the model with the performance annotation - frequency is default
    pm4py.view_ocdfg(ocdfg, annotation="performance ", performance_aggregation="median")

def object_centric_petri_net():
    ocel = pm4py.read_ocel(os.path.join("tests", "input_data", "ocel", "C:/Temp/Utad/PM4PY/example_log_oc.jsonocel"))
    model = pm4py.discover_oc_petri_net(ocel)
    pm4py.view_ocpn(model)

def object_interactions_graph():
    ocel = pm4py.read_ocel("C:/Temp/Utad/PM4PY/example_log_oc.jsonocel")
    from pm4py.algo.transformation.ocel.graphs import object_interaction_graph
    graph = object_interaction_graph.apply(ocel)
    print(graph)

def feature_extraction_ocel():
    ocel = pm4py.read_ocel("C:/Temp/Utad/PM4PY/example_log.jsonocel")
    from pm4py.algo.transformation.ocel.features.events import algorithm
    data, feature_names = algorithm.apply(ocel, parameters={"str_obj_attr": ["prova"], "num_obj_attr": ["prova2"]})
    print(feature_names)

def correlation_miner():
    df = pd.read_csv(os.path.join("tests", "input_data", "C:/Temp/Utad/PM4PY/receipt.csv"))
    df = pm4py.format_dataframe(df)
    df = df[["concept:name", "time:timestamp"]]
    from pm4py.algo.discovery.correlation_mining import algorithm as correlation_miner
    frequency_dfg, performance_dfg = correlation_miner.apply(df, parameters={"pm4py:param:activity_key": "concept:name",
                                    "pm4py:param:timestamp_key": "time:timestamp"})
    activities_freq = dict(df["concept:name"].value_counts())
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    gviz_freq = dfg_visualizer.apply(frequency_dfg, variant=dfg_visualizer.Variants.FREQUENCY, activities_count=activities_freq, parameters={"format": "svg"})
    gviz_perf = dfg_visualizer.apply(performance_dfg, variant=dfg_visualizer.Variants.PERFORMANCE, activities_count=activities_freq, parameters={"format": "svg"})
    dfg_visualizer.view(gviz_freq)
    dfg_visualizer.view(gviz_perf)

def reachability_graph():
    #Maximal Decomposition
    log = pm4py.read_xes(os.path.join("tests", "input_data", "C:/Temp/Utad/PM4PY/running-example.xes"))
    net, im, fm = pm4py.discover_petri_net_alpha(log)
    from pm4py.objects.petri_net.utils.decomposition import decompose
    list_nets = decompose(net, im, fm)
    for index, model in enumerate(list_nets):
        subnet, s_im, s_fm = model
        #pm4py.save_vis_petri_net(subnet, s_im, s_fm, str(index)+".png")

    #reachability graph
    from pm4py.objects.petri_net.utils import reachability_graph
    ts = reachability_graph.construct_reachability_graph(net, im)
    from pm4py.visualization.transition_system import visualizer as ts_visualizer
    gviz = ts_visualizer.apply(ts, parameters={ts_visualizer.Variants.VIEW_BASED.value.Parameters.FORMAT: "svg"})
    ts_visualizer.view(gviz)

def token_based_replay():
    log = pm4py.read_xes(os.path.join("tests", "input_data", "running-example.xes"))
    net, initial_marking, final_marking = pm4py.discover_petri_net_alpha(log)
    replayed_traces = pm4py.conformance_diagnostics_token_based_replay(log, net, initial_marking, final_marking)

def event_distribution():
    log = pm4py.read_xes(os.path.join("tests", "input_data", "C:/Temp/Utad/PM4PY/receipt.xes"))
    pm4py.view_events_distribution_graph(log, distr_type="days_week", format="svg")

def detection_batches():
    #calca
    log = pm4py.read_xes(os.path.join("tests", "input_data", "C:/Temp/Utad/PM4PY/receipt.xes"))
    from pm4py.algo.discovery.batches import algorithm
    batches = algorithm.apply(log)
    #The results can be printed on the screen as follows   for act_res in batches:
    for act_res in batches:
        print("")
        print("activity: "+act_res[0][0]+" resource: "+act_res[0][1])
        print("number of distinct batches: "+str(act_res[1]))
        for batch_type in act_res[2]:
            print(batch_type, len(act_res[2][batch_type]))

if __name__ == "__main__":
    log_path = "C:/Temp/Utad/PM4PY/running-example.xes"
    #import_csv("C:/Temp/Utad/PM4PY/running-example.csv")
    #import_xes("C:/Temp/Utad/PM4PY/running-example.xes")
    #filters("C:/Temp/Utad/PM4PY/running-example.xes")
    #process_discovery_tree("C:/Temp/Utad/PM4PY/running-example.xes")
    #process_discovery_process_map(log_path)
    #process_discovery_heuristic_miner(log_path)
    #import_ocel_and_statistics()
    #timestamp_based_interleaving()
    #network_analysis()
    #link_analysis()
    #object_centric_flows_multigraphs()
    #object_centric_petri_net()
    #object_interactions_graph()
    #feature_extraction_ocel()
    #correlation_miner()
    #reachability_graph()
    #event_distribution()
    detection_batches()