import pandas as pd
import re
from owlready2 import *
from datetime import datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom
from lxml import etree
import pickle
import pm4py
import os
import os.path
import sys # Add missing import statement for sys module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..", "..")))
from app.src import configs
from app.src.utils import onto_util
from app.src.utils import archimate_util
from app.src.utils import ai_gen_util

onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
#onto = get_ontology("EA Mining OntoUML Teste V1_3.owl").load()
onto = get_ontology(configs.OWL_FILE["file_name"]).load()
ns_gufo = onto.get_namespace("http://purl.org/nemo/gufo#")
ns_core = onto.get_namespace("http://eamining.edu.pt/core#")
ns_process_view = onto.get_namespace("http://eamining.edu.pt/process-view#")

def get_process_from_ontology():
    """
        Get the processes from the ontology
        returns:
            processes: 
    """
    try:
        # select the activities connections from the ontology
        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                PREFIX ns_core: <http://eamining.edu.pt/core#>
                PREFIX ns_process_view: <http://eamining.edu.pt/process-view#>

                SELECT distinct ?process
                WHERE {
                    ?process a ns_process_view:Process .
                }
        """
        processes = list(default_world.sparql(query)) 
        #df_processes = pd.DataFrame(columns=['case_id', 'activity_connection', 'antecedent_activity_name', 'antecedent_request_time'])
        # for process_tuple in processes:
        #     process = process_tuple[0]

        return processes
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In get_event_log module :", __name__)
        raise error    
    
def add_archimate_process_elements(root, processes):   
    """
        Create the xml element for the process
    """
    
    contextfull_process = False #To verify if the process has a context pool or not, default is False
    isActorNew = False
    try:
        
        namespaces = {'': 'http://www.opengroup.org/xsd/archimate/3.0/'}  
        elements = root.find(".//elements", namespaces)   
        if elements is None:
            elements = ET.SubElement(root, "elements")
        
        process_element_number = 0 
        event_number = 0
        for process_tuple in processes:
            process_element_number += 1
            process = process_tuple[0]
            # get macro process name
            label_parts = process.label[0].split(': ')            
            if len(label_parts) > 1:
                process_name_text = label_parts[1]
            else:
                process_name_text = process.label[0]    
                        
            # Create the Business Process elements
            for label in process.label:
                label_parts = label.split(': ')
                if label_parts[0] == "context_pool":
                    contextfull_process = True
                    context_pool = label_parts[1]
                    #process_id = process.name.replace("/", "-").replace("_", "")
                    process_identifier = f"id-process-{context_pool}"
                    process_exists = elements.find(f".//element[@identifier='{process_identifier}']", namespaces)
                    if process_exists is None:
                        process_element = ET.SubElement(elements, "element", attrib={"identifier": process_identifier, "xsi:type": "BusinessProcess"})
                        process_name = ET.SubElement(process_element, "name")
                        process_name.text = context_pool  
                        root, isActorNew = add_archimate_actors_to_process(root, process, process_identifier)    
            if contextfull_process == False:
                #process_id = process.name.replace("/", "-").replace("_", "")
                process_identifier = f"id-process-{process_element_number}"
                process_exists = elements.find(f".//element[@identifier='{process_identifier}']", namespaces)
                if process_exists is None:
                    process_element = ET.SubElement(elements, "element", attrib={"identifier": process_identifier, "xsi:type": "BusinessProcess"})
                    process_name = ET.SubElement(process_element, "name")
                    process_name.text = process_name_text  
                    root, isActorNew = add_archimate_actors_to_process(root, process, process_identifier)            
                
            # Create the Business Event elements
            if contextfull_process == True:
                root, event_number = add_archimate_event_process_elements(root, None, process_name_text, event_number) 
            else:
                root, event_number = add_archimate_event_process_elements(root, process_identifier, process_name_text, event_number)   
        
        return root, contextfull_process
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In add_archimate_process_elements module :", __name__)
        raise error

def add_archimate_actors_to_process(root, process, process_identifier):
    
    namespaces = {'': 'http://www.opengroup.org/xsd/archimate/3.0/'}  
    
    isActorNew = False 
        
    try:
        labels  = process.label
        for label in labels:
            label_parts = label.split(': ')
            part0 = label_parts[0]
            if part0 != "partner":
                continue
            actor_name = label_parts[1]
            actor_identifier = f"id-actor-{actor_name}"
            #elements = root.find("elements")
            elements = root.find(".//elements", namespaces) 
            if elements is None:
                elements = ET.SubElement(root, "elements")

            actor_exists = None
            for element in elements:
                if element.get("identifier") == actor_identifier:
                    actor_exists = element
                    break
            if actor_exists is None:
                actor_element = ET.SubElement(elements, "element", attrib={"identifier": actor_identifier, "xsi:type": "BusinessActor"})
                actor_element_name = ET.SubElement(actor_element, "name")
                actor_element_name.text = actor_name
                isActorNew = True
            #relationships
            #relationships = root.find("relationships")
            relationships = root.find(".//relationships", namespaces) 
            if relationships is None:
                relationships = ET.SubElement(root, "relationships")            
            relationship_id = f"id-relation-{actor_name}-{process_identifier}"
            relationship_exists = root.find(f".//relationship[@identifier='{relationship_id}']", namespaces)
            if relationship_exists is None:
                relationship = ET.SubElement(relationships, "relationship ", attrib={"identifier": relationship_id, "source": process_identifier, "target": actor_identifier, "xsi:type":"Serving" })                
                relationship_name = ET.SubElement(relationship, "name")
                relationship_name.text = relationship_id
        
        return root, isActorNew
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In create_archimate_actors_to_process module :", __name__)
        raise error

def add_archimate_event_process_elements(root, process_identifier, process_name, event_number):   
    """
        Create the xml element for the process
        args:
            root: xml.etree.ElementTree
            process_identifier: str # The identifier of the process, in case of contextfull process it is None because the process identifier ig get from activity pattern
                if the process_identifier is None, the process is a contextfull process
            process_name: str
            event_number: int
    """
    try:
        namespaces = {'': 'http://www.opengroup.org/xsd/archimate/3.0/'}  
        elements = root.find(".//elements", namespaces) 
        #elements = root.find("elements")
        if elements is None:
            elements = ET.SubElement(root, "elements")
            
        # Load the HeuristicsNet object from the file
        directory = configs.TEMP_PROCESSING_FILES["pkl_file_path"]
        #datahora = datetime.now().strftime("%Y%m%d%H%M")
        with open(f"{directory}/heu_net_{process_name}.pkl", 'rb') as f:
            heu_net = pickle.load(f)
        
        # Get the activities from the HeuristicsNet
        activities = heu_net.activities
        # for activity_name, activity_id in activities:
        for activity in activities:
            event_number += 1
            # Create the Business Event elements
            # activity_id =  activity.replace("/", "-").replace("_", "")
            activity_name = ai_gen_util.translate_uri_to_task_name(activity)
            # activity_name = activity
            event_identifier = f"id-event-{event_number}"
            event_exists = elements.find(f".//element[@identifier='{event_identifier}']", namespaces)
            if event_exists is None:
                event_element = ET.SubElement(elements, "element", attrib={"identifier": event_identifier, "xsi:type": "BusinessEvent" })
                event_element_name = ET.SubElement(event_element, "name")
                event_element_name.text = activity_name
                properties = ET.SubElement(event_element, "properties")
                property_element = ET.SubElement(properties, "property", attrib={"propertyDefinitionRef": "uri"})
                value_element = ET.SubElement(property_element, "value", attrib={"xml:lang": "pt"})
                value_element.text = activity
                
            
            #relationships BusinessEvent with process (BusinessProcess)
            if process_identifier == None:
                process_context = re.search(r'/([^/]+)/v1', activity).group(1)
                relationships = root.find(".//relationships", namespaces) 
                if relationships is None:
                    relationships = ET.SubElement(root, "relationships")            
                relationship_id = f"id-relation-{event_number}"
                relationship_exists = root.find(f".//relationship[@identifier='{relationship_id}']", namespaces)
                if relationship_exists is None:
                    relationship = ET.SubElement(relationships, "relationship ", attrib={"identifier": relationship_id, "source": f"id-process-{process_context}", "target": event_identifier, "xsi:type":"Association" })                
                    relationship_name = ET.SubElement(relationship, "name")
                    relationship_name.text = relationship_id           
            else:
                relationships = root.find(".//relationships", namespaces) 
                if relationships is None:
                    relationships = ET.SubElement(root, "relationships")            
                relationship_id = f"id-relation-{event_number}"
                relationship_exists = root.find(f".//relationship[@identifier='{relationship_id}']")
                if relationship_exists is None:
                    relationship = ET.SubElement(relationships, "relationship ", attrib={"identifier": relationship_id, "source": process_identifier, "target": event_identifier, "xsi:type":"Association" })                
                    relationship_name = ET.SubElement(relationship, "name")
                    relationship_name.text = relationship_id
        
        
        # save_archimate_exchange_model(root)
        # relations = root.findall(".//relationship")
        return root, event_number
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In create_archimate_process_elements module :", __name__)
        raise error    
    
def add_actor_process_view_diagrams(root):
    """ 
        Create the process view by actor
    """
    try:    
        
        # Get the elements from the root
        namespaces = {'': 'http://www.opengroup.org/xsd/archimate/3.0/'} 
        elements = root.findall(".//element")
        # Find the <diagrams> element
        diagrams = root.find(".//diagrams", namespaces)        

        # Count the number of elements that are of type BusinessActor
        total_ba = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessActor') 
        
        # if total_ba > 0:
        #     # Create the root element for the ArchiMate model
        #     root = ET.Element("model", attrib={
        #         "xmlns": "http://www.opengroup.org/xsd/archimate/3.0/",
        #         "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        #         "xsi:schemaLocation": "http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd",
        #         "identifier": "id-ea-mining-exchange-model-1",
        #     })            
        
        for element in elements:
            # Check if the element is a BusinessProcess or BusinessEvent        
            if element.get("xsi:type") == "BusinessActor": 
                actor_identifier = element.get('identifier') 
                actor_name = element.find('name').text                
                # Create the diagram               
                diagram_view = ET.SubElement(diagrams, "view", attrib={"identifier": f"id-view-ea-{actor_name}-process-view", "viewpoint":"Application Usage", "xsi:type":"Diagram"})
                diagram_view_name = ET.SubElement(diagram_view, "name", attrib={"xml:lang": "en"})
                diagram_view_name.text = f"API extracted process view for {actor_name}" 
                diagram_view_documentation = ET.SubElement(diagram_view, "documentation", attrib={"xml:lang": "en"})
                diagram_view_documentation.text = f"Process View Mined from API Logs for Business Actor {actor_name}."  
                
        return root         
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In create_archimate_diagram module :", __name__)
        raise error          
        

def add_process_view_diagram_nodes_contextfull_by_actor(root):

    #x: The x-coordinate of the top-left corner of the element. This determines the horizontal position of the element from the left side of the parent element or the screen.
    #y: The y-coordinate of the top-left corner of the element. This determines the vertical position of the element from the top of the parent element or the screen.
    #w: The width of the element. This determines how wide the element is.
    #h: The height of the element. This determines how tall the element is.

    try:
        
        # Get the elements from the root
        namespaces = {'': 'http://www.opengroup.org/xsd/archimate/3.0/'} 
        elements = root.findall(".//element")
        #diagram_view = root.find(".//view[@identifier='id-view-ea-process-view']", namespaces)

        element_width = 100
        axis_width = 1200        
        distance_between_elements = 150
             
        # Count the number of elements that are of type BusinessProcess
        # total_bp = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessProcess')     
        # Count the number of elements that are of type BusinessEvent
        # total_be = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessEvent')
        # Count the number of elements that are of type BusinessActor
        total_ba = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessActor')

        # Initialize position variables
        bp_h = 150 # height of the BusinessProcess
        #bp_w = 10 + total_be * 250 # width of the BusinessProcess
        be_w = 240 # width of the BusinessEvent
        
        x_offset = 100  # Initial x offset for positioning elements
        xy_increment = 100  # Increment for x and y position for each element
        y_ba = 50  # y position for BusinessActors
        y_bp = 50  # initial y position for BusinessProcess
        y_be = 100  # y position for BusinessEvents
        count_bp = 0
        count_be = 0
        count_ba = 0
        element_index = 0
        node_number = 0
        connection_number = 0
        be_antecedent_identifier = None
        # business_process_list = []
        aux_matrix = {}
        x_aux = 50
        max = 0
        antecedent_actor = None 

        root_copy = etree.fromstring(ET.tostring(root))
        #namespaces = {'ns': 'http://www.opengroup.org/xsd/archimate/3.0/'} 
        

        # Find BusinessActor and mount the diagram node.
        for element in elements:
            element_type = element.get("xsi:type")
            if element_type == "BusinessActor":               
                # Inicializing BusinessProcess variables
                y_bp = 50  # reinitializing the initial y position for BusinessProcess
                count_bp = 0 # reinitializing the count of BusinessProcess
                total_bp = 0
                business_process_list = [] # reinitializing the list of BusinessProcess
                
                # inicialize the BusinessEvent variables
                count_be = 0 # reinitializing the count of BusinessEvent
                y_be = 100  # reinitializing the initial y position for BusinessEvent
                max = 0 # reinitializing the max position for BusinessEvent
                total_be = 1 # reinitializing the total of BusinessEvent 
                actor_id_list_4_nodes = [] # reinitializing the list of BusinessEvent to create the connections 
                relationships_list = set() # reinitializing the list of relationships to create the connection           
                
                actor_identifier = element.get('identifier')
                actor_name = element.find('name').text                 
                
                relationships = root.find(".//relationships", namespaces)
                for relationship in relationships:
                    if relationship.get("target") == actor_identifier:
                        total_bp += 1
                        id_process = relationship.get("source")
                        relationships_process = root.find(".//relationships", namespaces)
                        for relationship_process in relationships_process:
                            if relationship_process.get("source") == id_process and relationship_process.get("xsi:type") == "Association": #Events are associated with the process and actors are served
                                total_be += 1 
                                relationships_list.add(relationship_process.get("identifier"))                       
                
                bp_w = 50 + total_be * 255 # Inicialize width of the BusinessProcess                                            
                
                #count_ba += 1
                #x = x_offset + (count_ba * x_increment)
                x = 25
                total_y_bp = total_bp * (bp_h + xy_increment)
                #fator_y = 0.5 / total_ba
                #y_ba = total_y_bp * (fator_y / count_ba)
                y_ba = total_y_bp / 2
                y = int(y_ba)
                node_number += 1 
                node_identifier = f"id-node-{node_number}"
                view_id = f"id-view-ea-{actor_name}-process-view"
                diagram_id = f"id-view-ea-{actor_name}-process-view"
                diagrams = root.find(".//diagrams", namespaces)       
                             
                # Create the diagram               
                diagram_view = ET.SubElement(diagrams, "view", attrib={"identifier": f"id-view-ea-{actor_name}-process-view", "viewpoint":"Application Usage", "xsi:type":"Diagram"})
                diagram_view_name = ET.SubElement(diagram_view, "name", attrib={"xml:lang": "en"})
                diagram_view_name.text = f"API extracted process view for {actor_name}" 
                diagram_view_documentation = ET.SubElement(diagram_view, "documentation", attrib={"xml:lang": "en"})
                diagram_view_documentation.text = f"Process View Mined from API Logs for Business Actor {actor_name}."                              
             
                diagram_view_actor_node = ET.SubElement(diagram_view, "node", attrib={"identifier":node_identifier, "xsi:type":"Element", "elementRef":actor_identifier, "x":str(x) , "y":str(y), "w":"120", "h":"50"})                                             
                actor_id_list_4_nodes.append(node_identifier)
                

                # Find BusinessProcess and mount the diagram node for the process
                relationships = root.find(".//relationships", namespaces)
                for relationship in relationships:
                    if relationship.get("target") == actor_identifier:
                    # Add the source attribute (process) to the list
                        actor_id_process = relationship.get("source")
                        #process_identifier = element.get('identifier')
                        element_process = root.find(f".//element[@identifier='{actor_id_process}']")
                        if element_process is not None and element_process.get("xsi:type") == "BusinessProcess":       
                            element_type = element_process.get("xsi:type")
                            # Check if the element is a BusinessProcess or BusinessEvent                     
                            process_identifier = element_process.get('identifier')
                            process_name = element_process.find('name').text 
                            business_process_list.append(process_name)
                            count_bp += 1
                            x = 350 
                            if count_bp > 1:
                                y_bp = y_bp + bp_h + xy_increment
                            y = int(y_bp)
                            node_number += 1
                            node_identifier = f"id-node-{node_number}"
                            diagram_view_process_node = ET.SubElement(diagram_view, "node", attrib={"identifier":node_identifier, "xsi:type":"Element", "elementRef":process_identifier, "x":str(x) , "y":str(y), "w":str(bp_w), "h":str(bp_h)})           
                            actor_id_list_4_nodes.append(node_identifier)
                            relationships_list.add(relationship.get("identifier"))
                            
                            # Create the Business Event nodes for the process    
                            event_relationships = root.find(".//relationships", namespaces)
                            for event_relationship in event_relationships:
                                if event_relationship.get("source") == process_identifier:
                                    event_identifier = event_relationship.get("target")
                                    relationships_list.add(relationship.get("identifier"))
                                    element_event = root.find(f".//element[@identifier='{event_identifier}']")
                                    if element_event is not None and element_event.get("xsi:type") == "BusinessEvent":
                                        element_type = element_event.get("xsi:type")
                                        event_name = element_event.find('name').text                                     
                                        count_be += 1
                                        #calculate x and y position
                                        if process_name not in aux_matrix:
                                            # inicialize the posicioanment of the first event
                                            aux_matrix[process_name] = {"lastpos": x_offset}                      
                                        
                                        lastpos = aux_matrix[process_name]["lastpos"] 
                                            
                                        # for i, j in aux_matrix.items():
                                        #     if j["lastpos"] > max:
                                        #         max = j["lastpos"]                     

                                        if (lastpos < max):
                                            print(f" mudou max: {lastpos} --> lastpos: {lastpos}")
                                            x_aux = max 
                                        else:
                                            print(f" não mudou max: {max} --> lastpos: {lastpos}")
                                            x_aux = lastpos + (be_w + xy_increment) 
                                            max = x_aux # coloquei em 23/08
                                            
                                        x = int(x_aux)
                                        aux_matrix[process_name].update({"lastpos": x})                    
                                                
                                        business_process_position = business_process_list.index(process_name) 
                                        y_be_aux = y_be     
                                        if business_process_position > 0:
                                            y_be_aux =  y_be_aux + ((bp_h + xy_increment) * business_process_position) 
                                        y = int(y_be_aux)
                                        
                                        node_number += 1
                                        node_identifier = f"id-node-{node_number}"
                                        diagram_view_event_node = ET.SubElement(diagram_view, "node", attrib={"identifier":node_identifier, "xsi:type":"Element", "elementRef":event_identifier, "x":str(x) , "y":str(y), "w":str(be_w), "h":"50"})                                 
                                        actor_id_list_4_nodes.append(node_identifier)

                                        element_index = element_index + 1 
                                        relationship_id = f"id-relation-be-{element_index}"
                                        relationships_list.add(relationship_id)

                                        #relationships
                                        relationships = root.find(".//relationships", namespaces)
                                        if relationships is None:
                                            relationships = ET.SubElement(root, "relationships")
                                        relationship_exists = root.find(f".//relationship[@identifier='{relationship_id}']", namespaces)              
                                        if relationship_exists is None:
                                            if be_antecedent_identifier is not None:
                                                # verify it the antecedent and the element are connected to the same BusinessProcess and the process with the same BusinessActor
                                                #event_actor = None
                                                antecedent_event_process = None
                                                                    
                                                event_process = event_relationship.get("source")
                        
                                                relationships = root.find(".//relationships", namespaces) 
                                                for relationship in relationships:
                                                    if relationship.get("source") == event_process and relationship.get("xsi:type") == "Serving":
                                                            target = relationship.get("target")
                                                            if target.startswith("id-actor"):
                                                                event_actor = target
                                                                relationships_list.add(relationship.get("identifier"))
                                                    if relationship.get("target") == be_antecedent_identifier:
                                                        #antecedent_relation = relationship
                                                        if relationship.get("source").startswith("id-process"):
                                                            antecedent_event_process = relationship.get("source")
                                                            relationships_list.add(relationship.get("identifier"))
                                                            
                                                        #antecedent_event_process = relationship.get("source")
                                                        antecedent_relation_actors = root.find(".//relationships", namespaces)
                                                        for antecedent_relation_actor in antecedent_relation_actors:
                                                            #if antecedent_relation_actor.get("source") == antecedent_event_process and antecedent_relation_actor.get("xsi:type") == "Serving":
                                                            if antecedent_relation_actor.get("source") == antecedent_event_process:
                                                                target = antecedent_relation_actor.get("target")
                                                                if target.startswith("id-actor"):
                                                                    antecedent_actor = target
                                                                    relationships_list.add(relationship.get("identifier"))
                                                                
                                                if event_actor == antecedent_actor:
                                                    relationship = ET.SubElement(relationships, "relationship ", attrib={"identifier": relationship_id, "source": be_antecedent_identifier, "target": event_identifier, "xsi:type":"Flow" })                
                                                    relationship_name = ET.SubElement(relationship, "name")
                                                    relationship_name.text = relationship_id
                                                    relationships_list.add(relationship_id)
                                    
                                        be_antecedent_identifier = event_identifier                                

                # create the connections
                nodes = root.findall(".//node")
                for node in nodes:
                    element_ref = node.get('elementRef')
                    node_identifier = node.get('identifier')
                    
                    if node_identifier not in actor_id_list_4_nodes:
                        continue
                                            
                    relationships = root.find(".//relationships", namespaces) 
                    for relationship in relationships:
                        # source and target need to be different
                        rel_source = relationship.get("source")
                        rel_target = relationship.get("target")

                        if rel_source != element_ref:
                            continue   
        
                        relationship_id = relationship.get("identifier")                       
                        if relationship_id not in relationships_list:
                            continue
                        
                        source_node = node.get('identifier')
                        target_node_obj = root.find(".//node[@elementRef='"+ rel_target +"']")
                        target_node = target_node_obj.get('identifier')
                        if target_node is None:
                            continue
                        
                        # if source is BusinessProcess and target is BusinessEvent dont create the connection
                        source_node_obj = root.find(".//node[@elementRef='"+ rel_source +"']") 
                        source_element_ref = source_node_obj.get('elementRef')               
                        source_element = None
                        elements = root.findall(".//element")
                        for el in elements:
                            if el.get("identifier") == source_element_ref:
                                source_element = el
                                break
                        target_element_ref = target_node_obj.get('elementRef')
                        target_element = None
                        for el_t in elements:
                            if el_t.get("identifier") == target_element_ref:
                                target_element = el_t
                                break                
                        if source_element is not None and target_element is not None:
                            source_type = source_element.get('xsi:type')
                            target_type = target_element.get('xsi:type')
                            if source_type == "BusinessProcess" and target_type == "BusinessEvent":
                                # Skipping connection creation: source is BusinessProcess and target is BusinessEvent")
                                continue
                        
                        connection_number += 1
                        connection_idenfitier = f"id-connection-{connection_number}"
                        diagram_view_connection = ET.SubElement(diagram_view, "connection", attrib={"identifier": connection_idenfitier, "xsi:type":"Relationship", "source":source_node, "target":target_node, "relationshipRef":relationship_id})
        
        return root
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In create_archimate_diagram module :", __name__)
        raise error        

def add_process_view_diagram_nodes_contextfull(root):
    """
        I need add the nodes at the end of processing to calculate the x, y, w, h
    """
    try:
        #x: The x-coordinate of the top-left corner of the element. This determines the horizontal position of the element from the left side of the parent element or the screen.
        #y: The y-coordinate of the top-left corner of the element. This determines the vertical position of the element from the top of the parent element or the screen.
        #w: The width of the element. This determines how wide the element is.
        #h: The height of the element. This determines how tall the element is.
        
        # Get the elements from the root
        namespaces = {'': 'http://www.opengroup.org/xsd/archimate/3.0/'} 
        elements = root.findall(".//element")
        diagram_view = root.find(".//view[@identifier='id-view-ea-process-view']", namespaces)

        element_width = 100
        axis_width = 1200        
        distance_between_elements = 150
             
        # Count the number of elements that are of type BusinessProcess
        total_bp = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessProcess')     
        # Count the number of elements that are of type BusinessEvent
        total_be = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessEvent')
        # Count the number of elements that are of type BusinessActor
        total_ba = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessActor')

        # Initialize position variables
        bp_h = 150 # height of the BusinessProcess
        bp_w = 10 + total_be * 250 # width of the BusinessProcess
        be_w = 240 # width of the BusinessEvent
        
        x_offset = 100  # Initial x offset for positioning elements
        xy_increment = 100  # Increment for x and y position for each element
        y_ba = 50  # y position for BusinessActors
        y_bp = 50  # initial y position for BusinessProcess
        y_be = 100  # y position for BusinessEvents
        count_bp = 0
        count_be = 0
        count_ba = 0
        node_number = 0
        connection_number = 0
        be_antecedent_identifier = None
        business_process_list = []
        aux_matrix = {}
        x_aux = 50
        max = 0
        vx = 0
        actor_changes = 0
        antecedent_actor = None 

        root_copy = etree.fromstring(ET.tostring(root))
        #namespaces = {'ns': 'http://www.opengroup.org/xsd/archimate/3.0/'} 
        
        
        # Iterate over the elements
        for element in elements:
            element_type = element.get("xsi:type")
            # Check if the element is a BusinessProcess or BusinessEvent
            element_identifier = element.get('identifier')
            
            if element_type == "BusinessActor":
                #actor_changes = True
                count_ba += 1
                #x = x_offset + (count_ba * x_increment)
                x = 25
                total_y_bp = total_bp * (bp_h + xy_increment)
                fator_y = 1.5 / total_ba
                y_ba = total_y_bp * (fator_y / count_ba)
                y = int(y_ba)
                node_number += 1 
                node_identifier = f"id-node-all-{node_number}"
                diagram_view_node = ET.SubElement(diagram_view, "node", attrib={"identifier":node_identifier, "xsi:type":"Element", "elementRef":element_identifier, "x":str(x) , "y":str(y), "w":"120", "h":"50"})                                             
                # restart the x position of the Business Event
                #aux_matrix[event_process].update({"lastpos": 350}) 
                
            elif element_type == "BusinessProcess":
                business_process_list.append(element_identifier)
                count_bp += 1
                x = 350 
                if count_bp > 1:
                    y_bp = y_bp + bp_h + xy_increment
                y = int(y_bp)
                node_number += 1
                node_identifier = f"id-node-all-{node_number}"
                diagram_view_node = ET.SubElement(diagram_view, "node", attrib={"identifier":node_identifier, "xsi:type":"Element", "elementRef":element_identifier, "x":str(x) , "y":str(y), "w":str(bp_w), "h":str(bp_h)})                 
            
            elif element_type == "BusinessEvent":
                count_be += 1
                relationships = root.find(".//relationships", namespaces)
                for relationship in relationships:
                    if relationship.get("target") == element_identifier:
                        event_relation = relationship
                        break
                event_process = event_relation.get("source")
                #calculate x and y position
                if event_process not in aux_matrix:
                    # inicialize the posicioanment of the first event
                    aux_matrix[event_process] = {"lastpos": x_offset}                      
                
                lastpos = aux_matrix[event_process]["lastpos"] 
                     
                if actor_changes > 0:
                    # x_aux = x_offset + be_w + xy_increment 
                    # keys_to_remove = [key for key in aux_matrix.keys() if key != event_process]
                    # for key in keys_to_remove:
                    #     aux_matrix.pop(key)
                    # actor_changes = 0
                    # max = x_aux
                    actor_changes = 0
                    aux_matrix[event_process] = {"lastpos": x_offset}
                    max = x_offset
                else:
                    for i, j in aux_matrix.items():
                        if j["lastpos"] > max:
                            max = j["lastpos"]                     
                    if (lastpos < max):
                        print(f" mudou max: {lastpos} --> lastpos: {lastpos}")
                        x_aux = max 
                    else:
                        print(f" não mudou max: {max} --> lastpos: {lastpos}")
                        x_aux = lastpos + (be_w + xy_increment) 
                    
                x = int(x_aux)
                aux_matrix[event_process].update({"lastpos": x})                    
                        
                business_process_position = business_process_list.index(event_process) 
                y_be_aux = y_be     
                if business_process_position > 0:
                    y_be_aux =  y_be_aux + ((bp_h + xy_increment) * business_process_position) 
                y = int(y_be_aux)
                
                node_number += 1
                node_identifier = f"id-node-all-{node_number}"
                diagram_view_node = ET.SubElement(diagram_view, "node", attrib={"identifier":node_identifier, "xsi:type":"Element", "elementRef":element_identifier, "x":str(x) , "y":str(y), "w":str(be_w), "h":"50"})                                 
                
                relationship_id = f"id-relation-be-{count_be}"
                #relationships
                relationships = root.find(".//relationships", namespaces)
                if relationships is None:
                    relationships = ET.SubElement(root, "relationships")
                relationship_exists = None
                for relationship in relationships:
                    if relationship.get("identifier") == relationship_id:
                        relationship_exists = relationship
                        break   
                    
                if relationship_exists is None:
                    if be_antecedent_identifier is not None:
                        # verify it the antecedent and the element are connected to the same BusinessProcess and the process with the same BusinessActor
                        event_actor = None
                        antecedent_event_process = None
                                               
                        event_process = event_relation.get("source")
 
                        relationships = root.find(".//relationships", namespaces) 
                        for relationship in relationships:
                            if relationship.get("source") == event_process and relationship.get("xsi:type") == "Serving":
                                    target = relationship.get("target")
                                    if target.startswith("id-actor"):
                                        event_actor = target
                            if relationship.get("target") == be_antecedent_identifier:
                                #antecedent_relation = relationship
                                if relationship.get("source").startswith("id-process"):
                                    antecedent_event_process = relationship.get("source")
                                    
                                #antecedent_event_process = relationship.get("source")
                                antecedent_relation_actors = root.find(".//relationships", namespaces)
                                for antecedent_relation_actor in antecedent_relation_actors:
                                    #if antecedent_relation_actor.get("source") == antecedent_event_process and antecedent_relation_actor.get("xsi:type") == "Serving":
                                    if antecedent_relation_actor.get("source") == antecedent_event_process:
                                        target = antecedent_relation_actor.get("target")
                                        if target.startswith("id-actor"):
                                            antecedent_actor = target
                                         
                        if event_actor == antecedent_actor:
                            relationship = ET.SubElement(relationships, "relationship ", attrib={"identifier": relationship_id, "source": be_antecedent_identifier, "target": element_identifier, "xsi:type":"Flow" })                
                            relationship_name = ET.SubElement(relationship, "name")
                            relationship_name.text = relationship_id
                        else:
                            actor_changes = actor_changes + 1
              
                be_antecedent_identifier = element_identifier

        # create the connections
        nodes = root.findall(".//node")
        for node in nodes:
            element_ref = node.get('elementRef')
            #relationships = root.find("relationships")
            relationships = root.find(".//relationships", namespaces) 
            for relationship in relationships:
                # source and target need to be different
                rel_source = relationship.get("source")
                rel_target = relationship.get("target")
                if rel_source != element_ref:
                    continue
                                
                relationship_id = relationship.get("identifier")
                source_node = node.get('identifier')
                if not source_node.startswith("id-node-all"):
                    continue
                
                target_node_obj = root.find(".//node[@elementRef='"+ rel_target +"']")
                target_node = target_node_obj.get('identifier')
                if target_node is None:
                    continue
                
                # if source is BusinessProcess and target is BusinessEvent dont create the connection
                source_node_obj = root.find(".//node[@elementRef='"+ rel_source +"']") 
                source_element_ref = source_node_obj.get('elementRef')               
                #source_element = root.find(f".//elements/element[@identifier='{source_element_ref}']", namespaces)
                #source_element = root.findall(f".//element[@identifier='{source_element_ref}']", namespaces)
                #elements = root.find(".//elements", namespaces)
                source_element = None
                elements = root.findall(".//element")
                for el in elements:
                    if el.get("identifier") == source_element_ref:
                        source_element = el
                        break
                target_element_ref = target_node_obj.get('elementRef')
                #target_element = root.find(f".//elements/element[@identifier='{target_element_ref}']", namespaces)
                target_element = None
                for el_t in elements:
                    if el_t.get("identifier") == target_element_ref:
                        target_element = el_t
                        break                
                if source_element is not None and target_element is not None:
                    source_type = source_element.get('xsi:type')
                    target_type = target_element.get('xsi:type')
                    if source_type == "BusinessProcess" and target_type == "BusinessEvent":
                        # Skipping connection creation: source is BusinessProcess and target is BusinessEvent")
                        continue
                
                connection_number += 1
                connection_idenfitier = f"id-connection-all-{connection_number}"
                diagram_view_connection = ET.SubElement(diagram_view, "connection", attrib={"identifier": connection_idenfitier, "xsi:type":"Relationship", "source":source_node, "target":target_node, "relationshipRef":relationship_id})
        
        return root
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In create_archimate_diagram module :", __name__)
        raise error        
    
def add_process_view_diagram_nodes(root):
    """
        I need add the nodes at the end of processing to calculate the x, y, w, h
    """
    try:
        #x: The x-coordinate of the top-left corner of the element. This determines the horizontal position of the element from the left side of the parent element or the screen.
        #y: The y-coordinate of the top-left corner of the element. This determines the vertical position of the element from the top of the parent element or the screen.
        #w: The width of the element. This determines how wide the element is.
        #h: The height of the element. This determines how tall the element is.
        
        #print_root_xml(root)    
        # Get the elements from the root
        elements = root.findall(".//element")
        diagram_view = root.find(".//view[@identifier='id-view-ea-process-view']")

        element_width = 100
        axis_width = 1200        
        distance_between_elements = 150
        
        # Count the number of elements that are of type BusinessProcess
        total_bp = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessProcess')     
        # Count the number of elements that are of type BusinessEvent
        total_be = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessEvent')
        # Count the number of elements that are of type BusinessActor
        total_ba = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessActor')

        if total_bp == 0:
            print("No BusinessProcess elements found in the model in add_process_view_diagram_nodes(root).")
            return root
        
        # Initialize position variables
        
        level_bp = 0
        level_be = 0
        y_offset = int((total_be // total_bp) * 100)
        y_bp = 400
        y_be = 10
        y_ba = int((400 * total_bp) / 2)
        y_ba_offset = int((total_bp // total_ba) * 100)
        count_bp = 0
        count_be = 0
        count_ba = 0
        node_number = 0
        bp_relationships = None
        connection_number = 0
        be_antecedent_identifier = None
        antecedent_node_identifier = None

        root_copy_xpaths = etree.fromstring(ET.tostring(root))
        namespaces = {'ns': 'http://www.opengroup.org/xsd/archimate/3.0/'} 
        
        # Iterate over the elements
        for element in elements:
            element_type = element.get("xsi:type")
            # Check if the element is a BusinessProcess or BusinessEvent
            element_identifier = element.get('identifier')
            if element_type == "BusinessProcess":
                count_bp += 1
                level_bp += 1
                if level_bp > 1:
                    y_bp += y_offset
                y = y_bp
                x = 250 
                node_number += 1
                node_identifier = f"id-node-{node_number}"
                diagram_view_node = ET.SubElement(diagram_view, "node", attrib={"identifier":node_identifier, "xsi:type":"Element", "elementRef":element_identifier, "x":str(x) , "y":str(y), "w":"120", "h":"50"})  
                be_antecedent_identifier = None # reset the antecedent identifier
            elif element_type == "BusinessEvent":
                count_be += 1
                x = 500
                y_be = y_be + 100
                y = y_be  # Set y position for BusinessEvent elements 
                
                #creating node
                node_number += 1
                node_identifier = f"id-node-{node_number}"
                diagram_view_node = ET.SubElement(diagram_view, "node", attrib={"identifier":node_identifier, "xsi:type":"Element", "elementRef":element_identifier, "x":str(x) , "y":str(y), "w":"240", "h":"50"})                                 
                
                #creating the relationship flow
                event_number = f"be-{count_be}"
                relationship_id = f"id-relation-{event_number}"
                #relationships
                relationships = root.find("relationships")
                #relationships = root.find("ns:relationships", namespaces=namespaces)
                if relationships is None:
                    relationships = ET.SubElement(root, "relationships")
                relationship_exists = root.find(f".//relationship[@identifier='{relationship_id}']")
                #relationship_exists = root.find(f".//ns:relationship[@identifier='{relationship_id}']", namespaces=namespaces)
                
                if relationship_exists is None:
                    if be_antecedent_identifier is not None:
                        #TODO verificar se o antecedente e o elemento estão conectados ao mesmo BusinessProcess
                        #target_value = 'id-event-2'
                        # verify it the antecedent and the element are connected to the same BusinessProcess
                        #event_relation = root.find(f".//relationship[@target='{element_identifier}']")
                        event_relation = root_copy_xpaths.xpath(f".//ns:relationship[@target='{element_identifier}']", namespaces=namespaces)
                        antecedent_relation = root_copy_xpaths.xpath(f".//ns:relationship[@target='{be_antecedent_identifier}']", namespaces=namespaces)
                        event_process = event_relation[0].get("source")
                        antecedent_event_process = antecedent_relation[0].get("source")
                        if event_process == antecedent_event_process:
                            relationship = ET.SubElement(relationships, "relationship ", attrib={"identifier": relationship_id, "source": be_antecedent_identifier, "target": element_identifier, "xsi:type":"Flow" })                
                            relationship_name = ET.SubElement(relationship, "name")
                            relationship_name.text = relationship_id
                        # criar connection
                    # if antecedent_node_identifier is not None:
                    #     connection_number += 1
                    #     connection_idenfitier = f"id-connection-{connection_number}"
                    #     diagram_view_connection = ET.SubElement(diagram_view, "connection", attrib={"identifier": connection_idenfitier, "xsi:type":"Relationship", "source":antecedent_node_identifier, "target":node_identifier, "relationshipRef":relationship_id})
                be_antecedent_identifier = element_identifier
                #antecedent_node_identifier = node_identifier
            if element_type == "BusinessActor":
                count_ba += 1
                y_ba = y_ba + y_ba_offset
                y = y_ba
                x = 50 
                node_number += 1
                node_identifier = f"id-node-{node_number}"
                diagram_view_node = ET.SubElement(diagram_view, "node", attrib={"identifier":node_identifier, "xsi:type":"Element", "elementRef":element_identifier, "x":str(x) , "y":str(y), "w":"120", "h":"50"})                                 

        # create the connections
        nodes = root.findall(".//node")
        for node in nodes:
            element_ref = node.get('elementRef')
            #relationshipsall = root.findall(".//relationship[@source='"+ element_ref +"']") 
            relationshipsall = root.find(".//relationship[@source='"+ element_ref +"']") 
            #print(f"Relationships: {relationshipsall}")
            relationships = root.find("relationships")
            for relationship in relationships:
                
                rel_source = relationship.get("source")
                rel_target = relationship.get("target")
                if rel_source != element_ref:
                    continue
                
                relationship_id = relationship.get("identifier")
                source_node = node.get('identifier')
                target_node_obj = root.find(".//node[@elementRef='"+ rel_target +"']")
                target_node = target_node_obj.get('identifier')
                if target_node is None:
                    continue
                
                connection_number += 1
                connection_idenfitier = f"id-connection-{connection_number}"
                diagram_view_connection = ET.SubElement(diagram_view, "connection", attrib={"identifier": connection_idenfitier, "xsi:type":"Relationship", "source":source_node, "target":target_node, "relationshipRef":relationship_id})
        
        return root
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In create_archimate_diagram module :", __name__)
        raise error        
   
   

# def print_root_xml(root):
        
#         clone_root = root
#         xml_string = ET.tostring(clone_root,encoding='utf-8').decode('utf-8')
#         # Parse the XML string and convert it to a pretty-printed XML string
#         dom = xml.dom.minidom.parseString(xml_string)
#         pretty_xml_string = dom.toprettyxml()
#         # Print the pretty-printed XML string
#         #print("#################### pretty_xml_string ##########################")
#         #print(pretty_xml_string)
#         #print("#################### pretty_xml_string ##########################") 
#         return pretty_xml_string       
    
        
def extract_archimate_process(file_name):
    """
        Extract the process from the ontology and create the xml element
    """
    try:
        #root = prepare_archimate_exchange_model()
        # root = archimate_util.prepare_archimate_exchange_model()
        root = archimate_util.load_archimate_model_xml(file_name)
        processes = get_process_from_ontology()
        root = add_archimate_process_elements(root, processes)
        root = add_process_view_diagram_nodes(root)
        # print_root_xml(root)
        archimate_util.save_archimate_exchange_model(root) 
        isValid = archimate_util.check_archimate_model_exchange_xml      
        if isValid:
            print("The XML document is well-formed.")
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In extract_archimate_process module :", __name__)
        raise error           

def extract_archimate_process_contexfull(file_name):
    """
        Extract the process from the ontology and create the xml element grouping processes by API Contexts
    """
    try:
        #root = prepare_archimate_exchange_model()
        #root = archimate_util.prepare_archimate_exchange_model()
        root = archimate_util.load_archimate_model_xml(file_name)
        #archimate_util.print_root_xml(root)
        processes = get_process_from_ontology()
        root, contextfull_process = add_archimate_process_elements(root, processes)
        if contextfull_process == True:
            root = add_process_view_diagram_nodes_contextfull_by_actor(root)
            root = add_process_view_diagram_nodes_contextfull(root)
        else:
            root = add_process_view_diagram_nodes(root)
        #archimate_util.print_root_xml(root)
        #save_archimate_exchange_model(root, file_name) 
        archimate_util.save_archimate_exchange_model(root, file_name)
        isValid = archimate_util.check_archimate_model_exchange_xml(file_name)      
        if isValid:
            print("The XML document is well-formed.")
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In extract_archimate_process module :", __name__)
        raise error     