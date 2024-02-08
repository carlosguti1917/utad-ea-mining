
#from Service.EventBuildMySQL import getLogs
from Service.EventBuildArango import getLogs
from repository import MongoDbRepository as mongo
from repository import ArangodbRepository as arangodb
from domain.Uri import Uri

print("start processing")
uri_str = "https://apiplatform.sensedia.com/sandbox/crm/clients/241/address"
client_id = "319b7e7d3767c27a0c19d988d4f20241"
method = "POST"
request_timestamp = "2022-06-25 11:01:00"
uri = Uri(None,  uri_str, client_id, method, "", request_timestamp)
uri2 = Uri(None, "https://apiplatform.sensedia.com/sandbox/crm/clients/241/teste", "319b7e7d3767c27a0c19d988d4f20241", method, "", "2022-06-25 11:02:00")


logs = getLogs()

# teste do find path no swagger a partir de uma URI
#mongo = mongo.MongoDbRepository.find_path_swagger(uri)

# teste find_uri_operation
#arangodb.ArangodbRepository.find_operation_uri(uri)
#arangodb.ArangodbRepository.create_operation_uri(uri)

#teste save_edge_correlation
#arangodb.ArangodbRepository.save_edge_correlation(uri, uri2)

print("End of processing")