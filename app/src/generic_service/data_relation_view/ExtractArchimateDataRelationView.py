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
from app.src.utils import ai_gen_util

onto_path.append("app/src/api_gateway_load/repository/") 
onto = get_ontology(configs.OWL_FILE["file_name"]).load()
ns_gufo = onto.get_namespace("http://purl.org/nemo/gufo#")
ns_core = onto.get_namespace("http://eamining.edu.pt/core#")
ns_data_relation_view = onto.get_namespace("http://eamining.edu.pt/data-relation-view#")

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

     

def add_archimate_data_relation_element(cdo_list, file_name=None):   
    """
        Create the xml element for the each element in the correlated_data_objects_list
    """
    #root = old_root
    root = archimate_util.load_archimate_model_xml(file_name)
    try:

        namespaces = {'': 'http://www.opengroup.org/xsd/archimate/3.0/'}  
        elements = root.find(".//elements", namespaces)   
        #print("Elements: ", len(elements))     

        if elements is None:
            elements = ET.SubElement(root, "elements")
        
        domain_element_number = 0
        entity_number = 0
        #relation_number = sum(1 for element in elements if element.get('identifier').startswith("id-relation")) 
        relation_number = 0
        domain_list = []
        entity_list = []
        
        for cdo in cdo_list:
            # add domain elements to the achinmate model
            domain_name = cdo.domain_name[0]           
            if not domain_name in domain_list:
                domain_element_number += 1
                domain_identifier = f"id-domain-{domain_element_number}"                
                domain_element = ET.SubElement(elements, "element", attrib={"identifier": domain_identifier, "xsi:type": "DataObject"} )
                domain_element_name = ET.SubElement(domain_element, "name")
                #domain_element_name.text = domain_name  
                domain_element_name.text = ai_gen_util.translate_resource_to_entity_name(entity_name)
                domain_list.append(domain_name)

            # add entity elements to the achinmate model
            entity_name = cdo.entity_name[0]
            if not entity_name in entity_list:
                entity_number += 1
                entity_identifier = f"id-entity-{entity_number}"
                entity_element = ET.SubElement(elements, "element", attrib={"identifier": entity_identifier, "xsi:type": "DataObject" })
                entity_element_name = ET.SubElement(entity_element, "name")
                #entity_element_name.text = entity_name
                entity_element_name.text= ai_gen_util.translate_resource_to_entity_name(entity_name)
                entity_list.append(entity_name) 
                
                # add relationships to the achinmate model
                relationships = root.find(".//relationships", namespaces) 
                if relationships is None:
                    relationships = ET.SubElement(root, "relationships") 
                
                relationship_id = f"id-relation-de-{relation_number}" # de = domain-entity
                relationship_exists = root.find(f".//relationship[@identifier='{relationship_id}']", namespaces)
                if relationship_exists is None:
                    relation_number += 1 
                    relationship_id = f"id-relation-de-{relation_number}" # de = domain-entity
                    relationship = ET.SubElement(relationships, "relationship ", attrib={"identifier": relationship_id, "source": domain_identifier, "target": entity_identifier, "xsi:type":"Aggregation" })                
                    relationship_name = ET.SubElement(relationship, "name")
                    relationship_name.text = relationship_id                                            
        
        elements_check = root.find(".//elements", namespaces) 
        print("Elements: ", len(elements_check))
        print("Elements: ", len(elements))
        archimate_util.save_archimate_exchange_model(root, file_name)
        return root
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In add_archimate_data_relation_element module :", __name__)
        raise error
    

    
