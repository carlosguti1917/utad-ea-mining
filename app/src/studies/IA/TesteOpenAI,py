from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-WEvon27M2Wru6SMOd5ZvT3BlbkFJQQUOaLyAOuJCgnLEZTmY"))

def get_chat_response(prompt, model="gpt-3.5-turbo"):
    """Generate a response from the OpenAI API for a given prompt."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Exemplo de uso
if __name__ == "__main__":
    user_prompt = "Translate the endpoint GET_/sandbox/ProcessBusinessUnit1/v1/Customer to a short name for a human task in a BPMN."
    response = get_chat_response(user_prompt)
    if response:
        print(f"AI Response: {response}")
