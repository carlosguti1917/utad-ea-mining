# Example: reuse your existing OpenAI setup
from openai import OpenAI
import json

import os
import os.path
import sys # Add missing import statement for sys module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', "..")))
from app.src import configs

# Point to the local server
client = OpenAI(base_url=configs.AI_MODEL["base_url"], api_key=configs.AI_MODEL["api_key"])
#client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# messages is a list of messages in the conversation. It includes:
# A system message that sets the context or instructions for the model.
# A user message that provides the input or question to the model.


def translate_uri_to_task_name(uri):
  system_message = """It should always return a JSON with two fields named as 'task_name' with the suggested name of the task
                      and the original string representing the API uri named as original_endpoint. 
                      If the suggested task_name has more tha one word, each word should be separated by an space.
                      The task_name should consider the verb in the beginning of the string and the last noun in the uri string.
                      Each uppercase letter followed by a lowercase letter separates the words in the task_name, such as in camelCase string pattern. 
                      In the same way, in strings with underscore each underscore separates words in the task_name and 
                      for string with hyphen each hyphen separates words in the task_name. All these words should be separated by an space.
                      The followin words represent the api envirionment and should be ignorad for task_name: sandbox, qa, hml, dev, prod, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev.
                      The task_name should be short with no more than six words.
                      The response should be in the format: 
                        {
                            "task_name": "<generated task name>",
                            "original_endpoint": "<input URI>"
                        }
                      The task_name should be repeated, unless it has the same uri and original_endpoint value.
                      Some exemple of expected resulting content are: 
                            {"task_name": "Get Card", "original_endpoint": "GET_/sandbox/ProcessBusinessUnit2/v1/Card/x/x"},
                            {"task_name": "Get Shop", "original_endpoint": "GET_/sandbox/ProcessBusinessUnit1/v1/Shop"},
                            {"task_name": "Promise Loyalty Card Association", "original_endpoint": "POST_/sandbox/ProcessBusinessUnit2/v1/Association/PromiseLoyaltyCardAssociationOrder"},
                            {"task_name": "Promise Purchase Consumer Order", "original_endpoint": "POST_/sandbox/ProcessBusinessUnit3/v1/Purchase/PromisePurchaseConsumerOrder"},
                            {"task_name": "Declare Purchase Consumer Order", "original_endpoint": "POST_/sandbox/ProcessBusinessUnit3/v1/Purchase/DeclarePurchaseConsumerOrder"}.
                      """
  completion = client.chat.completions.create(
      model="lmstudio-ai/gemma-2b-it-GGUF",
      #model=configs.AI_MODEL["model"],
      messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Translate the API {uri} to a business short name to name a BPMN Service Task."}
      ],
      temperature=0.6,
    )

  try:
    response_content = completion.choices[0].message.content
    # Parse the content to extract the 'task_name'
    response_json = json.loads(response_content)
    task_name = response_json.get('task_name')
    print(f"Original Endpoint: {uri}, Task Name: {task_name}")
    return task_name
  except json.JSONDecodeError:
      print(f"Invalid JSON format received. translate_to_task_name ({uri}):")
      raise json.JSONDecodeError 
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


def translate_process_name_to_domain_context(domain):
  system_message = """It should always return a JSON with two fields named as 'data_domain_name' with the suggested name of the domain
                      and the original string representing the Data Domain as original_domain. 
                      If the suggested data_domain_name has more tha one word, each word should be separated by an space.
                      Each uppercase letter followed by a lowercase letter separates the words in the data_domain_name, such as in camelCase string pattern. 
                      In the same way, in strings with underscore each underscore separates words in the data_domain_name and 
                      for string with hyphen each hyphen separates words in the data_domain_name. All these words should be separated by an space.
                      The followin words represent the api envirionment and should be ignorad for data_domain_name: sandbox, qa, hml, dev, prod, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev, homolog, homologation, homologacao, homologação, homolog, production, producao, produção, test, teste, testing, demo, development, desenvolvimento, desenv, dev.
                      The data_domain_name should be short with no more than four words.
                      Retun the result in JSON format.
                      """
  completion = client.chat.completions.create(
      model="lmstudio-ai/gemma-2b-it-GGUF",
      messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Translate the Domain {domain} to a business short name to name a Data Domain Context."}
      ],
      temperature=0.8,
    )

  try:
    response_content = completion.choices[0].message.content
    #response_content = completion.json()
    # Parse the content to extract the 'task_name'
    response_json = json.loads(response_content)
    task_name = response_json.get('task_name')
    print(f"Original Endpoint: {domain}, Task Name: {task_name}")
    return task_name
  except json.JSONDecodeError:
      print(f"Invalid JSON format received. translate_to_task_name ({uri}):")
      raise json.JSONDecodeError 
  except Exception as error:   
      print('Ocorreu problema {} '.format(error.__class__))
      print("mensagem", str(error))
      print(f"In create_archimate_process_elements module :", __name__)
      raise error      
