# Example: reuse your existing OpenAI setup
from openai import OpenAI
import json

import os
import os.path
import sys # Add missing import statement for sys module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..")))
from app.src import configs

# Point to the local server
#client = OpenAI(base_url=configs.AI_MODEL["base_url"], api_key=configs.AI_MODEL["api_key"]) # no need to pass the base_url when using the open AI server
client = OpenAI(api_key=configs.AI_MODEL["api_key"])
#client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def translate_uri_to_task_name(uri):
  system_message = """It should always return a JSON with two fields named as 'task_name' with the suggested name of the task
                      and the original string representing the API uri named as original_endpoint. 
                      If the suggested task_name has more than one word, each word should be separated by a space.
                      The task_name should consider the verb at the beginning of the string and the last noun in the URI string.
                      Each uppercase letter followed by a lowercase letter separates the words in the task_name, such as in the camelCase string pattern. 
                      In the same way, in strings with underscores, each underscore separates words in the task_name and 
                      for strings with a hyphen, each hyphen separates words in the task_name. A space should separate all these words.
                      The followin words represent the api envirionment and should be ignorad for task_name: sandbox, qa, hml, dev, prod, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev.
                      The task_name should be short and should be no more than six words long.
                      The response should be in the format: 
                        {
                            "task_name": "<generated task name>",
                            "original_endpoint": "<input URI>"
                        }
                      The task_name should not be repeated unless it has the same URI and original_endpoint value.
                      Some examples of expected resulting content are: 
                            {"task_name": "Get Card", "original_endpoint": "GET_/sandbox/ProcessBusinessUnit2/v1/Card/x/x"},
                            {"task_name": "Get Shop", "original_endpoint": "GET_/sandbox/ProcessBusinessUnit1/v1/Shop"},
                            {"task_name": "Promise Loyalty Card Association", "original_endpoint": "POST_/sandbox/ProcessBusinessUnit2/v1/Association/PromiseLoyaltyCardAssociationOrder"},
                            {"task_name": "Declare Purchase Consumer Order", "original_endpoint": "POST_/sandbox/ProcessBusinessUnit3/v1/Purchase/DeclarePurchaseConsumerOrder"}.
                      """
  completion = client.chat.completions.create(
      #model="lmstudio-ai/gemma-2b-it-GGUF",
      model=configs.AI_MODEL["model"],
      messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Translate the API {uri} to a business short name to name a BPMN Service Task."}
      ],
      temperature=0.6,
      max_tokens=600,
      top_p=1,
      n=1,
      stream=False,
    )

  try:
    response_content = completion.choices[0].message.content
    # Parse the content to extract the 'task_name'
    response_json = json.loads(response_content)
    task_name = response_json.get('task_name')
    print(f"Original Endpoint: {uri}, Task Name: {task_name}")
    return task_name
  except json.JSONDecodeError as e:
      print(f"Invalid JSON format received. translate_to_task_name ({uri}):")
      raise e 
  except Exception as error:   
      print('Ocorreu problema {} '.format(error.__class__))
      print("mensagem", str(error))
      print(f"In create_archimate_process_elements module :", __name__)
      raise error      
  
def translate_string_to_process_name(original_name):
  system_message = """It should always return a JSON with two fields named as 'process_name' with the suggested name to the process 
              and the original string representing the API uri named as original_endpoint. 
              If the suggested process_name has more tha one word, each word should be separated by an space.
              Each uppercase letter followed by a lowercase letter separates the words in the task_name, such as in camelCase string pattern. 
              In the same way, in strings with underscore each underscore separates words in the task_name and 
              for string with hyphen each hyphen separates words in the process_name. All these words should be separated by an space.
              The followin words represent the api envirionment and should be ignorad for task_name: sandbox, qa, hml, dev, prod, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev.
              The process_name should be short with no more than six words.
              The response should be in the format: 
                {
                    "process_name": "<generated process_name>",
                    "original_name": "<input URI>"
                }
              The process_name should not be repeated, unless it has the same uri and original_name value.
              """
  completion = client.chat.completions.create(
      #model="lmstudio-ai/gemma-2b-it-GGUF",
      model=configs.AI_MODEL["model"],
      messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Translate the string {original_name} to a business short name to name a BPMN Service Task."}
      ],
      temperature=0.6,
      max_tokens=600,
      top_p=1,
      n=1,
      stream=False,
    )

  try:
    response_content = completion.choices[0].message.content
    # Parse the content to extract the 'task_name'
    response_json = json.loads(response_content)
    process_name = response_json.get('process_name')
    print(f"Original Endpoint: {original_name}, Task Name: {process_name}")
    return process_name
  except json.JSONDecodeError as e:
      print(f"Invalid JSON format received. translate_to_task_name ({original_name}):")
      raise e 
  except Exception as error:   
      print('Ocorreu problema {} '.format(error.__class__))
      print("mensagem", str(error))
      print(f"In create_archimate_process_elements module :", __name__)
      raise error 

  

def translate_api_list_to_task_name(api_list):
  task_names = []
  for api in api_list:
    task_name = translate_uri_to_task_name(api)
    task_names.append(task_name)
  return task_names

