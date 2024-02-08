import unittest

from repository import MongoDbRepository as mongo
from domain.Uri import Uri

class Test_FindFullPathSwagger():
    uri1 = "https://apiplatform.sensedia.com/sandbox/commerce/v1/carts/3456/itens"
    uri2 = "https://apiplatform.sensedia.com/sandbox/commerce/v1/carts/3456/itens?client_id=319b7e7d3767c2-f7a0c19d988d4f20001"


    # teste do find path no swagger a partir de uma URI
    path1 = mongo.MongoDbRepository.find_fullpath_swagger(uri1)
    path2 = mongo.MongoDbRepository.find_fullpath_swagger(uri2)

    print("path1", path1)
    print("path2", path2)


if __name__ == '__main__':
    #unittest.main()
    Test_FindFullPathSwagger()
