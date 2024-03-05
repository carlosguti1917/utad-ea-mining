from pymongo import MongoClient
from owlready2 import *
import sys
import os
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from api_gateway_load import configs

# Connect to MongoDB
myclient = MongoClient(configs.MONGO_DB_SERVER["host"])
mydb = myclient[configs.MONGO_DB_SERVER["databasename"]]
collection_call_detail = mydb["kong-api-call-cleaned"]

# Load the OWL ontology
#onto_path.append(".")  # Set the path to load the ontology
#onto_path.append("c:/gitHub/utad/utad-ea-mining/app/src/studies/OWL Converter/")  # Set the path to load the ontology
onto_path.append("app/src/studies/OWL Converter/")  # Set the path to load the ontology
print("onto_path = ", onto_path)
#onto = get_ontology("file://ontoeamining.owl").load()
onto = get_ontology("ontoeamining2.owl").load()
print(onto.ConsumerApp)
classes = list(onto.classes())  
individuals = list(onto.individuals())
propertis = list(onto.properties())

print("classes = ",list(onto.classes()))
print("individuals = ",list(onto.individuals()))
print("properties = ",list(onto.properties()))
print("data properties = ",list(onto.data_properties()))
print("object properties = ",list(onto.object_properties()))

teste = onto.search(iri = "*001") # o * indica que eu quero buscar todos os objetos terminados com Conumer001
print("teste = ",teste)

try:
    for i in teste:
        print("teste = ", i.name)
    #    print("teste namespade = ", i.namespace())
        print("teste iri = ", i.iri)
        print("teste classes = ", i.is_a)



    # Define the ontology classes and data property
    with onto:
        class ConsumerApp(Thing):
            pass

        class Partner(Thing):
            pass

        class client_id(DataProperty):
            pass

    # Iterate over MongoDB documents
    #for doc in collection_call_detail.find({}):
        # Extract client_id from JSON document
        #client_id = doc["_source"]["request"]["headers"]["client_id"]
        client_id = 664

        # Create individual for Consumer App and assign client_id
        app = ConsumerApp("App6")
        app.clientId = [client_id]
        app.name = 'ConsumerApp6'
        app.app_name = 'ConsumerApp5'

        # Create individual for Partner
        partner = Partner("Partner5")

        # Save the modified ontology


        onto.save(format='rdfxml')

    #onto.save("ontoeamining3.owl") # só ser for salvar um novo
    
    
except Exception as error:
    print('Ocorreu problema {} '.format(error.__class__))
    print("mensagem", str(error))
    print("In cleanIgnoredAttributes module :", __name__)          