def translate_endpoints_to_task_name(api_list):
    task_names = []
    completion = client.chat.completions.create(
        model="lmstudio-ai/gemma-2b-it-GGUF",
        messages=[
        {"role": "system", "content": """It should return a json list with two fields: the suggested task names in field named as 'task_name' and the original string representing the API endpoint named as original_endpoint. 
                                Exemple: [ "tasks" : {"task_name": "Promise Loyalty Card Association", "original_endpoint": "GET_/sandbox/ProcessBusinessUnit1/v1/PromiseLoyaltyCardAssociationOrder"}].
                                Each word in the task_name should be separated by an space.
                                The task_name should be short with no more than six words. 
                                the name of the json list should be 'tasks'.
                                Retun the result in JSON format.
                                """},
        {"role": "user", "content": f"For each API in the list {api_list} translate to a short name to name a human task in a bpmn."}
        ],
        temperature=0.7,
    )

    response_content = completion.choices[0].message.content
    # Parse the content to extract the 'task_name'
    response_json = json.loads(response_content)
    tasks = response_json.get('tasks', [])
    for task in tasks:
        original_endpoint = task.get('original_endpoint')
        task_name = task.get('task_name')
        print(f"Original Endpoint: {original_endpoint}, Task Name: {task_name}")
    
    return task_name


def translate_api_context_to_domain(domain):
  system_message = """It should always return a JSON with two fields named as data_domain_name with the suggested name of the domain 
                          and the original string representing the Data Domain as original_domain. 
                      If the suggested data_domain_name has more tha one word, each word should be separated by a space.
                      Each uppercase letter followed by a lowercase letter separates the words in the data_domain_name, such as in the camelCase string pattern. 
                      In the same way, in strings with an underscore, each underscore separates words in the data_domain_name and 
                      for strings with a hyphen, each hyphen separates words in the data_domain_name. A space should separate all these words.
                      The followin words represent the api envirionment and should be ignorad for data_domain_name: sandbox, qa, hml, dev, prod, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev.
                      The data_domain_name should be short and not more than four words long.
                      Retun the result in JSON format.
                      Avoid names with the string Domain in the data_domain_name.
                      Examples of expected resulting content are:
                          {"data_domain_name": "Business Process 1", "original_domain": "ProcessBusinessUnit1"}    
                    
                      """
  completion = client.chat.completions.create(
      model=configs.AI_MODEL["model"],
      messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Translate the Domain {domain} to a business short name in order to name a Data Domain Context."}
      ],
      temperature=0.6,
      max_tokens=600,
      top_p=1,
      n=1,
      stream=False,
    )

  try:
    response_content = completion.choices[0].message.content
    #response_content = completion.json()
    # Parse the content to extract the 'task_name'
    response_json = json.loads(response_content)
    data_domain_name = response_json.get('data_domain_name')
    print(f"Original Endpoint: {domain}, data_domain_name Name: {data_domain_name}") 
    return data_domain_name
  except json.JSONDecodeError:
      print(f"Invalid JSON format received. translate_api_context_to_domain ({domain}):")
      raise json.JSONDecodeError 
  except Exception as error:   
      print('Ocorreu problema {} '.format(error.__class__))
      print("mensagem", str(error))
      print(f"In create_archimate_process_elements module :", __name__)
      raise error      
    
def translate_resource_to_entity_name(original_name):
  system_message = """It should always return a JSON with two fields named as entity_name with the suggested name of the data entity
                      and the original string representing the resource named as original_endpoint. 
                      If the suggested entity_name has more than one word, each word should be separated by a space.
                      Each uppercase letter followed by a lowercase letter separates the words in the entity_name, such as in camelCase string pattern. 
                      In the same way, in strings with underscore each underscore separates words in the entity_name and for strings with hyphen each hyphen separates words in the entity_name. All these words should be separated by a space.
                      The following words represent the API environment and should be ignored for entity_name: sandbox, qa, hml, dev, prod, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev.
                      The entity_name should be short with no more than six words.
                      Avoid names with "Data Object" or "Archimate Data Object" in the entity_name.                   
                      The response should be in the format: 
                        {
                            "entity_name": "<generated entity name>",
                            "original_name": "<input original_name>"
                        }
                      Some examples of expected resulting content are: 
                            {"entity_name": "Orders", "original_name": "orders"},                      
                            {"entity_name": "Items", "original_name": "Items"},
                            {"entity_name": "Loyalty Card Association", "original_name": "PromiseLoyaltyCardAssociationOrder"},
                            {"entity_name": "Purchase Consumer Order", "original_name": "DeclarePurchaseConsumerOrder"}.
                      """
  completion = client.chat.completions.create(
      #model="lmstudio-ai/gemma-2b-it-GGUF",
      model=configs.AI_MODEL["model"],
      messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Translate the {original_name} to a entity name to name a Archimate Data Object."}      ],
      temperature=0.6,
      max_tokens=1000,
      top_p=1,
      n=1,
      stream=False,
    )

  try:
    response_content = completion.choices[0].message.content
    # Parse the content to extract the 'task_name'
    response_json = json.loads(response_content)
    entity_name = response_json.get('entity_name')
    print(f"Original URI: {original_name}, entity_name: {entity_name}")
    return entity_name
  except json.JSONDecodeError:
      print(f"Invalid JSON format received. translate_to_task_name ({uri}):")
      raise json.JSONDecodeError 
  except Exception as error:   
      print('Ocorreu problema {} '.format(error.__class__))
      print("mensagem", str(error))
      print(f"In create_archimate_process_elements module :", __name__)
      raise error        
