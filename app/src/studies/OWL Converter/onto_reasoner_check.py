from owlready2 import *
import sys
import os
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from api_gateway_load import configs

#owlready2.JAVA_EXE = "C:\\path\\to\\java.exe"

# Load the OWL ontology
onto_path.append("app/src/studies/OWL Converter/")  # Set the path to load the ontology
onto = get_ontology("ontoreasoner.owl").load()

# Define the ontology classes and data property
with onto:
    class ConsumerApp(Thing):
        pass

    class client_id(DataProperty):
        pass
    
    class clientId(DataProperty):
        pass        
    
    class app_name(DataProperty):
        pass            


try:
    app = ConsumerApp("ConsumerApp5")
    app.client_id.append("123456")
    #app.clientId.append("123456") # gera uma inconsistencia, pois o atritubo CliendId não existe
    app.app_name.append('ConsumerApp5')

    # Save the modified ontology
    sync_reasoner()
    inconsistency_list = list(default_world.inconsistent_classes())
    print('inconsistency_list', inconsistency_list)

        #onto.save(format='rdfxml')

    #onto.save("ontoeamining3.owl") # só ser for salvar um novo
    
    
except Exception as error:
    print('Ocorreu problema {} '.format(error.__class__))
    print("mensagem", str(error))
    print("In cleanIgnoredAttributes module :", __name__)          
