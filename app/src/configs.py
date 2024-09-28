## CONFIGURATIONS ##

from datetime import datetime


MAX_QUANTITY_ATTRIBUTES_SAMPLE = 20 # Maximum number of attributes to be sampled from the dataset in attribute utilitiy verificarion logic
QTD_LOG_CALLS_SAMPLE = 1000 # Maximum number of log calls to be sampled from the dataset (logstash) to be processed. A larger quantity needs more memory and processing time

# Idenfity the consumer app to be used in mining. It refers to the Consumer in Kong API Gateway and app.client_id/app.name in Sensedia API Gateway
# It is used to reduce de data sample to be processed focousing on specific consumer apps.
CONSUMER_APPS = [
  {
    "client_id": "69be440d-5a95-4eda-abd0-0924e4e2f957",
    "app_name": "acmeapp"
  },
  {
    "client_id": "9d2bb089-f916-43d7-804f-e72048db394a",
    "app_name": "EAminingApp"
  },
  {
    "client_id": "ff38289a-5a3b-44bb-9830-7cdb850dd2b3",
    "app_name": "OpenApp"
  },
  {
    "client_id": "123456",
    "app_name": "CamundaApp"
  },   
  {
    "client_id": "1234562",
    "app_name": "HealthCareApp"
  }  
  
]


APRIORI_INVERSE_ARGS = {
  "MIM_SUPPORT": 0.01,
  #"MAX_SUPPORT": 1, #  The item is present in all transactions, for small datasets tests
  #"MAX_SUPPORT": 0.5, #  The item is present in 50% of transactions, for small datasets tests, but suport booleans 
  "MAX_SUPPORT": 0.3, #  The item is present in 30% of transactions, for small datasets tests, small enums with 5 values
  #"MAX_SUPPORT": 0.1, #  The item is present in 10% of transactions, for small datasets tests, medium enums with 10 values
  #"MAX_SUPPORT": 0.06, #  The item is present in 6% of transactions, for medium datasets training set, enums with 15 values - Recomended
}

PM4PI_ARGS = {
  "TOP_K" : 3, # For tests with very small datasets
  #"TOP_K" : 4, # For tests with small datasets (10 tests sets)
  #"TOP_K" : 8, # For tests with medium datasets (More than 20 tests sets)
  #"TOP_K" : ?, # For tests with medium datasets (More than 50 tests sets)
}

# server
MONGO_DB_SERVER_1 = {
  "host": "192.168.0.15",
  "port": 27017,
}

MONGO_DB_SERVER = {
  "user" : "root",
  "password": "Admin123",
  "host": "mongodb://root:Admin123@192.168.0.15:27017/",
  "databasename": "eamining",
}

MYSQL_DB_SERVER = {
    "host": "192.168.0.15",
    "port": 3306,
    "user": "root",
    "password": "123",
}

ARANGO_DB_SERVER = {
    "host": "http://127.0.0.1:8529/",
    "user": "root",
    "password": "123",
}

ARANGO_PARAMS = {
    "uri_collection": "URI_V5",
    "edge_collection": "Operation_Uri_Correlation",
    "graph": "default_graph",
}

KONG = {
  "host": "192.168.0.15",
}

ELASTIC = {
  "kong_log": "https://192.168.0.15:9200/konglog*/_search",
}

# it only works with file .owl
OWL_FILE = {
  "file_path": "app/src/repository/",
  "file_name": "EA Mining OntoUML Teste V1_4.owl",
}

FREQUENT_API_ATTRIBUTES = {
  "file_name": "frequent_attributes.ignore",
}

TEMP_PROCESSING_FILES = {
  "file_path": "./temp/",
  "file_ftc_list_name": "ftc_list.csv",
  "file_name_cleaned_ftc_list": "ftc_list_cleaned.csv",
  "pkl_file_path": "./temp/process",
}

datahora = datetime.now().strftime("%Y%m%d%H%M")
ARCHIMATE_MODEL = {
  "datahora": datahora,
  "file_path": "./archimate/",
  "archimate_file_name": f"{datahora}_archimate_model_data.xml", 
}

SWAGGERS_FILE_PATH = {
  "file_path": "./docs/swaggers/",
}

DEVELOPER_PORTAL = {
  "url": "./docs/swaggers/",
}

SENSEDIA = {
  "domain_url": "https://manager-demov3.sensedia.com",
  "sensedia_auth": "d4667e61-9c24-48fb-b7fc-d192ff666a5c",
  "environment": "sandbox",
}

AI_MODEL = {
  # "model": "lmstudio-ai/gemma-2b-it-GGUF",
  # "base_url": "http://localhost:3000/v1",
  # "api_key": "lm-studio",
  # "model": "gpt-3.5-turbo",
  "model": "gpt-4o-mini",
  "base_url": "https://api.openai.com/v1/chat/completions",
  "api_key": "change-the-api-key",
}


