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
  "file_name": "EA Mining OntoUML Teste V1_4.owl",
}

FREQUENT_API_ATTRIBUTES = {
  "file_name": "frequent_attributes.ignore",
}

TEMP_PROCESSING_FILES = {
  "file_path": "./temp/",
  "file_ftc_list_name": "ftc_list.csv",
  "file_name_cleaned_ftc_list": "ftc_list_cleaned.csv",
}

APRIORI_INVERSE_ARGS = {
  "MIM_SUPPORT": 0.01,
  #"MAX_SUPPORT": 1, #  The item is present in all transactions, for small datasets tests
  "MAX_SUPPORT": 0.5, #  The item is present in 50% of transactions, for small datasets tests, but suport booleans 
  #"MAX_SUPPORT": 0.3, #  The item is present in 20% of transactions, for small datasets tests, small enums with 5 values
  #"MAX_SUPPORT": 0.1, #  The item is present in 10% of transactions, for small datasets tests, medium enums with 10 values
  #"MAX_SUPPORT": 0.06, #  The item is present in 6% of transactions, for medium datasets training set, enums with 15 values - Recomended
}

PM4PI_ARGS = {
  "TOP_K" : 3, # For tests with very small datasets
  #"TOP_K" : 5, # For tests with small datasets (10 tests sets)
  #"TOP_K__" : ?, # For tests with medium datasets (More than 20 tests sets)
  #"TOP_K__" : ?, # For tests with medium datasets (More than 50 tests sets)
}

ARCHIMATE_MODEL = {
  "file_path": "./archimate/",
  "archimate_file_name": "archimate_model.xml", 
}

SWAGGERS_FILE_PATH = {
  "file_path": "./docs/swaggers/",
}

DEVELOPER_PORTAL = {
  "url": "./docs/swaggers/",
}