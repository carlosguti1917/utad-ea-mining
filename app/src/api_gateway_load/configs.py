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
  "file_name": "EA Mining OntoUML Teste V1_3.owl",
}

FREQUENT_API_ATTRIBUTES = {
  "file_name": "frequent_attributes.ignore",
}