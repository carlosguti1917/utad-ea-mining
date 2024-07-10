import pandas as pd
import re
from owlready2 import *
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

def save_archimate_exchange_model(root):
# Create the XML tree and write it to a file
    try:
        #tree = ET.ElementTree(root)
        xml_string = ET.tostring(root,encoding='utf-8').decode('utf-8')

        # Parse the XML string and convert it to a pretty-printed XML string
        dom = xml.dom.minidom.parseString(xml_string)
        pretty_xml_string = dom.toprettyxml()
        # Print the pretty-printed XML string
        # print("#################### pretty_xml_string ##########################")
        # print(pretty_xml_string)
        # Save the XML string to a file
        file_path = configs.ARCHIMATE_MODEL["file_path"]        
        file_name = configs.ARCHIMATE_MODEL["archimate_file_name"]
        # Check if the directory exists
        if not os.path.exists(file_path):
            # If the directory doesn't exist, create it
            os.makedirs(file_path)        
        with open(file_path+file_name, "wb") as f:
            f.write(pretty_xml_string.encode('utf-8'))
            
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In save_archimate_exchange_model module :", __name__)
        raise error        

def prepare_archimate_exchange_model():
    """
        prepare the inicial xml of the archimate model
        returns:
            file: xml.etree.ElementTree (named as root)
    """
    try:
        # Create the root element for the ArchiMate model
        root = ET.Element("model", attrib={
            "xmlns": "http://www.opengroup.org/xsd/archimate/3.0/",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd",
            "identifier": "id-ea-mining-exchange-model-1",
        })

        # Add the name element to the root element
        name = ET.SubElement(root, "name", attrib={"xml:lang": "en"})
        name.text = "EA Mining Exchange Model"
        documentation = ET.SubElement(root, "documentation", attrib={"xml:lang": "en"})
        documentation.text = "Model generated by IA mining process to be imported in ArchiMate Tool."
        
        elements = ET.SubElement(root, "elements")
        relationships = ET.SubElement(root, "relationships")
        
        # Create the view and diagram
        views = ET.SubElement(root, "views")
        # view = ET.SubElement(views, "view", attrib={"name": "API extracted process"})
        diagrams= ET.SubElement(views, "diagrams")
        diagram_view = ET.SubElement(diagrams, "view", attrib={"identifier": "id-view-ea-process-view", "viewpoint":"Application Usage", "xsi:type":"Diagram"})
        diagram_view_name = ET.SubElement(diagram_view, "name", attrib={"xml:lang": "en"})
        diagram_view_name.text = "API extracted process view"
        diagram_view_documentation = ET.SubElement(diagram_view, "documentation", attrib={"xml:lang": "en"})
        diagram_view_documentation.text = "Process View Mined from API Logs."   
        
        diagram_dr_view = ET.SubElement(diagrams, "view", attrib={"identifier": "id-view-ea-data-relation-view", "viewpoint":"Application Usage", "xsi:type":"Diagram"})
        diagram_view_name = ET.SubElement(diagram_dr_view, "name", attrib={"xml:lang": "en"})
        diagram_view_name.text = "API extracted Data Relation view"
        diagram_view_documentation = ET.SubElement(diagram_dr_view, "documentation", attrib={"xml:lang": "en"})
        diagram_view_documentation.text = "Data Relation View Mined from API Logs."              
        
        return root
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In prepare_archimate_exchange_model module :", __name__)
        raise error
    
def add_archimate_process_elements(root, processes):   
    """
        Create the xml element for the process
    """
    try:
        elements = root.find("elements")
        if elements is None:
            elements = ET.SubElement(root, "elements")
        
        process_element_number = 0 
        event_number = 0
        for process_tuple in processes:
            process_element_number += 1
            process = process_tuple[0]
            process_id = process.name.replace("/", "-").replace("_", "")
            process_identifier = f"id-process-{process_element_number}"
            process_exists = elements.find(f".//element[@identifier='{process_identifier}']")
            label_parts = process.label[0].split(': ')
            if len(label_parts) > 1:
                process_name_text = label_parts[1]
            else:
                process_name_text = process.label[0]
            if process_exists is None:
                process_element = ET.SubElement(elements, "element", attrib={"identifier": process_identifier, "xsi:type": "BusinessProcess"})
                process_name = ET.SubElement(process_element, "name")
                process_name.text = process_name_text  
                root = add_archimate_actors_to_process(root, process, process_identifier)
            
            root, event_number = add_archimate_event_process_elements(root, process_identifier, process_name_text, event_number)   
        
        return root
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In add_archimate_process_elements module :", __name__)
        raise error

