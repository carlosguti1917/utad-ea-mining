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
from api_gateway_load import configs
from api_gateway_load.utils import onto_util

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
            process_name_text = label_parts[1]
            if process_exists is None:
                process_element = ET.SubElement(elements, "element", attrib={"identifier": process_identifier, "xsi:type": "BusinessProcess"})
                process_name = ET.SubElement(process_element, "name")
                process_name.text = process_name_text  
            
            # actor = process.actor
            # root = add_archimate_actors_to_process(root, actor)
            root, event_number = add_archimate_event_process_elements(root, process_identifier, process_name_text, event_number)   
        
        #save_archimate_exchange_model(root)
        # relationships = root.find("relationships")
        # # relationships = root.find('relationships')
        # if relationships is not None:
        #     # Iterate through child elements (relationships)
        #     for relationship in relationships:
        #         # Access attributes and child elements of each relationship
        #         print(relationship.tag, relationship.attrib)
        #         source = relationship.attrib['source']
        #         target = relationship.attrib['target']
        
        return root
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In create_archimate_process_elements module :", __name__)
        raise error

def add_archimate_actors_to_process(root, process):
    try:
        pass
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
        with open(f"{directory}heuristics_net{process_name}.pkl", 'rb') as f:
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
                relationship = ET.SubElement(relationships, "relationship ", attrib={"identifier": relationship_id, "source": process_identifier, "target": event_identifier, "xsi:type":"Serving" })                
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
        #diagram_view = root.find(".//view")
        #diagram_view = root.find(".//id-view-ea-process-view")
        diagram_view = root.find(".//view[@identifier='id-view-ea-process-view']")

        element_width = 100
        axis_width = 1200        
        distance_between_elements = 150
        
        # Count the number of elements that are of type BusinessProcess
        total_bp = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessProcess')
        print(f"Number of elements of type BusinessProcess: {total_bp}")   
        # available_space_bp = axis_width - (total_bp * (element_width + distance_between_elements))
        # if available_space_bp < 0:
        #     raise ValueError("Not enough space for all BusinessProcess elements with the given distance.")         
        # center_position_bp = axis_width // 2
        # half_available_space = available_space_bp // 2
        #starting_position = center_position_bp - half_available_space
        # while True:
        #     available_space_bp = axis_width - (total_bp * (element_width + distance_between_elements))  
        #     if available_space_bp < 0:
        #         total_bp = total_bp / 2
        #     else:
        #         break          
        # starting_x_bp = int((axis_width // total_bp) - (element_width // 2))
        
        # Count the number of elements that are of type BusinessEvent
        total_be = sum(1 for element in elements if element.attrib.get('xsi:type') == 'BusinessEvent')
        print(f"Number of elements of type BusinessProcess: {total_be}")   
        # available_space_be = axis_width - (total_be * (element_width + distance_between_elements))
        # if available_space_be < 0:
        #     print("Not enough space for all BusinessEvents elements with the given distance.")         
        # center_position_be = axis_width // 2
        # half_available_space_be = available_space_be // 2
        # while True:
        #     available_space_be = axis_width - (total_be * (element_width + distance_between_elements))  
        #     if available_space_be < 0:
        #         total_be = total_be / 2
        #     else:
        #         break            
        # starting_x_be = int((axis_width // total_be) - (element_width // 2))
        
        
        # Initialize position variables
        
        level_bp = 0
        level_be = 0
        y_offset = ((total_be // total_bp) * 100)
        y_bp = 400
        y_be = 10
        count_bp = 0
        count_be = 0
        node_number = 0
        bp_relationships = None
        connection_number = 0
        be_antecedent_identifier = None
        antecedent_node_identifier = None

        root_copy_xpaths = etree.fromstring(ET.tostring(root))
        namespaces = {'ns': 'http://www.opengroup.org/xsd/archimate/3.0/'} # replace with your namespace URI
        #element = root.xpath(".//ns:element[@name='specific_name']", namespaces=namespaces)
        #event_relation4 = root_copy_xpaths.xpath(f".//ns:relationship[@target='id-event-2']", namespaces=namespaces)
        
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
                diagram_view_node = ET.SubElement(diagram_view, "node", attrib={"identifier":node_identifier, "xsi:type":"Element", "elementRef":element_identifier, "x":str(x) , "y":str(y), "w":"120", "h":"50"})                                 
                
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
                                   
               

        nodes = root.findall(".//node")
        for node in nodes:
            element_ref = node.get('elementRef')
            #relationshipsall = root.findall(".//relationship[@source='"+ element_ref +"']") 
            relationshipsall = root.find(".//relationship[@source='"+ element_ref +"']") 
            print(f"Relationships: {relationshipsall}")
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
        print("#################### pretty_xml_string ##########################")
        print(pretty_xml_string)
        print("#################### pretty_xml_string ##########################") 
        return pretty_xml_string       
    
def check_xml():
    # Parse the XML string and convert it to a pretty-printed XML string
    
    file_path = configs.ARCHIMATE_MODEL["file_path"]        
    file_name = configs.ARCHIMATE_MODEL["archimate_file_name"]
    # Check if the directory exists
    # with open(file_path+file_name, "rb") as f:
    #     f.load(pretty_xml_string.encode('utf-8'))
    
    # Parse the XML document and get the root element
    tree = ET.parse(file_path+file_name)
    root = tree.getroot()
    
    xml_string = ET.tostring(root, encoding='utf-8').decode('utf-8')

    dom = xml.dom.minidom.parseString(xml_string)
    pretty_xml_string_copy = dom.toprettyxml()

    # Check if the XML document is well-formed
    try:
        etree.fromstring(pretty_xml_string_copy)
        print("The XML document is well-formed.")
        return True
    except etree.XMLSyntaxError:
        print("The XML document is not well-formed.")
        
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
        isValid = check_xml()       
        if isValid:
            print("The XML document is well-formed.")
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In extract_archimate_process module :", __name__)
        raise error           
    

if __name__ == "__main__":
    extract_archimate_process()    