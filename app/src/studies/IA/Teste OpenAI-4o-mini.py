import json
import os
import requests
import fitz
from openai import OpenAI
from bs4 import BeautifulSoup

# Configure OpenAI API key from environment variable
api_key = "sk-None-ZQN3nqyM2lVVtjoV0VKAT3BlbkFJIb58i8rDR64SojScttIE"
if not api_key:
    raise ValueError("OpenAI API key not set in environment variables.")
#client = OpenAI(api_key=api_key)
client = OpenAI(base_url="http://localhost:3000/v1", api_key="lm-studio")

# Function to call the language model and structure the data
def call_language_model(edital_text):
    json_template = """
    Example JSON output format:
    ```json
    {
        "numero_edital": 363,
        "data_publicacao": "15/06/2024",
        "orgao": "Coordenadoria Estadual de Gestão de Trânsito - CET/MG",
        "veiculos": [
            {
                "placa": "BQL7527",
                "chassi": "9BGLK19BRPB301463",
                "marca_modelo": "GM/VECTRA GLS",
                "ano_fabricacao": 1993
            },
            {
                "placa": "GYP1834",
                "chassi": "9C2KC08108R076776",
                "marca_modelo": "HONDA/CG 150 TITAN KS",
                "ano_fabricacao": 2007
            },
            {
                "placa": "HCN3534",
                "chassi": "9C2KC08305R004284",
                "marca_modelo": "HONDA/CG 150 JOB",
                "ano_fabricacao": 2004
            }
        ]
    }
    ```
    """
    
    prompt = f"Format the following text into JSON, remove invalid or duplicate information. Your response should be JSON only:\n\n{edital_text}\n\n{json_template}"
    
    try:
        completion = client.chat.completions.create(
            # model="gpt-4o-mini",
            model="bullerwins/Meta-Llama-3.1-8B-Instruct-GGUF",
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling language model: {e}")
        return None

# Function to transform string to JSON
def transform_to_json(input_string):
    try:
        formatted_string = input_string.replace('\\n', '\n').replace('\\"', '"')
        formatted_string = formatted_string.strip('```json').strip('```')
        json_object = json.loads(formatted_string)
        return json_object
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

# Function to check if the URL is a PDF
def is_pdf(url):
    try:
        response = requests.head(url)
        content_type = response.headers.get('content-type', '').lower()
        return 'pdf' in content_type
    except requests.RequestException as e:
        print(f"Error checking if URL is PDF: {e}")
        return False

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

# Function to extract text from an HTML page
def extract_text_from_html(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text
    except requests.RequestException as e:
        print(f"Error extracting text from HTML: {e}")
        return ""

# Main script
url = "https://www.transito.mg.gov.br/publico/files/upload/Notifica%C3%A7%C3%A3o%20de%20leil%C3%A3o%20-%20Abaet%C3%A9%20-%20363-2024.pdf"

if is_pdf(url):
    try:
        response = requests.get(url)
        pdf_content = response.content
        pdf_path = "notificacao_leilao.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        edital_text = extract_text_from_pdf(pdf_path)
        os.remove(pdf_path)
    except requests.RequestException as e:
        print(f"Error downloading PDF: {e}")
        edital_text = ""
else:
    edital_text = extract_text_from_html(url)

if edital_text:
    structured_data_string = call_language_model(edital_text)
    if structured_data_string:
        structured_data_json = transform_to_json(structured_data_string)
        if structured_data_json:
            print(json.dumps(structured_data_json, indent=4))
            with open("output.json", "w") as f:
                json.dump(structured_data_json, f, indent=4)
        else:
            print("Failed to transform structured data string to JSON.")
    else:
        print("Failed to call language model.")
else:
    print("Failed to extract text from the provided URL.")