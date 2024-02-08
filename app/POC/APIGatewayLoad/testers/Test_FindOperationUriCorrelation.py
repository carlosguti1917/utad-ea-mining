import unittest

import repository.ArangodbRepository as arangodb
from domain.Uri import Uri

class Test_FindOperationUriCorrelation(unittest.TestCase):
    uri1 = Uri(None, "https://apiplatform.sensedia.com/sandbox/commerce/v1/carts", "319b7e7d3767c27a0c19d988d4f20001", "POST", "https://apiplatform.sensedia.com/sandbox/commerce/v1/carts/{id}", "2022/06/27 11:54:29 +0000")
    uri2 = Uri(None, "https://apiplatform.sensedia.com/sandbox/commerce/v1/carts/3456/itens",
               "319b7e7d3767c27a0c19d988d4f20001", "POST", "https://apiplatform.sensedia.com/sandbox/commerce/v1/carts/{id}/itens/{itemid}", "2022/06/27 11:55:25 +0000")

    arangodb.ArangodbRepository.find_operation_uri_correlation(uri1, uri2)


if __name__ == '__main__':
    unittest.main()
