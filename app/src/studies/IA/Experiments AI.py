# Example: reuse your existing OpenAI setup
from openai import OpenAI
import json

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# messages is a list of messages in the conversation. It includes:
# A system message that sets the context or instructions for the model.
# A user message that provides the input or question to the model.

def test1():
  completion = client.chat.completions.create(
    model="lmstudio-ai/gemma-2b-it-GGUF",
    messages=[
      {"role": "system", "content": "It should return the suggested task name in a field named as 'task_name'. The task_name should be short with no more than four words."},
      {"role": "user", "content": "Convert the API POST_/sandbox/ProcessBusinessUnit2/v1/Association/PromiseLoyaltyCardAssociationOrder to a short name to name a human task in a bpmn."}
    ],
    temperature=0.7,
  )

  message = completion.choices[0].message
  response_content = completion.choices[0].message.content
  # Parse the content to extract the 'task_name'
  response_json = json.loads(response_content)
  task_name = response_json.get('task_name')
  print("Task Name:", task_name)


def translate_to_task_name(api_name):
    system_message = """It should always return a JSON string with the suggested task name in a field named as 'task_name' 
                                        and the original string representing the API endpoint named as original_endpoint.
                                        Exemple of expected resulting content: {"task_name": "Promise Loyalty Card Association", "original_endpoint": "GET_/sandbox/ProcessBusinessUnit1/v1/PromiseLoyaltyCardAssociationOrder"}
                                        The task_name should be short with no more than six words."""
    
    completion = client.chat.completions.create(
        model="lmstudio-ai/gemma-2b-it-GGUF",
        messages=[
        {"role": "system", "content":system_message},
        {"role": "user", "content": f"Translate the endpoint {api_name} to a short name to name a human task in a bpmn."}
        ],
        temperature=0.7
    )

    try:
        response_content = completion.choices[0].message.content
        print(f"Response Content: {response_content}")
        # Parse the content to extract the 'task_name'
        response_json = json.loads(response_content)
        task_name = response_json.get('task_name')
        return task_name
    except json.JSONDecodeError:
        print(f"Invalid JSON format received. translate_to_task_name ({api_name}):")
        raise json.JSONDecodeError      

def translate_api_list_to_task_name(api_list):
  task_names = []
  for api in api_list:
    task_name = translate_to_task_name(api)
    task_names.append(task_name)
  return task_names

def translate_apis_to_task_name(api_list):
    task_names = []
    completion = client.chat.completions.create(
        model="lmstudio-ai/gemma-2b-it-GGUF",
        messages=[
        {"role": "system", "content": """It should return a json list with two fields: the suggested task names in field named as 'task_name' and the original string representing the API endpoint named as original_endpoint. 
                                Exemple: [ "tasks" : {"task_name": "Promise Loyalty Card Association", "original_endpoint": "GET_/sandbox/ProcessBusinessUnit1/v1/PromiseLoyaltyCardAssociationOrder"}]
                                Each word in the task_name should be separated by an space.
                                The task_name should be short with no more than six words. 
                                the name of the json list should be 'tasks'.
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


# completion = client.chat.completions.create(
#   model="lmstudio-ai/gemma-2b-it-GGUF",
#   messages=[
#     {"role": "system", "content": "It should return the suggested task name in a field named as 'task_name'. The task_name should be short with no more than four words."},
#     {"role": "user", "content": "Convert the API POST_/sandbox/ProcessBusinessUnit2/v1/Association/PromiseLoyaltyCardAssociationOrder to a short name to name a human task in a bpmn."}
#   ],
#   temperature=0.7,
# )

# message = completion.choices[0].message
# response_content = completion.choices[0].message.content
# # Parse the content to extract the 'task_name'
# response_json = json.loads(response_content)
# task_name = response_json.get('task_name')

# print("Task Name:", task_name)

taks_list = ["GET_/sandbox/ProcessBusinessUnit1/v1/Customer", 
             "POST_/sandbox/ProcessBusinessUnit2/v1/Association/PromiseLoyaltyCardAssociationOrder",
             "GET_/sandbox/ProcessBusinessUnit2/v1/Card/x/x",
             "POST_/sandbox/ProcessBusinessUnit3/v1/Purchase/DeclarePurchaseConsumerOrder",
             "POST_/sandbox/ProcessBusinessUnit2/v1/Purchase/AcceptPurchaseConsumerOrder",
             "POST_/sandbox/ProcessBusinessUnit2/v1/Association/DeclareLoyaltyCardAssociationOrder",
             "GET_/sandbox/ProcessBusinessUnit1/v1/Shop",
             "POST_/sandbox/ProcessBusinessUnit1/v1/Association/RequestLoyaltyCardAssociationOrder",
             "POST_/sandbox/ProcessBusinessUnit3/v1/Purchase/PromisePurchaseConsumerOrder",
             "POST_/sandbox/ProcessBusinessUnit1/v1/Association/AcceptLoyaltyCardAssociationOrder",
             "POST_/sandbox/ProcessBusinessUnit2/v1/Association/AssociateLoyaltyCard"]

#new_list = translate_apis_to_task_name(taks_list)
#print(new_list)

task = translate_to_task_name("POST_/sandbox/ProcessBusinessUnit2/v1/Association/PromiseLoyaltyCardAssociationOrder")
print(task) 