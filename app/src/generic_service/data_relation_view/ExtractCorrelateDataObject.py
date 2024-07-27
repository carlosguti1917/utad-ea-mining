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


def get_resources_from_domain(domain):
    """ Get all API Resources filterd by the uri parameter, replacing the {id} by a regex pattern
    """
    resource_list = []   
    aux_uri = f"/{domain}/v"
    resource_uri_pattern = aux_uri.replace("\\", "\\\\")
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
    try:
        resources = list(graph.query(query))
        for tuple in resources:
            res_uri = str(tuple[0])
            resource = default_world[res_uri]
            resource_list.append(resource)
        
        return resource_list
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In get_resources_from_domain module :", __name__)
        raise error  


def get_api_domains(onto):
    """ Get all API Domain
    """
    try:
        api_domain_list = []
        # query = f"""
        #     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        #     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        #     PREFIX ns_data_relation_view: <http://eamining.edu.pt/data-relation-view#>

        #     SELECT ?api_domain
        #     WHERE {{
        #         ?api_domain a ns_data_relation_view:APIDomain .
        #     }}
        # """
        # domains = list(default_world.sparql(query)) 
        domains = list(onto.search(type=ns_data_relation_view.APIDomain))
        # for domain in domains:
        #     api_domain_list.append(domain)
        
        return domains 
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In get_api_domains module :", __name__)
        raise error  


def mining_frequent_data_domain_correlations(onto):
    """ Mining Frequent Data Domain Correlations
        it creates a FrequentDataDomainCorrelation for each API Resource and Data Domain correlation and save it in the ontology
    """
    fddc_list = []
    try:
        with onto:
            #domains = get_api_domains(onto)
            domains = list(onto.search(type=ns_data_relation_view.APIDomain))
            for domain in domains:
                domain_nm = domain.name
                resources = get_resources_from_domain(domain_nm)
                for resource in resources:
                    entity_name = open_api_util.get_last_resource_name(resource.resource_name[0])
                    fddc_name = f"fddc_{domain_nm}_{entity_name}"
                    fddc = onto_util.get_individual(onto, ns_data_relation_view.FrequentDataDomainCorrelation, "http://eamining.edu.pt/", fddc_name)
                    if fddc is not None:
                        continue
                    fddc = ns_data_relation_view.FrequentDataDomainCorrelation(fddc_name)
                    fddc.label.append(f"fddc={domain_nm}:{entity_name}")
                    # create role Entity
                    entity = ns_data_relation_view.APIEntity(entity_name)
                    # create role DataDomain
                    data_domain = ns_data_relation_view.DataDomain(domain_nm)
                    # fddc mediates entity and data domain
                    fddc.mediates.append(entity)
                    fddc.mediates.append(data_domain)
                    fddc_list.append(fddc)
            sync_reasoner()
            onto.save(format="rdfxml")
        return fddc_list    
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In mining_frequent_data_domain_correlations() :", __name__)        
        raise error                 

def mining_correlated_data_objects(onto):
    """ Mining Correlated Data Objects
        it gets all FrequentDataDomainCorrelation and create a CorrelatedDataObject for each pair of API Entity and Data Domain    
    """
    cdo_list = []
    try:
        with onto:
            fddc_list = list(onto.search(type=ns_data_relation_view.FrequentDataDomainCorrelation))
            for fddc in fddc_list:
                entity = fddc.mediates[0]
                data_domain = fddc.mediates[1]
                entity_name = entity.name
                data_domain_name = data_domain.name
                cdo_name = f"cdo_{data_domain_name}_{entity_name}_"
                cdo = onto_util.get_individual(onto, ns_data_relation_view.CorrelatedDataObjects, "http://eamining.edu.pt/", cdo_name)
                if cdo is not None:
                    continue
                cdo = ns_data_relation_view.CorrelatedDataObjects(cdo_name)
                cdo.label.append(f"cdo={data_domain_name}:{entity_name}")
                cdo.CorrelatedDomain.append(data_domain)
                cdo.CorrelatedEntity.append(entity)
                cdo.domain_name.append(data_domain_name)
                cdo.entity_name.append(entity_name)
                
                cdo_list.append(cdo)
            
            sync_reasoner()
            onto.save(format="rdfxml")                
        return cdo_list
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In mining_correlated_data_objects() :", __name__)        
        raise error
    

               