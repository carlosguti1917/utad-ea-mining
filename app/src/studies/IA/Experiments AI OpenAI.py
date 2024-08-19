import openai
import json
import os

# Configure OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY", "sk-proj-e0Dk9M4YcTtRDk7gF1UoT3BlbkFJoIlxcwjSX2U1CKmpgPNT")
if not api_key:
    raise ValueError("OpenAI API key not set in environment variables.")

openai.api_key = api_key

def translate_to_task_name(api_name):
    system_message = (
        "It should always return a JSON string with the suggested task name "
        "in a field named 'task_name' and the original string representing the API endpoint named 'original_endpoint'. "
        "Example of expected resulting content: {\"task_name\": \"Promise Loyalty Card Association\", "
        "\"original_endpoint\": \"GET_/sandbox/ProcessBusinessUnit1/v1/PromiseLoyaltyCardAssociationOrder\"} "
        "The task_name should be short with no more than six words."
    )
    
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Translate the endpoint {api_name} to a short name to name a human task in a BPMN."}
        ],
        temperature=0.7
    )

    try:
        response_content = completion.choices[0].message['content']
        print(f"Response Content: {response_content}")
        response_json = json.loads(response_content)
        task_name = response_json.get('task_name')
        return task_name
    except json.JSONDecodeError:
        print(f"Invalid JSON format received. translate_to_task_name ({api_name}):")
        return None

def translate_apis_to_task_name(api_list):
    task_names = []
    system_message = (
        "It should return a json list with two fields: the suggested task names in field named 'task_name' "
        "and the original string representing the API endpoint named 'original_endpoint'. "
        "Example: [{\"task_name\": \"Promise Loyalty Card Association\", "
        "\"original_endpoint\": \"GET_/sandbox/ProcessBusinessUnit1/v1/PromiseLoyaltyCardAssociationOrder\"}] "
        "Each word in the task_name should be separated by a space. "
        "The task_name should be short with no more than six words. "
        "The name of the json list should be 'tasks'."
    )
    
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"For each API in the list {api_list} translate to a short name to name a human task in a BPMN."}
        ],
        temperature=0.7
    )

    response_content = completion.choices[0].message['content']
    try:
        response_json = json.loads(response_content)
        tasks = response_json.get('tasks', [])
        for task in tasks:
            original_endpoint = task.get('original_endpoint')
            task_name = task.get('task_name')
            task_names.append(task_name)
            print(f"Original Endpoint: {original_endpoint}, Task Name: {task_name}")
    except json.JSONDecodeError:
        print(f"Invalid JSON format received. translate_apis_to_task_name:")
        task_names = []
    
    return task_names

# Example usage
task_list = [
    "GET_/sandbox/ProcessBusinessUnit1/v1/Customer",
    "POST_/sandbox/ProcessBusinessUnit2/v1/Association/PromiseLoyaltyCardAssociationOrder",
    "GET_/sandbox/ProcessBusinessUnit2/v1/Card/x/x",
    "POST_/sandbox/ProcessBusinessUnit3/v1/Purchase/DeclarePurchaseConsumerOrder",
    "POST_/sandbox/ProcessBusinessUnit2/v1/Purchase/AcceptPurchaseConsumerOrder",
    "POST_/sandbox/ProcessBusinessUnit2/v1/Association/DeclareLoyaltyCardAssociationOrder",
    "GET_/sandbox/ProcessBusinessUnit1/v1/Shop",
    "POST_/sandbox/ProcessBusinessUnit1/v1/Association/RequestLoyaltyCardAssociationOrder",
    "POST_/sandbox/ProcessBusinessUnit3/v1/Purchase/PromisePurchaseConsumerOrder",
    "POST_/sandbox/ProcessBusinessUnit1/v1/Association/AcceptLoyaltyCardAssociationOrder",
    "POST_/sandbox/ProcessBusinessUnit2/v1/Association/AssociateLoyaltyCard"
]

new_list = translate_apis_to_task_name(task_list)
print(new_list)
