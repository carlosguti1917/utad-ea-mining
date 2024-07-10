import os
import json
import yaml
from owlready2 import *
import sys # Add missing import statement for sys module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..", "..")))
from app.src import configs
from app.src.utils import spmf_converter
from app.src.utils import onto_util
from app.src.utils import open_api_util

onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
onto = get_ontology(configs.OWL_FILE["file_name"]).load()
ns_gufo = onto.get_namespace("http://purl.org/nemo/gufo#")
ns_core = onto.get_namespace("http://eamining.edu.pt/core#")
ns_data_relation_view = onto.get_namespace("http://eamining.edu.pt/data-relation-view#")

# get ontology
onto = get_ontology("http://eamining.edu.pt")
onto.load()


def get_api_documentations_from_files(onto):
    
    doc_list = []
    # Load all Swagger files
    file_path = configs.SWAGGERS_FILE_PATH["file_path"]
    #file_path =  "./docs/tests/" # for tests only
        
    try: 
        with onto:
            for filename in os.listdir(file_path):
                print(filename)
                if filename.endswith('.yaml'):
                    with open(os.path.join(file_path, filename), 'r') as f:
                        data = yaml.safe_load(f)
                        # Extract the necessary information
                        servers_url = []
                        servers = data['servers']
                        if not servers:
                            break
                                        
                        # Create the OWL elements and associate the reserouce schema
                        cls = ns_core.APIDocumentation
                        api_doc_name = f"{data['info']['title']} {data['info']['version']}"
                        api_documentation = onto_util.get_individual(onto, cls, 'http://eamining.edu.pt/', api_doc_name) 
                        if api_documentation is None:                           
                            api_documentation = ns_core.APIDocumentation(api_doc_name)
                            for server in servers:          
                                api_documentation.api_documentation_url.append(server['url'])
                                        
                        # add resources schema to the ontology API Documentation
                        for path, path_data in data['paths'].items():
                            for method, method_data in path_data.items():
                                #full_resource_uri = api_documentation_url + path
                                #print(f"method_data {method_data}")
                                print(f"path_data {path}")
                                resource_uri = path
                                if method == 'get':
                                    if '200' in method_data['responses']:
                                        if 'content' in method_data['responses']['200']:
                                            api_component = method_data['responses']['200']['content']['application/json']['schema']
                                    elif '201' in method_data['responses']:
                                        if 'content' in method_data['responses']['201']:
                                            api_component = method_data['responses']['201']['content']['application/json']['schema']                                
                                    elif '202' in method_data['responses']:
                                        if 'content' in method_data['responses']['202']:
                                            api_component = method_data['responses']['202']['content']['application/json']['schema']  
                                    else:
                                        break
                                if method == 'post' or method == 'put' or method == 'patch':
                                    if 'requestBody' not in method_data:
                                        print(f"requestBody not found {method_data}")
                                        break
                                    if 'content' in method_data['requestBody']:
                                        # for tests only application/json is considered. However, it is necessary to consider other types
                                        if 'content' in method_data['requestBody'] and 'application/json' in method_data['requestBody']['content']:
                                            api_component = method_data['requestBody']['content']['application/json']['schema']
                                        else:
                                            break
                                    else:
                                        break
                                                                                            
                                api_component_schema = json.dumps(api_component)
                                                    
                                # Get the schema definition from the components section
                                if not 'items' in api_component:
                                    if '$ref' in api_component:
                                        sw_resource_schema = api_component['$ref'].split('/')[-1]
                                elif '$ref' in api_component['items']:
                                    sw_resource_schema = api_component['items']['$ref'].split('/')[-1]
                                    
                                if not sw_resource_schema:
                                    # swagger resource scheme has to be found
                                    break
                                
                                schema_definition = data['components']['schemas'][sw_resource_schema]
                                #schema_definition = data['components']['schemas']

                                # Get the attributes of the resource
                                if 'items' in schema_definition and 'properties' in schema_definition['items']:
                                    attributes = schema_definition['items']['properties']
                                elif 'properties' in schema_definition:
                                    attributes = schema_definition['properties']
                                
                                resource_schema = f"{sw_resource_schema} {attributes}"
                                api_documentation.label.append(api_doc_name)
                                api_documentation.label.append(f"resource_uri:{resource_uri}")                            
                                api_documentation.data_schema.append(resource_schema)
                                
                        doc_list.append(api_documentation)
                                                        
            # Save the ontology to a file
            #onto.save(file='output.owl', format='rdfxml')
            if len(doc_list) > 0:
                sync_reasoner()
                onto.save(format="rdfxml")
        
        return doc_list
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In get_api_documentations_from_files module :", __name__)
        raise error    
    

