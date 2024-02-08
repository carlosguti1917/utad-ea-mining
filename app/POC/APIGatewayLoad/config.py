# server
MONGO_DB_SERVER_1 = {
  "host": "192.168.0.15",
  "port": 27017,
}

MONGO_DB_SERVER = {
  "host": "mongodb://192.168.0.15:27017",
  "databasename": "eadatabase",
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