def add_archimate_actors_to_process(root, process, process_identifier):
    try:
        labels  = process.label
        for label in labels:
            label_parts = label.split(': ')
            part0 = label_parts[0]
            if part0 != "partner":
                continue
            actor_name = label_parts[1]
            actor_identifier = f"id-actor-{actor_name}"
            elements = root.find("elements")
            if elements is None:
                elements = ET.SubElement(root, "elements")
            actor_exists = elements.find(f".//element[@identifier='{actor_identifier}']")
            if actor_exists is None:
                actor_element = ET.SubElement(elements, "element", attrib={"identifier": actor_identifier, "xsi:type": "BusinessActor"})
                actor_element_name = ET.SubElement(actor_element, "name")
                actor_element_name.text = actor_name
            #relationships
            relationships = root.find("relationships")
            if relationships is None:
                relationships = ET.SubElement(root, "relationships")            
            relationship_id = f"id-relation-{actor_name}-{process_identifier}"
            relationship_exists = root.find(f".//relationship[@identifier='{relationship_id}']")
            if relationship_exists is None:
                relationship = ET.SubElement(relationships, "relationship ", attrib={"identifier": relationship_id, "source": process_identifier, "target": actor_identifier, "xsi:type":"Serving" })                
                relationship_name = ET.SubElement(relationship, "name")
                relationship_name.text = relationship_id
        
        return root
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In create_archimate_actors_to_process module :", __name__)
        raise error

def add_archimate_event_process_elements(root, process_identifier, process_name, event_number):   
    """
        Create the xml element for the process
    """
    try:
        elements = root.find("elements")
        if elements is None:
            elements = ET.SubElement(root, "elements")
            
        # Load the HeuristicsNet object from the file
        directory = "./temp/process/"       
        with open(f"{directory}heuristics_net_{process_name}.pkl", 'rb') as f:
            heu_net = pickle.load(f)
        #pm4py.view_heuristics_net(heu_net)  
        
        # Get the activities from the HeuristicsNet
        activities = heu_net.activities
        # for activity_name, activity_id in activities:
        for activity in activities:
            event_number += 1
            # activity_name = activity.name
            # activity_id = activity.id
            # print(f"Activity name: {activity_name}, Activity ID: {activity_id}")
            # Create the Business Event elements
            activity_id =  activity.replace("/", "-").replace("_", "")
            event_identifier = f"id-event-{event_number}"
            event_exists = elements.find(f".//element[@identifier='{event_identifier}']")
            if event_exists is None:
                event_element = ET.SubElement(elements, "element", attrib={"identifier": event_identifier, "xsi:type": "BusinessEvent" })
                event_element_name = ET.SubElement(event_element, "name")
                event_element_name.text = activity
            
            #relationships
            relationships = root.find("relationships")
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
            elif element_type == "BusinessEvent":
                count_be += 1
                x = 500
                y_be = y_be + 100
                y = y_be  # Set y position for BusinessEvent elements 
                
                #creating node
                node_number += 1
                node_identifier = f"id-node-{node_number}"
                diagram_view_node = ET.SubElement(diagram_view, "node", attrib={"identifier":node_identifier, "xsi:type":"Element", "elementRef":element_identifier, "x":str(x) , "y":str(y), "w":"240", "h":"50"})                                 
                
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
                        target_value = 'id-event-2'
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
   
   

def print_root_xml(root):
        
        clone_root = root
        xml_string = ET.tostring(clone_root,encoding='utf-8').decode('utf-8')
        # Parse the XML string and convert it to a pretty-printed XML string
        dom = xml.dom.minidom.parseString(xml_string)
        pretty_xml_string = dom.toprettyxml()
        # Print the pretty-printed XML string
        #print("#################### pretty_xml_string ##########################")
        #print(pretty_xml_string)
        #print("#################### pretty_xml_string ##########################") 
        return pretty_xml_string       
    
        
def extract_archimate_process():
    """
        Extract the process from the ontology and create the xml element
    """
    try:
        root = prepare_archimate_exchange_model()
        processes = get_process_from_ontology()
        root = add_archimate_process_elements(root, processes)
        root = add_process_view_diagram_nodes(root)
        # print_root_xml(root)
        save_archimate_exchange_model(root) 
        isValid = archimate_util.check_archimate_model_exchange_xml      
        if isValid:
            print("The XML document is well-formed.")
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In extract_archimate_process module :", __name__)
        raise error           
    