def relate_api_documentation_to_api_resource(api_documentation, api_resource):
    """ Relate API Documentations to the API Resource
    """
    # get the api resource from ontology that has the same resource_uri
    api_domain_map = None
    try:
        #resource_uri = api_documentation.label[1].split(":")[1]
        #api_resources = get_resources_from_resource_uri(resource_uri)

        # Create the relator Documented API
        relator_documented_api = ns_core.DocumentedAPI()     
        # Create the property mediates between the Frequente Temporal Correlation and the API Antecedent Activity
        relator_documented_api.mediates.append(api_resource)
        relator_documented_api.mediates.append(api_documentation) 
        #api_resource.isDocumentedBy.append(api_documentation)                                         
                                            
        # Create the API Domain an Relator API Domain Map
        domain = open_api_util.get_api(api_documentation.api_documentation_url[0])
        api_domain = onto_util.get_individual(onto, ns_data_relation_view.APIDomain, 'http://eamining.edu.pt/', domain)
        if api_domain is None:
            api_domain = ns_data_relation_view.APIDomain(domain)
            api_domain.label.append(f"domain:{domain}")
        
        if not has_inverse_mediates_with_domain_map(api_domain, api_documentation):      
            api_domain_map = ns_data_relation_view.APIDomainMap()
            api_domain_map.mediates.append(api_documentation)
            api_domain_map.mediates.append(api_domain)
            api_documentation.pertainsTo.append(api_domain)
            api_documentation.belongsTo.append(api_domain)
        
        #onto.sync_reasoner()
        #onto.save(format="rdfxml")
        return relator_documented_api, api_domain_map
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In get_api_documentations_from_files module :", __name__)
        raise error     
    
def has_inverse_mediates_with_domain_map(api_domain, api_documentation):
    for api_domain_map in ns_data_relation_view.APIDomainMap.instances():
        if api_domain in api_domain_map.mediates:
            if api_domain_map.mediates[0] == api_documentation:
                return True
    return False

def get_resources_from_resource_uri(resource_uri):
    """ Get all API Resources filterd by the uri parameter, replacing the {id} by a regex pattern
    """
    resource_list = []
    
    aux_uri = resource_uri.replace("{id}", "\\d+")+"$"  # replace the id by a regex pattern
    #regex_uri = f"^{aux_uri}$"
    #resource_uri_pattern  = r"/sandbox/ecommerce/v1/carts/\\d+/itens"
    #FILTER(REGEX(?resource_uri, "/sandbox/ecommerce/v1/carts/[0-9]+/itens"))  
    resource_uri_pattern = aux_uri.replace("\\", "\\\\")
    try:
        query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX ns_core: <http://eamining.edu.pt/core#>
            PREFIX aPIR: <aPIResource:>

            SELECT ?resource
            WHERE {{
                ?resource a ns_core:APIResource .
                ?resource aPIR:resource_uri ?resource_uri .
                
                FILTER(REGEX(?resource_uri, "{resource_uri_pattern}"))
            }}
        """
        graph = default_world.as_rdflib_graph()
        resources = list(graph.query(query))
        for tuple in resources:
            res_uri = str(tuple[0])
            resource = default_world[res_uri]
            resource_list.append(resource)
        
        return resource_list
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In get_resources_from_resource_uri({resource_uri}) module :", __name__)
        raise error   

def get_api_documentations():
    """ Get all API Documentation
    """
    api_docs_list = []
    query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX ns_core: <http://eamining.edu.pt/core#>

        SELECT ?api_documentation
        WHERE {{
            ?api_documentation a ns_core:APIDocumentation .
        }}
    """
    docs = list(default_world.sparql(query)) 
    for tuple in docs:
        doc = tuple[0]
        api_docs_list.append(doc)
    
    return api_docs_list 

def correlate_resources_to_documentations(onto):
    """ Correlate the API Resources to the API Documentations
    """
    documented_api_list = []
    try:
        with onto:
            api_docs = get_api_documentations()
            for api_doc in api_docs:
                url_contexts = open_api_util.split_url(api_doc.api_documentation_url[0]) 
                resource_base_path = f"{url_contexts['environment'] + '/' if url_contexts['environment'] else '/'}{url_contexts['API']}/{url_contexts['version']}"
                for label in api_doc.label: 
                    if label.startswith("resource_uri:"):   
                        aux_resource_uri = label.split(":/")[1]
                        # converting the resource_uri to the same pattern of the call                    
                        resource_uri = f"{resource_base_path}/{aux_resource_uri}"
                        api_resources = get_resources_from_resource_uri(resource_uri)
                        for api_resource in api_resources:
                            documented_api_list.append(relate_api_documentation_to_api_resource(api_doc, api_resource))
            
            if len(documented_api_list) > 0:                    
                sync_reasoner()
                onto.save(format="rdfxml")
        
        return documented_api_list
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In get_api_documentations_from_files module :", __name__)
        raise error             