def add_data_relation_view_diagram_nodes(file_name):
    """
        It add the nodes to the data relation view diagram
        It need add the nodes at the end of processing to calculate the x, y, w, h
    """
    root = archimate_util.load_archimate_model_xml(file_name)
    
    try:
        #x: The x-coordinate of the top-left corner of the element. This determines the horizontal position of the element from the left side of the parent element or the screen.
        #y: The y-coordinate of the top-left corner of the element. This determines the vertical position of the element from the top of the parent element or the screen.
        #w: The width of the element. This determines how wide the element is.
        #h: The height of the element. This determines how tall the element is.
        
        #archimate_util.print_root_xml(root)    
        # Get the elements from the root
        namespaces = {'': 'http://www.opengroup.org/xsd/archimate/3.0/'}         
        elements = root.findall(".//elements/element", namespaces)
        print("Elements: ", len(elements))
        diagram_view = root.find(".//view[@identifier='id-view-ea-data-relation-view']", namespaces)
        # if diagram_view is None create it       
        if diagram_view is None:
            views = root.find('.//views', namespaces)
            if views is None:
                views = ET.SubElement(root, 'views')
            diagrams = views.find('.//diagrams', namespaces)
            if diagrams is None:
                diagrams = ET.SubElement(views, 'diagrams')
            diagram_view = ET.SubElement(diagrams, "view", attrib={"identifier": "id-view-ea-data-relation-view", "viewpoint":"Application Usage", "xsi:type":"Diagram"})
            diagram_view_name = ET.SubElement(diagram_view, "name", attrib={"xml:lang": "en"})
            diagram_view_name.text = "API extracted Data Relation view"
            diagram_view_documentation = ET.SubElement(diagram_view, "documentation", attrib={"xml:lang": "en"})
            diagram_view_documentation.text = "Data Relation View Mined from API Logs."                    
        

        element_width = 100
        axis_width = 1200        
        distance_between_elements = 150
        
        # Count the number of elements that are domain
        total_domains = sum(1 for element in elements if element.get('identifier') and element.get('identifier').startswith("id-domain")) 
        total_entities = sum(1 for element in elements if element.get('identifier') and element.get('identifier').startswith("id-entity"))
        connections = root.findall(".//views/diagrams/view/connection", namespaces) 
        connection_number = max(
            (int(connection.get('identifier').split('-')[-1]) for connection in connections if connection.get('identifier') and connection.get('identifier').startswith("id-connection-")),
            default=0 
        )
        
        # Initialize position variables       
        #y_offset = int((total_entities // total_domains) * 100)
        y_domain = 1
        y_entity = 10
        count_domain = 0
        count_entity = 0
        node_number = 0
        nodes = root.findall(".//views/diagrams/view/node", namespaces)        
        #node_number = max(int(node.get('identifier').split('-')[-1]) for node in nodes if node.get('identifier').startswith("id-node-"))
        node_number = max(
            (int(node.get('identifier').split('-')[-1]) for node in nodes if node.get('identifier') and node.get('identifier').startswith("id-node-")),
            default=0 
        )        
                
        # Iterate over the elements
        for element in elements:
            # Check if the element is a domain or entity
            element_identifier = element.get('identifier')           
            if element_identifier and element_identifier.startswith("id-entity"):
                entity_ref_identifier = element_identifier
                count_entity += 1
                x = 500
                y_entity = y_entity + 100
                y = y_entity   
                node_number += 1
                entity_node_identifier = f"id-node-{node_number}"
                diagram_view_node = ET.SubElement(diagram_view, "node", attrib={"identifier":entity_node_identifier, "xsi:type":"Element", "elementRef":entity_ref_identifier, "x":str(x) , "y":str(y), "w":"120", "h":"50"})                                 
                #entity_number = f"entity-{count_entity}"
                #relationship_id = f"id-relation-{entity_number}"
            elif element_identifier and element_identifier.startswith("id-domain"):
                domain_ref_identifier = element_identifier
                count_domain += 1
                #y_domain += y_offset
                relationships_number = root.findall(".//relationship[@source='"+ element_identifier +"']", namespaces) 
                print("Relationships: ", len(relationships_number))
                y_domain = y_entity + len(relationships_number) * 50
                y = y_domain
                x = 250 
                node_number += 1
                domain_node_identifier = f"id-node-{node_number}"               
                diagram_view_node = ET.SubElement(diagram_view, "node", attrib={"identifier":domain_node_identifier, "xsi:type":"Element", "elementRef":domain_ref_identifier, "x":str(x) , "y":str(y), "w":"120", "h":"50"})                 
                
        # create the connections
        nodes = root.findall(".//node")
        for node in nodes:
            element_ref = node.get('elementRef')
            if not (element_ref.startswith("id-domain") or element_ref.startswith("id-entity")):
                continue
            relationships = root.findall(".//relationship[@source='"+ element_ref +"']", namespaces) 
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
        
        archimate_util.save_archimate_exchange_model(root)
        return root
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In create_archimate_diagram module :", __name__)
        raise error        
   
        
def extract_archimate_data_relation_view(file_name):
    """
        Extract the archimate data relation view from the ontology and create the xml element
    """
    try:
        # get Correlated Data Objects
        cdo_list = list(onto.search(type=ns_data_relation_view.CorrelatedDataObjects))
        root_dr = add_archimate_data_relation_element(cdo_list, file_name)

        root_diagram = add_data_relation_view_diagram_nodes(file_name)
        # archimate_util.print_root_xml(root_diagram)  
 
        isValid = archimate_util.check_archimate_model_exchange_xml(file_name)       
        if isValid:
            print("The XML document is well-formed.")
            
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In extract_archimate_data_relation_view() module :", __name__)
        raise error           
    
