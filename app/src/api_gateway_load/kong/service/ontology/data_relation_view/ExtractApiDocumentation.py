import os
import json
import yaml
from owlready2 import *
import sys # Add missing import statement for sys module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..", "..")))
from api_gateway_load import configs
from api_gateway_load.utils import spmf_converter
from api_gateway_load.utils import onto_util

onto_path.append("app/src/api_gateway_load/repository/")  # Set the path to load the ontology
onto = get_ontology(configs.OWL_FILE["file_name"]).load()
ns_gufo = onto.get_namespace("http://purl.org/nemo/gufo#")
ns_core = onto.get_namespace("http://eamining.edu.pt/core#")
ns_data_relation_view = onto.get_namespace("http://eamining.edu.pt/data-relation-view#")

# get ontology
onto = get_ontology("http://eamining.edu.pt/core#")


def get_api_documentations_from_files(onto):
    # Load all Swagger files
    file_path = configs.SWAGGERS_FILE_PATH["file_path"]
    #file_name = configs.TEMP_PROCESSING_FILES["file_ftc_list_name"]
    #df = pd.read_csv(file_path + file_name)
    try: 
        for filename in os.listdir(file_path):
            if filename.endswith('.yaml'):
                with open(os.path.join(file_path, filename), 'r') as f:
                    data = yaml.safe_load(f)

                    # Extract the necessary information
                    api_documentation_url = data['servers'][0]['url']
                    #api_documentation_url = configs.DEVELOPER_PORTAL["url"]
                    
                    for path, path_data in data['paths'].items():
                        for method, method_data in path_data.items():
                            full_resource_uri = api_documentation_url + path
                            resource_uri = path
                            #data_schema = json.dumps(method_data['responses']['200']['schema'])
                            data_component = method_data['responses']['200']['content']['application/json']['schema']
                            data_schema = json.dumps(data_component)
                            
                            # Get the schema definition from the components section
                            if '$ref' in data_component['items']:
                                print(data_component['items']['$ref'])
                            schema_name = data_component['items']['$ref'].split('/')[-1]
                            schema_definition = data['components']['schemas']['Product']

                            # Get the attributes of the resource
                            attributes = schema_definition['properties']

                            # Create the OWL elements
                            cls = ns_core.APIDocumentation
                            api_documentation = onto_util.get_individual(onto, cls, 'http://eamining.edu.pt/', api_documentation_url) 
                            if api_documentation is None:                           
                                api_documentation = ns_core.APIDocumentation(api_documentation_url) 
                                api_documentation.label.append(api_documentation_url)
                                api_documentation.api_documentation_url.append(api_documentation_url)
                                api_documentation.data_schema.append(data_schema)
                            
                            # get the api resource from ontology that has the same resource_uri
                            api_resources = get_resources_from_resource_uri(resource_uri)
                            for api_resource in api_resources:
                                api_resource.isDocumentedBy.append(api_documentation)
                                # Create the relator Documented API
                                relator_documented_api = ns_core.DocumentedAPI()                                               
                                # Create the property mediates between the Frequente Temporal Correlation and the API Antecedent Activity
                                relator_documented_api.mediates.append(api_resource)
                                relator_documented_api.mediates.append(api_documentation) 
                                                               
                            # create the API Domain
                            api_domain = ns_data_relation_view.APIDomain()
                            relator_documented_api = ns_data_relation_view.APIDomainMap()
                            relator_documented_api.mediates.append(api_documentation)
                            relator_documented_api.mediates.append(api_domain)
                                                    
        # Save the ontology to a file
        #onto.save(file='output.owl', format='rdfxml')
        onto.sync_reasoner()
        #onto.save(format="rdfxml")
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In get_api_documentations_from_files module :", __name__)
        raise error    

def get_resources_from_resource_uri(uri):
    """ Get all API Resources filterd by the uri parameter
    """
    resource_list = []
    query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX ns_core: <http://eamining.edu.pt/core#>
        PREFIX aPIR: <aPIResource:>

        SELECT ?resource
        WHERE {{
            ?resource a ns_core:APIResource .
            ?resource aPIR:resource_uri ?resource_uri .
            FILTER( 
                ?resource_uri = '{uri}'
            )

        }}
    """
    resources = list(default_world.sparql(query)) 
    for tuple in resources:
        resource = tuple[0]
        resource_list.append(resource)
    
    return resource_list
           

doc = get_api_documentations_from_files(onto)